# Local weights (gitignored)

Weights live under `models/` (and optionally `weights/`). Never commit `*.gguf`.

## Spark (stand-behind host)

```text
$HOME/models/laguna-s-2.1/laguna-s-2.1-Q4_K_M.gguf
```

| Field | Value |
|-------|--------|
| Immutable authority | [poolside/Laguna-S-2.1-GGUF](https://huggingface.co/poolside/Laguna-S-2.1-GGUF) @ `fc4e481289523cf7d0df668da6d1d391616141ca` |
| Optional mirror | [hizrianraz/Laguna-S-2.1-GGUF](https://huggingface.co/hizrianraz/Laguna-S-2.1-GGUF) @ `510501dace2ff4e559644934a44c177ff8bd9f15` (official Poolside bytes; explicit override only) |
| File | `laguna-s-2.1-Q4_K_M.gguf` |
| sha256 | `a8b55c75714ea73fd90ec85de5defdc0b8d88ca0ad2108343cdd8fc22f7583e4` |
| Size | 96,031,829,760 bytes (~96.0 GB / ~89.4 GiB) |
| Pull | `./scripts/pull_official_gguf.sh` |
| Serve | `./scripts/serve_spark.sh` (default `:8000`, loopback) |
| Pack authority | `SHA256SUMS` at pack root (`diy_gguf: false`) |

The audited launcher requires this to be a current-user-owned regular file with
one hard link. Symlinked model files or symlinked parent directories are rejected.

### Pull → serve contract (provenance bind)

1. `pull_official_gguf.sh` downloads the pinned upstream Q4 to a partial path, verifies exact bytes + **SHA-256**, then publishes it atomically.
2. On match: writes `PULL_COMPLETE_<file>` next to the weight (repo/rev/sha/bytes/expected).
3. Serve independently rechecks exact bytes + SHA; the marker is never trusted as identity evidence.
4. `serve_spark.sh` requires one-model residency: no other supported server, enough `MemAvailable` for the model plus **12 GiB**, and zero existing swap use.
5. It also requires the measured engine patch plus operator-pinned binary and
   dynamic-library-closure SHA-256 values, an authorized immutable pack revision
   and independently pinned launcher SHA-256, binds the model and binary by open
   descriptor, verifies DGX Spark/GB10/arm64 identity, reserves port 8000,
   requires a random API key, rejects absent and wrong bearer tokens, checks
   exact identity at `/v1/models`, and writes a no-clobber target receipt. The
   receipt is a candidate for independent source-match review, not self-clearance.
6. Peak non-swap ≤ **112 GiB** remains a soak/receipt axis — not asserted by the precheck alone.
7. The audited launcher is **loopback-only**. An external tunnel or TLS proxy is
   a separate deployment surface and requires its own review.
8. Smoke ≠ headline · evidence bind ≠ gate clearance · verifier ≠ gate clearance.

### Residency (SAQS)

| Axis | Value |
|------|--------|
| Free before warm (min) | Exact Q4 bytes + 12 GiB reserve |
| Peak non-swap (max) | 112 GiB (soak receipt) |
| Weight host | DGX Spark only |
| Mac ≤32 GB | client → Spark `:8000` only — **no** local S weights |

## Mac ≤32 GB class

Full S weights: **do not** land on ≤32 GB unified-memory Macs. Client → Spark `:8000` only.

## XS

Separate pack `Laguna-XS-2.1-Mac-Agentic/models/` — not this tree. S weights never stage/upload on Mac internal.
