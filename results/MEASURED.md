# Laguna-S-2.1 on DGX Spark — measured 2026-07-29


## Claim boundaries (Sol reframe)

- hermes protocol: **tools validated, not executed** (see measured.json)
- agent_smoke / hermes scores = **format & routing regression smokes**, not long-horizon agent proof
- historical `long_04` chose `list_dir` but supplied `path=/`; the bf82eab receipt is preserved and **does not prove path safety**. Future cases reject that argument.
- engine evidence pins source commit `04b2b72`, embedded version, and the historical short receipt's exact `+<cmath>` patch. No measured binary SHA was retained. The strict launcher now accepts only that patch shape, requires an operator-pinned target binary digest, and writes a target-host launch receipt. Final clearance must retain that receipt; it does not retroactively add a binary digest to this historical measurement.
- server_bench marks labeled 2k/8k used prompts of **836** and **3236** tokens (not full 2k/8k packs)
- gen headline ~21.47 t/s is **128 completion** tokens on a **67-token** prompt (single short-gen point)


Independent Spark measurement note — multi-bench

## Stamp
- When: **2026-07-29 13:22:05 UTC+07:00**
- Host: NVIDIA DGX Spark (GB10)
- Pack git: `bf82eab` (bf82eab5fd6c1fb04e863f0c4b05b5658dec4aee)
- Headline quant: **Q4_K_M** (held)

## Weights / serve
- File: `laguna-s-2.1-Q4_K_M.gguf`
- sha256: `a8b55c75714ea73fd90ec85de5defdc0b8d88ca0ad2108343cdd8fc22f7583e4`
- Engine: poolsideai/llama.cpp `04b2b72` · CUDA Spark
- Serve: `0.0.0.0:8000` · `-c 8192 -ngl -1 --parallel 1 --alias local-laguna --jinja -fa on`
- That wildcard bind is retained as historical provenance, not a current run command. The hardened v2 launcher is loopback-only.

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

## Agent smoke (historical format/routing receipt)
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
- Mac full-S: client-only
- public_promo_before_launch: false
- XS not in S freeze

## Measured summary
**Q4 live on Spark · ~21.47 t/s gen128 · 40/40 format/routing smoke · hermes 27/27 validated-not-executed**

## DFlash (optional, same day)
- gen128 **15.286 t/s** · 2k 2.253s · 8k 5.556s
- **DO_NOT_PROMOTE** vs pinned Q4 baseline
- Evidence: `results/dflash_2026-07-29/` · pin: `results/LAST_GREEN_PIN.md`
