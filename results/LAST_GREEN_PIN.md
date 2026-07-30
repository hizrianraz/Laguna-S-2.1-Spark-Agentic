# Last green pin — Laguna-S-2.1-Spark-Agentic

**Pinned 2026-07-29** after DFlash DO_NOT_PROMOTE.

## Measured captain pin (not launch clearance)

| Field | Value |
|-------|-------|
| Quant | official `laguna-s-2.1-Q4_K_M.gguf` |
| sha256 | `a8b55c75714ea73fd90ec85de5defdc0b8d88ca0ad2108343cdd8fc22f7583e4` |
| Engine | poolsideai/llama.cpp laguna `04b2b72` |
| Gen128 | **~21.47 tok/s** |
| agent_smoke | **40/40 historical format/routing smoke** · 84.86s · temp 0.0 · path safety not proven |
| hermes v2 | **27/27 tools validated, not executed** · 100.1s · temp 0.0 |
| Measure tip (provenance) | `bf82eab` — not necessarily current docs tip |
| Serve | `-c 8192 -ngl -1 --parallel 1 --alias local-laguna --jinja -fa on` |
| Evidence | `results/MEASURED.md`, `results/measured.json` (`throughput` + `quote_gen_tok_s`), `results/launch_lock.json`, `results/server_bench.json` |

## Explicit rejects

| Path | Decision | Why |
|------|----------|-----|
| DFlash `draft-dflash` | **DO_NOT_PROMOTE** | gen128 **15.286** vs **21.47** (−28.8%); prefill worse · `results/dflash_2026-07-29/` |
| UD-IQ3_S | not headline | 38/40 on older runner · pointer only |

## Restore command (current secure wrapper)

```bash
export LAGUNA_ENGINE="$HOME/src/llama.cpp-laguna"
: "${LAGUNA_EXPECT_PACK_REVISION:?set the authorized 40-hex Hub commit}"
export LAGUNA_EXPECT_PACK_REVISION
export LAGUNA_EXPECT_LAUNCHER_SHA256="547ccf1f6f6cbae3fff15995ff4fecccbb876c3f6d5e015f6ab6a622ed9d4c2f"
printf '%s  %s\n' "$LAGUNA_EXPECT_LAUNCHER_SHA256" scripts/serve_spark.sh | sha256sum -c -
engine_pin_output="$(LAGUNA_PRINT_RUNTIME_PINS=1 ./scripts/serve_spark.sh)"
printf '%s\n' "$engine_pin_output" # inspect/approve before export
export LAGUNA_EXPECT_ENGINE_SHA256="$(printf '%s\n' "$engine_pin_output" | awk -F= '$1=="LAGUNA_EXPECT_ENGINE_SHA256"{print $2}')"
[[ "$LAGUNA_EXPECT_ENGINE_SHA256" =~ ^[0-9a-f]{64}$ ]] || exit 2
unset engine_pin_output
dso_pin_output="$(LAGUNA_PRINT_RUNTIME_PINS=2 ./scripts/serve_spark.sh)"
printf '%s\n' "$dso_pin_output" # inspect/approve complete manifest before export
export LAGUNA_EXPECT_DSO_MANIFEST_SHA256="$(printf '%s\n' "$dso_pin_output" | awk -F= '$1=="LAGUNA_EXPECT_DSO_MANIFEST_SHA256"{print $2}')"
[[ "$LAGUNA_EXPECT_DSO_MANIFEST_SHA256" =~ ^[0-9a-f]{64}$ ]] || exit 2
unset dso_pin_output
export LAGUNA_API_KEY="$(openssl rand -hex 32)"
export OPENAI_API_KEY="$LAGUNA_API_KEY"
./scripts/serve_spark.sh
```

The raw historical flags remain in the table for provenance; do not bypass the
authenticated launcher. Do not quote DFlash as speedup on this pack.
