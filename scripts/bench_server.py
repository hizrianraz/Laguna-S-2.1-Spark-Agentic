#!/usr/bin/env python3
"""Lightweight OpenAI server bench at 2k/8k-shaped prompts."""

from __future__ import annotations

import argparse
import json
import time
import urllib.request


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
    with urllib.request.urlopen(req, timeout=600) as resp:
        data = json.loads(resp.read().decode())
    dt = time.perf_counter() - t0
    usage = data.get("usage") or {}
    return data, dt, usage


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default="http://127.0.0.1:8000/v1")
    ap.add_argument("--api-key", default="sk-local")
    ap.add_argument("--model", default="local-laguna")
    ap.add_argument("--out", default="results/server_bench.json")
    ap.add_argument("--ctx-mark", action="append", default=[])
    args = ap.parse_args()
    marks = args.ctx_mark or ["2k", "8k"]

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
            chat(args.base_url, args.api_key, args.model, messages[:1] + [{"role": "user", "content": "hi"}], 8)
        except Exception as e:
            print("warmup fail", e)
        try:
            data, dt, usage = chat(args.base_url, args.api_key, args.model, messages, 32)
            comp = usage.get("completion_tokens") or 0
            prompt_t = usage.get("prompt_tokens") or 0
            tps = (comp / dt) if dt > 0 else None
            row = {
                "mark": mark,
                "latency_s": round(dt, 3),
                "prompt_tokens": prompt_t,
                "completion_tokens": comp,
                "completion_tok_s": round(tps, 3) if tps is not None else None,
                "content": ((data["choices"][0]["message"].get("content")) or "")[:80],
            }
        except Exception as e:
            row = {"mark": mark, "error": f"{type(e).__name__}: {e}"}
        print(row)
        rows.append(row)

    out = {
        "base_url": args.base_url,
        "model": args.model,
        "rows": rows,
        "ts": time.time(),
    }
    from pathlib import Path

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out, indent=2) + "\n")
    print("wrote", args.out)


if __name__ == "__main__":
    main()
