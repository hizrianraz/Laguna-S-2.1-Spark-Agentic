---
license: openmdw-1.1
license_name: openmdw-1.1
license_link: https://huggingface.co/poolside/Laguna-S-2.1/blob/main/LICENSE.md
language:
  - en
base_model:
  - poolside/Laguna-S-2.1
  - poolside/Laguna-S-2.1-GGUF
pipeline_tag: text-generation
tags:
  - deployment-pack
  - evaluation-pack
  - runtime-pack
  - laguna
  - laguna-s
  - laguna-s-2.1
  - poolside
  - moe
  - agentic-coding
  - coding
  - tool-use
  - function-calling
  - agents
  - dgx-spark
  - nvidia
  - cuda
  - llama.cpp
  - openai-compatible
  - measured
  - reproducible
  - not-a-model
---

# Laguna-S-2.1-Spark-Agentic

## Parameters

| | |
|--|--|
| **Total** | **~118B** (HF count 117.56B BF16) |
| **Active / token** | **~8B** |
| **Arch** | MoE · `LagunaForCausalLM` · 256 experts (top-10) + 1 shared |
| **Source** | [poolside/Laguna-S-2.1](https://huggingface.co/poolside/Laguna-S-2.1) |
| **This pack** | **runtime only** — no weights here |

> HF sidebar **Parameters** badge stays empty on purpose (no checkpoint in this repo).
> Use the table above for size. Full detail: [Model parameters](#model-parameters-upstream--not-this-pack).

**Measured DGX Spark deployment pack** for
[poolside/Laguna-S-2.1](https://huggingface.co/poolside/Laguna-S-2.1)
(118B total · ~8B active/token · MoE · agentic coding).

> This repository is a **runtime / evaluation pack**, not a model checkpoint and not a re-quant.
> Hugging Face may still list it under Models; treat it as a **runbook + harness + receipts**.

## Positioning

**Unique contribution:** proving how the **official** Poolside Q4_K_M behaves on a **single DGX Spark** — pinned engine, fail-closed digests, closed harness, honest negatives (DFlash).

**Not coded as:** boutique quant producer, base-model trainer, or long-horizon agent reliability proof.

| | |
|--|--|
| **Role** | Flagship measured deployment recipe |
| **Weights authority** | [poolside/Laguna-S-2.1-GGUF](https://huggingface.co/poolside/Laguna-S-2.1-GGUF) |
| **Optional mirror** | [hizrianraz/Laguna-S-2.1-GGUF](https://huggingface.co/hizrianraz/Laguna-S-2.1-GGUF) · byte-identical upstream · **not** re-quantized by this account |
| **Default quant** | Official Poolside `Q4_K_M` · ~89.4 GiB |
| **Host** | NVIDIA DGX Spark (GB10) |
| **agent_smoke** | **40/40** tool-format / routing **regression smoke** (see honesty section) |
| **Launch window** | 2026-08-03 12:00 WIB · freeze 2026-08-02 18:00 WIB |
| **Affiliation** | Independent · not Poolside · not Nous Research |

Launch calendar: [`LAUNCH_AUG3.md`](./LAUNCH_AUG3.md)

---

## Download weights (authoritative = Poolside)

Prefer upstream; mirror is convenience only:

```bash
# recommended
hf download poolside/Laguna-S-2.1-GGUF laguna-s-2.1-Q4_K_M.gguf --local-dir ~/models/laguna-s-2.1

# optional convenience mirror (same bytes)
hf download hizrianraz/Laguna-S-2.1-GGUF laguna-s-2.1-Q4_K_M.gguf --local-dir ~/models/laguna-s-2.1

echo "a8b55c75714ea73fd90ec85de5defdc0b8d88ca0ad2108343cdd8fc22f7583e4  laguna-s-2.1-Q4_K_M.gguf" \
  | (cd ~/models/laguna-s-2.1 && sha256sum -c -)
```

This pack is **not** the bulk weight host. It publishes **serve pins, digests, and smoke harness**.

---

## Model tree

```text
poolside/Laguna-S-2.1                 ← base (official)
├── poolside/Laguna-S-2.1-GGUF        ← official GGUF authority
├── hizrianraz/Laguna-S-2.1-GGUF      ← byte-identical mirror (not re-quant)
└── hizrianraz/Laguna-S-2.1-Spark-Agentic  ← this pack (runtime · measured)
```

HF **Model tree** = README YAML `base_model` → `poolside/Laguna-S-2.1` + `poolside/Laguna-S-2.1-GGUF`.
This pack is **not** a checkpoint.

---

## Model parameters (upstream · not this pack)

This repo hosts **no checkpoint weights**, so the HF sidebar **Parameters** widget stays empty by design.
Sizes below are copied from the upstream base — not re-counted here.

| Field | Value | Source |
|-------|-------|--------|
| Architecture | MoE · `LagunaForCausalLM` | poolside config |
| Total parameters | **~118B** (HF safetensors count **117.56B** BF16) | [poolside/Laguna-S-2.1](https://huggingface.co/poolside/Laguna-S-2.1) |
| Activated / token | **~8B** | upstream card (118B-A8B) |
| Experts | 256 routed (top-10) + 1 shared | upstream card + config |
| Pack role | runtime / smoke harness only | this repo |

---

## Why this pack

1. Pinned Spark serve settings that clear tool-format smoke
2. Fixed harnesses you can re-run (no vibes)
3. Official digests for fail-closed verify
4. OpenAI-compatible client notes for tool-agent stacks
5. Negative results retained (DFlash slower — do not promote)

---

## Highlights (measured tip · 2026-07-29 13:22 WIB)

| Metric | Result |
|--------|--------|
| Host | NVIDIA DGX Spark (GB10) |
| Quant | Official `laguna-s-2.1-Q4_K_M.gguf` |
| Engine | `poolsideai/llama.cpp` @ `04b2b72` (branch `laguna`) |
| Serve context flag | `-c 8192` |
| agent_smoke | **40/40** · 84.86 s · temp 0.0 · **format/routing smoke** |
| hermes_agent_smoke v2 | **27/27** · 100.1 s · temp 0.0 · **one-response; tools validated not executed** |
| Generation throughput (sole short-gen headline) | **~21.47 tok/s** @ **128 completion** tokens (prompt 67) |
| Measure tip | pack `bf82eab` |

Artifacts:
[`results/MEASURED.md`](./results/MEASURED.md) ·
[`results/measured.json`](./results/measured.json) ·
[`results/agent_smoke.json`](./results/agent_smoke.json) ·
[`results/hermes_agent_smoke.json`](./results/hermes_agent_smoke.json)

---

## Honesty clock (read before quoting scores)

### What 40/40 and 27/27 are

Useful **tool-format and routing regression smokes** on a fixed case list.

Receipt language (hermes suite): **tools validated, not executed**.

### What they are not

- Not long-horizon agent reliability
- Not multi-turn tool-result continuation proof
- Not exact argument-value / schema-hard proof for every case
- Not SWE-bench / BFCL / Terminal-Bench substitutes

### Bench label correction (server_bench marks)

Recorded prefill marks were labeled **2k** / **8k** for convenience.
Actual prompt token counts on the receipt:

| Mark label | Actual `prompt_tokens` | Latency | Completion |
|------------|------------------------|---------|------------|
| `2k` | **836** | 1.597 s | 3 tokens ("OK") |
| `8k` | **3236** | 4.78 s | 3 tokens ("OK") |

Do **not** cite these as full 2K/8K filled-context prefill rates.

### Generation headline limits

- **~21.47 tok/s** is one short-gen point: **67 prompt / 128 completion** tokens
- Same-day suite also logged gen8 ~10.6 t/s and gen256 ~21.9 t/s
- Not a multi-seed soaked long-session figure; warm-rep / p50-p95 TTFT / peak RAM still to strengthen

External signal bar (future, not claimed): BFCL V4 · τ-bench · Terminal-Bench 2.

---

## Quick start

```bash
# 1) Engine — pin the measured commit
git clone https://github.com/poolsideai/llama.cpp
cd llama.cpp
git checkout 04b2b72cb54048ead292884adbe11f284e3ec950
# Spark/GNU may need the isfinite patch in docs/BUILD_SPARK.md
cmake -B build -G "Unix Makefiles" \
  -DCMAKE_BUILD_TYPE=Release \
  -DGGML_CUDA=ON \
  -DCMAKE_CUDA_ARCHITECTURES=121a \
  -DLLAMA_CURL=ON
cmake --build build -j --target llama-server llama-cli llama-bench

# 2) Weights — upstream first + fail-closed digest
huggingface-cli download poolside/Laguna-S-2.1-GGUF \
  laguna-s-2.1-Q4_K_M.gguf \
  --local-dir ~/models/laguna-s-2.1
cp /path/to/this/pack/SHA256SUMS ~/models/laguna-s-2.1/
(cd ~/models/laguna-s-2.1 && sha256sum -c SHA256SUMS)

# 3) Serve (flags match last-green pin)
./build/bin/llama-server \
  -m ~/models/laguna-s-2.1/laguna-s-2.1-Q4_K_M.gguf \
  --host 127.0.0.1 --port 8000 \
  --ctx-size 8192 -ngl -1 --jinja \
  -fa on --alias local-laguna

# 4) Smoke — model id must match --alias
cd /path/to/this/pack
python eval/agent_smoke/run_smoke.py \
  --base-url http://127.0.0.1:8000/v1 \
  --model local-laguna

# 5) Optional hermes-class suite (does not replace step 4)
python eval/hermes_agent_smoke/run_hermes_smoke.py \
  --base-url http://127.0.0.1:8000/v1 \
  --model local-laguna \
  --out results/hermes_agent_smoke.json
```

| Guide | Path |
|-------|------|
| Spark notes | [`SPARK.md`](./SPARK.md) |
| Reproduce | [`docs/REPRODUCE.md`](./docs/REPRODUCE.md) |
| Build | [`docs/BUILD_SPARK.md`](./docs/BUILD_SPARK.md) |
| Last-green pin | [`results/LAST_GREEN_PIN.md`](./results/LAST_GREEN_PIN.md) |
| Sample client | [`hermes/`](./hermes/) |

---

## License

Base model and official GGUF: **OpenMDW-1.1** (Poolside).

- Pack copy: [`LICENSE`](./LICENSE)
- Upstream: https://huggingface.co/poolside/Laguna-S-2.1/blob/main/LICENSE

Retain notices. Pack scripts and eval harnesses are separate files with clear provenance.

---

## Base identity (pinned)

| Field | Value |
|-------|--------|
| Base model | `poolside/Laguna-S-2.1` |
| Base revision | `00af5a51782109b587a3b3bbf11875e566036fa7` |
| Architecture | 118B total · ~8B active/token · MoE |
| Official GGUF (authority) | `poolside/Laguna-S-2.1-GGUF` |
| Optional mirror | `hizrianraz/Laguna-S-2.1-GGUF` · **mirror only** |
| GGUF revision (upstream pin) | `fc4e481289523cf7d0df668da6d1d391616141ca` |
| Stand-behind quant | **official** `laguna-s-2.1-Q4_K_M.gguf` |
| Engine | `poolsideai/llama.cpp` · branch `laguna` · [PR #25165](https://github.com/ggml-org/llama.cpp/pull/25165) |

### Official GGUF digests (HF LFS metadata)

| File | sha256 |
|------|--------|
| `laguna-s-2.1-Q4_K_M.gguf` | `a8b55c75714ea73fd90ec85de5defdc0b8d88ca0ad2108343cdd8fc22f7583e4` |
| `laguna-s-2.1-Q8_0.gguf` | `d946b221d69f2c5f87a986952bcd3cfb75831e5a6a2184e626e361663e1bfe2b` |
| `laguna-s-2.1-F16.gguf` | `2036c9dcf70f59738d480d1da2a2a59c0a3a3c5bd4ab8c43a61d77fba031e1f8` |
| `laguna-s-2.1-DFlash-BF16.gguf` | `2ee8aa30338d6599bc7a8ce008cc57c56f2c2b2fdc21f6db9ecda203c751bfd4` |
| `laguna-s-2.1.imatrix` | `4a4f480f57a3251e3acfb1d35ffba64720662536135e4ca4f4d05b0732539be2` |

Pack verify file (GNU 2-column, Q4 default): [`SHA256SUMS`](./SHA256SUMS)

---

## Which quant to pull

| Goal | Artifact | Notes |
|------|----------|-------|
| **Default agent serve (Spark)** | Poolside **S Q4_K_M** | Headline smoke + short-gen |
| Higher fidelity (Spark) | Poolside **S Q8_0** | More RAM |
| Speculative decode experiment | + Poolside **DFlash-BF16** | Measured slower · **DO_NOT_PROMOTE** |
| Full **S** on Mac ≤32 GB RAM | **No local S weights** | Use Mac as **client → Spark** only |

`diy_gguf: false`. Do **not** claim “first quant”. Mirror ≠ re-quant.

---

## Tool-agent wiring (OpenAI-compatible)

OpenAI `chat.completions` + `tools` / `tool_calls` shape.
**Not** a Nous Research product claim or endorsement.
“Hermes-class” in older notes = that wire shape only.

```bash
export OPENAI_BASE_URL=http://127.0.0.1:8000/v1   # /v1 required
export OPENAI_API_KEY=sk-local
export OPENAI_MODEL=local-laguna

python hermes/sample_client.py

python eval/agent_smoke/run_smoke.py \
  --base-url "$OPENAI_BASE_URL" --model local-laguna
python eval/hermes_agent_smoke/run_hermes_smoke.py \
  --base-url "$OPENAI_BASE_URL" --model local-laguna \
  --out results/hermes_agent_smoke.json
```

Agent loop contract (production agents; richer than current smoke):

1. POST messages + tool schemas
2. If `tool_calls` → execute **only** offered names → append `role=tool`
3. Repeat until final `content`
4. Sanitize invalid prior `function.arguments` JSON before re-send

Config snippet: [`hermes/config.example.yaml`](./hermes/config.example.yaml)

---

## Scoreboard (honest)

Freeze clock: **2026-08-02 18:00 WIB** — no new claims after freeze without re-measure.

| Host | Quant | Ctx flag | Gen tok/s (128 compl.) | agent_smoke | hermes v2 | Role |
|------|-------|----------|------------------------|-------------|-----------|------|
| DGX Spark GB10 | official Q4_K_M | 8192 | **~21.47** (short-gen) | **40/40 format smoke** | **27/27 validated-not-executed** | **Headline pack** · engine `04b2b72` · tip `bf82eab` |

Ship minimum smoke ceiling historically used: **≥38/40** on this harness. Current: **40/40**.

Mandate: strengthen with multi-seed, actual tool execution, arg-value checks, warm TTFT stats — not ship day scope unless left green after freeze.

---

## Scope

**In scope**

- Measured Spark deployment packing
- Official weight pointers + digests
- Reproducible smoke harness + receipts

**Out of scope**

- Claiming this account quantized the weights
- Classifying this docs pack as a loadable GGUF model in prose
- Long-horizon agent SOTA claims from format smoke alone
- Fake or off-host benches labeled as Spark
- Local full-S weights on Mac hosts with ≤32 GB RAM
- Public announce / trending push before **2026-08-03 12:00 WIB**
- Shipping unmeasured XS/Qwen30/DeepSeek as peer “models”

---

## Attribution

| Component | Credit |
|-----------|--------|
| Model | Poolside Laguna S 2.1 © Poolside · OpenMDW-1.1 |
| GGUF | Poolside official conversions (authoritative) |
| Optional mirror | Byte-identical copy for bandwidth convenience only |
| Engine | poolsideai/llama.cpp `laguna` (+ upstream llama.cpp) |
| Pack, measurements, smokes | Independent work by [hizrianraz](https://huggingface.co/hizrianraz) |

## Disclaimer

Independent measurements on one DGX Spark.
Not affiliated with, endorsed by, or representing Poolside or Nous Research.

Updated local stage (Sol reframe): 2026-07-30 00:45 WIB
