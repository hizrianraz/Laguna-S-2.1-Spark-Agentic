# Last green pin — Laguna-S-2.1-Spark-Agentic

**Pinned 2026-07-29** after DFlash DO_NOT_PROMOTE.

## Headline (ship this)

| Field | Value |
|-------|-------|
| Quant | official `laguna-s-2.1-Q4_K_M.gguf` |
| sha256 | `a8b55c75714ea73fd90ec85de5defdc0b8d88ca0ad2108343cdd8fc22f7583e4` |
| Engine | poolsideai/llama.cpp laguna `04b2b72` |
| Gen128 | **~21.47 tok/s** |
| agent_smoke | **40/40** · 84.86s · temp 0.0 |
| hermes v2 | **27/27** · 100.1s · temp 0.0 |
| Measure tip (provenance) | `bf82eab` — not necessarily current docs tip |
| Serve | `-c 8192 -ngl -1 --parallel 1 --alias local-laguna --jinja -fa on` |
| Evidence | `results/MEASURED.md`, `results/measured.json` (`throughput` + `quote_gen_tok_s`), `results/launch_lock.json`, `results/server_bench.json` |

## Explicit rejects

| Path | Decision | Why |
|------|----------|-----|
| DFlash `draft-dflash` | **DO_NOT_PROMOTE** | gen128 **15.286** vs **21.47** (−28.8%); prefill worse · `results/dflash_2026-07-29/` |
| UD-IQ3_S | not headline | 38/40 on older runner · pointer only |

## Restore command (baseline)

```bash
./build/bin/llama-server \
  -m ~/models/laguna-s-2.1/laguna-s-2.1-Q4_K_M.gguf \
  --host 127.0.0.1 --port 8000 \
  --ctx-size 8192 -ngl -1 -fa on --jinja \
  --alias local-laguna --metrics
```

Do not quote DFlash as speedup on this pack.
