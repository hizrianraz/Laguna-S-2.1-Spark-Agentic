# Laguna-S-2.1 on DGX Spark — measured 2026-07-28

personal · not Ainfera · not Neptune

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
| gen8_short | 45 | 4 | 0.511 | 7.82 |
| gen128 | 61 | 128 | 6.057 | **21.13** |
| prefill_heavy (1.6k→3) | 1655 | 3 | 2.647 | (gen low; prefill)~ |
| script 2k filler | 836 | 3 | 1.826 | n/a (max_tokens=3 OK) |
| script 8k filler | 3236 | 3 | 4.731 | n/a (max_tokens=3 OK) |

Primary gen number to quote: **~21 tok/s** @ 128 completion tokens, short prompt, temp=0.

Note: `results/server_bench.json` is prefill-latency oriented (replies "OK"); not digests gen throughput.

## Agent smoke (40 cases)
- **38/40 pass · 95.0% · 96.7s**
- by category:
  - tool_json 8/8
  - multi_step 8/8
  - error_repair 5/6 (`repair_04` — server HTTP 500 parse tool-call args JSON)
  - no_invented_tools 6/6
  - short_code 6/6
  - long_horizon 5/6 (`long_06` — runner KeyError `'tool'` on response)

## Failures (not blocking first serve)
1. `repair_04` — engine rejected malformed tool-call JSON from model (`json.exception.parse_error`)
2. `long_06` — smoke runner assumption (KeyError `tool`); investigate case schema / message shape

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
