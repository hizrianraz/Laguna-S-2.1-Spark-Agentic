# Quant comparison scoreboard — Laguna-S-2.1 (2026-07-28)

Purpose: same-family quant map + **measured Spark evidence** for our stand-behind choice.
Not a global HF top-10 claimsheet. Global trending needs downloads/likes/recency — our wedge is **measured agent runtime on Spark + official digest binding**.

## Our stand-behind (measured live)

| Field | Value |
|-------|-------|
| Pack | `hizrianraz/laguna-s-2.1-spark` |
| Weights | official `poolside/Laguna-S-2.1-GGUF` · `laguna-s-2.1-Q4_K_M.gguf` |
| sha256 | `a8b55c75714ea73fd90ec85de5defdc0b8d88ca0ad2108343cdd8fc22f7583e4` |
| Host | DGX Spark GB10 · 121 Gi |
| Engine | poolside llama.cpp `04b2b72` laguna + isfinite patch |
| Serve | `:8000` · ctx 8192 · ngl -1 · jinja · fa on · alias `local-laguna` |
| Gen128 | **21.016 tok/s** · 128 tok · 6.091s |
| Prefill marks | 2k→1.022s · 8k→1.521s (OK replies) |
| agent_smoke | **40/40 (100%)** prior lock; live reconfirm this session |
| hermes_agent_smoke v2 | **27/27 (100%)** · 102.68 s · `results/hermes_agent_smoke.json` |

## Same-family GGUF landscape (HF metadata)

| Source | Likes | Downloads | Role vs us |
|--------|------:|----------:|------------|
| `poolside/Laguna-S-2.1-GGUF` | 157 | 90106 | official |
| `unsloth/Laguna-S-2.1-GGUF` | 222 | 129601 | unsloth |
| `bartowski/Laguna-S-2.1-GGUF` | 7 | 5235 | bartowski |
| `lmstudio-community/Laguna-S-2.1-GGUF` | 1 | 2991 | lmstudio |

### Size-class picks (single file or last shard size shown for multi-part — **sum shards for full disk**)

| Class | Official Poolside | Unsloth (example) | Bartowski (example) | LM Studio | Fit note |
|-------|-------------------|-------------------|---------------------|-----------|----------|
| Agent default Q4 | **`Q4_K_M` 96.03 GB** (our measure) | `Laguna-S-2.1-UD-Q4_K_XL-00003-of-00003.gguf` ~23.42 GB shard/file UD-Q4_K_XL | `Laguna-S-2.1-Q4_K_M-00002-of-00002.gguf` ~31.94 GB shard/file | `Laguna-S-2.1-Q4_K_M-00002-of-00002.gguf` ~31.22 GB shard/file | Spark 128G OK for official Q4_K_M |
| Dense Q8 | `Q8_0` 128.75 GB | multi-part Q8_0 | multi-part Q8_0 | multi-part Q8_0 | Heavy on 128G; optional |
| Smaller third-party | — | `Laguna-S-2.1-UD-IQ4_XS-00003-of-00003.gguf` ~7.74 GB shard/file / `Laguna-S-2.1-UD-Q3_K_M-00003-of-00003.gguf` ~4.04 GB shard/file | IQ/Q3 family present | — | Laptop/Mac candidates **after** freeze |

## Fair comparison method (locked)

1. **Same harness**: `eval/agent_smoke` (40 cases) + `scripts/bench_server.py` + gen128 chat.
2. **Same host**: DGX Spark only for headline numbers.
3. **Same engine**: poolside `laguna` fork at pinned SHA when model needs Laguna ops; stock llama.cpp only if it loads cleanly — note fork delta.
4. **Digest-bind**: publish sha256; no silent re-quant.
5. **No server swap during launch lock** without explicit founder go: live Laguna Q4 stays up.

## What we will / will not claim

| Claim | Status |
|-------|--------|
| First/only Laguna quant | **No** — Poolside/Unsloth/Bartowski exist |
| Best universal tok/s | **No** without same-harness wins |
| Spark-measured agent smoke 40/40 on official Q4_K_M | **Yes** (evidence in `results/`) |
| Spark-measured Unsloth UD-IQ3_S agent smoke ≥38/40 (not headline) | **Yes** · 38/40 · `results/sku_unsloth-ud-iq3-s/` |
| Full Laguna on iPhone / Android | **No** — explicit non-fit |
| Global HF top-10 overall | **Not a commit** — optimize pack cluster + agent evidence |
| Top tier *among Laguna Spark packs / measured agent runtimes* | **Target** |

## Cross-family (Nemotron) note

- On disk Spark: `Nemotron-3-Super-120B-Q4_K.gguf` ~66G.
- **Not swapped in** this window (would drop live Laguna serve).
- Post-freeze same-harness pulse is the fair path if founder wants scientific cross-base compare.

## Laptop / Mac mini / PC path (Aug 3 accelerated — parallel track)

**Unlocked 2026-07-28** for pack docs + pointer wiring before promo clock.
Does **not** move public promo. Live Q4 restored on `:8000` after one brief IQ3 window.

### IQ3_S same-harness (done 2026-07-28)

| Field | Value |
|-------|-------|
| SKU | Unsloth `Laguna-S-2.1-UD-IQ3_S.gguf` |
| sha256 | `8a9ab3f8b3ff1723441cd251e873b295a7ef086d78dbae7515e5e27c8382b002` |
| Host | DGX Spark (not Mac) |
| agent_smoke | **38/40 · 95% · 71s** |
| ship gate (≥38) | **met** |
| Headline? | **No** — row is pointer + delta |
| Evidence | `results/sku_unsloth-ud-iq3-s/` |
| Caveat | Spark runner lacked sanitize / any_of_tools; fails = closed harness IDs on Q4 |

### Remaining order

1. Hold Aug 3 lock: official Q4_K_M + 40/40 + hermes 27/27 + pack docs (**still lead**).
2. Optional: re-smoke IQ3 with **fixed** harness when GPU free (expect possible 40/40; do not block claims).
3. Pull `UD-IQ4_XS` if disk allows; smoke only when free.
4. Never relabel Mac/PC numbers as Spark; never claim iPhone/Android for full Laguna.
5. DIY imatrix only if it **beats** official/Unsloth on agent_smoke.

## Live bench stamp

- gen_bench: `[{"label": "gen8_short", "prompt_tokens": 49, "completion_tokens": 4, "latency_s": 0.47, "tok_s": 8.505}, {"label": "gen128", "prompt_tokens": 55, "completion_tokens": 128, "latency_s": 6.091, "tok_s": 21.016}, {"label": "prefill_heavy_gen64", "prompt_tokens": 424, "completion_tokens": 4, "latency_s": 1.074, "tok_s": 3.724}]`
- server_bench: `[{"mark": "2k", "latency_s": 1.022, "prompt_tokens": 836, "completion_tokens": 3, "completion_tok_s": 2.935, "content": "OK"}, {"mark": "8k", "latency_s": 1.521, "prompt_tokens": 3236, "completion_tokens": 3, "completion_tok_s": 1.973, "content": "OK"}]`
- captured_unix: 1785240774.865332

