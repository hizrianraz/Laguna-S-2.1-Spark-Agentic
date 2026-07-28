# Local weights (gitignored)

Weights live under `models/` (and optionally `weights/`). Never commit `*.gguf`.

## Spark (stand-behind host)

```text
models/laguna-s-2.1-Q4_K_M.gguf
```

Official: `poolside/Laguna-S-2.1-GGUF` · sha256 `a8b55c75714ea73fd90ec85de5defdc0b8d88ca0ad2108343cdd8fc22f7583e4` · ~89.4 GiB

Canonical serve path may stay `~/models/laguna-s-2.1/` with a symlink into this pack.

## Mac ≤32G

Full S weights: **do not** land on founder Mac. Client → Spark `:8000` only.

## XS

Separate pack `laguna-xs-2.1-mac/models/` — not this tree.
