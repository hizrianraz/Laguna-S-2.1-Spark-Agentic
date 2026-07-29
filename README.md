---
license: openmdw-1.1
base_model: poolside/Laguna-S-2.1
base_model_relation: quantized
tags:
  - laguna-s-2.1
  - moe
  - agentic-coding
  - dgx-spark
  - llama.cpp
  - hermes-class
  - openai-compatible
  - measured
library_name: gguf
pipeline_tag: text-generation
---

# Laguna-S-2.1-Spark-Agentic

Personal DGX Spark runtime pack for [poolside/Laguna-S-2.1](https://huggingface.co/poolside/Laguna-S-2.1)  
(118B total · ~8B active/token · MoE · agentic coding).

| | |
|--|--|
| **Author** | hizrianraz · personal, independent |
| **Launch** | 2026-08-03 12:00 WIB |
| **Content freeze** | 2026-08-02 18:00 WIB |
| **Weight host** | DGX Spark only |
| **Default quant** | Official Poolside `Q4_K_M` |
| **Not affiliated with** | Poolside · Nous Research |

This repository publishes **measured serve settings, digests, and agent smoke results**.  
It does **not** re-host GGUF weights by default.

Sibling research track (separate model):  
[`Laguna-XS-2.1-Mac-Agentic`](https://huggingface.co/hizrianraz/Laguna-XS-2.1-Mac-Agentic)

Calendar and definition of done: [`LAUNCH_AUG3.md`](./LAUNCH_AUG3.md)

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
| Measure tip | `bf82eab` · 2026-07-29 13:22 WIB |

Artifacts:  
[`results/MEASURED.md`](./results/MEASURED.md) ·  
[`results/measured.json`](./results/measured.json) ·  
[`results/agent_smoke.json`](./results/agent_smoke.json) ·  
[`results/hermes_agent_smoke.json`](./results/hermes_agent_smoke.json)

---

## What this pack provides

1. **Pinned Spark serve path** — CUDA 13 / GB10 · OpenAI-compatible `llama-server`
2. **Fixed agent smoke suite** — tool JSON, multi-step, repair, no invented tools (40 cases)
3. **Hermes-class smoke v2** — additional 27-case suite (does not replace the 40-case bar)
4. **Official digests only** — GNU `SHA256SUMS` for fail-closed verify
5. **Sample OpenAI-compatible client** oriented at tool-agent runtimes

DIY / third-party quants are published only when they beat official artifacts on the **same harness**.  
Otherwise this pack binds the official Poolside GGUF and reports the Spark delta.

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
| Official GGUF repo | `poolside/Laguna-S-2.1-GGUF` |
| GGUF revision | `fc4e481289523cf7d0df668da6d1d391616141ca` |
| Stand-behind quant | **official** `laguna-s-2.1-Q4_K_M.gguf` |
| Optional denser | official `laguna-s-2.1-Q8_0.gguf` |
| Engine | `poolsideai/llama.cpp` · branch `laguna` · PR trail [ggml-org/llama.cpp#25165](https://github.com/ggml-org/llama.cpp/pull/25165) |

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
| Full **S** on founder Mac ≤32G | **No local S weights** | Mac is **client → Spark** only |
| Higher fidelity (Spark) | Poolside **S Q8_0** | More RAM |
| Smaller community box (pointer) | Unsloth UD-IQ4_XS / Bartowski IQ4_XS | Third-party · re-run smoke |
| Tighter Spark pointer | Unsloth **UD-IQ3_S** (~48 GB) | Spark **38/40** on older runner · **not** headline |
| Speculative decode experiment | + Poolside **DFlash-BF16** | Measured slower · **DO_NOT_PROMOTE** |
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

Under launch lock, power is **agent fitness on a fixed harness**, not boutique re-quant names.

1. Poolside protects the **signal path** on official Q4 (imatrix + first-party chat template).
2. Same digest → strangers can **reproduce** without trusting a private pack-hosted binary.
3. Our headline is **40/40 agent_smoke + 27/27 hermes-class** on that exact file — not a mystery mixtype.
4. DIY / third-party only lands if it **beats** official by a clear margin on the **same** smoke runners, with method disclosure. Today: `diy_gguf: false`.

Looking unique on HF alone is not a reason to re-quant.

---

## Hermes-class wiring (copy-paste)

“Hermes-class” = OpenAI `chat.completions` + `tools` / `tool_calls` shape.  
**Not** a Nous Research product claim or endorsement.

```bash
# Spark already serving with captain flags:
#   -c 8192 -ngl -1 --jinja -fa on --alias local-laguna

export OPENAI_BASE_URL=http://127.0.0.1:8000/v1   # /v1 required
export OPENAI_API_KEY=sk-local
export OPENAI_MODEL=local-laguna

# Smoke probe (one shot, no tool execution)
python hermes/sample_client.py

# Launch-bar suites (temp 0)
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
4. Sanitize invalid prior `function.arguments` JSON before re-send (see runner / sample notes)

Config snippet for OpenAI-compatible agent stacks: [`hermes/config.example.yaml`](./hermes/config.example.yaml)  
Full notes + failure matrix: [`hermes/README.md`](./hermes/README.md)

Optional research expansion (not freeze bar):  
`eval/hermes_agent_smoke/cases_layer_b_v3.json` (**35** cases) — live claim only after Spark measure file exists.

---

## Quick start (stranger path)

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

# 2) Weights — official Q4 + fail-closed digest check
huggingface-cli download poolside/Laguna-S-2.1-GGUF \
  laguna-s-2.1-Q4_K_M.gguf \
  --revision fc4e481289523cf7d0df668da6d1d391616141ca \
  --local-dir ~/models/laguna-s-2.1
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
| Full Spark notes | [`SPARK.md`](./SPARK.md) |
| Reproduce | [`docs/REPRODUCE.md`](./docs/REPRODUCE.md) |
| Build | [`docs/BUILD_SPARK.md`](./docs/BUILD_SPARK.md) |
| Last-green pin | [`results/LAST_GREEN_PIN.md`](./results/LAST_GREEN_PIN.md) |
| Sample client | [`hermes/`](./hermes/) |

---

## Scoreboard

Freeze clock: **2026-08-02 18:00 WIB** · no new claims after freeze without re-measure.

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
| DFlash | gen128 **15.286 t/s** · **DO_NOT_PROMOTE** · served with `-ngl 99` (baseline pin `-ngl -1`) · [`results/dflash_2026-07-29/`](./results/dflash_2026-07-29/) |
| Locks | diy_gguf **false** · weights **Spark-only** · founder Mac **client-only** · public promo only after **2026-08-03 12:00 WIB** · XS **not** in S freeze |

Ship minimum smoke: **≥38/40**. Stretch / current measured: **40/40**.

---

## Scope boundaries

**In scope**

- Personal measured Spark runtime pack
- Official weight pointers + digests
- Reproducible agent evaluation harness

**Out of scope**

- Bare GGUF re-upload when official is the stand-behind artifact
- Org / company product branding on this surface
- Fake or off-host benches labeled as Spark
- Local full-S weights on founder Mac ≤32G
- Public announce / trending push before **2026-08-03 12:00 WIB**
- XS rows inside the S freeze lock set

---

## Attribution

| Component | Credit |
|-----------|--------|
| Model | Poolside Laguna S 2.1 © Poolside · OpenMDW-1.1 |
| GGUF | Poolside official conversions |
| Engine | poolsideai/llama.cpp `laguna` (+ upstream llama.cpp) |
| Pack, measurements, smokes | Personal work by **hizrianraz** |

## Disclaimer

Independent personal measurements on one DGX Spark.  
Not affiliated with, endorsed by, or representing Poolside or Nous Research.  

“Hermes-class” describes an OpenAI-compatible tool-calling runtime shape only — **not** a Nous endorsement.
