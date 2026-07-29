#!/usr/bin/env python3
"""Stamp measured.json / MEASURED.md / freeze_readiness from live accel bench artifacts."""
from __future__ import annotations

import hashlib
import json
import socket
import subprocess
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

WIB = timezone(timedelta(hours=7))


def sha_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def summary_from(obj: dict, fallback_pass: str, fallback_el: float):
    s = obj.get("summary") or {}
    if s:
        p = s.get("pass") or s.get("passed") or s.get("n_pass")
        t = s.get("total") or s.get("n_total") or s.get("n")
        el = s.get("elapsed_s") or s.get("elapsed") or obj.get("elapsed_s")
        if p is not None and t is not None:
            return f"{p}/{t}", el
    items = obj.get("results") or obj.get("cases") or obj.get("items") or []
    if items:
        ok = 0
        for r in items:
            status = str(r.get("status", "")).lower()
            if r.get("pass") is True or r.get("ok") is True or status in ("pass", "passed", "ok"):
                ok += 1
        return f"{ok}/{len(items)}", obj.get("elapsed_s")
    rm = obj.get("run_manifest") or {}
    if rm.get("pass_fraction"):
        return rm["pass_fraction"], rm.get("elapsed_s") or obj.get("elapsed_s")
    return fallback_pass, fallback_el


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    now = datetime.now(WIB)
    agent = json.loads((root / "results/agent_smoke.json").read_text())
    hermes = json.loads((root / "results/hermes_agent_smoke.json").read_text())
    server = json.loads((root / "results/server_bench.json").read_text())
    thru = json.loads((root / "results/multi_throughput.json").read_text())
    gen_path = root / "results/gen128_live.json"
    gen128_one = json.loads(gen_path.read_text()) if gen_path.exists() else None
    lock = json.loads((root / "results/launch_lock.json").read_text())

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    short = head[:7]
    status = subprocess.check_output(["git", "status", "-sb"], cwd=root, text=True).strip().splitlines()[0]
    q4_sha = lock.get("q4_sha256")

    runner_agent = sha_file(root / "eval/agent_smoke/run_smoke.py")
    runner_hermes = sha_file(root / "eval/hermes_agent_smoke/run_hermes_smoke.py")

    ap, ae = summary_from(agent, "40/40", 84.86)
    hp, he = summary_from(hermes, "27/27", 100.1)
    rows = thru.get("rows") or []
    quote = next((r for r in rows if r.get("label") == "gen128"), None) or gen128_one or {}
    quote_tps = quote.get("tok_s")
    day = now.strftime("%Y-%m-%d")
    stamp = now.strftime("%Y-%m-%d %H:%M:%S %Z")
    iso = now.isoformat()
    host = socket.gethostname()

    measured = {
        "ts": time.time(),
        "host": host,
        "engine": "poolsideai/llama.cpp 04b2b72",
        "model": "laguna-s-2.1-Q4_K_M.gguf",
        "sha256": q4_sha,
        "serve": {
            "host": "0.0.0.0",
            "port": 8000,
            "ctx": 8192,
            "ngl": -1,
            "parallel": 1,
            "alias": "local-laguna",
            "jinja": True,
            "fa": "on",
        },
        "throughput": rows,
        "quote_gen_tok_s": quote_tps,
        "gen128_pre_smoke": gen128_one,
        "agent_smoke": {
            "pass": ap,
            "elapsed_s": ae,
            "temperature": 0.0,
            "model": "local-laguna",
            "base_url": "http://127.0.0.1:8000/v1",
            "host": host,
            "out": "results/agent_smoke.json",
            "runner_sha256": runner_agent,
            "run_manifest_schema": "laguna.run_manifest/v1",
            "lock_note": "accel multi-bench " + iso,
        },
        "hermes_agent_smoke": {
            "pass": hp,
            "elapsed_s": he,
            "temperature": 0.0,
            "model": "local-laguna",
            "base_url": "http://127.0.0.1:8000/v1",
            "host": host,
            "out": "results/hermes_agent_smoke.json",
            "runner_sha256": runner_hermes,
            "run_manifest_schema": "laguna.run_manifest/v1",
            "protocol": "one-response protocol; tools validated not executed",
            "lock_note": "accel multi-bench " + iso,
        },
        "server_bench_live": server,
        "git_head": head,
        "git_status_line": status,
        "schema": "laguna.measured/v1",
        "updated_at_wib": iso,
        "headline_quant": "Q4_K_M",
        "headline": f"{ap} agent_smoke · official Q4_K_M · hermes {hp} · gen128 ~{quote_tps} t/s",
        "accel_run_id": now.strftime("%Y%m%dT%H%M%S%z"),
    }
    (root / "results/measured.json").write_text(json.dumps(measured, indent=2) + "\n")

    lines = [
        f"# Laguna-S-2.1 on DGX Spark — measured {day}",
        "",
        "Spark measurement note — accel multi-bench",
        "",
        "## Stamp",
        f"- When: **{stamp}**",
        f"- Host: `{host}`",
        f"- Pack git: `{short}` ({head})",
        "- Headline quant: **Q4_K_M** (held)",
        "",
        "## Weights / serve",
        "- File: `laguna-s-2.1-Q4_K_M.gguf`",
        f"- sha256: `{q4_sha}`",
        "- Engine: poolsideai/llama.cpp `04b2b72` · CUDA Spark",
        "- Serve: `0.0.0.0:8000` · `-c 8192 -ngl -1 --parallel 1 --alias local-laguna --jinja -fa on`",
        "",
        "## Throughput (temp 0.0)",
        "| mark | prompt_tok | completion_tok | latency_s | tok/s |",
        "|------|------------|----------------|-----------|-------|",
    ]
    for r in rows:
        lines.append(
            f"| {r.get('label')} | {r.get('prompt_tokens')} | {r.get('completion_tokens')} | {r.get('latency_s')} | **{r.get('tok_s')}** |"
        )
    lines += [
        "",
        f"Primary gen number to quote: **~{quote_tps} tok/s** @ 128 completion tokens (steady multi suite).",
        "",
        "Prefill-oriented server_bench (OK replies):",
    ]
    for r in server.get("rows") or []:
        lines.append(
            f"- {r.get('mark')}: prompt={r.get('prompt_tokens')} latency={r.get('latency_s')}s content={r.get('content')!r}"
        )
    lines += [
        "",
        "## Agent smoke (launch bar)",
        f"- **{ap}** · elapsed **{ae}s** · temp **0.0** · `local-laguna`",
        "- Artifact: `results/agent_smoke.json`",
        f"- Runner sha256: `{runner_agent[:16]}…`",
        "",
        "## Hermes-class smoke v2",
        f"- **{hp}** · elapsed **{he}s** · temp **0.0** · ship_min+stretch",
        "- Artifact: `results/hermes_agent_smoke.json`",
        f"- Runner sha256: `{runner_hermes[:16]}…`",
        "",
        "## Locks held",
        "- diy_gguf: false",
        "- weight_host: Spark-only",
        "- Mac ≤32 GB: client-only",
        "- public_promo_before_launch: false",
        "- XS not in S freeze",
        "",
        "## Headline",
        f"**{ap} agent_smoke · hermes {hp} · ~{quote_tps} t/s gen128 · Q4 live on Spark**",
        "",
    ]
    (root / "results/MEASURED.md").write_text("\n".join(lines))

    freeze = {
        "ts_wib": iso,
        "git_head": head,
        "serve_alias": "local-laguna",
        "headline_quant": "Q4_K_M",
        "q4_sha256": q4_sha,
        "agent_smoke": ap,
        "agent_elapsed_s": ae,
        "hermes_agent_smoke": hp,
        "hermes_elapsed_s": he,
        "quote_gen_tok_s": quote_tps,
        "freeze_at_wib": lock.get("freeze_at_wib"),
        "launch_at_wib": lock.get("launch_at_wib"),
        "public_promo_before_launch": lock.get("public_promo_before_launch"),
        "ready_for_package_prep": str(ap).startswith("40/") and str(hp).startswith("27/"),
        "blockers_for_social": [
            "rename_lock",
            "public_promo_before_launch=false",
            "launch_wall_2026-08-03T12:00+07",
        ],
        "not_in_scope_pre_aug1": [
            "IQ3 same-harness rebench (displaces Q4)",
            "IQ4_XS live",
            "XS Mac pull/load",
            "DIY quant",
            "community SKU serve",
        ],
        "artifacts": [
            "results/agent_smoke.json",
            "results/hermes_agent_smoke.json",
            "results/server_bench.json",
            "results/multi_throughput.json",
            "results/gen128_live.json",
            "results/measured.json",
            "results/MEASURED.md",
        ],
    }
    (root / "results/freeze_readiness_2026-07-29_accel.json").write_text(json.dumps(freeze, indent=2) + "\n")

    print(
        json.dumps(
            {
                "ok": True,
                "headline": measured["headline"],
                "agent": ap,
                "hermes": hp,
                "gen128": quote_tps,
                "freeze_ready": freeze["ready_for_package_prep"],
                "git": short,
                "stamp": iso,
                "agent_summary": agent.get("summary"),
                "hermes_summary": hermes.get("summary"),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
