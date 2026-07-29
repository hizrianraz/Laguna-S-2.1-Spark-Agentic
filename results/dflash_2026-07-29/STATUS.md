# DFlash status — 2026-07-29

## Decision
**DO_NOT_PROMOTE**

## Why
- gen128: **15.286 tok/s** vs baseline **~21.47 tok/s** (-28.8%)
- prefill 2k: **2.253s** vs baseline **~1.6s**
- prefill 8k: **5.556s** vs baseline **~4.78s**

## Evidence
- `results/dflash_2026-07-29/throughput.json`
- `results/dflash_2026-07-29/server_bench.json`
- `results/dflash_2026-07-29/measured.json`
- server log: `results/dflash_2026-07-29/server.log`

## Locks held
- Headline remains official Q4_K_M · 40/40 · hermes 27/27 · ~21.5 t/s
- Do not claim DFlash speedup
- Restore baseline serve after this window

## Notes
- Spec path active on slots (`draft-dflash`); absolute throughput still lost to plain Q4 serve
- Long load (~10+ min) before health OK expected for Q4 + draft

DFlash DO_NOT_PROMOTE: gen128 15.286 t/s vs baseline 21.47 (-28.8%); 2k 2.253s vs ~1.6s; 8k 5.556s vs ~4.78s.
