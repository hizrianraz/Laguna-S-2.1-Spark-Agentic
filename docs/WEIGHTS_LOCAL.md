# Local weights (gitignored)

Weights live under `models/` (and optionally `weights/`). Never commit `*.gguf`.

## Spark (stand-behind host)

```text
models/laguna-s-2.1-Q4_K_M.gguf
# or symlink tree:
# $HOME/models/laguna-s-2.1/laguna-s-2.1-Q4_K_M.gguf
```

| Field | Value |
|-------|--------|
| Preferred mirror | [hizrianraz/Laguna-S-2.1-GGUF](https://huggingface.co/hizrianraz/Laguna-S-2.1-GGUF) (official Poolside bytes) |
| Upstream | [poolside/Laguna-S-2.1-GGUF](https://huggingface.co/poolside/Laguna-S-2.1-GGUF) |
| File | `laguna-s-2.1-Q4_K_M.gguf` |
| sha256 | `a8b55c75714ea73fd90ec85de5defdc0b8d88ca0ad2108343cdd8fc22f7583e4` |
| Size | ~89.4 GiB |
| Pull | `./scripts/pull_official_gguf.sh` |
| Serve | `./scripts/serve_spark.sh` (default `:8000`, loopback) |
| Pack authority | `SHA256SUMS` at pack root (`diy_gguf: false`) |

Canonical serve path may stay `$HOME/models/laguna-s-2.1/` with a symlink into this pack.

### Pull → serve contract (provenance bind)

1. `pull_official_gguf.sh` downloads one GGUF, verifies **sha256 against pack `SHA256SUMS`** (fail-closed on miss/mismatch).
2. On match: writes `PULL_COMPLETE_<file>` next to the weight (repo/rev/sha/bytes/expected).
3. Serve does **not** require the marker yet — **sha match is law**. Marker is provenance receipt for ops.
4. `serve_spark.sh` residency min (SAQS): refuses warm if free ≈ < **12 GiB** unless `SKIP_RESIDENCY_CHECK=1`.
5. Peak non-swap ≤ **112 GiB** is a soak/receipt axis — not asserted by the precheck alone.
6. Host default **loopback**; `EXPOSE_LAN=1` required for non-loopback.
7. Smoke ≠ headline · evidence bind ≠ gate clearance · verifier ≠ gate clearance.

### Residency (SAQS)

| Axis | Value |
|------|--------|
| Free before warm (min) | 12 GiB (`LAGUNA_MIN_FREE_GIB`) |
| Peak non-swap (max) | 112 GiB (soak receipt) |
| Weight host | DGX Spark only |
| Mac ≤32 GB | client → Spark `:8000` only — **no** local S weights |

## Mac ≤32 GB class

Full S weights: **do not** land on ≤32 GB unified-memory Macs. Client → Spark `:8000` only.

## XS

Separate pack `Laguna-XS-2.1-Mac-Agentic/models/` — not this tree. S weights never stage/upload on Mac internal.
