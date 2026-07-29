# Spark agentic quant fit — 4 models (2026-07-29)

Scope: single-node DGX Spark class (~121–128 Gi unified). Agentic usage = tools + multi-turn repair + OpenAI `/v1` Hermes-class client. Active-param math is a FLOP floor only; pack size decides residency.

Usable residency band after OS + light services + KV: **~90–105 Gi**.

Incumbent on Spark: Laguna-S-2.1 official Q4_K_M ~96 Gi, measured ~21 tok/s gen, agent_smoke 40/40. Do not displace without same-harness beat.

---

## Ranked bottom line

| Rank | Model | Residency | Offload | Agentic note | Decide |
|------|-------|-----------|---------|--------------|--------|
| 1 | **Qwen3-Coder-Next** | YES (Q4 ~45 Gi) | N/A needed | Built for coding agents; tool parsers shipped | **Next probe** |
| 2 | **Apertus-70B-Instruct-2509** | YES (Q4 ~41 Gi) | N/A | Dense 70B; agentic secondary; gated AUP | Serious spare / multilingual |
| 3 | **DeepSeek-V4-Flash** | Borderline IQ3-class ~90–96 Gi; Q4 ~144 Gi NO | Possible | Strong general/agent; experts already FP4 ship | Probe only after Qwen ladder mature |
| 4 | **Solar-Open2-250B** | IQ1/IQ2 edge only; Q4 ~141 Gi NO | Yes w/ fork | Interracial agent claim; **foreign arch** | **Hold** — engine tax + license other |

Do **not** pull all four overnight. One ladder at a time. Keep Laguna stand-behind.

---

## 1. Qwen/Qwen3-Coder-Next — FIRST ladder

| | |
|---|---|
| Arch | `qwen3_next` hybrid (Gated DeltaNet + MoE + Gated Attn) |
| Total / active | **80B / 3B** |
| Experts | 512 routed, top-10 + 1 shared |
| Context | 262k native |
| License | Apache-2.0 |
| BF16 pack | ~148.4 Gi |
| Official FP8 | ~74.9 Gi |
| RedHat NVFP4 | ~44.3 Gi |

**GGUF (summed):**

| Quant | Size (GiB) | Source note |
|-------|------------|-------------|
| Unsloth UD-Q4_K_XL | **46.2** (single file in tree) | root files + multi-shard dirs for thicker |
| Official Q4_K_M | **45.09** | `Qwen/Qwen3-Coder-Next-GGUF` |
| MXFP4_MOE | 44.73 | Unsloth |
| UD-Q3_K_M | ~33.5 | Unsloth |
| UD-IQ4_XS | ~35.8 | Unsloth |
| Q8 / UD-Q8 | ~79–80 | thicker |
| Unsloth guide | **>45 GB unified for 4-bit; >30 GB for 2-bit XL+** | Macifs; Spark is freer |

**Spark residency:** YES at Q4 and above under 50 Gi pack. Plenty of KY + concurrent headroom next to OS. Can co-exist with Laguna only if one is swapped/serialised — not dual warm.

**Agentic:** Primary product claim is coding agents, long-horizon tools, IDE scaffolds. Official vLLM/SGLang `--tool-call-parser qwen3_coder`. Unsloth notes llama.cpp tool-call parse fixes (2026-02). Best fit to "agentic on Spark" brief.

**Risks:** Hybrid DeltaNet path needs **current** llama.cpp / engine, not stale Spark runner. Do not DIY GGUF until official/Unsloth Q4 fails smoke vs Laguna by ≥10% or won't load.

**Ladder (one prefix only):**
1. Official `Qwen3-Coder-Next-Q4_K_M` (~45 Gi) **or** Unsloth `UD-Q4_K_XL` if imatrix spine preferred
2. Smoke: agent tools + multi-turn repair vs Laguna 40/40
3. Step up only if quality cliff (Q5 / Q6) or speed (MXFP4_MOE) wins on evidence
4. Kill: loops, broken tools, tok/s useless vs Laguna

---

## 2. swiss-ai/Apertus-70B-Instruct-2509 — dense spare

| | |
|---|---|
| Arch | Dense `apertus` (not MoE) |
| Total | **70B** (all active) |
| Context | 65k |
| License | Apache-2.0 **+ gated Acceptable Use** (SNAI/ETH/EPFL indemnify; PII filter duty) |
| BF16 | ~131.5 Gi |

**GGUF:**

| Quant | ~GiB |
|-------|------|
| Q4_K_M | **40.72** |
| UD-Q4_K_XL | 41.17 |
| Q5_K_M | 47.13 |
| Q3_K_M | 33.1 |
| Q8_0 | 69.87 |
| BF16 | 131.51 |

**Transformed quants:** RedHat FP8-dynamic ~67.8 Gi; NVFP4 ~39.9 Gi; w4a16 ~37.1 Gi.

**Spark residency:** YES at Q4/Q5 under ~50 Gi. Classic dense 70B Q4. Hosts fine on llama.cpp if arch is known; confirm Spark runner registers `apertus` before download.

**Agentic:** README has "Agentic Usage" section but product is multilingual fully-open transparency, **not** coding-agent first. Expect weaker tool-native behavior than Qwen3-Coder-Next / Solar / Laguna coding bar unless measured otherwise.

**Risks:** Gate form + ongoing PII hash-filter obligation. Not a free-blit publish base for a personal agent pack without policy read. Dense 70B Q4 active cost >> Qwen 3B-active MoE at same disk class → speed/agent may lose.

**Ladder:** Only if need multilingual compliant stack. Prefer Q4_K_M Unsloth/bartowski after load proof. Do not displace Laguna for chalk.

---

## 3. deepseek-ai/DeepSeek-V4-Flash — power, tight on disk

| | |
|---|---|
| Arch | MoE `deepseek_v4` hybrid attn (CSA/HCA) + MHC |
| Total / active | **284B / 13B** |
| Experts | 256 routed top-6 + 1 shared; **ship experts FP4**, rest FP8 block |
| Context | **1M** |
| License | MIT |
| Official pack | ~148.7 Gi (FP4/FP8 mixed already) |

**GGUF Unsloth (sum of shards):**

| Quant | Sum GiB | Residency on Spark |
|-------|---------|---------------------|
| UD-Q8_K_XL | 150.75 | NO full warm |
| UD-Q4_K_XL | **144.44** | NO full warm |
| UD-IQ4_XS/NL | 128.43 | NO / thrash risk |
| UD-Q3_K_XL/M | ~120.5 | NO full |
| UD-IQ3_S | **109.25** | Borderline–NO (over ~105) |
| UD-IQ3_XXS | **95.93** | Borderline YES if lean OS + short ctx |
| UD-Q2_K_XL | **90.18** | Plausible full residency |
| UD-IQ2_M / XXS | ~84.6 | Smaller |
| UD-IQ1_S | **76.87** | Fits disk/RAM; quality cliff risk |
| NVFP4 (nvidia) | **156.75** | NO residency; vLLM/SGLang path |
| DSpark | **155.44** | Spec decode add-on, not smaller base |

Unsloth card notes Q8 ~162 GB and "only 7 GB bigger than Q4" in their naming — tree confirms Q4 still ~144 Gi class: **not a 128 Gi full-residency Q4**.

**Spark:**
- Full residency: only aggressive IQ2/IQ3xxs / IQ1 territory — agent quality TBD.
- Honest Q4 residency: **no**.
- Offload / expert-page: possible if llama.cpp MoE offload proven on this arch; local NVMe only.
- NVFP4 ~157 Gi: engine path (SGLang PR noted for NVFP4), not full warm.

**Agentic:** Card lists agentic benches; tool/json structured out claimed on NVIDIA NVFP4 card. Broad generalist vs Qwen coder-specialist.

**Ladder (if opened):**
1. Do **not** start at Q4.
2. First smoke: `UD-Q2_K_XL` (~90 Gi) or `UD-IQ3_XXS` (~96 Gi) — residency stress @ ctx 4k–8k
3. Fail → expert-offload with local NVMe, or stop
4. Never pull multi-quant full repo; one prefix
5. DSpark only after base serve healthy (speculative overlay)

**DIY gate:** same as skill — only if marketed pack fails load or ≥10% agent_smoke / tok/s loss. Prefer Unsloth Dynamic 2.0 over late DIY.

---

## 4. upstage/Solar-Open2-250B — hold

| | |
|---|---|
| Arch | `solar_open2` Hybrid-Attn MoE (1 softmax + 3 linear KDA / block; NoPE; 1M ctx) |
| Total / active | **250B / 15B** |
| Experts | 320 routed top-8 + 1 shared |
| License | **other** (`upstage-solar-license`) — not Apache/MIT |
| BF16 pack | ~466 Gi |

**GGUF:**

| Quant | ~GiB | Note |
|-------|------|------|
| vcruz Q4_K_M | 141.39 | No full residency |
| vcruz IQ4_XS | 124.46 | Borderline thrash |
| prometheusAIR IQ4_XS | 126.88 | multi-shard |
| prometheusAIR Q2_K | 88.87 | Possible with offload/split |
| prometheusAIR IQ1_M | 56.30 | Edge residency |
| vcruz IQ1_M | 52.67 | Edge |
| Nota NVFP4 | ~142.8 | Transformers/vLLM class |
| Nota INT4 | ~133 | |
| Nota INT4 GlobalPruned | ~109.7 | Outside GGUF |

**Critical (prometheusAIR card):** GGUFs **do not run on mainline llama.cpp**. Need ~951-line `solar_open2` patch; until upstream merge, fork tax on Spark GB10 build (`121a`, isfinite, etc.). Measured guide hosts: 128 GB RAM + 96 GB Blackwell — more head than Spark unified alone for fat IQ4 without careful `-ncmoe` / `--no-mmap`.

**Agentic:** Strong product claim (tool parser `solar_open2`, Hermes Agent + Claude Code called out on card). Quality may be high — **engine + license block time-to-value**.

**Spark decide:** HOLD for agentic Spark pack until (a) arch in mainline or trusted Spark-built fork, (b) license read for personal redistribute, (c) one IQ2/Q2_K offload probe scheduled post-Qwen. Do not DIY-and-rehost under freeze pressure.

---

## Cross-cut for Hermes-class / agentic

1. **Protocol > boutique bit-width.** Tool JSON chroma, sanitize prior tool-args, jinja template, repair loops beat "one more IQ rung."
2. **Same-harness only** for rank claims vs Laguna: live `agent_smoke` + gen@≥128 + host-labeled tok/s + sha256.
3. **Serialize swaps** on Spark — cannot dual-warm ~90G Laguna + ~45–90G peer. Always restore Laguna cmdline to stand-behind port before session end.
4. **No K3 / multi-node framing** here; all four assessed single-box.
5. **Publish path:** personal measurements only; prefer official/Unsloth digests over DIY GGUF spam; positive personal framing (no exclusion-list branding).

---

## Recommended next actions (ordered)

1. **Keep Laguna-S Q4** as Spark stand-behind.
2. **Download one Qwen quant only** — prefer `Qwen/Qwen3-Coder-Next-GGUF` `Q4_K_M` (~45.09 Gi) or Unsloth `UD-Q4_K_XL` (~46.2 Gi) to Spark local NVMe `~/models/…`.
3. Prove load on current Spark engine (arch + tool parser). Short agent smoke vs Laguna.
4. Apertus Q4 only if multilingual/compliance need; check gated AUP first.
5. DeepSeek: open only after Qwen score known; start UD-Q2_K_XL / IQ3_XXS, never Q4-first.
6. Solar: hold for engine/license gate — research done, no pull.

---

## Sources (Hub tree API + README, live 2026-07-29)

- Official: `deepseek-ai/DeepSeek-V4-Flash`, `Qwen/Qwen3-Coder-Next`, `swiss-ai/Apertus-70B-Instruct-2509`, `upstage/Solar-Open2-250B`
- Quants sized: Unsloth GGUF trees (sum shards), Qwen official GGUF/FP8, nvidia/DeepSeek NVFP4, RedHat NVFP4/FP8/w4a16, prometheusAIR + vcruz Solar GGUF, nota-ai Solar NVFP4/INT4
- Skill canon: `single-node-moe-fit` v1.4.0

Spreadsheet purity: sizes are Hub `list_repo_tree` sums; re-verify LFS sha before serve.
