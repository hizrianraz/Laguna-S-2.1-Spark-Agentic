#!/usr/bin/python3 -I
"""Hermes-class agent_smoke runner for Laguna OpenAI-compatible servers.

Default cases.json = hardened canonical v4 (27); locked v2 receipts stay historical.
Pass --cases cases_layer_b_v3.json for the Layer B long-horizon expansion (35).
Reuses agent_smoke judges + prior-tool-arg sanitization. Branding is tool-agent
family shape only — not a Nous endorsement.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import resource
import sys
import time
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENT_SMOKE = ROOT / "agent_smoke" / "run_smoke.py"
CANONICAL_CASES_PATH = Path(__file__).resolve().with_name("cases.json")
CANONICAL_CASES_SHA256 = "748f152eb8ceeedb4f04bef336263519bf5739f4e5e3027f3ec56d5ae080ad89"
CANONICAL_SUITE = "hermes_agent_smoke"
CANONICAL_VERSION = 4
CANONICAL_BASE_URL = "http://127.0.0.1:8000/v1"
CANONICAL_MODEL = "local-laguna"
CANONICAL_TEMPERATURE = 0.0
CANONICAL_CONTRACT_ID = "hermes_agent_smoke/v4"
CANONICAL_CASE_IDS = (
    "term_01", "term_02", "term_03",
    "files_01", "files_02", "files_03", "files_04",
    "web_01", "web_02",
    "multi_01", "multi_02", "multi_03",
    "turn_01", "turn_02", "turn_03", "turn_04",
    "repair_01", "repair_02",
    "noinv_01", "noinv_02", "noinv_03",
    "browse_01", "mem_01", "cron_01", "args_01", "args_02", "safe_01",
)


def _load_agent_smoke():
    spec = importlib.util.spec_from_file_location("laguna_agent_smoke", AGENT_SMOKE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {AGENT_SMOKE}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    ap = argparse.ArgumentParser(description="Hermes-class agent smoke hardened v4")
    ap.add_argument("--base-url", default="http://127.0.0.1:8000/v1")
    ap.add_argument("--api-key", default=os.environ.get("OPENAI_API_KEY", ""))
    ap.add_argument("--api-key-file", default="", help="mode-0600 file containing the local bearer")
    ap.add_argument("--model", default="local-laguna")
    ap.add_argument("--cases", default=str(CANONICAL_CASES_PATH))
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    default_out = str(Path(__file__).resolve().parents[2] / "results" / f"hermes_agent_smoke_{stamp}.json")
    ap.add_argument("--out", default=default_out, help="new receipt path; existing files are never overwritten")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--ids", default="", help="comma ids")
    ap.add_argument("--sleep", type=float, default=0.2)
    ap.add_argument("--temperature", type=float, default=0.0)
    args = ap.parse_args()

    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    os.environ.pop("OPENAI_API_KEY", None)
    if args.api_key_file:
        args.api_key = Path(args.api_key_file).read_text(encoding="utf-8").strip()

    if not re.fullmatch(r"[A-Za-z0-9._~-]{32,256}", args.api_key):
        ap.error("a 32..256 character URL-safe bearer is required via --api-key-file, --api-key, or OPENAI_API_KEY")
    if args.limit < 0:
        ap.error("--limit must be zero or positive")
    if not args.out.strip():
        ap.error("--out must be a non-empty, new receipt path")

    smoke = _load_agent_smoke()
    cases_path = Path(args.cases)
    data = json.loads(cases_path.read_text())
    catalog_cases, ver = smoke.load_cases(cases_path)
    cases = list(catalog_cases)
    suite = data.get("suite", "hermes_agent_smoke")
    branding = data.get("branding", "")
    ship_min = data.get("ship_min")
    ship_stretch = data.get("ship_stretch", len(cases))

    if args.ids:
        want = {case_id.strip() for case_id in args.ids.split(",") if case_id.strip()}
        available = {case["id"] for case in cases}
        missing = sorted(want - available)
        if missing:
            ap.error(f"unknown case id(s): {','.join(missing)}")
        cases = [c for c in cases if c["id"] in want]
    if args.limit:
        cases = cases[: args.limit]
    if not cases:
        ap.error("no cases selected")

    catalog_status = smoke.assess_catalog_run(
        cases_path=cases_path,
        catalog_cases=catalog_cases,
        selected_cases=cases,
        canonical_path=CANONICAL_CASES_PATH,
        canonical_sha256=CANONICAL_CASES_SHA256,
        canonical_ids=CANONICAL_CASE_IDS,
    )
    request_profile = smoke.assess_request_profile(
        suite=suite,
        version=ver,
        base_url=args.base_url,
        model=args.model,
        temperature=args.temperature,
        canonical_suite=CANONICAL_SUITE,
        canonical_version=CANONICAL_VERSION,
        canonical_base_url=CANONICAL_BASE_URL,
        canonical_model=CANONICAL_MODEL,
        canonical_temperature=CANONICAL_TEMPERATURE,
    )
    authority_scope = bool(
        catalog_status["complete_catalog"]
        and request_profile["canonical_request_profile"]
    )

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
            msg = smoke.extract_message(resp, expected_model=args.model)
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

    diagnostic_meets_ship_min = (n_pass >= ship_min) if ship_min is not None else None
    diagnostic_meets_ship_stretch = n_pass >= int(ship_stretch or 0)
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
        "diagnostic_meets_ship_min": diagnostic_meets_ship_min,
        "diagnostic_meets_ship_stretch": diagnostic_meets_ship_stretch,
        "meets_ship_min": False,
        "meets_ship_stretch": False,
        "run_scope": "authoritative_full_catalog" if authority_scope else "diagnostic_non_authoritative",
        "complete_catalog": catalog_status["complete_catalog"],
        "request_profile_eligible": request_profile["canonical_request_profile"],
        "authority_scope": "suite_only",
        "authority_eligible": False,
        "suite_authority_eligible": False,
        "suite_green": False,
        "smoke_green": False,
        "release_green": False,
        "gate_clearance": False,
        "contract": {
            "id": CANONICAL_CONTRACT_ID,
            "catalog_sha256": CANONICAL_CASES_SHA256,
            "eligible": False,
        },
        "catalog": catalog_status,
        "request_profile": request_profile,
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
    summary["authority_eligible"] = smoke.is_authority_eligible(
        catalog_status=catalog_status,
        request_profile=request_profile,
        passed=n_pass,
        total=len(results),
        provenance_complete=summary.get("run_manifest", {}).get("provenance_complete", False),
    )
    summary["suite_authority_eligible"] = summary["authority_eligible"]
    summary["suite_green"] = summary["authority_eligible"]
    summary["smoke_green"] = summary["authority_eligible"]
    summary["contract"]["eligible"] = summary["authority_eligible"]
    summary["run_scope"] = (
        "authoritative_full_catalog"
        if summary["authority_eligible"]
        else "diagnostic_non_authoritative"
    )
    summary["meets_ship_min"] = bool(
        summary["authority_eligible"] and diagnostic_meets_ship_min
    )
    summary["meets_ship_stretch"] = bool(
        summary["authority_eligible"] and diagnostic_meets_ship_stretch
    )

    text = json.dumps(summary, indent=2)
    outp = smoke.write_receipt_atomic(
        args.out,
        text,
        (
            Path(__file__).resolve().parents[2] / "results" / "agent_smoke.json",
            Path(__file__).resolve().parents[2] / "results" / "hermes_agent_smoke.json",
        ),
    )
    print("wrote", outp)
    print(
        f"SUMMARY suite={suite} pass={n_pass}/{len(results)} "
        f"rate={summary['pass_rate']} elapsed={summary['elapsed_s']}s "
        f"ship_min={summary['meets_ship_min']} stretch={summary['meets_ship_stretch']} "
        f"scope={summary['run_scope']} authority_eligible={str(summary['authority_eligible']).lower()}"
    )
    # Diagnostic subsets/custom catalogs always use a distinct non-green status.
    if not authority_scope:
        print(
            "NON-AUTHORITATIVE: subset/custom catalog or noncanonical request profile is diagnostic only",
            file=sys.stderr,
        )
        return smoke.NON_AUTHORITATIVE_EXIT
    if not summary.get("run_manifest", {}).get("provenance_complete"):
        print("FAIL provenance is incomplete or the pack worktree is dirty", file=sys.stderr)
        return 3
    if summary["authority_eligible"]:
        return 0
    if ship_min is not None and n_pass < ship_min:
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
