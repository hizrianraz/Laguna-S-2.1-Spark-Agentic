# Smaller-device path — Mac mini / MacBook / PC / laptop

Status: **UNLOCKED for Aug 3 parallel track** (2026-07-28).
Still personal surface. Public promo clock unchanged: **2026-08-03 12:00 WIB**.

Canonical matrix → [`device-quant-matrix-aug3.md`](./device-quant-matrix-aug3.md)  
Pull helper → `scripts/pull_sku.sh`

## Bottom line

**Two roadmaps:** [`roadmap-dual-s-and-xs-2026-07-28.md`](./roadmap-dual-s-and-xs-2026-07-28.md)

**Founder Macs = MacBook Pro / Mac Studio ≤32G** (live Studio: M2 Max 32G).  
Full **S** weights **do not load** there. Default “Laguna Mac” = **client to Spark S**.  
**XS** is a **separate** 33B-A3B track for possible local Mac weights (Q4 ~19G) — prep only, unmeasured.

By Aug 3 (Roadmap A): Spark measured S bar + honest Mac client path + community fat-box S pointers.  
Roadmap B (XS) must **not** dilute or delay that freeze.

Do **not** swap the Spark official S Q4_K_M headline.  
Do **not** chase 64G Mac hardware we do not own.  
Do **not** call XS “S on Mac”.

## Order of work (accelerated)

1. Hold Spark official **S** Q4_K_M (40/40 + ~21 tok/s + digests).
2. Pack stranger reproduce path (Spark-weighted S).
3. Document **founder Mac ≤32G non-fit for full S weights** + OpenAI client → Spark.
4. Keep IQ3_S / IQ4 as **community S** pointers (Spark-measured SKU only).
5. Promote a **S** SKU to the scoreboard only if ≤ −2/40 vs official **and** host labeled.
6. **XS prep** (parallel): lock + matrix + dual roadmap — pull/smoke only after founder go; prefer WD_BLACK.

## Device targets

| Device class | RAM | Candidate | Engine | Aug 3 intent |
|--------------|-----|-----------|--------|--------------|
| DGX Spark | ~121G | Official **S** Q4_K_M (~96G) | poolside laguna CUDA | **stand-behind measured** |
| **Founder Mac · full S** | **≤32G** | **no full S weights** | Hermes / curl → Spark | **Laguna Mac = client** |
| **Founder Mac · XS parallel** | **32G** | official **XS** Q4_K_M (~18.9G) | laguna Metal / Ollama? | **research** · 0 smoke · see [`laguna-xs-2.1-mac-fit-2026-07-28.md`](./laguna-xs-2.1-mac-fit-2026-07-28.md) |
| Community workstation 64–128G | 64–128G | **S** UD-Q4_K_XL / IQ4_XS | CUDA / Metal | stranger pointer only |
| Community Mac/PC 48–64G | 48–64G | **S** UD-IQ3_S (Spark 38/40) | Metal/CUDA | stranger pointer; not founder Mac |
| Laptop 16–24G full S | 16–24G | no full S | — | distill / bonsai / or XS separate |

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
- "Runs on MacBook / Studio" weight claims for ≤32G founder fleet
- Waiting on / inventing a 64G Mac row for launch
- "Runs on any MacBook" claims
- Nemotron swap as Laguna headline
- Global HF top-10 from device count alone
- Public X/trending before Aug 3 12:00 WIB

## Authority

Personal founder pack. Third-party quants stay at source; we point + measure.

## Phone / tablet

Full Laguna (even IQ3) is **non-fit** for iPhone and Android. Mac/PC quant success does not carry to mobile. Distill/SLM only.

Deep research (bonsai path): [`phone-bonsai-ios-android-2026-07-28.md`](./phone-bonsai-ios-android-2026-07-28.md)

