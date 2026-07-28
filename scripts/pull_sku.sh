#!/usr/bin/env bash
# Pull a named Laguna GGUF SKU (official or third-party pointer tree).
# Does not rehost; writes into $LAGUNA_MODEL_DIR/<sku_id>/ and a sha256 list.
set -euo pipefail

SKU="${1:-}"
DEST_ROOT="${LAGUNA_MODEL_DIR:-$HOME/models/laguna-s-2.1}"
UA="${LAGUNA_UA:-hizrianraz-laguna-spark-pack}"

usage() {
  cat <<'EOF'
Usage: scripts/pull_sku.sh <sku_id>

SKU ids:
  official-q4km          poolside Q4_K_M (stand-behind)
  unsloth-ud-q4k-xl      Unsloth UD-Q4_K_XL (~73 GB, 3 shards)
  unsloth-ud-iq4-xs      Unsloth UD-IQ4_XS (~58 GB, 3 shards)
  unsloth-ud-iq3-s       Unsloth UD-IQ3_S (~48 GB, single)
  unsloth-ud-q2k-xl      Unsloth UD-Q2_K_XL (~40 GB, single)
  bartowski-iq4-xs       Bartowski IQ4_XS (~63 GB, 2 shards)

Env:
  LAGUNA_MODEL_DIR  default $HOME/models/laguna-s-2.1
  HF_TOKEN          optional for gated/rate limit
EOF
  exit 2
}

[[ -n "$SKU" ]] || usage

download() {
  local repo="$1" rev="$2" file="$3" outdir="$4"
  mkdir -p "$outdir"
  local url="https://huggingface.co/${repo}/resolve/${rev}/${file}"
  local out="${outdir}/$(basename "$file")"
  echo "pull $url"
  # Never echo token into logs.
  if [[ -n "${HF_TOKEN:-}" ]]; then
    curl -L --fail --retry 8 --retry-delay 15 -C - \
      -A "$UA" -H "Authorization: Bearer ${HF_TOKEN}" \
      -o "$out" "$url"
  else
    curl -L --fail --retry 8 --retry-delay 15 -C - \
      -A "$UA" -o "$out" "$url"
  fi
  (cd "$outdir" && sha256sum "$(basename "$file")" | tee -a SHA256SUMS.txt)
}

case "$SKU" in
  official-q4km)
    REV="${LAGUNA_GGUF_REV:-fc4e481289523cf7d0df668da6d1d391616141ca}"
    OUT="$DEST_ROOT/official-q4km"
    download poolside/Laguna-S-2.1-GGUF "$REV" laguna-s-2.1-Q4_K_M.gguf "$OUT"
    ;;
  unsloth-ud-q4k-xl)
    REV=main
    OUT="$DEST_ROOT/unsloth-ud-q4k-xl"
    for f in \
      UD-Q4_K_XL/Laguna-S-2.1-UD-Q4_K_XL-00001-of-00003.gguf \
      UD-Q4_K_XL/Laguna-S-2.1-UD-Q4_K_XL-00002-of-00003.gguf \
      UD-Q4_K_XL/Laguna-S-2.1-UD-Q4_K_XL-00003-of-00003.gguf
    do download unsloth/Laguna-S-2.1-GGUF "$REV" "$f" "$OUT"; done
    ;;
  unsloth-ud-iq4-xs)
    REV=main
    OUT="$DEST_ROOT/unsloth-ud-iq4-xs"
    for f in \
      UD-IQ4_XS/Laguna-S-2.1-UD-IQ4_XS-00001-of-00003.gguf \
      UD-IQ4_XS/Laguna-S-2.1-UD-IQ4_XS-00002-of-00003.gguf \
      UD-IQ4_XS/Laguna-S-2.1-UD-IQ4_XS-00003-of-00003.gguf
    do download unsloth/Laguna-S-2.1-GGUF "$REV" "$f" "$OUT"; done
    ;;
  unsloth-ud-iq3-s)
    REV=main
    OUT="$DEST_ROOT/unsloth-ud-iq3-s"
    download unsloth/Laguna-S-2.1-GGUF "$REV" Laguna-S-2.1-UD-IQ3_S.gguf "$OUT"
    ;;
  unsloth-ud-q2k-xl)
    REV=main
    OUT="$DEST_ROOT/unsloth-ud-q2k-xl"
    download unsloth/Laguna-S-2.1-GGUF "$REV" Laguna-S-2.1-UD-Q2_K_XL.gguf "$OUT"
    ;;
  bartowski-iq4-xs)
    REV=main
    OUT="$DEST_ROOT/bartowski-iq4-xs"
    # shard names verified via HF API probe — fail loudly if renamed
    mapfile -t FILES < <(python3 - <<'PY'
from huggingface_hub import HfApi
api=HfApi()
files=[s.rfilename for s in api.repo_info('bartowski/Laguna-S-2.1-GGUF', files_metadata=True).siblings
       if 'IQ4_XS' in s.rfilename and s.rfilename.endswith('.gguf')]
for f in sorted(files):
    print(f)
PY
)
    [[ ${#FILES[@]} -gt 0 ]] || { echo "no bartowski IQ4_XS files found"; exit 1; }
    for f in "${FILES[@]}"; do download bartowski/Laguna-S-2.1-GGUF "$REV" "$f" "$OUT"; done
    ;;
  *)
    echo "unknown sku: $SKU"
    usage
    ;;
esac

echo "done → $OUT"
echo "next: serve with poolside laguna llama-server; run eval/agent_smoke against that port"
echo "never relabel non-Spark hosts as Spark in results/"
