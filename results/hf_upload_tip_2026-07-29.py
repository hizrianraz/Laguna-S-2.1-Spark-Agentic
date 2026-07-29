#!/usr/bin/env python3
"""Docs-only HF tip upload for Laguna-S-2.1-Spark-Agentic. No weights."""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from huggingface_hub import HfApi, hf_hub_download

ROOT = Path(__file__).resolve().parents[1]
REPO_ID = "hizrianraz/Laguna-S-2.1-Spark-Agentic"
WIB = timezone(timedelta(hours=7))

# docs/receipts only — never GGUF
UPLOAD = [
    "README.md",
    "LAUNCH_AUG3.md",
    "SPARK.md",
    "docs/REPRODUCE.md",
    "research/quant-comparison-scoreboard-2026-07-28.md",
    "results/MEASURED.md",
    "results/LAST_GREEN_PIN.md",
    "results/freeze_notes_2026-07-29.md",
    "results/accel_receipts_2026-07-29.md",
    "results/baseline_rehealth_2026-07-29.md",
    "results/stranger_path_dry_2026-07-29.md",
    "results/three_jury_post_dflash_2026-07-29.md",
    "results/dflash_2026-07-29/STATUS.md",
    "results/dflash_2026-07-29/measured.json",
    "results/dflash_2026-07-29/throughput.json",
    "results/dflash_2026-07-29/server_bench.json",
    "results/dflash_2026-07-29/meta.txt",
    "results/dflash_2026-07-29/models.json",
    "prompts/chatgpt-analyze-laguna-s-2026-07-29.md",
    "prompts/claude-analyze-laguna-s-2026-07-29.md",
    "results/launch_lock.json",
    "results/measured.json",
    "results/agent_smoke.json",
    "results/hermes_agent_smoke.json",
    "results/freeze_gate_model_card_lock_set_2026-07-29.json",
    "results/freeze_readiness_2026-07-29_accel.json",
]


def main() -> int:
    head = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()
    short = head[:7]
    api = HfApi()
    missing = [p for p in UPLOAD if not (ROOT / p).is_file()]
    if missing:
        print("MISSING", missing, file=sys.stderr)
        return 2
    paths = [str(ROOT / p) for p in UPLOAD]
    commit = api.upload_folder(
        folder_path=str(ROOT),
        repo_id=REPO_ID,
        repo_type="model",
        allow_patterns=UPLOAD,
        commit_message=f"docs tip: DFlash DO_NOT_PROMOTE + last-green + jury + analyze prompts ({short})",
        create_pr=False,
    )
    # upload_folder may return string commit url or CommitInfo
    commit_sha = getattr(commit, "oid", None) or getattr(commit, "commit_id", None)
    if not commit_sha and isinstance(commit, str):
        # try parse from URL tail
        commit_sha = commit.rstrip("/").split("/")[-1]
    info = api.repo_info(repo_id=REPO_ID, repo_type="model")
    latest = getattr(info, "sha", None) or commit_sha
    siblings = sorted(s.rfilename for s in (info.siblings or []))
    out = {
        "repo_id": REPO_ID,
        "url": f"https://huggingface.co/{REPO_ID}",
        "commit": latest,
        "latest_commit": latest,
        "local_git_head": head,
        "private": bool(getattr(info, "private", False)),
        "siblings": siblings,
        "n_files": len(siblings),
        "launch_locked": True,
        "launch_at_wib": "2026-08-03T12:00:00+07:00",
        "freeze_at_wib": "2026-08-02T18:00:00+07:00",
        "freeze_gate_status": "filled",
        "freeze_gate_receipt": "results/freeze_gate_model_card_lock_set_2026-07-29.json",
        "measure_tip_pack_git": "bf82eab5fd6c1fb04e863f0c4b05b5658dec4aee",
        "measured_json_on_hf": "results/measured.json" in siblings,
        "agent_smoke_on_hf": "results/agent_smoke.json" in siblings,
        "hermes_agent_smoke_on_hf": "results/hermes_agent_smoke.json" in siblings,
        "dflash_status_on_hf": "results/dflash_2026-07-29/STATUS.md" in siblings,
        "last_green_pin_on_hf": "results/LAST_GREEN_PIN.md" in siblings,
        "analyze_prompts_on_hf": (
            "prompts/chatgpt-analyze-laguna-s-2026-07-29.md" in siblings
            and "prompts/claude-analyze-laguna-s-2026-07-29.md" in siblings
        ),
        "freeze_gate_on_hf": "results/freeze_gate_model_card_lock_set_2026-07-29.json"
        in siblings,
        "launch_lock_on_hf": "results/launch_lock.json" in siblings,
        "readme_on_hf": "README.md" in siblings,
        "updated_at_wib": datetime.now(WIB).isoformat(timespec="seconds"),
        "note": "docs/receipts only; weights untouched; DFlash DO_NOT_PROMOTE tip; launch still Aug 3 12:00 WIB",
        "uploaded_paths": UPLOAD,
        "upload_return": str(commit),
    }
    dst = ROOT / "results" / "hf_publish.json"
    dst.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "commit": latest, "n_files": len(siblings)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
