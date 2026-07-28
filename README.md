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

# Laguna-S-2.1 · DGX Spark pack (personal)

**Launch target: 2026-08-03 (WIB)** — see [`LAUNCH_AUG3.md`](./LAUNCH_AUG3.md)

Personal DGX Spark agent-runtime pack for [poolside/Laguna-S-2.1](https://huggingface.co/poolside/Laguna-S-2.1) (118B-A8B MoE, agentic coding).

Solo personal HF surface by **hizrianraz**. Independent measurements on one DGX Spark. Not affiliated with Poolside or Nous Research.

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
| Default agent serve on Spark (~121G) | Poolside **Q4_K_M** | **Stand-behind** · measured agent_smoke 40/40 · ~21 t/s |
| **Founder MacBook / Mac Studio (≤32G) · full S** | **no local S weights** | **Laguna Mac = client** → Spark `http://<spark>:8000/v1` · S IQ3 ~48G alone > 32G RAM |
| **Founder Mac ≤32G · XS parallel (not S)** | Poolside **XS** `Laguna-XS-2.1-Q4_K_M.gguf` (~18.9G) | **Separate 33B-A3B model** · disk candidate · **0 Mac smoke** · not a quant of S · see [`research/laguna-xs-2.1-mac-fit-2026-07-28.md`](./research/laguna-xs-2.1-mac-fit-2026-07-28.md) + dual roadmap |
| Higher fidelity, more RAM (Spark) | Poolside **Q8_0** | Routed experts Q8, signal BF16 |
| Community 64–96G box (pointer, not founder Mac) | Unsloth **UD-IQ4_XS** (~58 GB) or Bartowski **IQ4_XS** (~63 GB) | Third-party; strangers re-run smoke; see device matrix |
| Community 48–64G tight (Spark-measured pointer) | Unsloth **UD-IQ3_S** (~48 GB) | Spark same-harness **38/40** · not headline · **not** a MacBook claim |
| Aggressive experiment | Unsloth **UD-Q2_K_XL** (~40 GB) | Research only until measured |
| Speculative decode | + Poolside **DFlash-BF16** | Needs poolside `laguna` fork (`--spec-type draft-dflash`) |
| iPhone / Android phone or tablet | **non-fit** for full Laguna-S | ~40GB+ even at IQ3; mobile NPU/RAM is 4–12G class — need SLM/distill, not this MoE |

Pull by SKU id:

```bash
./scripts/pull_sku.sh official-q4km
./scripts/pull_sku.sh unsloth-ud-iq4-xs   # ~58 GB third-party
./scripts/pull_sku.sh unsloth-ud-iq3-s    # ~48 GB third-party
```

Device ladder → [`research/device-quant-matrix-aug3.md`](./research/device-quant-matrix-aug3.md)

**Do not** claim “first quant”. FP8 / NVFP4 / INT4 / GGUF already exist upstream and community.
**Do not** print third-party numbers as “Spark measured” without same-harness JSON under `results/sku_*`.

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

# 4) smoke (launch bar)
cd /path/to/this/pack
python eval/agent_smoke/run_smoke.py --base-url http://127.0.0.1:8000/v1 --model laguna-q4

# 5) optional Hermes-class suite (v2; does not replace the 40-case bar)
python eval/hermes_agent_smoke/run_hermes_smoke.py \
  --base-url http://127.0.0.1:8000/v1 --model laguna-q4 \
  --out results/hermes_agent_smoke.json
```

Full Spark notes → [`SPARK.md`](./SPARK.md)  
Hermes-class client → [`hermes/`](./hermes/)  
Smoke suite (launch bar) → [`eval/agent_smoke/`](./eval/agent_smoke/)  
Hermes-class smoke v2 → [`eval/hermes_agent_smoke/`](./eval/hermes_agent_smoke/)  
Measured run → [`results/MEASURED.md`](./results/MEASURED.md)

## Scoreboard (Spark · freeze before Aug 3)

| Host | Quant | Ctx | Gen tok/s | Smoke | RAM used | DFlash | Notes |
|------|-------|-----|-----------|-------|----------|--------|-------|
| DGX Spark GB10 | official Q4_K_M | 8192 | **~21.1** | **40/40 (100%)** | ~96–99 / 121 Gi | not measured | **Headline** · engine `04b2b72` + isfinite · Hermes-class |
| DGX Spark GB10 | Unsloth UD-IQ3_S | 8192 | short-gen ~41 t/s (tiny) | **38/40 (95%)** | ~46 G weights | not measured | **Not headline** · same-harness SKU · ship ≥38 met · [`results/sku_unsloth-ud-iq3-s/`](./results/sku_unsloth-ud-iq3-s/) |

Snapshot JSONs: [`results/measured.json`](./results/measured.json) · [`results/server_bench.json`](./results/server_bench.json) · [`results/agent_smoke.json`](./results/agent_smoke.json) · [`results/hermes_agent_smoke.json`](./results/hermes_agent_smoke.json) · [`results/sku_unsloth-ud-iq3-s/`](./results/sku_unsloth-ud-iq3-s/)  
Hermes-class suite live: **27/27** on Q4 — [`eval/hermes_agent_smoke/`](./eval/hermes_agent_smoke/)

### Measured detail (2026-07-28)

| Metric | Value |
|--------|--------|
| Quant (headline) | official `Q4_K_M` · sha256 `a8b55c75…` |
| Engine | poolside llama.cpp `04b2b72` + `math.h`/`::isfinite` host patch |
| Gen throughput | **~21 tok/s** @ 128 completion · ctx 8192 · `-ngl -1 -fa on` |
| Host mem after load | ~96–99 Gi used of 121 Gi |
| agent_smoke | **40/40 · 100%** (97.25 s / reconfirm ~88.96 s, 2026-07-28) |
| hermes_agent_smoke v2 | **27/27 · 100%** (102.68 s, 2026-07-28) · `results/hermes_agent_smoke.json` |
| Closed fails | harness: `repair_04` sanitize prior tool-args; `long_06` `any_of_tools` judge (not weights) |
| DFlash | not measured this run |
| Multi-device SKU (IQ3_S) | Unsloth UD-IQ3_S · sha256 `8a9ab3f8…` · **38/40 · 71s** on Spark (Q4 briefly stopped; **restored**) · fails `repair_04`/`long_06` on *stale* Spark runner (no sanitize); not claimed as weight regression · phone/tablet **non-fit** |

## What is **not** in this pack

- No bare GGUF re-upload when the official file is the stand-behind artifact
- No affiliate / org / company product claims
- No fake benches — only fixed `agent_smoke` + `llama-bench` / server timings you can re-run
- No off-Spark (rented cloud) numbers relabeled as Spark

## Reproducible method

See [`docs/REPRODUCE.md`](./docs/REPRODUCE.md) for exact clone SHAs, cmake flags (GB10/`121a`), download, measure, and smoke commands.

## Attribution

- Model: Poolside Laguna S 2.1 © Poolside, OpenMDW-1.1  
- GGUF: Poolside official conversions  
- Engine: poolsideai/llama.cpp `laguna` (+ upstream llama.cpp)  
- Pack, Spark measurements, agent_smoke, Hermes-oriented notes: personal work by **hizrianraz**

## Disclaimer

Independent personal measurements on one DGX Spark. Not affiliated with, endorsed by, or representing Poolside or Nous Research. “Hermes-class” means OpenAI-compatible tool-calling agent runtime shape only — **not** a Nous endorsement.

## Quant comparison (same-family)

- Live scoreboard: [`research/quant-comparison-scoreboard-2026-07-28.md`](research/quant-comparison-scoreboard-2026-07-28.md)
- Stand-behind: official Poolside **Q4_K_M** (headline) — IQ3_S is a measured smaller **pointer row**, not a default swap.
- Mac mini / MacBook / PC: ladder in [`research/device-quant-matrix-aug3.md`](research/device-quant-matrix-aug3.md); IQ3_S ship-min met on Spark.
- iPhone / Android: **explicit non-fit** for full Laguna — distill/SLM only.
