# SPARK.md — Laguna-S-2.1 on DGX Spark (GB10)

personal · not Ainfera · not Neptune · not Fin · not Gate0

Hardware target: **NVIDIA DGX Spark only** (GB10, Grace+Blackwell, ~128 GB unified).  
Do not run this pack’s claimed numbers on Verda or rented cloud and relabel them.

## Engine pin (measured on this Spark)

| Item | Value |
|------|--------|
| Repo | `github.com/poolsideai/llama.cpp` branch `laguna` |
| Commit | `04b2b72cb54048ead292884adbe11f284e3ec950` |
| Host patch | `common/speculative.cpp`: `math.h` + `::isfinite` (GNU 13.3) |
| CUDA arch | `121a` (GB10) |
| Bin version string | `version: 1 (04b2b72)` |


## Stack

| Layer | Choice |
|-------|--------|
| GPU | NVIDIA GB10 (CUDA sm_121 / cmake maps to `121a`) |
| Driver / toolkit observed | CUDA 13.0, nvcc 13.0.88 |
| Engine (required for Laguna GGUF + DFlash) | [poolsideai/llama.cpp](https://github.com/poolsideai/llama.cpp) branch **`laguna`** |
| Optional engine | upstream llama.cpp **≥ b10087** (Laguna support landed on trail of #25165) — prefer poolside fork for DFlash |
| API | `llama-server` OpenAI-compatible (`/v1/chat/completions`, `/v1/completions`, `/v1/models`) |
| Optional | vLLM FP8/NVFP4 paths from Poolside card — **not** default for this pack; GGUF+llama.cpp is the measured path |

## Build (CUDA, aarch64)

```bash
export PATH=/usr/local/cuda/bin:$PATH
export CUDA_HOME=/usr/local/cuda
export CC=/usr/bin/gcc CXX=/usr/bin/g++ CUDAHOSTCXX=/usr/bin/g++

git clone --branch laguna https://github.com/poolsideai/llama.cpp llama.cpp-laguna
cd llama.cpp-laguna
# pin when publishing numbers:
# git rev-parse HEAD

cmake -B build -G "Unix Makefiles" \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_C_COMPILER=/usr/bin/gcc \
  -DCMAKE_CXX_COMPILER=/usr/bin/g++ \
  -DCMAKE_CUDA_HOST_COMPILER=/usr/bin/g++ \
  -DGGML_CUDA=ON \
  -DCMAKE_CUDA_ARCHITECTURES=121 \
  -DLLAMA_CURL=ON

cmake --build build -j"$(nproc)" --target llama-server llama-cli llama-bench
```

Notes:

- CMake rewrites `121` → `121a` on this toolkit.
- NCCL missing is OK on single Spark.
- No sudo required if toolchain already installed (CUDA toolkit + g++ + make + cmake).

## Weights

Default stand-behind file (official, not re-uploaded unless delta exists):

```bash
huggingface-cli download poolside/Laguna-S-2.1-GGUF \
  laguna-s-2.1-Q4_K_M.gguf \
  --local-dir $HOME/models/laguna-s-2.1

sha256sum $HOME/models/laguna-s-2.1/laguna-s-2.1-Q4_K_M.gguf
# expect a8b55c75714ea73fd90ec85de5defdc0b8d88ca0ad2108343cdd8fc22f7583e4
```

Optional DFlash draft:

```bash
huggingface-cli download poolside/Laguna-S-2.1-GGUF \
  laguna-s-2.1-DFlash-BF16.gguf \
  --local-dir $HOME/models/laguna-s-2.1
```

Disk: Q4_K_M ≈ 90–96 GB logical (HF race); keep ≥200 GB free for download + KV headroom.

## Serve — OpenAI endpoint

```bash
./build/bin/llama-server \
  -m $HOME/models/laguna-s-2.1/laguna-s-2.1-Q4_K_M.gguf \
  --host 127.0.0.1 --port 8000 \
  --ctx-size 8192 \
  -ngl 99 \
  -fa on \
  --jinja \
  --metrics
```

With DFlash (poolside fork):

```bash
./build/bin/llama-server \
  -m $HOME/models/laguna-s-2.1/laguna-s-2.1-Q4_K_M.gguf \
  -md $HOME/models/laguna-s-2.1/laguna-s-2.1-DFlash-BF16.gguf \
  --spec-type draft-dflash --spec-draft-n-max 7 \
  --host 127.0.0.1 --port 8000 \
  --ctx-size 8192 -ngl 99 -fa on --jinja
```

Check:

```bash
curl -s http://127.0.0.1:8000/v1/models | head
curl -s http://127.0.0.1:8000/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"laguna","messages":[{"role":"user","content":"ping"}],"max_tokens":16}'
```

Point Hermes-class agents at:

```text
base_url = http://127.0.0.1:8000/v1
api_key  = sk-local   # unused by llama-server; placeholder
```

See `hermes/sample_client.py`.

### Context presets

| Preset | flags | use |
|--------|-------|-----|
| 2k smoke | `--ctx-size 2048` | quick agent_smoke / latency |
| 8k default agent | `--ctx-size 8192` | multi-step tools |
| 256k card default | `--ctx-size 262144` | long horizon (needs RAM headroom) |
| 1M native | `--ctx-size 1048576 --rope-scaling yarn --rope-scale 128 --yarn-orig-ctx 8192` | quality may drop; temp 0.7 top_p 0.95 |

## Measure — tok/s + memory

### llama-bench (prompt+gen)

```bash
./build/bin/llama-bench \
  -m $HOME/models/laguna-s-2.1/laguna-s-2.1-Q4_K_M.gguf \
  -ngl 99 -fa 1 \
  -p 2048,8192 -n 128 \
  -b 512
```

### Server wall-clock (agent-shaped)

```bash
python scripts/bench_server.py \
  --base-url http://127.0.0.1:8000/v1 \
  --ctx-mark 2k --ctx-mark 8k \
  --out results/server_bench.json
```

### Memory

While server is up:

```bash
# unified memory pressure (Spark)
free -h
nvidia-smi  # GB10 fields may show N/A for FB; use free/rss
ps -o pid,rss,cmd -p $(pgrep -f llama-server)
```

Record **RSS** of `llama-server`, host free mem before/after load, and ctx size.

## Measured results (2026-07-28 Spark)

Host: DGX Spark · GB10 · CUDA 13.0 · engine `04b2b72` · weight Q4_K_M @ `a8b55c75…`  
Serve proven: `-c 8192 -ngl -1 --parallel 1 --alias local-laguna --jinja -fa on` · load ~6.5 min · host ~96–99 Gi used after load (121 Gi total)

| Setting | prefill latency | tg tok/s | server RSS | notes |
|---------|-----------------|----------|------------|-------|
| ctx 8k, ngl -1, fa on | 836 prompt → 1.83 s; 3236 prompt → 4.73 s | **~21.1** @ 128 gen | ~2–3.4 Gi process RSS | unified mem holds weights; quote **21 tok/s** gen |
| gen8 short | — | ~7.8 | same | tiny completion noise floor |
| ctx 8k + DFlash | unmeasured | — | — | optional next |

Agent-shaped (tool round-trips, see smoke):

| Suite | quant | pass | n | notes |
|-------|-------|------|---|-------|
| agent_smoke v1 | Q4_K_M | **38/40 · 95%** | 40 | fails: `repair_04` tool-arg JSON HTTP500; `long_06` runner KeyError |

Raw: `results/MEASURED.md`, `results/measured.json`, `results/agent_smoke.json`, `results/server_bench.json`.

## Agent-shaped benches

Not MMLU. Fixed suite under `eval/agent_smoke/`:

1. **tool JSON** — emit valid tool call objects only from the offered schema  
2. **multi-step** — 2–4 tool hops before final answer  
3. **error repair** — recover from tool error payloads  
4. **no invented tools** — refuse / answer without calling names not in schema  
5. **short code** — small pure functions, exact stdout  
6. **long-horizon** — sticky constraints across turns  

```bash
python eval/agent_smoke/run_smoke.py \
  --base-url http://127.0.0.1:8000/v1 \
  --model local-laguna \
  --out results/smoke_q4km.json
```

## vLLM (optional, unmeasured default)

Poolside card documents FP8 / NVFP4 Docker mirrors. This pack’s **default credibility path is GGUF + llama.cpp** because:

- matches official GGUF story  
- OpenAI-compatible with one binary  
- reproducible on Spark without container registry lag  

If you measure vLLM on Spark, add a dated subsection here with image digest + tok/s — do not overwrite GGUF numbers.

## Forbidden host confusion

- Do **not** attribute Verda/cloud jobs to this file.  
- Do **not** mix Ainfera gateway base URLs into sample commands.  
- Personal HF only for publish.
