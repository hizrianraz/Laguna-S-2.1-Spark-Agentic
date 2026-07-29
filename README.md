---
license: openmdw-1.1
base_model: poolside/Laguna-S-2.1
base_model_relation: quantized
tags:
  - laguna-s-2.1
  - moe
  - gguf
  - quantized
  - agentic-coding
  - coding
  - code
  - tool-use
  - function-calling
  - agents
  - agentic
  - dgx-spark
  - nvidia
  - llama.cpp
  - openai-compatible
  - hermes-class
  - measured
  - cuda
library_name: gguf
pipeline_tag: text-generation
---

# Laguna-S-2.1-Spark-Agentic

Measured **DGX Spark** runtime pack for
[poolside/Laguna-S-2.1](https://huggingface.co/poolside/Laguna-S-2.1)
(118B total · ~8B active/token · MoE · agentic coding).

## Download weights first (main download surface)

→ **[hizrianraz/Laguna-S-2.1-GGUF](https://huggingface.co/hizrianraz/Laguna-S-2.1-GGUF)**  
File: `laguna-s-2.1-Q4_K_M.gguf` · ~89.4 GiB · official Poolside bytes

```bash
hf download hizrianraz/Laguna-S-2.1-GGUF laguna-s-2.1-Q4_K_M.gguf --local-dir ~/models/laguna-s-2.1
echo "a8b55c75714ea73fd90ec85de5defdc0b8d88ca0ad2108343cdd8fc22f7583e4  laguna-s-2.1-Q4_K_M.gguf" | (cd ~/models/laguna-s-2.1 && sha256sum -c -)
```

This pack is **not** the bulk weight host. It publishes **serve pins, digests, and agent smoke**.

| | |
|--|--|
| **Default quant** | Official Poolside `Q4_K_M` (mirrored) |
| **Weights (default)** | [`hizrianraz/Laguna-S-2.1-GGUF`](https://huggingface.co/hizrianraz/Laguna-S-2.1-GGUF) |
| **Upstream GGUF** | [`poolside/Laguna-S-2.1-GGUF`](https://huggingface.co/poolside/Laguna-S-2.1-GGUF) |
| **Weight host (measure)** | NVIDIA DGX Spark (GB10) |
| **agent_smoke** | **40/40** |
| **Launch** | 2026-08-03 12:00 WIB |
| **Content freeze** | 2026-08-02 18:00 WIB |
| **Affiliation** | Independent · not Poolside · not Nous Research |

Sibling (separate model, not an S quant):
[`Laguna-XS-2.1-Mac-Agentic`](https://huggingface.co/hizrianraz/Laguna-XS-2.1-Mac-Agentic) · weights [`Laguna-XS-2.1-GGUF`](https://huggingface.co/hizrianraz/Laguna-XS-2.1-GGUF)

Launch calendar: [`LAUNCH_AUG3.md`](./LAUNCH_AUG3.md)

---

## Why this pack

Most GGUF pages ship weights only.
This pack ships the **agent path**:

1. Pinned Spark serve settings that actually clear tool-use smoke
2. Fixed harnesses you can re-run (no vibes)
3. Official digests for fail-closed verify
4. OpenAI-compatible client notes for Hermes-class / tool-agent stacks

Headline power on this surface means **agent fitness on a fixed harness**, not boutique re-quant names.

**Strongest signal on this surface:** official Q4_K_M + pinned poolside `llama.cpp` laguna branch + **40/40 agent_smoke** and **27/27 hermes_agent_smoke** on DGX Spark — not an unmeasured boutique quant rename.

---

## Highlights (measured tip)

| Metric | Result |
|--------|--------|
| Host | NVIDIA DGX Spark (GB10) |
| Quant | Official `laguna-s-2.1-Q4_K_M.gguf` |
| Engine | `poolsideai/llama.cpp` @ `04b2b72` (branch `laguna`) |
| Context | 8192 |
| agent_smoke | **40/40** · 84.86 s · temp 0.0 |
| hermes_agent_smoke v2 | **27/27** · 100.1 s · temp 0.0 |
| Generation throughput | **~21.47 tok/s** @ 128 completion (sole headline) |
| Measure tip | pack `bf82eab` · 2026-07-29 13:22 WIB |

Artifacts:
[`results/MEASURED.md`](./results/MEASURED.md) ·
[`results/measured.json`](./results/measured.json) ·
[`results/agent_smoke.json`](./results/agent_smoke.json) ·
[`results/hermes_agent_smoke.json`](./results/hermes_agent_smoke.json)

Optional research expansion (does **not** replace freeze bars):
Hermes-class Layer B v3 **35/35** · 137.56 s ·
[`eval/hermes_agent_smoke/layer_b_v3_live_receipt.json`](./eval/hermes_agent_smoke/layer_b_v3_live_receipt.json)

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

# 2) Weights — preferred mirror (official Q4 bytes) + fail-closed digest check
huggingface-cli download hizrianraz/Laguna-S-2.1-GGUF \
  laguna-s-2.1-Q4_K_M.gguf \
  --local-dir ~/models/laguna-s-2.1
# Upstream alternative: poolside/Laguna-S-2.1-GGUF @ fc4e481289523cf7d0df668da6d1d391616141ca
cp /path/to/this/pack/SHA256SUMS ~/models/laguna-s-2.1/
(cd ~/models/laguna-s-2.1 && sha256sum -c SHA256SUMS)

# 3) Serve (flags match last-green pin)
./build/bin/llama-server \
  -m ~/models/laguna-s-2.1/laguna-s-2.1-Q4_K_M.gguf \
  --host 127.0.0.1 --port 8000 \
  --ctx-size 8192 -ngl -1 --jinja \
  -fa on --alias local-laguna

# 4) Launch-bar smoke — model id must match --alias
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

Base model and derivatives: **OpenMDW-1.1** (Poolside).

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
| Official GGUF repo (upstream) | `poolside/Laguna-S-2.1-GGUF` |
| Preferred mirror | [`hizrianraz/Laguna-S-2.1-GGUF`](https://huggingface.co/hizrianraz/Laguna-S-2.1-GGUF) |
| GGUF revision (upstream pin) | `fc4e481289523cf7d0df668da6d1d391616141ca` |
| Stand-behind quant | **official** `laguna-s-2.1-Q4_K_M.gguf` |
| Optional denser | official `laguna-s-2.1-Q8_0.gguf` |
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

```bash
cp /path/to/this/pack/SHA256SUMS ~/models/laguna-s-2.1/
(cd ~/models/laguna-s-2.1 && sha256sum -c SHA256SUMS)
# or: ./scripts/pull_official_gguf.sh
```

---

## Which quant to pull

| Goal | Artifact | Notes |
|------|----------|-------|
| **Default agent serve (Spark)** | Poolside **S Q4_K_M** | Headline · 40/40 · 27/27 · ~21.47 t/s |
| Higher fidelity (Spark) | Poolside **S Q8_0** | More RAM |
| Tighter Spark pointer | Unsloth **UD-IQ3_S** (~48 GB) | Spark **38/40** on older runner · **not** headline |
| Smaller community box | Unsloth UD-IQ4_XS / Bartowski IQ4_XS | Third-party · re-run smoke |
| Speculative decode experiment | + Poolside **DFlash-BF16** | Measured slower · **DO_NOT_PROMOTE** |
| Full **S** on Mac with ≤32 GB RAM | **No local S weights** | Use Mac as **client → Spark** only |
| Phone / tablet | **Non-fit** | Need SLM/distill, not this MoE |

**XS is a separate model**, not an S quant.
Mac-class XS notes: sibling pack + [`research/`](./research/).

```bash
./scripts/pull_sku.sh official-q4km
./scripts/pull_sku.sh unsloth-ud-iq3-s    # pointer only
```

Device ladder: [`research/device-quant-matrix-aug3.md`](./research/device-quant-matrix-aug3.md)

Do **not** claim “first quant”.
Do **not** label third-party numbers as Spark-measured without same-harness JSON under `results/sku_*`.

### Why official Q4_K_M for agents

1. Poolside protects the **signal path** on official Q4 (imatrix + first-party chat template).
2. Same digest → anyone can **reproduce** without trusting a third-party binary.
3. Headline is **40/40 agent_smoke + 27/27 hermes-class** on that exact file.
4. DIY / third-party only lands if it **beats** official on the **same** smoke runners, with method disclosure. Today: `diy_gguf: false`.

Looking unique on HF alone is not a reason to re-quant.

---

## Hermes-class / tool-agent wiring

“Hermes-class” = OpenAI `chat.completions` + `tools` / `tool_calls` shape.
**Not** a Nous Research product claim or endorsement.

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

Agent loop contract:

1. POST messages + tool schemas
2. If `tool_calls` → execute **only** offered names → append `role=tool`
3. Repeat until final `content`
4. Sanitize invalid prior `function.arguments` JSON before re-send

Config snippet: [`hermes/config.example.yaml`](./hermes/config.example.yaml)
Full notes: [`hermes/README.md`](./hermes/README.md)

Mac client pointing at Spark:

```bash
export OPENAI_BASE_URL=http://<spark-host>:8000/v1
export OPENAI_API_KEY=sk-local
export OPENAI_MODEL=local-laguna
```

---

## Scoreboard

Freeze clock: **2026-08-02 18:00 WIB** — no new claims after freeze without re-measure.

| Host | Quant | Ctx | Gen tok/s | agent_smoke | hermes v2 | Role |
|------|-------|-----|-----------|-------------|-----------|------|
| DGX Spark GB10 | official Q4_K_M | 8192 | **~21.47** | **40/40** | **27/27** | **Headline** · engine `04b2b72` · tip `bf82eab` |
| DGX Spark GB10 | Unsloth UD-IQ3_S | 8192 | short-gen only | **38/40** | — | Pointer · older runner · not default |

### Measured detail (2026-07-29 13:22 WIB)

| Field | Value |
|-------|--------|
| Q4 sha256 | `a8b55c75714ea73fd90ec85de5defdc0b8d88ca0ad2108343cdd8fc22f7583e4` |
| Serve flags | `-c 8192 -ngl -1 --jinja -fa on --alias local-laguna` |
| Gen headline | **~21.47 tok/s** @ 128 completion · multi suite in `results/measured.json` |
| Prefill (server_bench) | 2k · 1.597 s · OK · / · 8k · 4.78 s · OK |
| agent_smoke runner | `3bb81080…` |
| hermes v2 runner | `20c1e52a…` |
| Closed harness fails (not weights) | `repair_04` sanitize · `long_06` `any_of_tools` judge |
| DFlash | gen128 **15.286 t/s** · **DO_NOT_PROMOTE** · [`results/dflash_2026-07-29/`](./results/dflash_2026-07-29/) |
| Locks | diy_gguf **false** · weights **Spark-only** · Mac full-S **client-only** · public promo after **2026-08-03 12:00 WIB** · XS **not** in S freeze |

Ship minimum smoke: **≥38/40**. Current measured: **40/40**.

---

## Scope

**In scope**

- Measured Spark runtime pack
- Official weight pointers + digests
- Reproducible agent evaluation harness

**Out of scope**

- Bare GGUF re-upload when official is the stand-behind artifact
- Org / company product branding on this surface
- Fake or off-host benches labeled as Spark
- Local full-S weights on Mac hosts with ≤32 GB RAM
- Public announce / trending push before **2026-08-03 12:00 WIB**
- XS rows inside the S freeze lock set

---

## Attribution

| Component | Credit |
|-----------|--------|
| Model | Poolside Laguna S 2.1 © Poolside · OpenMDW-1.1 |
| GGUF | Poolside official conversions |
| Engine | poolsideai/llama.cpp `laguna` (+ upstream llama.cpp) |
| Pack, measurements, smokes | Independent work by [hizrianraz](https://huggingface.co/hizrianraz) |

## Disclaimer

Independent measurements on one DGX Spark.
Not affiliated with, endorsed by, or representing Poolside or Nous Research.

“Hermes-class” describes an OpenAI-compatible tool-calling runtime shape only — **not** a Nous endorsement.
