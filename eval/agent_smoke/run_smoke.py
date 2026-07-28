#!/usr/bin/env python3
"""Fixed agent_smoke runner for Laguna OpenAI-compatible servers.

Pass/fail only against the pinned cases.json — no free-form grading.
personal fixed smoke runner
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


def load_cases(path: Path):
    data = json.loads(path.read_text())
    return data["cases"], data.get("version", 1)


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


def judge(case, msg) -> tuple[bool, str]:
    exp = case["expect"]
    et = exp["type"]
    content = msg.get("content") or ""
    names = tool_names(msg)
    calls = parse_args_map(msg)

    if et == "tool_call":
        want = exp["tool"]
        if want not in names:
            # allow any_of variant mixed in
            return False, f"expected tool {want}, got {names}"
        if exp.get("args_contains"):
            matched = False
            for c in calls:
                if c["name"] != want:
                    continue
                args = c["arguments"]
                if args.get("__invalid_json__"):
                    continue
                ok = True
                for k in exp["args_contains"]:
                    if k not in args:
                        ok = False
                        break
                if ok:
                    matched = True
                    break
            if not matched:
                return False, f"tool {want} missing required arg keys {list(exp['args_contains'])}"
        return True, "ok"

    if et == "any_of_tools":
        allowed = set(exp["any_of_tools"])
        if not names:
            return False, "no tool called"
        if any(n in allowed for n in names) and all(n in allowed for n in names):
            return True, "ok"
        return False, f"tools {names} not subset/hit of {sorted(allowed)}"

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
    ap.add_argument("--out", default="")
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
            # strip None content weirdness for JSON
            messages = []
            for m in c["messages"]:
                mm = dict(m)
                if mm.get("content") is None and mm.get("tool_calls"):
                    mm["content"] = ""
                messages.append(mm)
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

    text = json.dumps(summary, indent=2)
    if args.out:
        Path(args.out).write_text(text + "\n")
        print("wrote", args.out)
    print(
        f"SUMMARY pass={n_pass}/{len(results)} rate={summary['pass_rate']} elapsed={summary['elapsed_s']}s"
    )
    return 0 if n_pass == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
