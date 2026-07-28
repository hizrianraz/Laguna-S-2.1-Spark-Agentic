#!/usr/bin/env python3
"""Hermes-class agent_smoke v2 runner for Laguna OpenAI-compatible servers.

Reuses agent_smoke judges + prior-tool-arg sanitization.
Suite is named hermes_agent_smoke — branding is tool-agent family shape only,
not a Nous Research endorsement.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENT_SMOKE = ROOT / "agent_smoke" / "run_smoke.py"


def _load_agent_smoke():
    spec = importlib.util.spec_from_file_location("laguna_agent_smoke", AGENT_SMOKE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {AGENT_SMOKE}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    ap = argparse.ArgumentParser(description="Hermes-class agent smoke v2")
    ap.add_argument("--base-url", default="http://127.0.0.1:8000/v1")
    ap.add_argument("--api-key", default="sk-local")
    ap.add_argument("--model", default="local-laguna")
    ap.add_argument("--cases", default=str(Path(__file__).with_name("cases.json")))
    ap.add_argument("--out", default="")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--ids", default="", help="comma ids")
    ap.add_argument("--sleep", type=float, default=0.2)
    ap.add_argument("--temperature", type=float, default=0.0)
    args = ap.parse_args()

    smoke = _load_agent_smoke()
    cases_path = Path(args.cases)
    data = json.loads(cases_path.read_text())
    cases = data["cases"]
    ver = data.get("version", 2)
    suite = data.get("suite", "hermes_agent_smoke")
    branding = data.get("branding", "")
    ship_min = data.get("ship_min")
    ship_stretch = data.get("ship_stretch", len(cases))

    if args.ids:
        want = set(args.ids.split(","))
        cases = [c for c in cases if c["id"] in want]
    if args.limit:
        cases = cases[: args.limit]

    results = []
    n_pass = 0
    t0 = time.time()
    for c in cases:
        row = {
            "id": c["id"],
            "category": c["category"],
            "pass": False,
            "reason": "",
            "latency_s": None,
        }
        t1 = time.time()
        try:
            messages = []
            for m in c["messages"]:
                mm = dict(m)
                if mm.get("content") is None and mm.get("tool_calls"):
                    mm["content"] = ""
                messages.append(mm)
            messages = smoke.sanitize_messages_for_server(messages)
            resp = smoke.post_chat(
                args.base_url,
                args.api_key,
                args.model,
                messages,
                c.get("tools") or [],
                temperature=args.temperature,
            )
            msg = smoke.extract_message(resp)
            ok, reason = smoke.judge(c, msg)
            row["pass"] = ok
            row["reason"] = reason
            row["message"] = {
                "content": (msg.get("content") or "")[:500],
                "tool_calls": msg.get("tool_calls"),
            }
            if ok:
                n_pass += 1
        except urllib.error.HTTPError as e:
            body = e.read()[:200]
            row["reason"] = f"HTTP {e.code}: {body!r}"
        except Exception as e:
            row["reason"] = f"{type(e).__name__}: {e}"
        row["latency_s"] = round(time.time() - t1, 3)
        results.append(row)
        flag = "PASS" if row["pass"] else "FAIL"
        print(f"{flag} {c['id']} ({c['category']}) {row['reason'][:100]}")
        time.sleep(args.sleep)

    cats = {}
    for r in results:
        d = cats.setdefault(r["category"], {"n": 0, "passed": 0})
        d["n"] += 1
        d["passed"] += int(r["pass"])

    summary = {
        "suite": suite,
        "version": ver,
        "branding": branding,
        "model": args.model,
        "base_url": args.base_url,
        "n": len(results),
        "passed": n_pass,
        "failed": len(results) - n_pass,
        "pass_rate": round(n_pass / len(results), 4) if results else 0.0,
        "elapsed_s": round(time.time() - t0, 2),
        "ship_min": ship_min,
        "ship_stretch": ship_stretch,
        "meets_ship_min": (n_pass >= ship_min) if ship_min is not None else None,
        "meets_ship_stretch": n_pass >= int(ship_stretch or 0),
        "by_category": cats,
        "results": results,
    }
    # Reuse agent_smoke provenance helper when present (same schema).
    # Pass this entrypoint as runner_path so hermes is not stamped as run_smoke.py.
    if hasattr(smoke, "build_run_manifest"):
        summary["run_manifest"] = smoke.build_run_manifest(
            suite=suite,
            version=ver,
            cases_path=cases_path,
            base_url=args.base_url,
            model=args.model,
            temperature=args.temperature,
            out_path=args.out or None,
            runner_path=Path(__file__).resolve(),
        )

    text = json.dumps(summary, indent=2)
    if args.out:
        outp = Path(args.out)
        outp.parent.mkdir(parents=True, exist_ok=True)
        outp.write_text(text + "\n")
        print("wrote", outp)
    print(
        f"SUMMARY suite={suite} pass={n_pass}/{len(results)} "
        f"rate={summary['pass_rate']} elapsed={summary['elapsed_s']}s "
        f"ship_min={summary['meets_ship_min']} stretch={summary['meets_ship_stretch']}"
    )
    # exit 0 if full pass; 2 if below ship_min; 1 otherwise
    if n_pass == len(results):
        return 0
    if ship_min is not None and n_pass < ship_min:
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
