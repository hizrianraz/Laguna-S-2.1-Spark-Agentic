# SKU measure — unsloth-ud-iq3-s

**Not headline.** Headline remains official Q4_K_M on Spark.

| Field | Value |
|-------|-------|
| Host | DGX Spark (gb10) |
| SKU | Unsloth `Laguna-S-2.1-UD-IQ3_S.gguf` |
| sha256 | `8a9ab3f8b3ff1723441cd251e873b295a7ef086d78dbae7515e5e27c8382b002` |
| bytes | 48428911520 (~45.1 Gi) |
| Engine | poolside llama.cpp laguna `04b2b72` |
| Serve | `:8000` briefly (Q4 stopped) · ctx 8192 · alias `local-laguna-iq3s` |
| agent_smoke | **38/40 · 95% · 71s** (2026-07-28 20:10 WIB) |
| fails | `repair_04`, `long_06` — same IDs as prior Q4 harness bugs; Spark runner was stale (no sanitize / any_of_tools) |
| ship gate | ≥ official−2 → **met** |
| Q4 restored | yes, alias `local-laguna` on `:8000` after measure |

Phone/tablet: **full Laguna non-fit** on iPhone/Android. See device matrix.
