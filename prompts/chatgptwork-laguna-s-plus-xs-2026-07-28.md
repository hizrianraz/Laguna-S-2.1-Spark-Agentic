# ChatGPT Work — Laguna S pack + XS Mac path (analysis only)

## Role
You are an external technical analyst. Advisory only.

## Hard denials
- No GPU, no deploy, no HF publish, no company-gate vault write, no git commit for the founder
- Do not treat this output as ship clearance
- Do not invent measured numbers

## Two tracks (never merge)

### Track A — Laguna-S-2.1 Spark pack (stand-behind)
- Personal pack: https://huggingface.co/hizrianraz/laguna-s-2.1-spark
- Local mirror path the founder will attach / paste: `~/code/hizrianraz/laguna-s-2.1-spark`
- Base: poolside/Laguna-S-2.1 (118B-A8B MoE)
- Weight host lock: **DGX Spark only**
- Founder Mac ≤32G: **client only** for full S — no local full-S weights
- Headline quant: official `poolside/Laguna-S-2.1-GGUF` `laguna-s-2.1-Q4_K_M.gguf`
  - sha256 `a8b55c75714ea73fd90ec85de5defdc0b8d88ca0ad2108343cdd8fc22f7583e4`
- Measured (Spark, 2026-07-28): agent_smoke **40/40**, hermes-class v2 **27/27**, ~**21 t/s** gen
- IQ3_S third-party pointer on Spark: **38/40** — not headline; always restore Q4 after alt smoke
- Launch: **2026-08-03 12:00 WIB** · freeze **2026-08-02 18:00**
- Branding: personal-only · no public promo before launch
- DIY GGUF: false unless measured win

### Track B — Laguna-XS-2.1 Mac ≤32G candidate (parallel, unmeasured)
- Base: https://huggingface.co/poolside/Laguna-XS-2.1  
  sha `205dc65dd4bda946c50da6b7522b215734fa107b`
- Shape: **33B total · 3B active** MoE (NOT a quant of S)
- Official GGUF: https://huggingface.co/poolside/Laguna-XS-2.1-GGUF
  - `Laguna-XS-2.1-Q4_K_M.gguf` ≈ **18.882 GiB** — disk candidate for ≤32G
  - `Laguna-XS-2.1-BF16.gguf` ≈ **62.334 GiB** — non-fit on founder Mac
- Poolside card says “Mac with 36 GB”; founder Studio is **exactly 32G** — tight, unproven
- Engine risk: llama.cpp Laguna path PR ggml-org/llama.cpp#25165 / poolside fork
- **Zero** founder same-harness agent_smoke on Mac for XS
- Forbidden labels: “S on Mac”, “S-lite”, “S-Mac=XS”, averaging S metrics with XS

## Inputs to analyze
1. Repo tree: README, LAUNCH_AUG3, research/device-quant-matrix-aug3.md, research/laguna-xs-2.1-mac-fit-2026-07-28.md, research/post-freeze-smaller-device-path.md, results/MEASURED.md, results/launch_lock.json, results/lorien_three_jury_spark_only_plus_xs_2026-07-28.json, results/hf_publish.json, eval/ layout
2. HF card for hizrianraz/laguna-s-2.1-spark (live)
3. poolside S + S-GGUF + XS + XS-GGUF cards (live sizes + claims)
4. Roadmap through freeze/launch

## Tasks
1. **Integrity audit (Track A):** overclaims, host-label blur, missing sha, freeze risks, promo creep
2. **Roadmap gap list:** what must be true by freeze 2026-08-02 18:00 for S pack honesty
3. **XS Mac path (Track B only):** realistic load envelope on 32G unified memory; quant options; engine gates; measurement checklist; pull order; what not to claim
4. **Separation check:** any doc line that could make a reader think full S runs on founder Mac
5. **Actionable cuts:** max 10 concrete doc/matrix edits (wording only) — no scope expansion

## Required output format
### A. Executive
- 5 bullets max

### B. Track A (S/Spark) findings
- table: finding | severity | evidence | fix

### C. Track B (XS/Mac) findings
- table: finding | severity | evidence | next measure step
- explicit: what is proven vs candidate

### D. Must-not list
- bullets the founder should keep locked

### E. Open questions
- ≤8, ranked

### F. Measurement checklist for XS Mac
- ordered, copy-pasteable

Stop after analysis. No ship decision language.
