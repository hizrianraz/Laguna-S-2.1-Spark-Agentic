#!/usr/bin/env python3
"""Fixed agent_smoke runner for Laguna OpenAI-compatible servers.

Pass/fail only against the pinned cases.json — no free-form grading.
Fixed smoke runner
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


def load_cases(path: Path):
    data = json.loads(path.read_text())
    return data["cases"], data.get("version", 1)


def build_run_manifest(
    *,
    suite: str,
    version,
    cases_path: Path,
    base_url: str,
    model: str,
    temperature: float = 0.0,
    out_path: str | None = None,
    runner_path: str | Path | None = None,
) -> dict:
    """Provenance block attached to every smoke receipt (nulls stay null — fail closed).

    runner_path: optional override for wrappers (e.g. hermes_agent_smoke) so the
    stamped runner is the entrypoint script, not this helper module.
    """
    cases_path = Path(cases_path)
    runner_file = Path(runner_path).resolve() if runner_path else Path(__file__).resolve()
    try:
        cases_sha = hashlib.sha256(cases_path.read_bytes()).hexdigest()
    except OSError:
        cases_sha = None
    try:
        runner_sha = hashlib.sha256(runner_file.read_bytes()).hexdigest()
    except OSError:
        runner_sha = None
    git_head = None
    try:
        # Prefer pack root from helper location (…/eval/agent_smoke → pack root parents[2])
        root = Path(__file__).resolve().parents[2]
        git_head = (
            subprocess.check_output(
                ["git", "-C", str(root), "rev-parse", "HEAD"],
                stderr=subprocess.DEVNULL,
                timeout=5,
            )
            .decode()
            .strip()
        )
    except Exception:
        git_head = None
    return {
        "schema": "laguna.run_manifest/v1",
        "suite": suite,
        "suite_version": version,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "host": {
            "hostname": socket.gethostname(),
            "platform": platform.platform(),
            "python": sys.version.split()[0],
        },
        "runner": {
            "path": str(runner_file),
            "sha256": runner_sha,
        },
        "cases": {
            "path": str(cases_path.resolve()) if cases_path.exists() else str(cases_path),
            "sha256": cases_sha,
        },
        "request": {
            "base_url": base_url,
            "model": model,
            "temperature": temperature,
        },
        "pack_git_head": git_head,
        "out": out_path,
        "env_note": {
            "LAGUNA_MODEL": os.environ.get("LAGUNA_MODEL"),
            "OPENAI_BASE_URL": os.environ.get("OPENAI_BASE_URL"),
        },
        "protocol": "one-response protocol; tools validated not executed",
    }


def post_chat(base_url: str, api_key: str, model: str, messages, tools, temperature=0.0, max_tokens=512, timeout=180):
    body = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if tools:
        body["tools"] = tools
        body["tool_choice"] = "auto"
    req = urllib.request.Request(
        base_url.rstrip("/") + "/chat/completions",
        data=json.dumps(body).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "laguna-agent-smoke/1.0",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


def extract_message(resp):
    return resp["choices"][0]["message"]


def tool_names(msg):
    names = []
    for tc in msg.get("tool_calls") or []:
        fn = tc.get("function") or {}
        n = fn.get("name")
        if n:
            names.append(n)
    # some servers put calls in content as JSON — do not count as valid tools
    return names


def parse_args_map(msg):
    out = []
    for tc in msg.get("tool_calls") or []:
        fn = tc.get("function") or {}
        raw = fn.get("arguments") or "{}"
        try:
            args = json.loads(raw) if isinstance(raw, str) else raw
        except json.JSONDecodeError:
            args = {"__raw__": raw, "__invalid_json__": True}
        out.append({"name": fn.get("name"), "arguments": args})
    return out


def _is_valid_json_args(raw) -> bool:
    if raw is None:
        return True
    if not isinstance(raw, str):
        return True
    try:
        json.loads(raw if raw.strip() else "{}")
        return True
    except json.JSONDecodeError:
        return False


def sanitize_messages_for_server(messages):
    """Coerce historical assistant tool-call arguments to valid JSON.

    llama-server and similar engines re-parse prior tool_call.arguments and
    HTTP 500 on invalid JSON before the model runs. A Hermes-class client
    must not forward raw broken args; keep the tool error turn, replace the
    broken arguments string with a valid JSON envelope that preserves the raw
    text for context. This keeps repair_04 a model test, not an engine crash.
    """
    out = []
    for m in messages:
        mm = dict(m)
        tcs = mm.get("tool_calls")
        if tcs:
            new_tcs = []
            for tc in tcs:
                tc2 = dict(tc)
                fn = dict(tc2.get("function") or {})
                raw = fn.get("arguments")
                if not _is_valid_json_args(raw):
                    fn["arguments"] = json.dumps(
                        {
                            "_invalid_json_arguments": True,
                            "_raw": raw if isinstance(raw, str) else repr(raw),
                        },
                        ensure_ascii=False,
                    )
                tc2["function"] = fn
                new_tcs.append(tc2)
            mm["tool_calls"] = new_tcs
        out.append(mm)
    return out



def _norm_path(p) -> str:
    """Normalize path strings for equality / sandbox checks (smoke labels only)."""
    if p is None:
        return ""
    if not isinstance(p, str):
        p = str(p)
    s = p.strip().replace("\\", "/")
    # drop surrounding quotes models sometimes emit
    if len(s) >= 2 and s[0] == s[-1] and s[0] in ("'", '"'):
        s = s[1:-1]
    while "//" in s:
        s = s.replace("//", "/")
    # strip leading ./ segments
    while s.startswith("./"):
        s = s[2:]
    # collapse trailing slash except root
    if len(s) > 1 and s.endswith("/"):
        s = s.rstrip("/")
    return s


def _path_under_sandbox(p) -> bool:
    """True iff path is a relative sandbox/... path (no abs, no .., no ~)."""
    n = _norm_path(p)
    if not n:
        return False
    if n.startswith("/") or n.startswith("~") or n.startswith("file:"):
        return False
    parts = [x for x in n.split("/") if x and x != "."]
    if any(x == ".." for x in parts):
        return False
    if not parts:
        return False
    return parts[0] == "sandbox"


def _arg_values_equal(got, want, *, path_key: bool = False) -> bool:
    if path_key:
        return _norm_path(got) == _norm_path(want)
    # bool-ish / number / string soft equality for content pins
    if isinstance(want, bool) or isinstance(got, bool):
        return bool(got) is bool(want) if type(got) is type(want) else got == want
    if isinstance(want, (int, float)) and isinstance(got, (int, float)):
        return got == want
    if isinstance(want, str) or isinstance(got, str):
        return str(got) == str(want)
    return got == want


def _match_args_equals(args: dict, expect_map: dict) -> tuple[bool, str]:
    """Strict key equality. Path-like keys compared via _norm_path."""
    if args.get("__invalid_json__"):
        return False, "invalid json args"
    path_keys = {"path", "file", "filepath", "filename", "dest", "destination", "target"}
    for k, want in expect_map.items():
        if k not in args:
            return False, f"missing key {k}"
        if not _arg_values_equal(args[k], want, path_key=(k.lower() in path_keys)):
            return False, f"args_equals mismatch on {k}: got={args.get(k)!r} want={want!r}"
    return True, "ok"


def _match_args_contains(args: dict, expect_map: dict) -> tuple[bool, str]:
    """Key presence; if expect value is not True/1, also require equality (path-normalized when path-like)."""
    if args.get("__invalid_json__"):
        return False, "invalid json args"
    path_keys = {"path", "file", "filepath", "filename", "dest", "destination", "target"}
    for k, want in expect_map.items():
        if k not in args:
            return False, f"missing key {k}"
        # True / 1 → presence only (legacy)
        if want is True or want == 1:
            continue
        if want is False or want == 0:
            # explicitly forbidden presence already handled by presence; treat as must be falsey
            if args[k]:
                return False, f"key {k} should be empty/false"
            continue
        if not _arg_values_equal(args[k], want, path_key=(k.lower() in path_keys)):
            return False, f"args_contains value mismatch on {k}: got={args.get(k)!r} want={want!r}"
    return True, "ok"


def _first_tool_args(calls, want_name: str):
    for c in calls:
        if c["name"] == want_name:
            return c["arguments"]
    return None


def judge_any_of_tools(exp, names) -> tuple[bool, str]:
    allowed = set(exp.get("any_of_tools") or exp.get("allowed") or [])
    if not names:
        return False, "no tool called"
    if any(n in allowed for n in names) and all(n in allowed for n in names):
        return True, "ok"
    return False, f"tools {names} not subset/hit of {sorted(allowed)}"


def judge(case, msg) -> tuple[bool, str]:
    exp = case["expect"]
    et = exp["type"]
    content = msg.get("content") or ""
    names = tool_names(msg)
    calls = parse_args_map(msg)

    if et == "tool_call":
        # Accept schema form {type: tool_call, any_of_tools: [...]} without KeyError
        if "tool" not in exp and exp.get("any_of_tools"):
            return judge_any_of_tools(exp, names)
        want = exp["tool"]
        if want not in names:
            return False, f"expected tool {want}, got {names}"
        args = _first_tool_args(calls, want)
        if args is None:
            return False, f"expected tool {want}, got {names}"

        # Optional: refuse non-sandbox paths when path_must_be_sandbox / sandbox_path
        if exp.get("path_must_be_sandbox") or exp.get("sandbox_path"):
            p = args.get("path") if isinstance(args, dict) else None
            if not _path_under_sandbox(p):
                return False, f"path not under sandbox/: {p!r}"

        # Optional: path_equals (normalized)
        if exp.get("path_equals") is not None:
            p = args.get("path") if isinstance(args, dict) else None
            if _norm_path(p) != _norm_path(exp["path_equals"]):
                return False, f"path_equals mismatch: got={p!r} want={exp['path_equals']!r}"

        # Strict args_equals (full pin)
        if exp.get("args_equals"):
            ok, why = _match_args_equals(args if isinstance(args, dict) else {}, exp["args_equals"])
            if not ok:
                return False, f"tool {want} {why}"
            # still allow extra keys unless exact_only
            if exp.get("exact_args_only"):
                extra = set(args) - set(exp["args_equals"]) - {"__raw__", "__invalid_json__"}
                if extra:
                    return False, f"unexpected arg keys {sorted(extra)}"

        # Legacy / hybrid args_contains — presence or value pins
        if exp.get("args_contains"):
            ok, why = _match_args_contains(args if isinstance(args, dict) else {}, exp["args_contains"])
            if not ok:
                return False, f"tool {want} {why}"

        # Optional content forbid on tool args (branding / path escapes as smoke labels)
        forbid = exp.get("args_content_forbids") or []
        if forbid and isinstance(args, dict):
            blob = json.dumps(args, ensure_ascii=False).lower()
            for f in forbid:
                if str(f).lower() in blob:
                    return False, f"forbidden arg content {f!r}"

        return True, "ok"

    if et == "any_of_tools":
        return judge_any_of_tools(exp, names)

    if et == "no_extra_tools":
        allowed = set(exp.get("allowed") or [])
        if any(n not in allowed for n in names):
            return False, f"invented or disallowed tools {names}"
        # pass if refuses in content OR uses only allowed tools OR no tools + refusal-ish
        if names and all(n in allowed for n in names):
            return True, "used only allowed"
        low = content.lower()
        if any(w in low for w in ["cannot", "can't", "unable", "not available", "no tool", "don't have", "do not have", "refuse", "not possible", "isn't available", "is not available"]):
            return True, "refused without inventing"
        if not names and content.strip():
            # soft pass: answered without tools and without inventing
            if not re.search(r"\b(shell|sudo|browser_open|network_scan|vector_db|finetune)\b", low):
                return True, "answered without disallowed tools"
        return False, f"no clear refusal; tools={names} content={content[:120]!r}"

    if et == "content_contains":
        needle = exp["needle"]
        if names:
            return False, f"unexpected tools {names}"
        if needle in content:
            return True, "ok"
        return False, f"missing needle {needle!r}"

    if et == "any_ok_tools":
        allowed = set(exp.get("allowed") or [])
        if names and any(n not in allowed for n in names):
            return False, f"disallowed tools {names}"
        forb = exp.get("content_forbids") or []
        for f in forb:
            if f in content:
                return False, f"forbidden content {f}"
        if names or content.strip():
            return True, "ok"
        return False, "empty"

    return False, f"unknown expect type {et}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default="http://127.0.0.1:8000/v1")
    ap.add_argument("--api-key", default="sk-local")
    ap.add_argument("--model", default="local-laguna")
    ap.add_argument("--cases", default=str(Path(__file__).with_name("cases.json")))
    # Default receipt path — smoke always leaves evidence unless --out "" overrides empty intentionally
    _default_out = str(Path(__file__).resolve().parents[2] / "results" / "agent_smoke_latest.json")
    ap.add_argument("--out", default=_default_out, help="receipt JSON path (default: results/agent_smoke_latest.json)")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--ids", default="", help="comma ids")
    ap.add_argument("--sleep", type=float, default=0.2)
    args = ap.parse_args()

    cases, ver = load_cases(Path(args.cases))
    if args.ids:
        want = set(args.ids.split(","))
        cases = [c for c in cases if c["id"] in want]
    if args.limit:
        cases = cases[: args.limit]

    results = []
    n_pass = 0
    t0 = time.time()
    for c in cases:
        row = {"id": c["id"], "category": c["category"], "pass": False, "reason": "", "latency_s": None}
        t1 = time.time()
        try:
            # strip None content weirdness for JSON; sanitize invalid prior tool args
            messages = []
            for m in c["messages"]:
                mm = dict(m)
                if mm.get("content") is None and mm.get("tool_calls"):
                    mm["content"] = ""
                messages.append(mm)
            messages = sanitize_messages_for_server(messages)
            resp = post_chat(args.base_url, args.api_key, args.model, messages, c.get("tools") or [])
            msg = extract_message(resp)
            ok, reason = judge(c, msg)
            row["pass"] = ok
            row["reason"] = reason
            row["message"] = {
                "content": (msg.get("content") or "")[:500],
                "tool_calls": msg.get("tool_calls"),
            }
            if ok:
                n_pass += 1
        except urllib.error.HTTPError as e:
            row["reason"] = f"HTTP {e.code}: {e.read()[:200]!r}"
        except Exception as e:
            row["reason"] = f"{type(e).__name__}: {e}"
        row["latency_s"] = round(time.time() - t1, 3)
        results.append(row)
        flag = "PASS" if row["pass"] else "FAIL"
        print(f"{flag} {c['id']} ({c['category']}) {row['reason'][:80]}")
        time.sleep(args.sleep)

    summary = {
        "suite": "agent_smoke",
        "smoke_class": "format_routing_regression",
        "smoke_note": "smoke!=headline; tools validated not executed; not long-horizon agent reliability",
        "launch_class": "tool_format_smoke",
        "version": ver,
        "model": args.model,
        "base_url": args.base_url,
        "n": len(results),
        "passed": n_pass,
        "failed": len(results) - n_pass,
        "pass_rate": round(n_pass / len(results), 4) if results else 0.0,
        "elapsed_s": round(time.time() - t0, 2),
        "by_category": {},
        "results": results,
    }
    cats = {}
    for r in results:
        d = cats.setdefault(r["category"], {"n": 0, "passed": 0})
        d["n"] += 1
        d["passed"] += int(r["pass"])
    summary["by_category"] = cats
    summary["run_manifest"] = build_run_manifest(
        suite="agent_smoke",
        version=ver,
        cases_path=Path(args.cases),
        base_url=args.base_url,
        model=args.model,
        temperature=0.0,
        out_path=args.out or None,
    )

    text = json.dumps(summary, indent=2)
    if args.out:
        outp = Path(args.out)
        outp.parent.mkdir(parents=True, exist_ok=True)
        outp.write_text(text + "\n")
        print("wrote", args.out)
    print(
        f"SUMMARY pass={n_pass}/{len(results)} rate={summary['pass_rate']} elapsed={summary['elapsed_s']}s"
    )
    return 0 if n_pass == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
