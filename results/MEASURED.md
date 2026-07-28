# Laguna-S-2.1 on DGX Spark — measured 2026-07-28

personal Spark measurement note

## Artifacts
- Model: poolside official `laguna-s-2.1-Q4_K_M.gguf` (90G)
- sha256: `a8b55c75714ea73fd90ec85de5defdc0b8d88ca0ad2108343cdd8fc22f7583e4` (LFS match)
- Engine: poolsideai/llama.cpp `04b2b72` laguna branch, CUDA build on Spark
- Host patch: `common/speculative.cpp` → `#include <math.h>` + `::isfinite` (GNU 13.3)
- Serve: `0.0.0.0:8000` · `-c 8192 -ngl -1 --parallel 1 --alias local-laguna --jinja -fa on`

## Memory (server loaded, post-smoke)
- Host RAM: 121 Gi total · ~96–99 Gi used · ~22–25 Gi available
- `llama-server` RSS: ~2.0–3.4 Gi (weights largely GPU/mapped; host free drops ~90G on load)
- Load-to-ready: ~6.5 min

## Throughput (chat completions, local)
| mark | prompt_tok | completion_tok | latency_s | tok/s |
|------|------------|----------------|-----------|-------|
| gen8_short | 49 | 4 | 0.47 | 8.51 |
| gen128 | 55 | 128 | 6.091 | **21.02** |
| prefill_heavy (1.6k→3) | 1655 | 3 | 2.647 | (gen low; prefill)~ |
| script 2k filler | 836 | 3 | 1.826 | n/a (max_tokens=3 OK) |
| script 8k filler | 3236 | 3 | 4.731 | n/a (max_tokens=3 OK) |

Primary gen number to quote: **~21 tok/s** @ 128 completion tokens, short prompt, temp=0.

Note: `results/server_bench.json` is prefill-latency oriented (replies "OK"); not digests gen throughput.

## Agent smoke (40 cases)
- **40/40 pass · 100% · 88.96s** (live reconfirm 2026-07-28 ~19:20 WIB; prior lock 97.25s)
- Prior baseline: 38/40 · 95% · 96.7s (same weights/engine; two harness bugs)
- by category:
  - tool_json 8/8
  - multi_step 8/8
  - error_repair 6/6
  - no_invented_tools 6/6
  - short_code 6/6
  - long_horizon 6/6

## Closed fails (harness, not weights)
1. `repair_04` — **case/engine, not model:** history held `{not-json` tool args; llama-server re-parsed priors and HTTP 500'd before decode. Fix: Hermes-class client `sanitize_messages_for_server` (valid JSON envelope + preserve `_raw`). Live after fix: **PASS** (~2.8s).
2. `long_06` — **runner schema, not model:** expect was `{type: tool_call, any_of_tools: [...]}` without `tool` → KeyError. Fix: judge accepts `tool_call` + `any_of_tools`. Live after fix: **PASS** (~2.6s).

Raw: `results/agent_smoke.json` (40/40).

## Hermes-class smoke v2 (live)

- Path: `eval/hermes_agent_smoke/` (27 cases, ship_min 24/27, stretch 27/27)
- Runner: `run_hermes_smoke.py` (reuses agent_smoke judges + sanitize)
- **Live 2026-07-28: 27/27 · 100% · 102.68 s** · model `local-laguna` · base Spark `:8000`
- Artifact: `results/hermes_agent_smoke.json`
- Branding: tool-agent family shape only; not Nous-endorsed
- Does **not** replace launch bar agent_smoke 40/40

## Serve recipe (proven)
```bash
export LD_LIBRARY_PATH=$HOME/src/llama.cpp-laguna/build/bin:$LD_LIBRARY_PATH
$HOME/src/llama.cpp-laguna/build/bin/llama-server \
  -m $HOME/models/laguna-s-2.1/laguna-s-2.1-Q4_K_M.gguf \
  --host 0.0.0.0 --port 8000 -c 8192 -ngl -1 \
  --parallel 1 --alias local-laguna --jinja -fa on
```

## Not done here
- Full `llama-bench` second-process while server holds GPU (OOM risk on 121G host)
- Competitive/agentic eval beyond smoke
- DFlash draft measure

## Published
- HF (docs only, no weight rehost): https://huggingface.co/hizrianraz/laguna-s-2.1-spark

## Quant comparison + multi-device (Aug 3 accelerated track)
- Scoreboard: [`research/quant-comparison-scoreboard-2026-07-28.md`](../research/quant-comparison-scoreboard-2026-07-28.md)
- Device matrix: [`research/device-quant-matrix-aug3.md`](../research/device-quant-matrix-aug3.md)
- Smaller-device path: [`research/post-freeze-smaller-device-path.md`](../research/post-freeze-smaller-device-path.md)
- Machine: [`results/quant_comparison.json`](./quant_comparison.json)
- Stand-behind remains official Q4_K_M on Spark.
- Pull helper: `scripts/pull_sku.sh`

### SKU same-harness: Unsloth UD-IQ3_S (not headline)

| Field | Value |
|-------|-------|
| File | `unsloth/Laguna-S-2.1-GGUF` · `Laguna-S-2.1-UD-IQ3_S.gguf` |
| sha256 | `8a9ab3f8b3ff1723441cd251e873b295a7ef086d78dbae7515e5e27c8382b002` |
| bytes | 48428911520 (~45.1 Gi) |
| Host / engine | Spark · same poolside laguna `04b2b72` |
| Serve window | Q4 stopped briefly; IQ3 on `:8000` alias `local-laguna-iq3s`; **Q4 restored** after |
| agent_smoke | **38/40 · 95% · 71.0 s** (2026-07-28 20:10 WIB) |
| fails | `repair_04`, `long_06` |
| Harness caveat | Spark pack `run_smoke.py` md5 `c1a587c8…` lacked `sanitize_messages_for_server` + `any_of_tools` judge (local fixed md5 `4b2fe7af…`). Same two fails were **harness-closed on Q4** earlier. IQ3 still meets ship gate ≥38/40 end-to-end on the runner that ran. |
| Promotion | ship-min **met** · pointer + delta only · **not** default quant |
| Phone / tablet | **full Laguna non-fit** (iPhone + Android) — need SLM/distill |

Raw: [`results/sku_unsloth-ud-iq3-s/`](./sku_unsloth-ud-iq3-s/)
