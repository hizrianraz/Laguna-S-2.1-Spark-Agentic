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

# personal · not Ainfera · not Neptune · not Fin · not Gate0

**Launch target: 2026-08-03 (WIB)** — see [`LAUNCH_AUG3.md`](./LAUNCH_AUG3.md)

Personal DGX Spark agent-runtime pack for [poolside/Laguna-S-2.1](https://huggingface.co/poolside/Laguna-S-2.1) (118B-A8B MoE, agentic coding).

This is **not** an Ainfera product, not Neptune Core, not Fin-70B, and not Gate0.
Unrelated to company org ships. Solo founder personal HF surface only.

## What this is

Credibility pack for Hermes-class / tool-agent runtimes:

1. **Measured Spark serve** (GB10 / CUDA 13 / llama.cpp Laguna fork)
2. **Fixed agent smoke suite** (tool JSON, multi-step, error repair, no invented tools)
3. **OpenAI-compatible sample client** oriented at Hermes-class agents
4. **Pointers + digests** to official weights — **not** a bare GGUF re-upload

DIY quants ship **only** if they beat official Poolside/Unsloth GGUF on measured Spark agent metrics. Otherwise we bind the official artifact and publish the Spark delta.

## License

Base model and derivatives under **OpenMDW-1.1** (Poolside).
Read the full text: [`LICENSE`](./LICENSE) and upstream
https://huggingface.co/poolside/Laguna-S-2.1/blob/main/LICENSE

You must retain notices, and if you ship Modified Materials with custom code under §3.3 you need a notice file. This pack's original scripts/eval are separate files with clear provenance notes.

## Base identity (pinned)

| Field | Value |
|-------|--------|
| Base | `poolside/Laguna-S-2.1` |
| Base revision (card freeze) | `00af5a51782109b587a3b3bbf11875e566036fa7` |
| Shape | 118B total · ~8B active/token · MoE |
| Official GGUF repo | `poolside/Laguna-S-2.1-GGUF` @ `fc4e481289523cf7d0df668da6d1d391616141ca` |
| Stand-behind quant (default) | **official** `laguna-s-2.1-Q4_K_M.gguf` (~68–96 GB on-disk LFS) |
| Optional denser | official `laguna-s-2.1-Q8_0.gguf` |
| Optional smaller third-party | Unsloth `UD-Q4_K_XL` (~40 GB) — third-party, not first-party claim |
| llama.cpp fork | `poolsideai/llama.cpp` branch `laguna` (DFlash + Laguna). Upstream PR trail: ggml-org/llama.cpp#25165 |

### Official GGUF sha256 (from HF LFS metadata)

| File | sha256 |
|------|--------|
| `laguna-s-2.1-Q4_K_M.gguf` | `a8b55c75714ea73fd90ec85de5defdc0b8d88ca0ad2108343cdd8fc22f7583e4` |
| `laguna-s-2.1-Q8_0.gguf` | `d946b221d69f2c5f87a986952bcd3cfb75831e5a6a2184e626e361663e1bfe2b` |
| `laguna-s-2.1-F16.gguf` | `2036c9dcf70f59738d480d1da2a2a59c0a3a3c5bd4ab8c43a61d77fba031e1f8` |
| `laguna-s-2.1-DFlash-BF16.gguf` | `2ee8aa30338d6599bc7a8ce008cc57c56f2c2b2fdc21f6db9ecda203c751bfd4` |
| `laguna-s-2.1.imatrix` | `4a4f480f57a3251e3acfb1d35ffba64720662536135e4ca4f4d05b0732539be2` |

Verify after download:

```bash
sha256sum -c SHA256SUMS
```

## Quant guide (what to pull)

| Goal | Artifact | Notes |
|------|----------|-------|
| Default agent serve on 128 GB unified (Spark) | Poolside **Q4_K_M** | Best official quality/size for agents; imatrix K-quant, signal path Q8_0 |
| Higher fidelity, more RAM | Poolside **Q8_0** | Routed experts Q8, signal BF16 |
| Disk-tight experiment | Unsloth **UD-Q4_K_XL** | Smaller; third-party dynamic quant — re-run `agent_smoke` yourself |
| Speculative decode | + Poolside **DFlash-BF16** | Needs poolside `laguna` fork (`--spec-type draft-dflash`) |

**Do not** claim “first quant”. FP8 / NVFP4 / INT4 / GGUF already exist upstream and community.

## One-evening stranger path (S1)

```bash
# 1) engine (poolside laguna fork)
git clone --branch laguna https://github.com/poolsideai/llama.cpp
cd llama.cpp
cmake -B build -G "Unix Makefiles" \
  -DCMAKE_BUILD_TYPE=Release \
  -DGGML_CUDA=ON \
  -DCMAKE_CUDA_ARCHITECTURES=121 \
  -DLLAMA_CURL=ON
cmake --build build -j --target llama-server llama-cli llama-bench

# 2) weights (official — do not re-host unless you have a measured delta)
huggingface-cli download poolside/Laguna-S-2.1-GGUF \
  laguna-s-2.1-Q4_K_M.gguf \
  --local-dir ~/models/laguna-s-2.1

# 3) serve OpenAI-compatible
./build/bin/llama-server \
  -m ~/models/laguna-s-2.1/laguna-s-2.1-Q4_K_M.gguf \
  --host 127.0.0.1 --port 8000 \
  --ctx-size 8192 -ngl 99 --jinja \
  -fa on

# 4) smoke
cd /path/to/this/pack
python eval/agent_smoke/run_smoke.py --base-url http://127.0.0.1:8000/v1 --model laguna-q4
```

Full Spark notes → [`SPARK.md`](./SPARK.md)  
Hermes-class client → [`hermes/`](./hermes/)  
Smoke suite → [`eval/agent_smoke/`](./eval/agent_smoke/)  
Measured run → [`results/MEASURED.md`](./results/MEASURED.md)

## Scoreboard (Spark · freeze before Aug 3)

| Host | Quant | Ctx | Gen tok/s | Smoke | RAM used | DFlash | Notes |
|------|-------|-----|-----------|-------|----------|--------|-------|
| DGX Spark GB10 | official Q4_K_M | 8192 | **~21.1** | **38/40 (95%)** | ~96–99 / 121 Gi | not measured | engine `04b2b72` + isfinite patch |

Snapshot JSONs: [`results/measured.json`](./results/measured.json) · [`results/server_bench.json`](./results/server_bench.json) · [`results/agent_smoke.json`](./results/agent_smoke.json)

### Measured detail (2026-07-28)

| Metric | Value |
|--------|--------|
| Quant | official `Q4_K_M` · sha256 `a8b55c75…` |
| Engine | poolside llama.cpp `04b2b72` + `math.h`/`::isfinite` host patch |
| Gen throughput | **~21 tok/s** @ 128 completion · ctx 8192 · `-ngl -1 -fa on` |
| Host mem after load | ~96–99 Gi used of 121 Gi |
| agent_smoke | **38/40 · 95%** (~97 s) |
| Named fails | `repair_04` HTTP500 bad tool-arg JSON · `long_06` runner KeyError |
| DFlash | not measured this run |

## What is **not** in this pack

- No Ainfera routing, no Neptune staged gates, no Fin weights
- No Verda/cloud CREATE for this workstream
- No fake benches — only fixed `agent_smoke` + `llama-bench` / server timings you can re-run
- No spam GGUF re-upload when the official file is the stand-behind artifact (S5)

## Reproducible method

See [`docs/REPRODUCE.md`](./docs/REPRODUCE.md) for exact clone SHAs, cmake flags (GB10/`121a`), download, measure, and smoke commands.

## Attribution

- Model: Poolside Laguna S 2.1 © Poolside, OpenMDW-1.1  
- GGUF: Poolside official conversions  
- Engine: poolsideai/llama.cpp `laguna` (+ upstream llama.cpp)  
- Pack, Spark measurements, agent_smoke, Hermes-oriented notes: personal work by **hizrianraz**

## Disclaimer

Independent personal measurements on one DGX Spark. Not affiliated with, endorsed by, or representing Poolside, Nous Research, Hermes Agent product claims, or Ainfera Inc. product lines. “Hermes-class” means OpenAI-compatible tool-calling agent runtime shape only — **not** a Nous endorsement.
