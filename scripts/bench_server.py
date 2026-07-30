#!/usr/bin/python3 -I
"""Lightweight OpenAI server bench at 2k/8k-shaped prompts."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import resource
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

NO_PROXY_OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))
CANONICAL_SUITE = "server_bench"
CANONICAL_VERSION = 1
CANONICAL_BASE_URL = "http://127.0.0.1:8000/v1"
CANONICAL_MODEL = "local-laguna"
CANONICAL_TEMPERATURE = 0.0
CANONICAL_MARKS = ("2k", "8k")
CANONICAL_MAX_TOKENS = 32
CANONICAL_SENTINEL = "OK"
CANONICAL_CONTRACT_ID = "server_bench/v1"
NON_AUTHORITATIVE_EXIT = 4


def _reject_json_constant(value):
    raise ValueError(f"non-standard JSON constant: {value}")


def _unique_json_object(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError(f"duplicate JSON object key: {key}")
        obj[key] = value
    return obj


def parse_json_strict(raw: str):
    return json.loads(raw, parse_constant=_reject_json_constant, object_pairs_hook=_unique_json_object)


def validate_chat_result(data, usage, expected_model=None):
    """Return response content only when the receipt has positive token evidence."""
    if not isinstance(data, dict) or data.get("error") is not None:
        raise ValueError("response is not an error-free JSON object")
    choices = data.get("choices")
    if not isinstance(choices, list) or len(choices) != 1:
        raise ValueError("response must contain exactly one choice")
    message = choices[0].get("message") if isinstance(choices[0], dict) else None
    if not isinstance(message, dict) or message.get("role") != "assistant":
        raise ValueError("response message role must equal 'assistant'")
    content = message.get("content") if isinstance(message, dict) else None
    if not isinstance(content, str) or not content.strip():
        raise ValueError("response content must be non-empty")
    if content.strip() != CANONICAL_SENTINEL:
        raise ValueError(
            f"response must equal the benchmark sentinel {CANONICAL_SENTINEL!r}, got {content!r}"
        )
    if expected_model is not None and data.get("model") != expected_model:
        raise ValueError(f"response model must equal {expected_model!r}")
    prompt_tokens = usage.get("prompt_tokens") if isinstance(usage, dict) else None
    completion_tokens = usage.get("completion_tokens") if isinstance(usage, dict) else None
    if isinstance(prompt_tokens, bool) or not isinstance(prompt_tokens, int) or prompt_tokens <= 0:
        raise ValueError("prompt_tokens must be a positive integer")
    if isinstance(completion_tokens, bool) or not isinstance(completion_tokens, int) or completion_tokens <= 0:
        raise ValueError("completion_tokens must be a positive integer")
    return content, prompt_tokens, completion_tokens


def validate_marks(marks) -> list[str]:
    """Require the complete, non-duplicated launch benchmark profile."""
    if not isinstance(marks, list) or len(marks) != 2 or set(marks) != {"2k", "8k"}:
        raise ValueError("benchmark requires exactly one --ctx-mark 2k and one --ctx-mark 8k")
    return marks


def assess_request_profile(*, base_url: str, model: str, marks: list[str]) -> dict:
    actual = {
        "suite": CANONICAL_SUITE,
        "version": CANONICAL_VERSION,
        "base_url": base_url,
        "model": model,
        "temperature": CANONICAL_TEMPERATURE,
        "ctx_marks": list(marks),
        "max_tokens": CANONICAL_MAX_TOKENS,
        "sentinel": CANONICAL_SENTINEL,
    }
    expected = {
        "suite": CANONICAL_SUITE,
        "version": CANONICAL_VERSION,
        "base_url": CANONICAL_BASE_URL,
        "model": CANONICAL_MODEL,
        "temperature": CANONICAL_TEMPERATURE,
        "ctx_marks": list(CANONICAL_MARKS),
        "max_tokens": CANONICAL_MAX_TOKENS,
        "sentinel": CANONICAL_SENTINEL,
    }
    return {
        "actual": actual,
        "expected": expected,
        "canonical_request_profile": actual == expected,
    }


def build_run_manifest(*, base_url: str, model: str, marks: list[str], out_path: str) -> dict:
    runner = Path(__file__).resolve()
    root = runner.parents[1]
    runner_sha256 = hashlib.sha256(runner.read_bytes()).hexdigest()
    git_env = {
        "PATH": "/usr/bin:/bin",
        "LC_ALL": "C",
        "LANG": "C",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": "/dev/null",
    }
    git_head = None
    git_status = None
    git_error = None
    try:
        git_head = (
            subprocess.check_output(
                ["/usr/bin/git", "-C", str(root), "rev-parse", "HEAD"],
                stderr=subprocess.DEVNULL,
                timeout=5,
                env=git_env,
            )
            .decode()
            .strip()
        )
        git_status = (
            subprocess.check_output(
                [
                    "/usr/bin/git",
                    "-C",
                    str(root),
                    "status",
                    "--porcelain=v1",
                    "--untracked-files=all",
                ],
                stderr=subprocess.DEVNULL,
                timeout=10,
                env=git_env,
            )
            .decode()
            .splitlines()
        )
    except (OSError, subprocess.SubprocessError) as exc:
        git_head = None
        git_status = None
        git_error = f"{type(exc).__name__}: Git provenance unavailable"
    return {
        "schema": "laguna.run_manifest/v1",
        "suite": CANONICAL_SUITE,
        "version": CANONICAL_VERSION,
        "runner": {"path": str(runner), "sha256": runner_sha256},
        "request": {
            "base_url": base_url,
            "model": model,
            "temperature": CANONICAL_TEMPERATURE,
            "ctx_marks": list(marks),
            "max_tokens": CANONICAL_MAX_TOKENS,
            "sentinel": CANONICAL_SENTINEL,
        },
        "pack_git_head": git_head,
        "pack_git_clean": git_status == [],
        "pack_git_status": git_status,
        "pack_git_error": git_error,
        "provenance_complete": bool(
            isinstance(git_head, str)
            and re.fullmatch(r"[0-9a-f]{40}", git_head)
            and re.fullmatch(r"[0-9a-f]{64}", runner_sha256)
            and git_status == []
        ),
        "out": out_path,
    }
def write_new_receipt(path: str, payload: dict) -> Path:
    root = Path(__file__).resolve().parents[1]
    out = Path(os.path.abspath(os.path.expanduser(path)))
    if out == root / "results" / "server_bench.json":
        raise ValueError("refusing to overwrite locked historical results/server_bench.json")
    component = out
    while component != component.parent:
        if component.is_symlink():
            raise ValueError(f"receipt path contains a symlink component: {component}")
        component = component.parent
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists() or out.is_symlink():
        raise FileExistsError(f"refusing to overwrite existing receipt: {out}")
    fd, temporary = tempfile.mkstemp(prefix=f".{out.name}.", suffix=".tmp", dir=out.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.link(temporary, out, follow_symlinks=False)
        os.unlink(temporary)
    except Exception:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise
    return out


def chat(base, key, model, messages, max_tokens):
    body = {
        "model": model,
        "messages": messages,
        "temperature": 0.0,
        "max_tokens": max_tokens,
    }
    req = urllib.request.Request(
        base.rstrip("/") + "/chat/completions",
        data=json.dumps(body).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
            "User-Agent": "laguna-spark-bench/0.1",
        },
        method="POST",
    )
    t0 = time.perf_counter()
    with NO_PROXY_OPENER.open(req, timeout=600) as resp:
        data = parse_json_strict(resp.read().decode())
    dt = time.perf_counter() - t0
    usage = data.get("usage") or {}
    return data, dt, usage


def main():
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    api_key = os.environ.pop("OPENAI_API_KEY", "")
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default=CANONICAL_BASE_URL)
    ap.add_argument("--model", default=CANONICAL_MODEL)
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    ap.add_argument("--out", default=f"results/server_bench_{stamp}.json")
    ap.add_argument("--ctx-mark", action="append", default=[])
    args = ap.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9._~-]{32,256}", api_key):
        ap.error("OPENAI_API_KEY must be a 32..256 character URL-safe bearer")
    if not args.out.strip():
        ap.error("--out must be a non-empty path")
    marks = args.ctx_mark or list(CANONICAL_MARKS)
    try:
        marks = validate_marks(marks)
    except ValueError as exc:
        ap.error(str(exc))
    request_profile = assess_request_profile(
        base_url=args.base_url,
        model=args.model,
        marks=marks,
    )

    filler = ("alpha beta gamma delta " * 200).strip()
    plans = {
        "2k": filler[:8000],
        "8k": (filler * 4)[:32000],
    }
    rows = []
    for mark in marks:
        prompt = plans.get(mark) or filler
        messages = [
            {"role": "system", "content": "Reply with exactly: OK"},
            {"role": "user", "content": f"Context mark {mark}. Ignore the bulk.\n\n{prompt}\n\nSay OK."},
        ]
        # warmup
        try:
            chat(args.base_url, api_key, args.model, messages[:1] + [{"role": "user", "content": "hi"}], 8)
        except Exception as e:
            print("warmup fail", e)
        try:
            data, dt, usage = chat(
                args.base_url,
                api_key,
                args.model,
                messages,
                CANONICAL_MAX_TOKENS,
            )
            content, prompt_t, comp = validate_chat_result(data, usage, expected_model=args.model)
            tps = (comp / dt) if dt > 0 else None
            row = {
                "mark": mark,
                "latency_s": round(dt, 3),
                "prompt_tokens": prompt_t,
                "completion_tokens": comp,
                "completion_tok_s": round(tps, 3) if tps is not None else None,
                "content": content[:80],
            }
        except Exception as e:
            row = {"mark": mark, "error": f"{type(e).__name__}: {e}"}
        print(row)
        rows.append(row)

    n_ok = sum(1 for row in rows if "error" not in row)
    measurement_complete = bool(rows and n_ok == len(rows))
    request_profile_eligible = request_profile["canonical_request_profile"]
    run_manifest = build_run_manifest(
        base_url=args.base_url,
        model=args.model,
        marks=marks,
        out_path=args.out,
    )
    authority_eligible = bool(
        measurement_complete
        and request_profile_eligible
        and run_manifest["provenance_complete"]
    )
    if authority_eligible:
        status = "PASS"
    elif not run_manifest["provenance_complete"]:
        status = "DIAGNOSTIC_PASS" if measurement_complete else "DIAGNOSTIC_FAIL"
    elif request_profile_eligible:
        status = "FAIL"
    else:
        status = "DIAGNOSTIC_PASS" if measurement_complete else "DIAGNOSTIC_FAIL"
    out = {
        "suite": CANONICAL_SUITE,
        "version": CANONICAL_VERSION,
        "status": status,
        "base_url": args.base_url,
        "model": args.model,
        "temperature": CANONICAL_TEMPERATURE,
        "ctx_marks": marks,
        "n_ok": n_ok,
        "n_total": len(rows),
        "measurement_complete": measurement_complete,
        "run_scope": (
            "authoritative_canonical_profile"
            if authority_eligible
            else "diagnostic_non_authoritative"
        ),
        "request_profile_eligible": request_profile_eligible,
        "authority_scope": "suite_only",
        "authority_eligible": authority_eligible,
        "suite_authority_eligible": authority_eligible,
        "suite_green": authority_eligible,
        "bench_green": authority_eligible,
        "release_green": False,
        "gate_clearance": False,
        "contract": {
            "id": CANONICAL_CONTRACT_ID,
            "runner_sha256": run_manifest["runner"]["sha256"],
            "eligible": authority_eligible,
        },
        "request_profile": request_profile,
        "run_manifest": run_manifest,
        "rows": rows,
        "ts": time.time(),
    }
    receipt = write_new_receipt(args.out, out)
    print("wrote", receipt)
    if not request_profile_eligible:
        print(
            "NON-AUTHORITATIVE: noncanonical benchmark request profile is diagnostic only",
            file=sys.stderr,
        )
        return NON_AUTHORITATIVE_EXIT
    if not run_manifest["provenance_complete"]:
        print("FAIL provenance is incomplete or the pack worktree is dirty", file=sys.stderr)
        return 3
    return 0 if authority_eligible else 1


if __name__ == "__main__":
    raise SystemExit(main())
