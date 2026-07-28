#!/usr/bin/env bash
# Pull official Poolside GGUF (not a DIY requant). Verify sha256 against SHA256SUMS.
set -euo pipefail

REV="${LAGUNA_GGUF_REV:-fc4e481289523cf7d0df668da6d1d391616141ca}"
FILE="${1:-laguna-s-2.1-Q4_K_M.gguf}"
DEST="${LAGUNA_MODEL_DIR:-$HOME/models/laguna-s-2.1}"
REPO="poolside/Laguna-S-2.1-GGUF"
URL="https://huggingface.co/${REPO}/resolve/${REV}/${FILE}"

mkdir -p "${DEST}"
cd "${DEST}"
echo "pull ${URL}"
curl -L --fail --retry 8 --retry-delay 15 -C - \
  -A 'manwe-laguna-pack' \
  -o "${FILE}" \
  "${URL}"
sha256sum "${FILE}" | tee "sha256_${FILE}.txt"
echo "verify against pack SHA256SUMS (must match)"
