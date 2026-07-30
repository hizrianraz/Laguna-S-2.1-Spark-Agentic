#!/usr/bin/env bash
# Pull official Poolside GGUF (not a DIY requant). Verify sha256 against pack SHA256SUMS — fail closed.
# DAY-0 AUTHORITY: Q4_K_M only · sha in SHA256SUMS · diy_gguf=false · NVFP4/DFlash not day-0 serve path
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SUMS="${LAGUNA_SHA256SUMS:-${ROOT}/SHA256SUMS}"
# Preferred mirror = our GGUF host (official Poolside bytes). Override to force upstream.
REPO="${LAGUNA_GGUF_REPO:-hizrianraz/Laguna-S-2.1-GGUF}"
# Revision: main on our mirror; pin upstream with LAGUNA_GGUF_REV when REPO=poolside/...
REV="${LAGUNA_GGUF_REV:-main}"
FILE="${1:-laguna-s-2.1-Q4_K_M.gguf}"
DEST="${LAGUNA_MODEL_DIR:-$HOME/models/laguna-s-2.1}"
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

# provenance receipt + downloader marker (serve does not require it yet — sha is laws)
bytes="$(wc -c < "${FILE}" | tr -d ' ')"
marker="PULL_COMPLETE_${FILE}"
{
  echo "file=${FILE}"
  echo "repo=${REPO}"
  echo "rev=${REV}"
  echo "sha256=${got}"
  echo "bytes=${bytes}"
  echo "expected_sha256=${expected}"
  echo "status=pull_complete"
  echo "diy_gguf=false"
  echo "written_at=$(date -Iseconds 2>/dev/null || date)"
} | tee "${marker}"
echo "OK sha256 match ${FILE} · marker=${marker}"
