#!/usr/bin/env bash
# Pull official Poolside GGUF (not a DIY requant). Verify sha256 against pack SHA256SUMS — fail closed.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SUMS="${LAGUNA_SHA256SUMS:-${ROOT}/SHA256SUMS}"
REV="${LAGUNA_GGUF_REV:-fc4e481289523cf7d0df668da6d1d391616141ca}"
FILE="${1:-laguna-s-2.1-Q4_K_M.gguf}"
DEST="${LAGUNA_MODEL_DIR:-$HOME/models/laguna-s-2.1}"
REPO="poolside/Laguna-S-2.1-GGUF"
URL="https://huggingface.co/${REPO}/resolve/${REV}/${FILE}"

if [[ ! -f "${SUMS}" ]]; then
  echo "FAIL-CLOSED: missing pack SHA256SUMS at ${SUMS}" >&2
  exit 2
fi

# Pack format: GNU sha256sum 2-column (sha256  filename). Comments OK. awk accepts legacy 3-col too.
expected="$(
  awk -v f="${FILE}" '
    $0 ~ /^[[:space:]]*#/ { next }
    NF >= 2 && $NF == f { print $1; found=1; exit }
    END { if (!found) exit 1 }
  ' "${SUMS}"
)" || {
  echo "FAIL-CLOSED: ${FILE} not listed in ${SUMS}" >&2
  exit 2
}

if [[ ! "${expected}" =~ ^[0-9a-fA-F]{64}$ ]]; then
  echo "FAIL-CLOSED: bad expected hash for ${FILE}: ${expected}" >&2
  exit 2
fi

mkdir -p "${DEST}"
cd "${DEST}"
echo "pull ${URL}"
curl -L --fail --retry 8 --retry-delay 15 -C - \
  -A 'hizrianraz-laguna-spark-pack' \
  -o "${FILE}" \
  "${URL}"

got="$(sha256sum "${FILE}" | awk '{print $1}')"
echo "${got}  ${FILE}" | tee "sha256_${FILE}.txt"
echo "expected ${expected}"
echo "got      ${got}"

if [[ "${got}" != "${expected}" ]]; then
  echo "FAIL-CLOSED: sha256 mismatch for ${FILE}" >&2
  echo "  expected ${expected}" >&2
  echo "  got      ${got}" >&2
  echo "  leaving file in place for inspection; do not serve" >&2
  exit 3
fi

echo "OK sha256 match ${FILE}"
