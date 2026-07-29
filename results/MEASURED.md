# Laguna-S-2.1 on DGX Spark — measured 2026-07-29

personal Spark measurement note — accel multi-bench

## Stamp
- When: **2026-07-29 13:22:05 UTC+07:00**
- Host: `Hizrian-Razs-DGX-Spark`
- Pack git: `bf82eab` (bf82eab5fd6c1fb04e863f0c4b05b5658dec4aee)
- Headline quant: **Q4_K_M** (held)

## Weights / serve
- File: `laguna-s-2.1-Q4_K_M.gguf`
- sha256: `a8b55c75714ea73fd90ec85de5defdc0b8d88ca0ad2108343cdd8fc22f7583e4`
- Engine: poolsideai/llama.cpp `04b2b72` · CUDA Spark
- Serve: `0.0.0.0:8000` · `-c 8192 -ngl -1 --parallel 1 --alias local-laguna --jinja -fa on`

## Throughput (temp 0.0)
| mark | prompt_tok | completion_tok | latency_s | tok/s |
|------|------------|----------------|-----------|-------|
| gen8_short | 46 | 4 | 0.377 | **10.612** |
| gen128 | 67 | 128 | 5.962 | **21.47** |
| gen256 | 59 | 247 | 11.288 | **21.881** |

Primary gen number to quote: **~21.47 tok/s** @ 128 completion tokens (steady multi suite).

Prefill-oriented server_bench (OK replies):
- 2k: prompt=836 latency=1.597s content='OK'
- 8k: prompt=3236 latency=4.78s content='OK'

## Agent smoke (launch bar)
- **40/40** · elapsed **84.86s** · temp **0.0** · `local-laguna`
- Artifact: `results/agent_smoke.json`
- Runner sha256: `3bb81080879ddf78…`

## Hermes-class smoke v2
- **27/27** · elapsed **100.1s** · temp **0.0** · ship_min+stretch
- Artifact: `results/hermes_agent_smoke.json`
- Runner sha256: `20c1e52a8a22306b…`

## Locks held
- diy_gguf: false
- weight_host: Spark-only
- founder Mac: client-only
- public_promo_before_launch: false
- XS not in S freeze

## Headline
**40/40 agent_smoke · hermes 27/27 · ~21.47 t/s gen128 · Q4 live on Spark**

## DFlash (optional, same day)
- gen128 **15.286 t/s** · 2k 2.253s · 8k 5.556s
- **DO_NOT_PROMOTE** vs pinned Q4 baseline
- Evidence: `results/dflash_2026-07-29/` · pin: `results/LAST_GREEN_PIN.md`
