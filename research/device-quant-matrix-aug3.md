# Device → quant matrix (Aug 3 accelerated track)

Status: **pre-launch parallel track** (unlocked 2026-07-28).
Personal pack only. Headline remain **Spark + official Q4_K_M**.

Promo: pack docs OK now · public trending/social still **2026-08-03 12:00 WIB**.

## Bottom line

Full **Laguna-S-2.1** (~118B MoE) does **not** fit founder Macs.

**Founder Mac lock (2026-07-28):** MacBook Pro / Mac Studio in this house are **≤32G** (live Studio probe: M2 Max · **32G**).  
That means: **no full Laguna weights on Mac**. Mac role = **client to Spark**, not weight host.

We still publish a community ladder (48–64G+ boxes other people own) as *pointers* — never as “our Mac runs it.”

| Device class | RAM (usable) | Prefer quant | Source | Total ~disk | Expect | Pack claim by Aug 3 |
|--------------|--------------|--------------|--------|-------------|--------|---------------------|
| DGX Spark GB10 | ~121 Gi | **official Q4_K_M** | poolside | **96.0 GB** | agent bar | **Stand-behind · measured 40/40 · ~21 t/s** |
| **Founder MacBook / Mac Studio (≤32G) · full S** | **≤32G** | **No full S weights** | — | — | OS + app already fill RAM | **Mac = OpenAI client → Spark :8000** · full-S weight non-fit |
| **Founder Mac ≤32G · XS parallel** | **32G** (Studio live) | **XS Q4_K_M** (~18.9 Gi) | `poolside/Laguna-XS-2.1-GGUF` | **18.882 GiB** | disk candidate only | **separate model 33B-A3B** · **0 Mac smoke** · not S · see [`Laguna-XS-2.1-Mac-Agentic-fit-2026-07-28.md`](./Laguna-XS-2.1-Mac-Agentic-fit-2026-07-28.md) |
| Community fat Mac / mini (64–128G) *others* | 64–128G | Unsloth **UD-IQ4_XS** or Bartowski **IQ4_XS** | unsloth / bartowski | **~58 / ~63 GB** | near-Q4 if engine OK | community pointer only · **not founder-measured** |
| Community Mac/PC 48–64G *others* | ~48–64G | Unsloth **UD-IQ3_S** (first) | unsloth | **~48 GB** | quality dip | Spark same-harness IQ3_S **38/40** pointer · not Mac-local |
| PC workstation 64–96G CUDA | 64–96G | Bartowski **Q4_K_S** / **IQ4_XS** / Unsloth **UD-Q4_K_S** | bartowski / unsloth | **~69 / ~63 / ~69 GB** | if VRAM+RAM enough | pointer + CUDA note |
| Laptop 16–32G (any brand) full S | 16–32G | **No full S SKU** | — | — | distill / XS parallel | **full S non-fit** · XS is different product |
| iPhone / iPad / Android phone·tablet | ~4–12G class | **No full Laguna-S SKU** | — | — | MoE weights alone ~40GB+ | **explicit non-fit** — bonsai/SLM only; see [`phone-bonsai-ios-android-2026-07-28.md`](./phone-bonsai-ios-android-2026-07-28.md) |

Sizes are **sum of GGUF shards** (HF live probe 2026-07-28). Runtime RAM ≫ disk; leave OS + KV headroom.

### Founder “Laguna Mac” definition

| Phrase | Means | Does not mean |
|--------|-------|---------------|
| Laguna Mac (default) | Mac as **Hermes / OpenAI client** talking to Spark **S** | Full **S** weights in Mac unified memory |
| Laguna Spark | Weight host + measured bar for **S** (Q4 40/40) | — |
| Laguna XS on Mac | Separate **33B-A3B** track · Q4 ~19G candidate | A quant of S · measured ship · “S on Mac” |
| Community 64G ladder | Docs for strangers with fat boxes running **S** quants | Founder hardware claim |

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
| Spark | poolside `llama.cpp` `laguna` + CUDA | default pack path · **only weight host we stand behind** |
| Founder Mac ≤32G | **no local llama-server for full Laguna** | client: `OPENAI_BASE_URL=http://<spark>:8000/v1` · Tailscale OK |
| Community fat Mac Metal (64G+) | llama.cpp Metal **or** MLX if available | stranger path only; may need laguna fork — test load first |
| PC CUDA | laguna fork or upstream ≥ Laguna support | ngl defendable on 24GB+ VRAM only for *active* path; MoE still RAM-heavy |
| PC ROCm / laptop iGPU | experimental | do not claim ship |

## Phone / mobile (locked non-fit)

**Quant success on Mac mini / MacBook / PC does not imply iPhone or Android.**

- Full Laguna-S-2.1 is ~118B MoE. Smallest honest GGUF class we measured still **~45 Gi on disk** (UD-IQ3_S).
- Mobile NPU/RAM envelopes are roughly **4–12 GB**, with OS + UI overhead.
- No App Store / Play path claims for full weights.
- Path if founder wants mobile later: **distill / SLM / on-device small model** — separate product, not this pack's quant ladder.
- Do not market “quantized to phone” from desktop IQ3/IQ4 wins.

## What we will not say by Aug 3

- "Runs on MacBook Pro / Mac Studio" without saying **≤32G = client only**
- "Our Mac runs full Laguna" / any founder-Mac weight claim
- "Runs on any MacBook" / 16–32G laptop full Laguna weights
- "Runs on iPhone / Android" for full Laguna (even quantized)
- Replacing official Q4 as default without measure win
- Bulk multi-quant LFS rehost of Unsloth tree into our HF model
- Global HF top-10 from device count alone
- Mac/PC numbers labeled as Spark
- IQ3_S / IQ4_XS as "Laguna Mac" headline (those are **community ≥48G**, not founder Mac)

## Aug 3 pack shape

1. **Headline**: Spark official Q4_K_M measured row  
2. **Laguna Mac story**: Hermes/OpenAI **client → Spark** (copy-paste) · weight non-fit ≤32G in one line  
3. **Community ladder**: 48–64G+ pointers only · no founder-Mac measure row  
4. **Scripts**: `scripts/pull_sku.sh <sku_id>` (Spark / fat-box strangers)  
5. **Measured smaller row(s)**: only if same-harness JSON under `results/sku_<id>/` (Spark today)  
6. **Hermes-class suite**: live **27/27** on Q4 · `results/hermes_agent_smoke.json`  

## Schedule (accelerated)

| When | Work |
|------|------|
| Jul 28–29 | Matrix + pull scripts + docs; Hermes v2 live on Q4; IQ3_S pointer done |
| Jul 30 | Card: Mac ≤32G client path + non-fit; stranger REPRODUCE |
| Jul 31–Aug 1 | Buffer · no Mac weight chase |
| Aug 2 18:00 | Freeze claims |
| Aug 3 12:00 | Promo go-live |

## Authority

Personal founder pack. Third-party quants remain Unsloth/Bartowski IP — we **point + measure**, default **do not rehost**.
