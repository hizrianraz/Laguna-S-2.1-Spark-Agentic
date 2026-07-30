# Spark Agentic Quant Standard (SAQS)

Updated: 2026-07-30
Status: **working claim standard, not a certification** — smoke scores are not headlines
Canonical public copy: this file; each pack carries an identical copy and its own `results/triple_aug3_lock.json`.

## Defensible innovation

Quantization cannot make an upstream model smarter.

What this family is trying to make defensible:

> Reproducible, evidence-labeled deployment profiles for one 128 GB DGX Spark.
> Security, retention, and specialization are claims only after their named gates pass.

Day 0 is not three equally measured models: Laguna is measured, Qwen is Preview,
and DeepSeek is an unmeasured HOLD scaffold.

## Three evidence classes (day-0 authority)

| Role | Public pack (today) | Canonical day-0 Spark artifact | Specialization (honest) |
|------|---------------------|--------------------------------|-------------------------|
| Flagship measured path | `Laguna-S-2.1-Spark-Agentic` | Official Poolside **Q4_K_M** GGUF + llama.cpp **04b2b72** (~96.0 GB / ~89.4 GiB). DFlash **DO_NOT_PROMOTE**. NVFP4 is post-launch only. | Repo-maintenance deployment target; format/routing measured; **not** long-horizon reliability proof |
| Interactive-coding Preview | `Qwen3-Coder-Next-Spark-Agentic` | [Qwen/Qwen3-Coder-Next-FP8](https://huggingface.co/Qwen/Qwen3-Coder-Next-FP8) (~75 GiB), pinned and single-residency only | Historical 2/2 API/chat availability probe; no day-0 throughput, concurrency, retention, or tool-success claim |
| Experimental research pointer | `DeepSeek-V4-Flash-REAP25-Spark-Agentic` | [twaggs88/DeepSeek-V4-Flash-REAP25-DSpark-ds4-GGUF](https://huggingface.co/twaggs88/DeepSeek-V4-Flash-REAP25-DSpark-ds4-GGUF) (~85 GiB), absent under HOLD | Unmeasured, non-runnable day 0, **NO_HERO** |

### DeepSeek naming (critical)

- Official DeepSeek-V4-Flash-DSpark ≈ **155 GiB** — **does not fit** one 128 GB Spark.
- “**DSpark**” = DeepSeek’s **speculative-decoding module**, **not** “DGX Spark”.
- Single-Spark path = **25% expert-pruned (REAP25) + Pulsar** derivative.
- **Canonical public ID** (rename done 2026-07-30):

  `DeepSeek-V4-Flash-REAP25-Spark-Agentic`

- Legacy id `DeepSeek-V4-Flash-Spark-Agentic` = redirect stub only.
- Cards must never imply untouched official DeepSeek-V4-Flash on one Spark.
- Loader: pinned **`ds4-server` only**. TYPE40 is not loadable by llama.cpp, Ollama, vLLM, or Transformers.

## Release unit under test

Always the **complete** unit:

```
checkpoint + tokenizer/template + runtime + parser + agent scaffold + security policy
```

Same scaffold, task budget, tool schemas, and seeds for reference vs quantized variants.

Laguna `40/40` and Hermes `27/27` are format/routing regression receipts with
documented scope limits. Qwen `2/2` is API/chat availability only. DeepSeek has
zero measured executions. **Never** convert any of them into agent benchmarks or retention percentages.

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

## Future SAQS certification targets

These are certification targets for later comparative claims. They are **not**
claims that the Aug 3 Preview/HOLD entries have passed, and they are not a reason
to relabel missing evidence as measured.

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
- **Agent-calibrated NVFP4** (Qwen speed lane) is a **named exception track**: only ship as our quant repo after SAQS gates + license clarity — **default Aug 3 = official FP8 Preview; NVFP4 = post-launch hold / exception track**.

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

- Bind **127.0.0.1** by default; any LAN exposure requires explicit opt-in and authentication
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
| Laguna S | **Measured path** on official **Q4_K_M** + llama.cpp **04b2b72** (smoke ≠ headline; not long-horizon proof) | Flagship hero candidate Aug 3 20:00 only after explicit freeze clearance · DFlash DO_NOT_PROMOTE · NVFP4 post-launch only |
| Qwen3-Coder-Next | Official FP8 **Preview**; historical 2/2 API/chat probe only; NVFP4 post-launch | `hero_cta: null` until a dated `:8001` remeasurement and explicit gate |
| DeepSeek REAP25 | **Experimental / HOLD**, TYPE40 absent, pinned `ds4-server` path not yet validated | **NO_HERO** (`hero_cta: null`) |

Listing all three does not authorize sequential promotion. Each CTA requires its own explicit gate.

honesty: smoke ≠ headline · verifier ≠ gate clearance · local rewrite ≠ freeze clearance
