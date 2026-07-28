# Post-freeze path — Mac mini / MacBook / PC / laptop quants

Status: **gated** — only after Aug 3 launch bar holds on Spark official Q4_K_M.
Personal surface only. Freeze lock still applies until launch.

## Bottom line

Do **not** ship smaller SKUs to chase top-10 before the Spark Q4 bar is public and stable.

Win sequence:

1. Hold Spark official Q4_K_M (40/40 agent_smoke + ~21 tok/s gen128 + digests).
2. Publish pack so strangers can reproduce.
3. Then map smaller third-party quants with the **same harness**.
4. Only promote a Mac/PC SKU if agent quality stays within −2/40 of official (or better).

## Why this order

- Global HF top-10 is **reach**, not one better GGUF.
- Our defensible win is **measured agent runtime on Spark + official digest binding**.
- DIY or third-party small quants without same-harness evidence dilute the card.

## Device targets (after unlock)

| Device class | RAM ballpark | Candidate class | Engine |
|--------------|--------------|-----------------|--------|
| DGX Spark (now) | 128G | Official Q4_K_M (~96G) | poolside llama.cpp laguna |
| High-end workstation | 64–128G | Q4_K_M / UD-Q4_K_XL | llama.cpp CUDA/Metal/ROCm |
| Mac Studio / mini M-series maxed | 64–128G unified | UD-Q4 / IQ4 family or MLX port | llama.cpp Metal or MLX |
| MacBook 32–48G | 32–48G | IQ3 / UD-Q3 / aggressive IQ4 | Metal/MLX — expect quality drop |
| PC laptop 16–24G | 16–24G | Likely **not** full Laguna-S-2.1; need distill or MoE-off path — out of scope unless research proves otherwise | — |

Sizes above are order-of-magnitude from current HF shard layouts; **sum all shards** before claiming fit.

## Gate checklist for any new SKU card section

- [ ] Same `eval/agent_smoke` 40 cases
- [ ] Same method doc (temp, max tokens, tools schema)
- [ ] Host labeled honestly (never call Mac numbers "Spark")
- [ ] sha256 + source repo (Unsloth/Bartowski/official)
- [ ] Delta vs Spark official Q4_K_M published
- [ ] Fail cases listed (no silent drop)
- [ ] Founder go before any public claim change

## Promotion rule

Promote third-party or DIY only if:

- agent_smoke ≥ official − 2 (i.e. ≥38/40 if official is 40), **and**
- clear device-fit win (RAM/speed), **and**
- method fully disclosed

Else: keep as research footnote only.

## Explicit non-goals until founder reopen

- No freeze break for boutique GGUF
- No bulk multi-size rehost of Unsloth tree
- No Nemotron swap as Laguna headline
- No claim of global HF top-10 from device proliferation alone
