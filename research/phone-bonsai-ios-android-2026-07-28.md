# Phone bonsai — fit Laguna agent identity to iOS / Android

Status: research (2026-07-28). Personal. Not a scoreboard claim.

Premise lock: **full Laguna-S-2.1 (even IQ3_S ~ half-size of Q4) does not fit phone RAM**.
Mac mini / MacBook / PC quant success does **not** carry to iPhone or Android.
Phone path = **bonsai** (distill / SLM / stack split), not another GGUF of the same MoE.

Stand-behind headline unchanged: Spark official Q4_K_M 40/40.

---

## Bottom line

| Claim | Verdict |
|-------|---------|
| Quant full Laguna onto iPhone/Android | **No** |
| Same 40/40 agent_smoke bar on-device | **No** (bar too big; model too big) |
| Ship a **Laguna-shaped small agent** on phone | **Yes**, separate SKU family |
| Best shape | **Bonsai student 0.5B–2B** + tool router + optional cloud teacher |
| Best runtimes | iOS: MLC-LLM / llama.cpp Metal · Android: MLC / llama.cpp + ExecuTorch where PyTorch path |
| Identity | New card prefix e.g. `laguna-bonsai-*` — never rebrand full Laguna |

---

## Why full Laguna cannot phone-fit

### RAM envelope (order of magnitude)

Weights only (no KV), approximate GB:

| params | Q4_K_M | Q3 / IQ3 | BitNet~1.58 |
|--------|--------|----------|-------------|
| 0.5B | 0.28 | 0.20–0.23 | ~0.12 |
| 1B | 0.57 | 0.40–0.45 | ~0.25 |
| 2B | 1.1 | 0.8–0.9 | ~0.50 |
| 3B | 1.7 | 1.2–1.4 | ~0.75 |
| 7–8B dense | 4–5 | 3–3.6 | ~1.8–2.0 |
| **Laguna-S-2.1 MoE Q4** | **~90–96G** | IQ3 still tens of GB | n/a |

Practical app budget after OS (soft):

| device class | device RAM | usable app ~ | safe model+KV |
|--------------|------------|--------------|---------------|
| iPhone 15/16 class | 8G | ~3–3.5G | **≤ ~2.5–2.7G** |
| iPhone Pro class | 12G | ~5–5.5G | **≤ ~4.5G** |
| Android 8G | 8G | ~3–3.5G | **≤ ~2.5G** |
| Android flagship 12G | 12G | ~5–5.5G | **≤ ~4.5G** |

Add KV @ 4k–8k, tokenizer, UI, OS jetsam headroom → **phone hard ceiling is ~1–3B @ 4-bit**, not 100B-class sparse MoE on disk.

Sparse MoE still **stores all experts**. Activation sparsity ≠ download/RAM sparsity unless you **prune experts / nest** (FlexMoE-class) and re-export a tiny subnetwork — still a new model, not “quant the GGUF harder.”

### iOS-specific

- Jetsam kills apps that grow past device class budget; no swap like desktop.
- Background freeze; long agent loops are foreground or push-driven.
- Store path: ANE / Metal preferred for App Store polish; C++ via MLC or llama.cpp is proven for indie / TestFlight.
- Core ML conversion helps ANE for supported ops; exotic MoE kernels often **fail conversion** → keep phone student dense/simple.

### Android-specific

- Huge RAM skew (6G–16G+). Must ship **tiered assets** or download-on-first-run by RAM class.
- NNAPI / Vulkan / OpenCL backends vary by OEM; MLC + llama.cpp are the portable bets.
- ExecuTorch (Meta) is the PyTorch-native production path (Meta on-device apps); great if student stays in ET-known archs.
- Thermal + big.LITTLE: sustained tokens crack after tens of seconds; design short tool turns, not 2k-token monologues.

---

## What “bonsai” means here

Bonsai ≠ max Q-drop on the same tree.

Bonsai = **genetic reduction + shape prune + water small pot**:

1. **Smaller genome** — student 0.5B / 1B / 2B dense (or BitNet 2B).
2. **Shape for the pot** — deep-thin MobileLLM-style, GQA, shared embed, short default context (2k–4k on device).
3. **Teach from Laguna** — distillation / imitation on **agent traces**, not only chat Wikipedia-MJ.
4. **Split the organism** — on-device planner / tool-caller; heavy reasoning optional cloud teacher (Laguna Spark) with privacy gate.
5. **Never claim the tree is the forest** — separate HF / scoreboard row; humble discipline on agent bar.

---

## Research stack that matters (2024–2026)

### Architecture for sub-billion / ~1B on-device

| work | id | takeaway for us |
|------|----|-----------------|
| MobileLLM | 2402.14905 | Deep-thin + embed share + GQA beats naive wide-small. Architecture > just “more tokens” under 1B. |
| MobileLLM-Pro ~1B | 2511.06719 | SOTA-class ~1B, 128k via positional distillation, merges, minor 4-bit hit. Template for phone **general** LM. |
| MobileLLM-R1 | 2509.24945 | Sub-B **reasoning** with open recipes; CoT can emerge well below “big model only.” |
| MobileLLM-Flash | 2603.15954 | **Latency-guided** NAS / prune from backbone; ExecuTorch-friendly; attention skipping for long ctx. Industry deploy shape. |
| MiniCPM 1.2B/2.4B | 2404.06395 | SLM can match older 7–13B class on many tasks with good recipe. |
| MiniCPM-V | 2408.01800 | Multimodal **on phone** exists — but dual-modality budget fights pure agent tools; later track. |
| TinyLLM | 2412.15304 | 30–120M **task-curated** can beat larger generalists on narrow tasks — backs ultra-narrow phone specialists. |

### Extreme compression

| work | id | takeaway |
|------|----|----------|
| BitNet b1.58 2B4T | 2504.12285 | Native ~1.58-bit 2B open weights; real memory/energy wins if runtime is bitnet.cpp-class. |
| bitnet.cpp | 2410.16144 | Fast lossless ternary on CPU/ARM — relevant Android / iOS CPU fallback. |
| FBI-LLM | 2407.07093 | Fully binary via autoregressive distillation — research edge, hardware story still maturing. |
| EdgeRazor | 2605.04062 | Mixed-precision QAD; sub-2-bit MobileLLM/Qwen6e-1 students — if we push below 4-bit quality. |

### MoE → smaller (only if we ever bonsai *from* Laguna MoE body)

| work | id | takeaway |
|------|----|----------|
| FlexMoE | 2606.27866 | One train → **nested** deployable subnets across budgets. Closest “prune Laguna into device ladder” research. |
| MoE++ | 2410.07348 | Zero-compute experts — arch idea, not a free phone port of poolside MoE. |

Do **not** expect expert-pruning alone to bring Laguna-S-2.1 to 2G without catastrophic agent regression. Treat MoE prune as research; default phone path = **dense student**.

### Tools / agents with small models

| work | id | takeaway |
|------|----|----------|
| Small LLMs Are Weak Tool Learners | 2401.07324 | Single small LM fails full agent stack; **split** planner / caller / summarizer across small specialists. **Core bonsai pattern.** |

So for phone agent:

- Student-A: intent + plan (short JSON)
- Student-B: tool call format only
- Student-C: summarize / speak to user
- Optional: cloud Laguna for hard multi-step

This is how you keep Hermes-*shaped* behavior without 90G on device.

### Speculative / test-time

- Speculative decoding with **tiny draft on-device** verifying against mid student helps tok/s; draft can be 100–300M.
- Latent recurrent depth (2502.05171) = spend compute not tokens — interesting if thermal allows loop depth, research-only for Aug track.

---

## Runtime map (ship-relevant)

| stack | iOS | Android | notes |
|-------|-----|---------|-------|
| **MLC-LLM** | Metal A-series | OpenCL Adreno/Mali | Universal compile; OpenAI-compat engine; indie-friendly. |
| **llama.cpp** | Metal | Android NDK / Vulkan | GGUF path; matches our desktop harvest methodology. |
| **ExecuTorch** | yes | yes | PyTorch-native; Meta prod; LLM examples for Llama-class. Prefer if we train/export in PT. |
| **MediaPipe Tasks** | yes | yes | Strong for vision/audio tasks; LLM story secondary to MLC/ET. |
| **Core ML** | ANE | n/a | Convert when ops allow; fail-closed for exotic MoE. |
| **bitnet.cpp** | CPU | CPU/ARM | Only for BitNet students. |
| **MLX** | — | — | Mac; not phone. |

Recommendation:

- **Prototype path:** Q4/Q5 GGUF of dense student → llama.cpp iOS/Android samples (same smoke harness flavor, reduced bar).
- **Product path:** MLC or ExecuTorch once architecture freezes.
- **Do not** start phone path by converting Laguna MoE GGUF.

---

## Honest capability ladder (agent)

Desktop Laguna Spark: **40/40** agent_smoke + 27/27 Hermes-class (measured).

Phone expectations if we bonsai correctly:

| SKU class | size | likely role | ~/40-style agent bar |
|-----------|------|-------------|----------------------|
| bonsai-nano | 0.5B Q4 | classify, rewrite, single tool | **ship_min phone bar** (new suite ~12–20 cases), not 40/40 |
| bonsai-mini | 1B Q4 | plan + 1–2 tools | partial multi-step |
| bonsai-edge | 2B Q4 / BitNet2B | on-device default agent | better multi-step; still << Laguna |
| hybrid | student + Laguna cloud | full agent when online | cloud holds 40/40; device holds offline floor |

Define a **phone_agent_smoke** (separate harness): shorter tools schema, stricter latency, thermal budget, offline/online modes. Never scoreboard-merge with Spark 40/40.

---

## Distillation recipe (actionable)

### Data (the real moat)

Mine from Laguna teacher (Spark):

1. Agent trajectories that **passed** harness (tool JSON, multi-step, error repair).
2. Hard negatives: invented tools, broken JSON, overlong.
3. Synthetic repairs: corrupt → Laguna fix pairs.
4. Privacy scrub before any leave-box export.

Avoid: generic UltraChat-only SFT — tools won’t stick (see 2401.07324).

### Loss stack

1. **SFT** on clean tool traces (strict schema).
2. **On-policy distill** where student acts, teacher grades / relabels (best agent transfer).
3. Optional **token KD** (KL to teacher) on non-tool chat for fluency.
4. Optional preference (DPO/odds-ratio) on “good tool vs bad tool” pairs.

### Train budget (order)

- Student init: Qwen2.5-0.5B/1.5B-Instruct or MobileLLM-Pro / Gemma-3-1B class — pick one ecosystem and stay.
- LoRA first (days), full FT if LoRA plateaus.
- Quant-aware or post-train Q4_K_M/IQ4_XS export via llama.cpp / MLC convert.
- Always restore desktop teacher for eval of **teacher** quality; student has own card.

Gates (align Scientium-style joy when personal track hardens):

- Gate P0: student builds + loads iOS sim **or** Android emulator with < budget RAM.
- Gate P1: phone_agent_smoke ship_min.
- Gate P2: human 20-turn soak + thermal (surface temps / throttle).
- No “Laguna on iPhone” public line. Ever. Name it bonsai.

---

## Hybrid privacy pattern (recommended product)

```
[User on phone]
    → local bonsai (default)
         → simple tools (calendar, notes, local files perimeter)
    → hard / long / coding / multi-tool
         → optional escalate to Spark Laguna (TLS, founder network only)
         → return summary only to device
```

Privacy principle lock: sensitive founder inference stays on-box / sovereign; phone bonsai is personal endpoint class, not fleet A2A dump.

---

## Non-goals (phone)

- Scoreboard promote any phone number as Laguna-S-2.1
- Claim IQ3 Mac success ⇒ iPhone
- App Store “100B on phone” vibes
- Full 8k–128k context default on 8G phones
- Unsloth multi-quant rehost of Laguna for mobile

---

## Aug 3 vs later

### By 2026-08-03 12:00 WIB (docs + honesty only)

- Device matrix already: phone = **non-fit full model**
- This note linked from post-freeze path + matrix
- Optional: one **bare** public line on HF card: “Mobile: distill/SLM track only; full weights not phone-fit.”
- No phone weight publish required for Aug 3 clock

### Post-freeze build order (if founder greenlights compute)

1. Freeze phone_agent_smoke v0 (12–20 cases) + ship_min.
2. Choose student base (default lean: **Qwen2.5-1.5B-Instruct** or **MobileLLM-Pro-class 1B**).
3. Harvest Laguna tool traces on Spark (offline JSONL).
4. SFT + schema constrain → GGUF Q4 → MacBook smoke first (faster loop).
5. MLC or llama.cpp iOS sim + Android emulator RAM probe.
6. Only then TestFlight / internal APK.
7. Hybrid escalate toggle last.

---

## Decision packet (one decision)

**D1 — Phone track posture after Aug 3**

- A) **Docs-only** through promo clock (recommended default): non-fit declared; bonsai plan parked.
- B) **Open bonsai spike** post-freeze: trace harvest + 0.5–1.5B SFT week, no public claim.
- C) **Hybrid product spike**: bonsai offline floor + Laguna cloud escalate design (needs privacy review).

Default if silence: A until founder opens B/C.

---

## Sources (anchors)

- MobileLLM 2402.14905 · MobileLLM-Pro 2511.06719 · MobileLLM-R1 2509.24945 · MobileLLM-Flash 2603.15954  
- MiniCPM 2404.06395 · MiniCPM-V 2408.01800  
- BitNet b1.58 2B4T 2504.12285 · bitnet.cpp 2410.16144 · FBI-LLM 2407.07093 · EdgeRazor 2605.04062  
- FlexMoE 2606.27866 · TinyLLM 2412.15304  
- Small LLMs weak tool learners 2401.07324  
- ExecuTorch 2605.08195 · MLC-LLM (llm.mlc.ai)  
- Pack priors: `device-quant-matrix-aug3.md`, `post-freeze-smaller-device-path.md`  
- Measured IQ3_S agent_smoke 38/40 on Spark does **not** change phone non-fit

---

## One-line canon

**Phone gets a bonsai student taught by Laguna — never Laguna shoehorned into a phone.**
