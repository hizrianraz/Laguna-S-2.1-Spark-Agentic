# SPARK.md — Laguna-S-2.1 on DGX Spark (GB10)

DGX Spark operator notes only.

Hardware target: **NVIDIA DGX Spark only** (GB10, Grace+Blackwell, ~128 GB unified).  
Do not run this pack’s claimed numbers on rented cloud hosts and relabel them as Spark.

## Engine pin (measured on this Spark)

| Item | Value |
|------|--------|
| Repo | `github.com/poolsideai/llama.cpp` branch `laguna` |
| Commit | `04b2b72cb54048ead292884adbe11f284e3ec950` |
| Host patch | `common/speculative.cpp`: exact `+#include <cmath>` only · patched source SHA-256 `3952ed9f…f48b9` |
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
LAGUNA_PACK_ROOT="$(pwd)"  # run from the deployment-pack root
export LAGUNA_ENGINE="$HOME/src/llama.cpp-laguna"
export PATH=/usr/local/cuda/bin:$PATH
export CUDA_HOME=/usr/local/cuda
export CC=/usr/bin/gcc CXX=/usr/bin/g++ CUDAHOSTCXX=/usr/bin/g++

git clone https://github.com/poolsideai/llama.cpp "$LAGUNA_ENGINE"
cd "$LAGUNA_ENGINE"
git checkout --detach 04b2b72cb54048ead292884adbe11f284e3ec950
# Apply the exact measured +<cmath>-only compatibility patch from
# docs/BUILD_SPARK.md before compiling. Other patch shapes are not accepted by
# the strict launch profile.
# pin when publishing numbers:
# git rev-parse HEAD

cmake -B build -G "Unix Makefiles" \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_C_COMPILER=/usr/bin/gcc \
  -DCMAKE_CXX_COMPILER=/usr/bin/g++ \
  -DCMAKE_CUDA_HOST_COMPILER=/usr/bin/g++ \
  -DGGML_CUDA=ON \
  -DCMAKE_CUDA_ARCHITECTURES=121a \
  -DLLAMA_CURL=ON

cmake --build build -j"$(nproc)" --target llama-server llama-cli llama-bench
cd "$LAGUNA_PACK_ROOT"
```

Notes:

- CMake rewrites `121` → `121a` on this toolkit.
- NCCL missing is OK on single Spark.
- No sudo required if toolchain already installed (CUDA toolkit + g++ + make + cmake).

## Weights

Default stand-behind file (official Poolside bytes at an immutable upstream revision):

```bash
# required launch path: immutable upstream pull + atomic SHA verification
for trusted_root in "$HOME/src" "$HOME/models" "$HOME/.local/state"; do
  [[ ! -L "$trusted_root" ]] || { echo "symlinked root: $trusted_root" >&2; exit 2; }
  install -d -m 700 -- "$trusted_root"
done

: "${LAGUNA_EXPECT_PACK_REVISION:?set the authorized 40-hex Hub commit}"
export LAGUNA_EXPECT_PACK_REVISION
export LAGUNA_EXPECT_LAUNCHER_SHA256="547ccf1f6f6cbae3fff15995ff4fecccbb876c3f6d5e015f6ab6a622ed9d4c2f"
printf '%s  %s\n' "$LAGUNA_EXPECT_LAUNCHER_SHA256" scripts/serve_spark.sh | sha256sum -c -
./scripts/pull_official_gguf.sh
```

Direct `hf download --local-dir` is not an equivalent launch path because it
bypasses the strict destination, lock, hardlink/symlink, and no-clobber gates.

Optional DFlash draft (upstream only today):

```bash
hf download poolside/Laguna-S-2.1-GGUF \
  laguna-s-2.1-DFlash-BF16.gguf \
  --revision fc4e481289523cf7d0df668da6d1d391616141ca \
  --local-dir $HOME/research/laguna-dflash
```

That research directory is never accepted by `serve_spark.sh` and cannot mint
launch authority.

Disk: Q4_K_M is exactly **96,031,829,760 bytes** (~96.0 GB / ~89.4 GiB);
keep ≥200 GB free when staging optional research artifacts and runtime headroom.

## Serve — OpenAI endpoint

```bash
for trusted_root in "$HOME/src" "$HOME/models" "$HOME/.local/state"; do
  [[ ! -L "$trusted_root" ]] || { echo "symlinked root: $trusted_root" >&2; exit 2; }
  install -d -m 700 -- "$trusted_root"
done

: "${LAGUNA_EXPECT_PACK_REVISION:?set the authorized 40-hex Hub commit}"
export LAGUNA_EXPECT_PACK_REVISION
export LAGUNA_EXPECT_LAUNCHER_SHA256="547ccf1f6f6cbae3fff15995ff4fecccbb876c3f6d5e015f6ab6a622ed9d4c2f"
printf '%s  %s\n' "$LAGUNA_EXPECT_LAUNCHER_SHA256" scripts/serve_spark.sh | sha256sum -c -

# Phase 1: hash only. Inspect/approve the binary before exporting its digest.
engine_pin_output="$(LAGUNA_PRINT_RUNTIME_PINS=1 ./scripts/serve_spark.sh)"
printf '%s\n' "$engine_pin_output"
export LAGUNA_EXPECT_ENGINE_SHA256="$(printf '%s\n' "$engine_pin_output" | awk -F= '$1=="LAGUNA_EXPECT_ENGINE_SHA256"{print $2}')"
[[ "$LAGUNA_EXPECT_ENGINE_SHA256" =~ ^[0-9a-f]{64}$ ]] || exit 2
unset engine_pin_output

# Phase 2: hash-gated ldd. Inspect the complete manifest before binding it.
dso_pin_output="$(LAGUNA_PRINT_RUNTIME_PINS=2 ./scripts/serve_spark.sh)"
printf '%s\n' "$dso_pin_output"
export LAGUNA_EXPECT_DSO_MANIFEST_SHA256="$(printf '%s\n' "$dso_pin_output" | awk -F= '$1=="LAGUNA_EXPECT_DSO_MANIFEST_SHA256"{print $2}')"
[[ "$LAGUNA_EXPECT_DSO_MANIFEST_SHA256" =~ ^[0-9a-f]{64}$ ]] || exit 2
unset dso_pin_output

export LAGUNA_API_KEY="$(openssl rand -hex 32)"
export OPENAI_API_KEY="$LAGUNA_API_KEY"
./scripts/serve_spark.sh
```

The launcher verifies the exact engine revision and measured `+<cmath>` patch,
the operator-pinned engine binary and resolved dynamic-library closure, Q4 bytes
and SHA-256, exact DGX Spark/GB10/arm64 identity, a host-wide launch lock,
absence of another model server, available memory for the model plus a 12 GiB
reserve, zero existing swap use, port availability, rejection of both absent
and wrong bearer tokens, positive-token protected readiness, and exact
`/v1/models` identity before declaring the server ready. The model and binary
are loaded through already-verified file descriptors. It writes a
mode-0600, no-clobber target-host launch receipt under `$HOME/.local/state/laguna/`
by default. The receipt binds the operator-declared immutable pack revision and
the independently pinned launcher digest. It is not self-clearing: compare both
values with the authorized Hub commit during independent review, then retain the
receipt. It does not refresh the historical smoke or clear the freeze alone.

Headline claims use **`-ngl -1`** (offload all / last-green pin). Older notes with `-ngl 99` are not the measured captain path.

The historical DFlash experiment is **DO_NOT_PROMOTE** and intentionally has no
runnable launch command here. Any future investigation must use a separate,
authenticated research launcher and a new receipt; it must not replace the
Q4 launch captain or reuse its claims.

Check:

```bash
curl --disable --noproxy '*' -s --config <(printf 'header = "Authorization: Bearer %s"\n' "$OPENAI_API_KEY") \
  http://127.0.0.1:8000/v1/models | head
curl --disable --noproxy '*' -s http://127.0.0.1:8000/v1/chat/completions \
  --config <(printf 'header = "Authorization: Bearer %s"\n' "$OPENAI_API_KEY") \
  -H 'Content-Type: application/json' \
  -d '{"model":"local-laguna","messages":[{"role":"user","content":"ping"}],"max_tokens":16}'
```

Point Hermes-class agents at:

```text
base_url = http://127.0.0.1:8000/v1
api_key  = $OPENAI_API_KEY   # same value as server-side LAGUNA_API_KEY
```

See `hermes/sample_client.py`.

### Context profiles

| Profile | status | use |
|---------|--------|-----|
| 8k (`--ctx-size 8192`) | **strict measured launcher** | the only context accepted by `serve_spark.sh` |
| 2k (`--ctx-size 2048`) | unmeasured research only | requires a separate launcher and new receipt |
| 256k (`--ctx-size 262144`) | unmeasured research only | requires capacity/quality validation, separate launcher, and new receipt |
| 1M (`--ctx-size 1048576 ...`) | upstream capability research only | no runnable preset or pack claim; requires separate capacity/quality work |

## Measure — tok/s + memory

### llama-bench (prompt+gen)

```bash
"$LAGUNA_ENGINE/build/bin/llama-bench" \
  -m $HOME/models/laguna-s-2.1/laguna-s-2.1-Q4_K_M.gguf \
  -ngl -1 -fa 1 \
  -p 2048,8192 -n 128 \
  -b 512
```

### Server wall-clock (agent-shaped)

```bash
/usr/bin/python3 -I -S scripts/bench_server.py \
  --base-url http://127.0.0.1:8000/v1 \
  --ctx-mark 2k --ctx-mark 8k
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
| ctx 8k, ngl -1, fa on | 836 prompt → 1.597 s; 3236 prompt → 4.78 s | **~21.47** @ 128 gen | ~2–3.4 Gi process RSS | unified mem; **sole headline gen = 21.47** (`results/measured.json`) |
| gen8 short | — | 10.612 | same | tiny completion noise floor — not a headline |
| ctx 8k + DFlash (`draft-dflash`) | 2k mark/836 actual: 2.253s · 8k mark/3,236 actual: 5.556s | **15.286** @ 128 gen | higher (draft+target) | trial `-ngl 99` vs baseline `-ngl -1` · **DO_NOT_PROMOTE** still (gen+prefill slower) · `results/dflash_2026-07-29/` |

Format/routing regression suites — **historical tip durations bind; tools are not executed**:

| Suite | quant | pass | n | notes |
|-------|-------|------|---|-------|
| agent_smoke v1 (historical receipt) | Q4_K_M | **40/40 · 100%** | 40 | **84.86 s** · temp 0.0 · format/routing only · `long_04 path=/` means path safety not proven · tip `bf82eab` |
| hermes_agent_smoke historical v2 | Q4_K_M | **27/27 · 100%** | 27 | **100.1 s** · catalog `3275a4a…a8ddfc` · one-response · locked `results/hermes_agent_smoke.json` |
| hermes_agent_smoke hardened v4 | — | **unmeasured** | 27 | current catalog `748f152e…0ad89`; suite-only future run, never release clearance |
| hermes Layer B historical v3 (research) | Q4_K_M | **35/35 · 100%** | 35 | **137.56 s** · catalog `829fd838…fa5e1` · **not freeze bar** |
| hermes Layer B current v3 diagnostic | — | **unmeasured** | 35 | catalog `0502e626…7d9ceb`; helper uses loopback port 8000 |
Raw: `results/MEASURED.md`, `results/measured.json`, `results/agent_smoke.json`, `results/hermes_agent_smoke.json`, `results/server_bench.json`.

## Agent-shaped benches

Not MMLU. Fixed suites under `eval/`:

**v1 historical receipt / v2 current future cases** (`eval/agent_smoke/`, 40 cases):

1. **tool JSON** — emit valid tool call objects only from the offered schema  
2. **multi-step** — 2–4 tool hops before final answer  
3. **error repair** — recover from tool error payloads  
4. **no invented tools** — refuse / answer without calling names not in schema  
5. **short code** — small pure functions, exact stdout  
6. **long-horizon-shaped prompts** — not proof of long-horizon reliability

**v4 hardened — Hermes-class** (`eval/hermes_agent_smoke/`, 27 cases, unmeasured):

Terminal / files / web / multi_tool / multi_turn / error_repair / no_invented / browser / memory_cron / args_strict / safety.  
OpenAI tool shape only — not a Nous endorsement.

```bash
/usr/bin/python3 -I -S eval/agent_smoke/run_smoke.py \
  --base-url http://127.0.0.1:8000/v1 \
  --model local-laguna

/usr/bin/python3 -I -S eval/hermes_agent_smoke/run_hermes_smoke.py \
  --base-url http://127.0.0.1:8000/v1 \
  --model local-laguna \
  --temperature 0
```

The dated `bf82eab` receipt files are historical authority and must not be
overwritten by a future run. Historical receipt path fields are labels, not
current file selectors: score identity is bound to the recorded catalog hash.
The v2 27/27 and historical Layer B 35/35 do not transfer to current v4/Layer B
bytes merely because filenames match.

Claim temperature **0.0**. Both suites are **one-response** (tools validated, not executed).

## vLLM (optional, unmeasured default)

Poolside card documents FP8 / NVFP4 Docker mirrors. This pack’s **default credibility path is GGUF + llama.cpp** because:

- matches official GGUF story  
- OpenAI-compatible with one binary  
- reproducible on Spark without container registry lag  

If you measure vLLM on Spark, add a dated subsection here with image digest + tok/s — do not overwrite GGUF numbers.

## Forbidden host confusion

- Do **not** attribute rented-cloud jobs to this file.  
- Do **not** mix non-local / third-party gateway base URLs into sample commands.  
- HF handle only for publish (`hizrianraz/*`).
