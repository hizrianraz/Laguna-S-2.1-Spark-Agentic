# Accel receipts — 2026-07-29 (Manwë)

## Closed this window

| Item | Result | Evidence |
|------|--------|----------|
| DFlash measure | **DO_NOT_PROMOTE** | gen128 15.286 vs bas 21.47 (−28.8%); 2k 2.253s; 8k 5.556s |
| DFlash scoreboard row | written | README / SPARK / research scoreboard |
| Last green pin | sealed | `results/LAST_GREEN_PIN.md` |
| Baseline restore | launched | Spark pid live; load in progress after DFlash teardown |
| Stranger-path dry | **DRY PASS** | serve flag `-ngl 99` → `-ngl -1` align |
| REPRODUCE exact | tightened | explicit serve block + DFlash non-default note |

## Numbers (do not invent beyond these)

- Headline Q4: 40/40 · hermes 27/27 · **21.47 t/s** gen128 · pack tip `bf82eab` · eng `04b2b72`
- DFlash: 15.286 t/s gen128 · **not** ship

## Still open (freeze path)

1. HF push of filled card + tip — hold until freeze gates / clean pushed HEAD
2. Public promo lock until **2026-08-03 12:00 WIB**
3. Baseline health re-confirm after load (~6–10 min typical)

## Locks held

- diy_gguf false
- weight_host Spark-only
- no DFlash speedup claim
- no company-gate vault write
