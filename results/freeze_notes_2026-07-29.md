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
| Pack measure tip | `bf82eab` |
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
- DFlash: measured, **DO_NOT_PROMOTE**

## Still open before freeze day

1. ~~Optional DFlash status row final~~ → **done 2026-07-29 · DO_NOT_PROMOTE** (`results/dflash_2026-07-29/`)
2. ~~Stranger-path dry re-run~~ → **DRY PASS** (`results/stranger_path_dry_2026-07-29.md`) · serve flag aligned to `-ngl -1`
3. ~~Baseline serve re-health after DFlash teardown~~ → **HEALTH_OK + chat OK** 2026-07-29 15:50 WIB (`results/baseline_rehealth_2026-07-29.md`)
4. HF tip push of DFlash/last-green/stranger/jury receipts (docs-only)
5. Clean pushed HEAD on freeze day (**2026-08-02 18:00 WIB**)
6. Public go-live **2026-08-03 12:00 WIB** (no early promo)

## Non-actions

- No accidental freeze today
- No public promo before Aug 3 12:00 WIB
- No XS inside S freeze artifact
- No re-bench required unless weights/runners change
- No DFlash speedup claim

## 2026-07-29 jury-fix rev (post dual seat)

- **S freeze lock_set is S-only.** Dropped `results/xs_mac_track_lock.json` from S `lock_set`.
- XS remains parallel `prepared_research` under its own lock; **not** an S freeze hash input.
- **Rehash at freeze:** on clean pushed HEAD (not dirty WT), recompute sha256 for every S lock_set member and stamp freeze gate. Docs tip may move; measure tip stays `bf82eab` until smoke/weights change.
- Gen headline sole: **~21.47 tok/s** from multi suite in `results/measured.json`. No 22.50 on launch surfaces.
- SHA256SUMS is GNU **2-column** for `sha256sum -c`.
