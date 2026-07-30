# Spark Agentic Quant Standard (SAQS)

Updated: 2026-07-30 19:40 WIB  
Pack tree copy: 2026-07-30T21:10:42+07:00 (identical binder; root SoT remains portfolio `/SPARK_AGENTIC_QUANT_STANDARD.md` until freeze rehash)  
Status: **working standard** — binds release claims; smoke scores are not headlines  
Authority companions: `triple_aug3_lock.json` v6 · `FAMILY_MATRIX_AUG3.md` · `CAMPAIGN_AUG3_5.md`

## Defensible innovation

Quantization cannot make an upstream model smarter.

What is defensible:

> Secure deployment and independent reproduction of role-specialized agent packs  
> per 128 GB DGX Spark — retention measured only under this standard.

Not: three near-identical “\*-Agentic” wrappers.  
Yes: three **role-specialized** packs measured under **one public standard**.

## Three role-specialized packs (day-0 authority)

| Role | Public pack (today) | Canonical day-0 Spark artifact | Specialization (honest) |
|------|---------------------|--------------------------------|-------------------------|
| Flagship measured path | `Laguna-S-2.1-Spark-Agentic` | Official Poolside **Q4_K_M** GGUF + llama.cpp **04b2b72** (~36 GiB). DFlash **DO_NOT_PROMOTE**. NVFP4 = post-launch measured track only ([poolside/Laguna-S-2.1-NVFP4](https://huggingface.co/poolside/Laguna-S-2.1-NVFP4) is **not** day-0 flagship) | Repo-maintenance agent runbook — format/routing measured; **not** long-horizon agent reliability proof |
| Interactive coder | `Qwen3-Coder-Next-Spark-Agentic` | Quality: [Qwen/Qwen3-Coder-Next-FP8](https://huggingface.co/Qwen/Qwen3-Coder-Next-FP8) (~75 GiB). Speed: **agent-calibrated** NVFP4 (~44 GiB) only after SAQS pass | Interactive coding **throughput** (quality FP8 day-0) |
| Experimental reasoner | `DeepSeek-V4-Flash-REAP25-Spark-Agentic` | [twaggs88/DeepSeek-V4-Flash-REAP25-DSpark-ds4-GGUF](https://huggingface.co/twaggs88/DeepSeek-V4-Flash-REAP25-DSpark-ds4-GGUF) (~85 GiB) | Experimental **long-context investigation** — **NO_HERO default** |

### DeepSeek naming (critical)

- Official DeepSeek-V4-Flash-DSpark ≈ **155 GiB** — **does not fit** one 128 GB Spark.
- “**DSpark**” = DeepSeek’s **speculative-decoding module**, **not** “DGX Spark”.
- Single-Spark path = **25% expert-pruned (REAP25) + Pulsar** derivative.
- **Canonical public ID** (rename done 2026-07-30):

  `DeepSeek-V4-Flash-REAP25-Spark-Agentic`

- Legacy id `DeepSeek-V4-Flash-Spark-Agentic` = redirect stub only.
- Cards must never imply untouched official DeepSeek-V4-Flash on one Spark.
- Loader: **llama-server / GGUF only** — refuse vLLM/transformers for TYPE40.

## Release unit under test

Always the **complete** unit:

```
checkpoint + tokenizer/template + runtime + parser + agent scaffold + security policy
```

Same scaffold, task budget, tool schemas, and seeds for reference vs quantized variants.

Smoke (`40/40`, `2/2`, hermes `27/27`) = **tool-format / routing regression only**.  
**Never** headline agent benchmarks. **Never** invent retention % from smoke.

## Public battery (shared)

| Suite | Why |
|-------|-----|
| [BFCL V4](https://gorilla.cs.berkeley.edu/leaderboard) | Function calling: no-call, multi-turn, long-context |
| [Terminal-Bench 2.0](https://github.com/harbor-framework/terminal-bench-2) | Executed terminal work |
| [DeepSWE](https://github.com/datacurve-ai/deep-swe) + fresh SWE-rebench / SWE-bench-Live slice | Repo engineering |
| [τ-bench](https://taubench.com/) | Stateful, policy-constrained tool use |
| [RULER](https://github.com/NVIDIA/RULER) 8K–128K | Effective context |
| [AgentDojo](https://agentdojo.spylab.ai/) + coding-specific safety suite | Prompt injection / tool-output attack |

Protocol:

- Closed-loop tasks **×5**
- Publish **raw trajectories**
- Report **pass@1** and **repeat reliability**
- Benchmark tasks **strictly outside** any calibration corpus

## Hard release gates

| Axis | Hard gate |
|------|-----------|
| Agentic quality | Side-by-side vs higher-precision reference (same unit) — target bar set only after study; **no day-0 % label** |
| Per-benchmark regression | No category worse by > **3 pp** (when retention study runs) |
| Tool-call schema validity | ≥ **99.5%** |
| Wrong-tool / no-call false positives | ≤ **1%** |
| Critical security | **Zero** exfiltration, host escape, unauthorized destructive actions |
| Spark residency | Peak **non-swapped** ≤ **112 GiB**; ≥ **12 GiB** free |
| Stability | 8h **or** 500-req soak, **zero** crash/OOM |
| Reproduction | **Two** clean-machine runs, **one** independent Spark owner |

DGX Spark = unified memory. Capture `/proc/meminfo`, swap, page faults, pressure — not only `nvidia-smi`.  
(Ref: NVIDIA DGX Spark known-issues guidance.)

## Agent-calibrated quantization (when we host quants)

Generic 20–64 UltraChat 2K samples are **not** agent calibration.

Licensed corpus: hundreds → low thousands of:

- Exact JSON-schema tool calls
- Correct **no-tool** decisions
- Parallel + sequential tools
- Failures, retries, timeouts
- Repo inspect / edit / test loops
- Long code contexts
- Multilingual instructions + code
- Malicious instructions **inside** tool output and repo files
- Each model’s **native** reasoning + tool-call format

MoE extras:

- Measure expert activation coverage
- Preserve routers, shared-expert gates, embeddings, norms, output head, attention/DeltaNet at higher precision when sensitivity justifies
- Per-layer expert precision from measured KL/Fisher — not one uniform width

Publish: calibration commit · per-layer format map · full quant command.  
Keep eval tasks outside calibration.

### diy_gguf vs agent NVFP4

- **`diy_gguf: false` remains** for Laguna GGUF mirrors — host / pin **official** GGUF only; continue no claiming “first quant”.
- **Laguna day-0** = official **Q4_K_M** path. Never promote NVFP4+DFlash as day-0 flagship RC.
- **Agent-calibrated NVFP4** (Qwen speed lane) is a **named exception track**: only ship as our quant repo after SAQS gates + license clarity — **default Aug 3 = FP8 quality, NVFP4 = technical preview / hold**.

## Native protocols — not one forced Hermes template

External: one OpenAI-compatible API.  
Internal: **native** formats only:

| Model | Internal |
|-------|----------|
| Laguna | `poolside_v1` reasoning + tool parsers |
| Qwen3-Coder-Next | `qwen3_coder` (**non-thinking**) |
| DeepSeek V4 Flash / REAP25 | native `encoding_dsv4` + reasoning modes via Pulsar |

Universal Hermes prompt is convenience-only. Do not use it for graded SAQS runs.

## Shared secure runtime — Spark Agent Kit (target)

```text
spark-agent install laguna --profile quality
spark-agent serve laguna
spark-agent verify laguna
spark-agent connect opencode
```

Each model manifest pins:

- Checkpoint revision + SHA-256
- Runtime / container digest
- Native parsers + sampling defaults
- Tested context / concurrency profiles
- Quantization + calibration revisions (if any)
- Known failures + signed receipts

Security defaults:

- Bind **127.0.0.1** — never 0.0.0.0
- Real random API token
- Inference process ≠ tool-execution process
- Workspace-only filesystem sandbox
- Network **off** unless explicitly allowed
- Confirm destructive / externally visible ops
- Path traversal + symlink-escape protection
- Secret redaction, resource limits, SBOM
- No floating `latest`, no unpinned downloads

## Three repository layers

| Layer | Contains | `base_model_relation` |
|-------|----------|------------------------|
| **Checkpoint** | Actual weight files we host | `quantized` only if we produced/host the quant |
| **Deployment pack** | Manifests, launcher, docs, security policy | **not** finetune; **not** quantized |
| **Evaluation / dataset** | Cases, traces, signed receipts | n/a (dataset card) |

Rules:

- Strip misleading `base_model: finetune` / finetune-tree residue on packs.
- Never inherit upstream BF16 scores as if measured on our quant.
- Side-by-side **reference vs quant** table required when claiming retention.
- No secret SKUs on public surfaces.

## Positioning (earned, not day-0 label)

Working North Star (post-gate):

> Three role-specialized, agent-calibrated, independently reproduced models  
> on one DGX Spark. Retention percentages only after SAQS-grade side-by-side study.

“All three strongest” = **post-launch earned result**, never an Aug 3 label.

## Aug 3 working ship classes

| Model | Aug 3 class | Notes |
|-------|-------------|-------|
| Laguna S | **Measured path** on official **Q4_K_M** + llama.cpp **04b2b72** (smoke ≠ headline; not long-horizon proof) | Flagship hero Aug 3 20:00 · DFlash DO_NOT_PROMOTE · NVFP4 post-launch only |
| Qwen3-Coder-Next | **Quality FP8** profile; NVFP4 agent-cal = **tech preview** until SAQS | Hero Aug 4 iff pinned path + closed-loop + mem/context |
| DeepSeek REAP25 | **Explicit experimental / HOLD** (Pulsar + REAP25 + native encoding) | **NO_HERO default** (`hero_cta: null`); Aug 5 only if freeze re-opens |

Sequential promote Aug 3–5 and likes7d overlap stay as in `CAMPAIGN_AUG3_5.md`.

honesty: smoke ≠ headline · verifier ≠ gate clearance · local rewrite ≠ freeze clearance
