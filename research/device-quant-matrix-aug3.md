# Device → quant matrix (Aug 3 accelerated track)

Status: **pre-launch parallel track** (unlocked 2026-07-28).
Personal pack only. Headline remain **Spark + official Q4_K_M**.

Promo: pack docs OK now · public trending/social still **2026-08-03 12:00 WIB**.

## Bottom line

Full **Laguna-S-2.1** (~118B MoE) does **not** fit every laptop.
We ship a **honest ladder** of third-party GGUF *pointers* + same-harness deltas — not bulk rehost, not fake laptop miracle claims.

| Device class | RAM (usable) | Prefer quant | Source | Total ~disk | Expect | Pack claim by Aug 3 |
|--------------|--------------|--------------|--------|-------------|--------|---------------------|
| DGX Spark GB10 | ~121 Gi | **official Q4_K_M** | poolside | **96.0 GB** | agent bar | **Stand-behind · measured 40/40 · ~21 t/s** |
| Mac Studio / high Mac mini (64–128G) | 64–128G | Unsloth **UD-IQ4_XS** or Bartowski **IQ4_XS** | unsloth / bartowski | **~58 / ~63 GB** | near-Q4 quality if engine OK | pointer + method; measure if host free |
| Mac Studio 64G tight | ~64G | Unsloth **UD-IQ3_S** / **UD-Q3_K_M** | unsloth | **~48 / ~54 GB** | quality dip | pointer; smoke before promote |
| MacBook / PC 48G | ~48G | Unsloth **UD-IQ3_XXS** / **UD-Q2_K_XL** | unsloth | **~44 / ~40 GB** | meaningful quality drop | research only unless ≥ official−2 |
| PC workstation 64–96G CUDA | 64–96G | Bartowski **Q4_K_S** / **IQ4_XS** or Unsloth **UD-Q4_K_S** | bartowski / unsloth | **~69 / ~63 / ~69 GB** | solid if VRAM+RAM enough | pointer + CUDA note |
| Laptop 16–32G | 16–32G | **No full Laguna SKU** | — | — | need distill / smaller base | **explicit non-fit** |

Sizes are **sum of GGUF shards** (HF live probe 2026-07-28). Runtime RAM ≫ disk; leave OS + KV headroom.

## Candidate IDs (pull scripts use these)

| sku_id | repo | path pattern | ~GB | target devices |
|--------|------|--------------|-----|----------------|
| `official-q4km` | `poolside/Laguna-S-2.1-GGUF` | `laguna-s-2.1-Q4_K_M.gguf` | 96.0 | Spark stand-behind |
| `unsloth-ud-q4k-xl` | `unsloth/Laguna-S-2.1-GGUF` | `UD-Q4_K_XL/*` (3 shards) | 73.4 | 96–128G workstation / fat Mac |
| `unsloth-ud-iq4-xs` | `unsloth/Laguna-S-2.1-GGUF` | `UD-IQ4_XS/*` (3 shards) | 57.6 | 64–96G Mac / PC |
| `unsloth-ud-iq3-s` | `unsloth/Laguna-S-2.1-GGUF` | `Laguna-S-2.1-UD-IQ3_S.gguf` | 48.4 | 64G Mac tight / 48–64G |
| `unsloth-ud-q2k-xl` | `unsloth/Laguna-S-2.1-GGUF` | `Laguna-S-2.1-UD-Q2_K_XL.gguf` | 39.7 | 48G class experiment |
| `bartowski-iq4-xs` | `bartowski/Laguna-S-2.1-GGUF` | `Laguna-S-2.1-IQ4_XS/*` | 63.3 | alt IQ4 for Radio / compare |

## Promotion gate (unchanged quality bar)

Promote a smaller SKU onto the **card scoreboard** only if:

1. Same `eval/agent_smoke` 40 cases (or named subset with disclaimer)
2. Same method (temp, max tokens, tools schema)
3. Host labeled honestly (never print Mac/PC numbers as "Spark")
4. sha256 + exact HF path
5. Delta vs Spark official Q4_K_M published
6. Fail cases listed
7. agent_smoke ≥ official − 2 (**≥38/40** if official is 40) **or** research footnote only
8. Founder go for any public claim change after freeze

Else: keep under `research/` + optional card "community ladder" table with **unmeasured** tag.

## Serve notes by OS

| Host | Engine | Notes |
|------|--------|-------|
| Spark | poolside `llama.cpp` `laguna` + CUDA | default pack path |
| Mac Metal | llama.cpp Metal **or** MLX port if available | Laguna ops may need laguna fork — test load first |
| PC CUDA | laguna fork or upstream ≥ Laguna support | ngl defendable on 24GB+ VRAM only for *active* path; MoE still RAM-heavy |
| PC ROCm / laptop iGPU | experimental | do not claim ship |

## What we will not say by Aug 3

- "Runs on any MacBook" / 16GB laptop full Laguna
- Replacing official Q4 as default without measure win
- Bulk multi-quant LFS rehost of Unsloth tree into our HF model
- Global HF top-10 from device count alone

## Aug 3 pack shape

1. **Headline**: Spark official Q4_K_M measured row  
2. **Device ladder**: this table on README + `research/device-quant-matrix-aug3.md`  
3. **Scripts**: `scripts/pull_sku.sh <sku_id>`  
4. **Measured smaller row(s)**: only if same-harness JSON exists under `results/sku_<id>/`  
5. **Hermes-class suite**: live **27/27** on Q4 · `results/hermes_agent_smoke.json`  

## Schedule (accelerated)

| When | Work |
|------|------|
| Jul 28–29 | Matrix + pull scripts + docs; Hermes v2 live on Q4; start 1–2 SKU downloads on Spark disk |
| Jul 30 | Alternate-port smoke for IQ4_XS or IQ3_S **without** killing :8000 Q4 if possible |
| Jul 31 | Mac path dry-run if RAM allows; stranger REPRODUCE |
| Aug 1 | Buffer / second measure window |
| Aug 2 18:00 | Freeze claims |
| Aug 3 12:00 | Promo go-live |

## Authority

Personal founder pack. Third-party quants remain Unsloth/Bartowski IP — we **point + measure**, default **do not rehost**.
