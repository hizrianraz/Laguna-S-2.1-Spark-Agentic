# Stranger-path dry + REPRODUCE exact — 2026-07-29 (jury-fix rev2)

Intent: verify a newcomer can follow pack docs without operator brain.
Full clone/rebuild of llama.cpp on Spark is **not** re-run here (engine already pinned `04b2b72`).
This is a **doc + path integrity dry** against live tree + live pins.
Label: **DRY / DOC PATH** — not a clean full rebuild receipt.

## Sources walked

1. `README.md` → One-evening stranger path (S1)
2. `docs/REPRODUCE.md` → full pin table + numbered steps
3. `SPARK.md` → build + serve + measured
4. `results/MEASURED.md` + `results/LAST_GREEN_PIN.md`

## Checklist

| # | Step | Status | Note |
|---|------|--------|------|
| 1 | License / OpenMDW accept before redistribute | PASS | REPRODUCE step 1 |
| 2 | Engine clone + pin measured SHA `04b2b72` | PASS | README stranger path + `results/engine_sha.txt` |
| 3 | CUDA arch `121` → `121a` note | PASS | BUILD_SPARK / SPARK |
| 4 | Record engine `git rev-parse HEAD` | PASS | → `results/engine_sha.txt` |
| 5 | Weight download + revision pin | PASS | GGUF rev `fc4e481…` + sha256 |
| 6 | `SHA256SUMS` GNU 2-col + `sha256sum -c` | **PASS** | root `SHA256SUMS` is 2-col; `scripts/pull_official_gguf.sh` fail-closed |
| 7 | Serve flags match measured | **PASS** | `-ngl -1` + `--alias local-laguna`; smoke uses `model=local-laguna` |
| 8 | `/v1/models` health gate | PASS | REPRODUCE |
| 9 | bench_server / llama-bench targets | PASS | llama-bench `-ngl -1` |
| 10 | agent_smoke 40 + optional hermes 27 | PASS | steps present |
| 11 | DIY gated | PASS | diy_gguf false |
| 12 | DFlash not default; DO_NOT_PROMOTE | PASS | optional path + disclose |
| 13 | HF surface id correct | PASS | `hizrianraz/Laguna-S-2.1-Spark-Agentic` |
| 14 | Scoreboard sole gen headline 21.47 | PASS | no 22.50 on launch surfaces |
| 15 | S freeze lock_set excludes XS | PASS | xs dropped from S lock_set |

## Exact REPRODUCE pins (copy)

```
Base model poolside/Laguna-S-2.1
Base revision 00af5a51782109b587a3b3bbf11875e566036fa7
GGUF repo poolside/Laguna-S-2.1-GGUF
GGUF revision fc4e481289523cf7d0df668da6d1d391616141ca
Default weight laguna-s-2.1-Q4_K_M.gguf
Q4_K_M sha256 a8b55c75714ea73fd90ec85de5defdc0b8d88ca0ad2108343cdd8fc22f7583e4
Engine github.com/poolsideai/llama.cpp branch laguna
Engine measured SHA 04b2b72cb54048ead292884adbe11f284e3ec950
Hardware DGX Spark GB10 only
Serve alias local-laguna
```

## Stranger serve one-liner (aligned to last green)

```bash
./build/bin/llama-server \
 -m ~/models/laguna-s-2.1/laguna-s-2.1-Q4_K_M.gguf \
 --host 127.0.0.1 --port 8000 \
 --ctx-size 8192 -ngl -1 --jinja -fa on \
 --alias local-laguna
```

Smoke clients must call `model=local-laguna` (or empty/default that resolves to alias) — not a stale internal id like `laguna-q4`.

## Jury fix this tick (rev2)

- SHA256SUMS → GNU 2-column; `sha256sum -c` works from weight dir
- Engine pin in stranger path (checkout `04b2b72…`)
- Serve alias `local-laguna` + smoke model aligned
- LAST_GREEN_PIN: dead `multi_throughput.json` pointer removed; evidence is MEASURED/measured.json
- S lock_set: drop XS; rehash-at-freeze noted
- LAUNCH: dropped 22.50 parenthetical; sole headline ~21.47
- PATCH prose: host-measured (Spark/GNU 13.3)
- Measure tip vs docs tip labeled

## Verdict

**DRY PASS (doc path)** — prior stranger FAIL items from dual seat closed on tree.

Not claimed: full clean rebuild wall-clock on a cold stranger host.
Remaining stranger cost: first-time CUDA build + ~96GB weight pull — documented, not path bugs.
