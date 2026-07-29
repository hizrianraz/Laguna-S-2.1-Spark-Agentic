# Stranger-path dry + REPRODUCE exact — 2026-07-29

Intent: verify a newcomer can follow pack docs without founder brain.
Full clone/rebuild of llama.cpp on Spark is **not** re-run here (engine already pinned `04b2b72`).
This is a **doc + path integrity dry** against live tree + live pins.

## Sources walked

1. `README.md` → One-evening stranger path (S1)
2. `docs/REPRODUCE.md` → full pin table + numbered steps
3. `SPARK.md` → build + serve + measured
4. `results/MEASURED.md` + `results/LAST_GREEN_PIN.md`

## Checklist

| # | Step | Status | Note |
|---|------|--------|------|
| 1 | License / OpenMDW accept before redistribute | PASS | stated in REPRODUCE step 1 |
| 2 | Engine clone branch `laguna` | PASS | command present README + SPARK |
| 3 | CUDA arch `121` → `121a` note | PASS | SPARK build section |
| 4 | Record engine `git rev-parse HEAD` | PASS | REPRODUCE step 3 → `results/engine_sha.txt` |
| 5 | Weight download + revision pin | PASS | REPRODUCE lists GGUF rev `fc4e481…` + sha256 |
| 6 | Serve flags match measured | **FIX DONE** | stranger path had `-ngl 99`; measured pin is `-ngl -1` — aligned below |
| 7 | `/v1/models` health gate | PASS | REPRODUCE step 5 |
| 8 | bench_server / llama-bench targets | PASS | steps 6–7 |
| 9 | agent_smoke 40 + optional hermes 27 | PASS | steps 8 / 8b |
| 10 | Populate SPARK from files only | PASS | step 9 |
| 11 | DIY gated | PASS | diy_gguf false + policy |
| 12 | DFlash not default path | PASS | optional; DO_NOT_PROMOTE measured |
| 13 | HF surface id correct | PASS | `hizrianraz/Laguna-S-2.1-Spark-Agentic` |
| 14 | Scoreboard row distinguishes headline vs IQ3 pointer | PASS | README scoreboard |

## Exact REPRODUCE pins (copy)

```
Base model          poolside/Laguna-S-2.1
Base revision       00af5a51782109b587a3b3bbf11875e566036fa7
GGUF repo           poolside/Laguna-S-2.1-GGUF
GGUF revision       fc4e481289523cf7d0df668da6d1d391616141ca
Default weight      laguna-s-2.1-Q4_K_M.gguf
Q4_K_M sha256       a8b55c75714ea73fd90ec85de5defdc0b8d88ca0ad2108343cdd8fc22f7583e4
Engine              github.com/poolsideai/llama.cpp branch laguna
Engine measured SHA 04b2b72cb54048ead292884adbe11f284e3ec950
Hardware            DGX Spark GB10 only
```

## Stranger serve one-liner (aligned to last green)

```bash
./build/bin/llama-server \
  -m ~/models/laguna-s-2.1/laguna-s-2.1-Q4_K_M.gguf \
  --host 127.0.0.1 --port 8000 \
  --ctx-size 8192 -ngl -1 --jinja -fa on \
  --alias local-laguna
```

## Verdict

**DRY PASS** after serve-flag align (`-ngl -1`).

Remaining stranger risk: first-time CUDA build time + ~96GB weight pull — documented, not blockers of path correctness.
HF push of card/tip still separate gate (freeze lock).
