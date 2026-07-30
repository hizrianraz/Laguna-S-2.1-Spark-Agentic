#!/usr/bin/env python3
"""Read-only validator for Laguna's locked historical acceleration receipts.

The former stamping helper could rewrite historical authority and accidentally
attribute old scores to current runners. That mutation path is intentionally
removed. New runs write dated receipts through their own no-clobber runners;
release authority changes require an explicit reviewed migration outside this
tool.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path


MEASURE_TIP = "bf82eab5fd6c1fb04e863f0c4b05b5658dec4aee"
Q4_SHA256 = "a8b55c75714ea73fd90ec85de5defdc0b8d88ca0ad2108343cdd8fc22f7583e4"
LOCKED = {
    "results/agent_smoke.json": "5fa770888a4fa247a742bef9618c1ca1b59c4c7ac7932d570abb6dac8e2501d1",
    "results/hermes_agent_smoke.json": "1c55e61e24ddf12065d2762fb5389dd834affb48eb8a2ba437d85ecf34e36c94",
    "results/measured.json": "1e2aa086462e93072a3842529ce1379695d20a910d87c8d4e7987e3b800a12a0",
    "results/server_bench.json": "44d07c31e487fe7c4236f15d7839e5db1b2d82f0606c224d4ce0c1000d5e49e4",
}
SMOKE_BINDINGS = {
    "agent_smoke": {
        "path": "results/agent_smoke.json",
        "n": 40,
        "version": 1,
        "runner_sha256": "3bb81080879ddf78d3d6295e333c78b1ecc1d84ba5a9e9dc19a0e677f54da48f",
        "cases_sha256": "1aa5e279dd42bc82e4b4a71a3cde648bec7b236b8f9dd055c663412835ac8e76",
    },
    "hermes_agent_smoke": {
        "path": "results/hermes_agent_smoke.json",
        "n": 27,
        "version": 2,
        "runner_sha256": "20c1e52a8a22306b81309c08984d6875cfff46e7382a46b674c1a6345030293b",
        "cases_sha256": "3275a4a570007fa8f948764a6873e055dc5a4a5ff257a1edc8bc342a02a8ddfc",
    },
}


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _count(value, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{label} must be an integer")
    return value


def summary_from(
    obj: dict,
    label: str,
    *,
    expected_suite: str | None = None,
    expected_n: int | None = None,
) -> tuple[str, float]:
    """Validate a row-backed receipt; header-only fractions are never evidence."""
    if not isinstance(obj, dict):
        raise ValueError(f"{label} receipt must be an object")
    if expected_suite is not None and obj.get("suite") != expected_suite:
        raise ValueError(f"{label}.suite must equal {expected_suite!r}")
    if obj.get("model") not in (None, "local-laguna"):
        raise ValueError(f"{label}.model must equal 'local-laguna'")
    passed = _count(obj.get("passed"), f"{label}.passed")
    total = _count(obj.get("n"), f"{label}.n")
    if total <= 0 or passed < 0 or passed > total:
        raise ValueError(f"{label} has invalid pass fraction {passed}/{total}")
    if expected_n is not None and total != expected_n:
        raise ValueError(f"{label} must contain exactly {expected_n} results")
    rows = obj.get("results")
    if not isinstance(rows, list) or len(rows) != total or not rows:
        raise ValueError(f"{label} must contain exactly {total} result rows")
    ids = []
    observed_passed = 0
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ValueError(f"{label} result {index} is not an object")
        case_id = row.get("id")
        if not isinstance(case_id, str) or not case_id:
            raise ValueError(f"{label} result {index} lacks a non-empty id")
        if not isinstance(row.get("pass"), bool):
            raise ValueError(f"{label} result {index} lacks a boolean pass field")
        ids.append(case_id)
        observed_passed += int(row["pass"])
    if len(set(ids)) != len(ids):
        raise ValueError(f"{label} result ids must be unique")
    if observed_passed != passed:
        raise ValueError(f"{label} rows say {observed_passed}/{total}, header says {passed}/{total}")
    elapsed = obj.get("elapsed_s")
    if isinstance(elapsed, bool) or not isinstance(elapsed, (int, float)) or not math.isfinite(elapsed) or elapsed <= 0:
        raise ValueError(f"{label}.elapsed_s must be a finite positive number")
    return f"{passed}/{total}", float(elapsed)


def validate_bench(obj: dict) -> None:
    rows = obj.get("rows") if isinstance(obj, dict) else None
    if not isinstance(rows, list) or len(rows) != 2:
        raise ValueError("server bench must contain exactly two rows")
    marks = [row.get("mark") for row in rows if isinstance(row, dict)]
    if sorted(marks) != ["2k", "8k"] or len(set(marks)) != 2:
        raise ValueError(f"server bench requires exactly one 2k and one 8k row; got {marks}")
    for index, row in enumerate(rows):
        if not isinstance(row, dict) or row.get("error"):
            raise ValueError(f"server bench row {index} is not successful")
        for key in ("prompt_tokens", "completion_tokens"):
            value = row.get(key)
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"server bench row {index} has invalid {key}")
        if not isinstance(row.get("content"), str) or row["content"].strip() != "OK":
            raise ValueError(f"server bench row {index} does not contain exact sentinel OK")


def validate_locked_smoke(root: Path, suite: str, binding: dict) -> tuple[str, float]:
    receipt = json.loads((root / binding["path"]).read_text())
    fraction, elapsed = summary_from(
        receipt,
        suite,
        expected_suite=suite,
        expected_n=binding["n"],
    )
    if receipt.get("version") != binding["version"]:
        raise ValueError(f"{suite}.version mismatch")
    if receipt.get("base_url") != "http://127.0.0.1:8000/v1":
        raise ValueError(f"{suite}.base_url mismatch")
    manifest = receipt.get("run_manifest")
    if not isinstance(manifest, dict):
        raise ValueError(f"{suite} lacks run_manifest")
    checks = {
        "suite": suite,
        "pack_git_head": MEASURE_TIP,
    }
    for key, expected in checks.items():
        if manifest.get(key) != expected:
            raise ValueError(f"{suite}.run_manifest.{key} mismatch")
    if (manifest.get("runner") or {}).get("sha256") != binding["runner_sha256"]:
        raise ValueError(f"{suite} historical runner SHA-256 mismatch")
    if (manifest.get("cases") or {}).get("sha256") != binding["cases_sha256"]:
        raise ValueError(f"{suite} historical cases SHA-256 mismatch")
    return fraction, elapsed


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    for relative, expected in LOCKED.items():
        actual = sha_file(root / relative)
        if actual != expected:
            raise SystemExit(f"locked historical artifact changed: {relative}: {actual}")

    summaries = {
        suite: validate_locked_smoke(root, suite, binding)
        for suite, binding in SMOKE_BINDINGS.items()
    }
    validate_bench(json.loads((root / "results/server_bench.json").read_text()))
    measured = json.loads((root / "results/measured.json").read_text())
    if measured.get("git_head") != MEASURE_TIP or measured.get("sha256") != Q4_SHA256:
        raise SystemExit("historical measured receipt authority mismatch")
    lock = json.loads((root / "results/launch_lock.json").read_text())
    if lock.get("schema") != "laguna.launch_lock/v4" or (lock.get("artifact") or {}).get("sha256") != Q4_SHA256:
        raise SystemExit("current launch lock does not bind the official Q4 authority")

    print(
        json.dumps(
            {
                "ok": True,
                "mode": "read_only_historical_validation",
                "rewrites_historical_authority": False,
                "measure_tip": MEASURE_TIP,
                "agent_smoke": summaries["agent_smoke"][0],
                "hermes_agent_smoke": summaries["hermes_agent_smoke"][0],
                "scope": "historical format/routing only; current hardened v2 not re-smoked",
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
