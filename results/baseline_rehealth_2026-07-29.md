# Baseline re-health — 2026-07-29 (post-DFlash)

## Live prove

| Field | Value |
|-------|-------|
| When | **2026-07-29 15:50:58 WIB** |
| Host | DGX Spark |
| Process | `llama-server` pid live · ~8–10 min uptime at probe |
| `/v1/models` | **HEALTH_OK** |
| Chat completions | content **`OK`** · model `local-laguna` · fingerprint `b1-04b2b72` |
| GPU | memory load present · util idle after ping |
| Serve mode | plain Q4 (no DFlash draft) |

## Decision

**Baseline last-green restored and verified.**  
Headline pin unchanged: Q4 · 40/40 · hermes 27/27 · **~21.47 t/s** gen128.

## Non-actions

- No re-smoke required (weights/runner unchanged)
- No DFlash claim
- No freeze today
