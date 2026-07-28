# Smaller-device path — Mac mini / MacBook / PC / laptop

Status: **UNLOCKED for Aug 3 parallel track** (2026-07-28).
Still personal surface. Public promo clock unchanged: **2026-08-03 12:00 WIB**.

Canonical matrix → [`device-quant-matrix-aug3.md`](./device-quant-matrix-aug3.md)  
Pull helper → `scripts/pull_sku.sh`

## Bottom line

Ship a **device ladder + pointers + same-harness deltas** by Aug 3.

Do **not** swap the Spark official Q4_K_M headline.

Full Laguna-S-2.1 does **not** fit 16–32G laptops — say so on the card.

## Order of work (accelerated)

1. Hold Spark official Q4_K_M (40/40 + ~21 tok/s + digests).
2. Pack stranger reproduce path.
3. Download + alternate-port smoke 1–2 smaller SKUs on Spark disk (IQ4_XS, IQ3_S).
4. Document Mac/PC/laptop fit honestly (including non-fit).
5. Promote a SKU to the scoreboard only if ≤ −2/40 vs official.

## Device targets

| Device class | RAM | Candidate | Engine | Aug 3 intent |
|--------------|-----|-----------|--------|--------------|
| DGX Spark | ~121G | Official Q4_K_M (~96G) | poolside laguna CUDA | **stand-behind measured** |
| Workstation 64–128G | 64–128G | UD-Q4_K_XL / IQ4_XS | CUDA / Metal | pointer + optional measure |
| Mac Studio / mini 64–128G | 64–128G | UD-IQ4_XS / IQ4_XS | Metal / laguna fork | pointer; measure if host free |
| Mac / PC 48–64G | 48–64G | UD-IQ3_S / Q3_K_* | Metal/CUDA | pointer; quality dip expected |
| MacBook / PC 32G | ~32G | **full Laguna non-fit** | — | explicit non-fit (this Studio is 32G) |
| Laptop 16–24G | 16–24G | no full Laguna | — | distill / smaller base later |

## Gate checklist (any scoreboard SKU)

- [ ] Same `eval/agent_smoke` 40 cases
- [ ] Same method (temp, max tokens, tools schema)
- [ ] Host labeled honestly (never Mac numbers as "Spark")
- [ ] sha256 + exact source path
- [ ] Delta vs Spark official Q4_K_M
- [ ] Fail cases listed
- [ ] ≥ official − 2 **or** research footnote only
- [ ] Founder go for post-freeze claim edits

## Non-goals

- Bulk multi-quant LFS rehost of Unsloth/Bartowski trees
- "Runs on any MacBook" claims
- Nemotron swap as Laguna headline
- Global HF top-10 from device count alone
- Public X/trending before Aug 3 12:00 WIB

## Authority

Personal founder pack. Third-party quants stay at source; we point + measure.

## Phone / tablet

Full Laguna (even IQ3) is **non-fit** for iPhone and Android. Mac/PC quant success does not carry to mobile. Distill/SLM only.

