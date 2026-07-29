# Freeze notes — 2026-07-29

## Gate

- Freeze gate: **model_card + lock files**
- Status: **FILLED** at `2026-07-29T14:43:26+07:00`
- Receipt: `results/freeze_gate_model_card_lock_set_2026-07-29.json`
- Freeze clock: still **2026-08-02 18:00 WIB** (do not freeze early)
- HF go-live: **2026-08-03 12:00 WIB**

## Live tip bound into card + locks

| Field | Value |
|-------|--------|
| Pack | `bf82eab` |
| Q4 sha256 | `a8b55c75714ea73fd90ec85de5defdc0b8d88ca0ad2108343cdd8fc22f7583e4` |
| agent_smoke | 40/40 · 84.86s |
| hermes v2 | 27/27 · 100.1s |
| gen128 | ~21.47 t/s |
| Engine | poolsideai/llama.cpp `04b2b72` |

## Locks held

- diy_gguf: false
- weight_host: Spark-only
- founder Mac: client-only (no local S)
- public_promo_before_launch: false
- XS: parallel, not in S freeze
- branding: personal-only

## Still open before freeze day

1. ~~Optional DFlash status row final~~ → **done 2026-07-29 · DO_NOT_PROMOTE** (`results/dflash_2026-07-29/`)
2. ~~Stranger-path dry re-run~~ → **DRY PASS** (`results/stranger_path_dry_2026-07-29.md`) · serve flag aligned to `-ngl -1`
3. HF push of filled card + tip artifacts
4. Clean pushed HEAD on freeze day
5. Baseline serve re-health after DFlash teardown (restore launched 2026-07-29 15:40 WIB)

## Non-actions

- No accidental freeze today
- No public promo before Aug 3 12:00 WIB
- No XS inside S freeze artifact
- No re-bench required unless weights/runners change
