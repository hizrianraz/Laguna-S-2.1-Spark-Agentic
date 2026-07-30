# Reproducible method — Laguna-S-2.1-Spark-Agentic pack

Personal reproducible method.

## Pins (card freeze)

| Item | Value |
|------|--------|
| Base model | `poolside/Laguna-S-2.1` |
| Base revision | `00af5a51782109b587a3b3bbf11875e566036fa7` |
| Official GGUF repo (upstream) | `poolside/Laguna-S-2.1-GGUF` |
| Optional byte-identical mirror | `hizrianraz/Laguna-S-2.1-GGUF` @ `510501dace2ff4e559644934a44c177ff8bd9f15` |
| GGUF revision (upstream pin) | `fc4e481289523cf7d0df668da6d1d391616141ca` |
| Default weight | `laguna-s-2.1-Q4_K_M.gguf` |
| Q4_K_M sha256 | `a8b55c75714ea73fd90ec85de5defdc0b8d88ca0ad2108343cdd8fc22f7583e4` |
| Engine | `github.com/poolsideai/llama.cpp` branch `laguna` |
| Hardware | DGX Spark GB10 only |

## Steps

1. Read OpenMDW-1.1 on the base model card/LICENSE. Accept constraints before redistribute.
   Before cloning or pulling, create the three audited roots:

```bash
for trusted_root in "$HOME/src" "$HOME/models" "$HOME/.local/state"; do
  [[ ! -L "$trusted_root" ]] || { echo "symlinked root: $trusted_root" >&2; exit 2; }
  install -d -m 700 -- "$trusted_root"
done
```

2. Build engine per `SPARK.md` (CUDA `121` → `121a`, `llama-server`).
3. Record `git rev-parse HEAD` of the engine tree into `results/engine_sha.txt`.
4. Download official GGUF (not a DIY re-quant unless you will measure a real delta):

```bash
# required launch helper (reads pack SHA256SUMS + pinned GGUF rev)
./scripts/pull_official_gguf.sh
```

Do not replace this with `hf download --local-dir` in a launch run: direct
download omits the strict filesystem, lock, and no-clobber publication gates.

Engine pin before build (measured commit, not floating branch tip):

```bash
git clone https://github.com/poolsideai/llama.cpp ~/src/llama.cpp-laguna
cd ~/src/llama.cpp-laguna
git checkout --detach 04b2b72cb54048ead292884adbe11f284e3ec950
# required measured +<cmath>-only host patch: docs/BUILD_SPARK.md
```

5. Serve with the fail-closed last-green launcher:

```bash
: "${LAGUNA_EXPECT_PACK_REVISION:?set the authorized 40-hex Hub commit}"
export LAGUNA_EXPECT_PACK_REVISION
export LAGUNA_EXPECT_LAUNCHER_SHA256="547ccf1f6f6cbae3fff15995ff4fecccbb876c3f6d5e015f6ab6a622ed9d4c2f"
printf '%s  %s\n' "$LAGUNA_EXPECT_LAUNCHER_SHA256" scripts/serve_spark.sh | sha256sum -c -
engine_pin_output="$(LAGUNA_PRINT_RUNTIME_PINS=1 ./scripts/serve_spark.sh)"
printf '%s\n' "$engine_pin_output" # inspect/approve the hash before export
export LAGUNA_EXPECT_ENGINE_SHA256="$(printf '%s\n' "$engine_pin_output" | awk -F= '$1=="LAGUNA_EXPECT_ENGINE_SHA256"{print $2}')"
[[ "$LAGUNA_EXPECT_ENGINE_SHA256" =~ ^[0-9a-f]{64}$ ]] || exit 2
unset engine_pin_output
dso_pin_output="$(LAGUNA_PRINT_RUNTIME_PINS=2 ./scripts/serve_spark.sh)"
printf '%s\n' "$dso_pin_output" # inspect/approve the full manifest before export
export LAGUNA_EXPECT_DSO_MANIFEST_SHA256="$(printf '%s\n' "$dso_pin_output" | awk -F= '$1=="LAGUNA_EXPECT_DSO_MANIFEST_SHA256"{print $2}')"
[[ "$LAGUNA_EXPECT_DSO_MANIFEST_SHA256" =~ ^[0-9a-f]{64}$ ]] || exit 2
unset dso_pin_output
export LAGUNA_API_KEY="$(openssl rand -hex 32)"
export OPENAI_API_KEY="$LAGUNA_API_KEY"
./scripts/serve_spark.sh
```

The launcher returns ready only after `/v1/models` reports exactly
`local-laguna`, both absent and incorrect bearer tokens are rejected, and an
authenticated one-token chat probe returns non-empty content with positive
token usage. `/v1/models` is called with authentication and is an identity/
health check, not the negative authentication proof.
Its v3 receipt is a source-bound review candidate, not clearance. Independently
compare `pack_source.declared_huggingface_revision` and
`pack_source.launcher_sha256` with the authorized Hub commit before accepting it.
Smoke / bench **`--model` must equal `--alias`** → `local-laguna`.

6. `llama-bench` @ prompt 2048 and 8192; save stdout to `results/llama_bench_q4km.txt`.
7. `/usr/bin/python3 -I -S scripts/bench_server.py --ctx-mark 2k --ctx-mark 8k` (the default is a new dated, no-clobber receipt).
8. `/usr/bin/python3 -I -S eval/agent_smoke/run_smoke.py --model local-laguna` (new dated receipt; historical authority cannot be overwritten).
8b. Optional Hermes-class: `/usr/bin/python3 -I -S eval/hermes_agent_smoke/run_hermes_smoke.py --model local-laguna` (same no-clobber rule).
9. Populate the tables in `SPARK.md` from those files only — never invent.
10. Publish pack (docs + results + scripts). **Host GGUF binary only if you have a measured unique artifact**; otherwise ship digests + download commands (S5).
11. Optional DFlash is **not** default. If tried on Spark, record with honesty — 2026-07-29 measure is **DO_NOT_PROMOTE** (`results/dflash_2026-07-29/`). Note: that trial used `-ngl 99` while baseline pin is `-ngl -1`; reject still holds (gen + prefill both slower).

## Personal HF publish surface

- User: `hizrianraz` (personal)
- Repo id: `hizrianraz/Laguna-S-2.1-Spark-Agentic`
- Card framing: personal measurements only; no org product claims

## DIY quant policy

Only if:

1. Official/Unsloth GGUF cannot load or is >10% worse on agent_smoke pass rate or tg tok/s at same ctx, **and**
2. You publish method + imatrix/source commit + full sha256 + smoke numbers

Otherwise: official GGUF + Spark delta docs only.
