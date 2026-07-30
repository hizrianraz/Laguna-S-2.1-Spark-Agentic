# Accel receipts — 2026-07-29 (Manwë)

## Closed this window

| Item | Result | Evidence |
|------|--------|----------|
| DFlash measure | **DO_NOT_PROMOTE** | gen128 15.286 vs bas 21.47 (−28.8%); 2k 2.253s; 8k 5.556s |
| DFlash scoreboard row | written | README / SPARK / research scoreboard |
| Last green pin | sealed | `results/LAST_GREEN_PIN.md` |
| Baseline restore + re-health | **HEALTH_OK + chat OK** | `results/baseline_rehealth_2026-07-29.md` · 15:50 WIB |
| Stranger-path dry | **DRY PASS** | serve flag `-ngl 99` → `-ngl -1` align |
| REPRODUCE exact | tightened | explicit serve block + DFlash non-default note |
| Three-jury consult (post-DFlash) | packaged | `results/three_jury_post_dflash_2026-07-29.json` + `.md` |
| ChatGPT + Claude analyze prompts | written | `prompts/chatgpt-analyze-laguna-s-2026-07-29.md` · `prompts/claude-analyze-laguna-s-2026-07-29.md` |

## Numbers (do not invent beyond these)

- Historical measured Q4 tuple: 40/40 format/routing · hermes 27/27 tools-not-executed · **21.47 t/s** gen128 · measure tip `bf82eab` · eng `04b2b72`
- DFlash: 15.286 t/s gen128 · **not** ship

## Still open (freeze path)

1. HF docs tip after this commit (docs-only, no weights)
2. Public promo lock until **2026-08-03 12:00 WIB**
3. Freeze clock **2026-08-02 18:00 WIB** — no early freeze

## Locks held

- diy_gguf false
- weight_host Spark-only
- no DFlash speedup claim
- no company-gate vault write
- measure tip sticks at bf82eab
