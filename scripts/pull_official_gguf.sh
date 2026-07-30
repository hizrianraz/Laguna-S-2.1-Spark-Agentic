#!/bin/bash -p
{ builtin set +x; } 2>/dev/null
# Pull the immutable official Poolside Q4_K_M artifact (not a DIY requant).
# The launch path accepts only the compiled filename/digest/size. A mirror may
# change repository+revision only; the resulting bytes must remain identical.
if [[ "$-" != *p* || "${BASH_SOURCE[0]}" != "$0" ]]; then
  /usr/bin/printf '%s\n' 'FAIL-CLOSED: execute this file directly; sourcing/plain bash is unsupported' >&2
  exit 126
fi
builtin unset POSIXLY_CORRECT POSIX_PEDANTIC BASH_COMPAT GLOBIGNORE
builtin set +o posix
builtin set -euo pipefail
IFS=$' \t\n'
PS4='+ '
builtin umask 077
builtin ulimit -c 0
if (( EUID == 0 || EUID != UID )); then
  /usr/bin/printf '%s\n' 'FAIL-CLOSED: pull as one unprivileged user with matching real/effective IDs' >&2
  exit 126
fi

readonly CLEAN_PATH="/usr/local/cuda/bin:/usr/bin:/bin"
builtin export PATH="${CLEAN_PATH}"
builtin unset LD_PRELOAD LD_AUDIT LD_LIBRARY_PATH CDPATH ENV BASH_ENV TMPDIR TMP TEMP \
  PYTHONPATH PYTHONHOME PYTHONSTARTUP PYTHONINSPECT PYTHONWARNINGS PYTHONUSERBASE
for inherited_function in awk basename cat cd chmod command curl date df dirname echo env export find grep mkdir mktemp printf pwd python3 readonly rm rmdir set sha256sum shasum stat tr unset wc; do
  builtin unset -f "${inherited_function}" 2>/dev/null || true
done
ROOT="$(builtin cd "$(/usr/bin/dirname "${BASH_SOURCE[0]}")/.." && builtin pwd -P)"
readonly OFFICIAL_REPO="poolside/Laguna-S-2.1-GGUF"
readonly OFFICIAL_REV="fc4e481289523cf7d0df668da6d1d391616141ca"
readonly OFFICIAL_FILE="laguna-s-2.1-Q4_K_M.gguf"
readonly OFFICIAL_SHA256="a8b55c75714ea73fd90ec85de5defdc0b8d88ca0ad2108343cdd8fc22f7583e4"
readonly OFFICIAL_BYTES=96031829760
readonly HEADROOM_BYTES=$((5 * 1024 * 1024 * 1024))

SUMS="${ROOT}/SHA256SUMS"
REPO="${LAGUNA_GGUF_REPO:-${OFFICIAL_REPO}}"
REV="${LAGUNA_GGUF_REV:-${OFFICIAL_REV}}"
FILE="${1:-${OFFICIAL_FILE}}"
DEST="${LAGUNA_MODEL_DIR:-$HOME/models/laguna-s-2.1}"
while [[ "${DEST}" != "/" && "${DEST}" == */ ]]; do
  DEST="${DEST%/}"
done
URL="https://huggingface.co/${REPO}/resolve/${REV}/${OFFICIAL_FILE}"

die() {
  echo "FAIL-CLOSED: $*" >&2
  exit 2
}

hash_file() {
  local candidate="$1"
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "${candidate}" | awk '{print $1}'
  elif command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "${candidate}" | awk '{print $1}'
  else
    die "no sha256sum/shasum available"
  fi
}

link_count() {
  if stat -c '%h' -- "$1" >/dev/null 2>&1; then
    stat -c '%h' -- "$1"
  else
    stat -f '%l' -- "$1"
  fi
}

stat_owner() {
  if stat -c '%u' -- "$1" >/dev/null 2>&1; then
    stat -c '%u' -- "$1"
  else
    stat -f '%u' -- "$1"
  fi
}

stat_mode() {
  if stat -c '%a' -- "$1" >/dev/null 2>&1; then
    stat -c '%a' -- "$1"
  else
    stat -f '%Lp' -- "$1"
  fi
}

validate_components_no_symlink() {
  local path="$1" component
  component="${path}"
  while [[ "${component}" != "/" && "${component}" != "." ]]; do
    [[ ! -L "${component}" ]] || die "path contains a symlink component: ${component}"
    component="$(dirname "${component}")"
  done
}

validate_trusted_directory_chain() {
  local path="$1" label="$2" component owner mode
  validate_components_no_symlink "${path}"
  component="${path}"
  while :; do
    [[ -d "${component}" && ! -L "${component}" ]] || die "${label} must preexist as a directory: ${component}"
    owner="$(stat_owner "${component}")" || die "cannot read owner for ${label}: ${component}"
    [[ "${owner}" == "0" || "${owner}" == "${EUID}" ]] || die \
      "${label} chain must be owned by root or the current user: ${component}"
    mode="$(stat_mode "${component}")" || die "cannot read mode for ${label}: ${component}"
    [[ "${mode}" =~ ^[0-7]{3,4}$ ]] || die "invalid mode for ${label}: ${component}"
    (( (8#${mode} & 0022) == 0 )) || die "${label} chain must not be group/world writable: ${component}"
    [[ "${component}" == "/" ]] && break
    component="$(dirname "${component}")"
  done
}

validate_leaf() {
  local path="$1" role="$2" links mode
  [[ -e "${path}" || -L "${path}" ]] || return 0
  [[ ! -L "${path}" ]] || die "${role} must not be a symlink: ${path}"
  [[ -f "${path}" ]] || die "${role} must be a regular file: ${path}"
  [[ -O "${path}" ]] || die "${role} must be owned by the current user: ${path}"
  links="$(link_count "${path}")"
  [[ "${links}" == "1" ]] || die "${role} must have exactly one hard link: ${path}"
  mode="$(stat_mode "${path}")" || die "cannot read mode for ${role}: ${path}"
  [[ "${mode}" =~ ^[0-7]{3,4}$ ]] || die "invalid mode for ${role}: ${path}"
  (( (8#${mode} & 0022) == 0 )) || die "${role} must not be group/world writable: ${path}"
}

validate_destination() {
  local nested entry name
  [[ -n "${DEST}" && "${DEST}" == /* ]] || die "LAGUNA_MODEL_DIR must be a non-empty absolute path"
  [[ "${DEST}" == "${ALLOWED_MODEL_ROOT}/laguna-s-2.1" ]] || die \
    "destination must equal <LAGUNA_ALLOWED_MODEL_ROOT>/laguna-s-2.1: ${DEST}"
  [[ "$(basename "${DEST}")" == "laguna-s-2.1" ]] || \
    die "destination basename must be exactly laguna-s-2.1: ${DEST}"
  case "${DEST}" in
    /|/home|/Users|/tmp|/tmp/*|/private/tmp|/private/tmp/*|/var|/usr|"${HOME}"|"${ROOT}"|"${ROOT}"/*)
      die "refusing broad, temporary-root, or in-pack destination: ${DEST}"
      ;;
  esac
  validate_components_no_symlink "${DEST}"
  if [[ -e "${DEST}" && ! -d "${DEST}" ]]; then
    die "destination exists but is not a directory: ${DEST}"
  fi
  [[ -d "${DEST}" ]] || return 0
  [[ -O "${DEST}" ]] || die "destination directory must be owned by the current user: ${DEST}"
  validate_trusted_directory_chain "${DEST}" "model destination"
  nested="$(find "${DEST}" -mindepth 1 -type l -print -quit)"
  [[ -z "${nested}" ]] || die "symlink is forbidden anywhere in the model destination: ${nested}"
  while IFS= read -r -d '' entry; do
    name="$(basename "${entry}")"
    case "${name}" in
      "${OFFICIAL_FILE}"|".${OFFICIAL_FILE}.part"|"PULL_COMPLETE_${OFFICIAL_FILE}"|"sha256_${OFFICIAL_FILE}.txt")
        validate_leaf "${entry}" "model-directory file"
        ;;
      ".${OFFICIAL_FILE}.pull.lock.d")
        [[ -d "${entry}" && ! -L "${entry}" ]] || die "invalid pull lock object: ${entry}"
        ;;
      *)
        die "unexpected object in strict launch model directory: ${entry}"
        ;;
    esac
  done < <(find "${DEST}" -mindepth 1 -maxdepth 1 -print0)
}

publish_no_clobber() {
  local source="$1" destination="$2"
  /usr/bin/env -i PATH="${CLEAN_PATH}" HOME="${HOME}" LC_ALL=C /usr/bin/python3 -I -S - "${source}" "${destination}" <<'PY'
import os
import sys

source, destination = sys.argv[1:]
try:
    os.link(source, destination, follow_symlinks=False)
except FileExistsError:
    raise SystemExit("destination appeared before atomic publication")
os.unlink(source)
PY
}

for command_name in awk basename cat chmod curl date df dirname env find grep mkdir mktemp pwd rm rmdir stat tr wc; do
  command -v "${command_name}" >/dev/null 2>&1 || die "missing required command: ${command_name}"
done
[[ -x /usr/bin/python3 ]] || die "missing trusted Python interpreter: /usr/bin/python3"

lexical_abs() {
  /usr/bin/env -i PATH="${CLEAN_PATH}" HOME="${HOME}" LC_ALL=C /usr/bin/python3 -I -S - "$1" <<'PY'
import os
import sys
path = os.path.abspath(os.path.expanduser(sys.argv[1]))
while path.startswith("//"):
    path = path[1:]
print(path)
PY
}
DEST="$(lexical_abs "${DEST}")"
ALLOWED_MODEL_ROOT="$(lexical_abs "${LAGUNA_ALLOWED_MODEL_ROOT:-$HOME/models}")"
while [[ "${ALLOWED_MODEL_ROOT}" != "/" && "${ALLOWED_MODEL_ROOT}" == */ ]]; do
  ALLOWED_MODEL_ROOT="${ALLOWED_MODEL_ROOT%/}"
done
validate_components_no_symlink "${ALLOWED_MODEL_ROOT}"
case "${ALLOWED_MODEL_ROOT}" in
  /|/home|/Users|/tmp|/tmp/*|/private/tmp|/private/tmp/*|/var|/usr|"${HOME}"|"${ROOT}"|"${ROOT}"/*)
    die "refusing broad, temporary, or in-pack allowed model root: ${ALLOWED_MODEL_ROOT}"
    ;;
esac
validate_trusted_directory_chain "${ALLOWED_MODEL_ROOT}" "allowed model root"
PARTIAL="${DEST}/.${OFFICIAL_FILE}.part"
TARGET="${DEST}/${OFFICIAL_FILE}"
MARKER="${DEST}/PULL_COMPLETE_${OFFICIAL_FILE}"
SIDECAR="${DEST}/sha256_${OFFICIAL_FILE}.txt"
LOCK_DIR="${DEST}/.${OFFICIAL_FILE}.pull.lock.d"

# FILE is intentionally not a generic path selector. This closes basename
# edge cases such as '..' and keeps every launch pull on the exact Q4 artifact.
[[ "${FILE}" == "${OFFICIAL_FILE}" ]] || die \
  "launch pull accepts only ${OFFICIAL_FILE}; experimental SKUs use scripts/pull_sku.sh and are never launch authority"
[[ "${REV}" =~ ^[0-9a-fA-F]{40}$ ]] || die "artifact revision must be an immutable 40-hex commit, got ${REV}"
if [[ "${REPO}" != "${OFFICIAL_REPO}" || "${REV}" != "${OFFICIAL_REV}" ]]; then
  [[ "${LAGUNA_ALLOW_ALTERNATE_SOURCE:-0}" == "1" ]] || die \
    "source is pinned to ${OFFICIAL_REPO}@${OFFICIAL_REV}; the mirror override requires LAGUNA_ALLOW_ALTERNATE_SOURCE=1"
fi

[[ -f "${SUMS}" && ! -L "${SUMS}" ]] || die "missing or symlinked pack SHA256SUMS at ${SUMS}"
expected="$(
  awk -v f="${OFFICIAL_FILE}" '
    $0 ~ /^[[:space:]]*#/ { next }
    NF >= 2 && $NF == f { print $1; found=1; exit }
    END { if (!found) exit 1 }
  ' "${SUMS}"
)" || die "${OFFICIAL_FILE} not listed in ${SUMS}"
[[ "${expected}" =~ ^[0-9a-fA-F]{64}$ ]] || die "bad expected hash for ${OFFICIAL_FILE}: ${expected}"
expected="$(printf '%s' "${expected}" | tr '[:upper:]' '[:lower:]')"
[[ "${expected}" == "${OFFICIAL_SHA256}" ]] || die "pack SHA256SUMS does not match compiled launch authority"

# All path validation occurs before the first destination write.
validate_destination
umask 077
mkdir -p "${DEST}"
validate_destination
chmod 0700 "${DEST}"
validate_destination
[[ "$(stat_mode "${DEST}")" == "700" ]] || die "destination directory must have mode 0700"

# mkdir is the lock primitive: it neither truncates nor follows a predictable
# lock-file symlink/hardlink. A stale lock must be inspected and removed by the
# operator; this script never guesses that an owner died.
if ! mkdir "${LOCK_DIR}" 2>/dev/null; then
  die "another pull (or a stale inspected lock) owns ${LOCK_DIR}"
fi
lock_owned=1
sidecar_tmp=""
marker_tmp=""
cleanup() {
  trap '' INT TERM HUP
  [[ -z "${sidecar_tmp:-}" ]] || rm -f -- "${sidecar_tmp}"
  [[ -z "${marker_tmp:-}" ]] || rm -f -- "${marker_tmp}"
  if [[ "${lock_owned:-0}" == "1" ]]; then
    rmdir "${LOCK_DIR}" 2>/dev/null || true
    lock_owned=0
  fi
}
trap cleanup EXIT
trap 'cleanup; exit 130' INT
trap 'cleanup; exit 143' TERM
trap 'cleanup; exit 129' HUP

validate_destination
for leaf in "${TARGET}" "${PARTIAL}" "${MARKER}" "${SIDECAR}"; do
  validate_leaf "${leaf}" "managed pull file"
done

target_ready=0
if [[ -f "${TARGET}" ]]; then
  existing_hash="$(hash_file "${TARGET}")"
  existing_bytes="$(wc -c < "${TARGET}" | tr -d '[:space:]')"
  if [[ "${existing_hash}" == "${OFFICIAL_SHA256}" && "${existing_bytes}" -eq "${OFFICIAL_BYTES}" ]]; then
    target_ready=1
    got="${existing_hash}"
    bytes="${existing_bytes}"
    if [[ -f "${MARKER}" && -f "${SIDECAR}" ]]; then
      [[ "$(cat "${SIDECAR}")" == "${OFFICIAL_SHA256}  ${OFFICIAL_FILE}" ]] || die "checksum sidecar does not match the verified target"
      for marker_line in \
        "schema=saqs.gguf_verification/v1" \
        "file=${OFFICIAL_FILE}" \
        "sha256=${OFFICIAL_SHA256}" \
        "bytes=${OFFICIAL_BYTES}" \
        "status=verified" \
        "diy_gguf=false"; do
        grep -Fqx "${marker_line}" "${MARKER}" || die "verification marker is missing ${marker_line}"
      done
      echo "already_verified=${TARGET}"
      echo "sha256=${existing_hash}"
      exit 0
    fi
    [[ ! -e "${MARKER}" && ! -e "${SIDECAR}" ]] || die \
      "only one verification sidecar exists; inspect rather than guessing recovery"
    echo "verified target exists without sidecars; rebuilding no-clobber verification receipts"
  else
    die "existing target is not the pinned Q4 artifact; leave it for inspection and choose a clean destination"
  fi
fi
if (( target_ready == 0 )); then
  [[ ! -e "${MARKER}" && ! -e "${SIDECAR}" ]] || die \
    "stale marker/checksum sidecar exists without a verified target; inspect the destination"

  partial_bytes=0
  if [[ -f "${PARTIAL}" ]]; then
    partial_bytes="$(wc -c < "${PARTIAL}" | tr -d '[:space:]')"
    [[ "${partial_bytes}" =~ ^[0-9]+$ && "${partial_bytes}" -le "${OFFICIAL_BYTES}" ]] || \
      die "partial file is larger than the pinned artifact: ${PARTIAL}"
  fi
  remaining_bytes=$((OFFICIAL_BYTES - partial_bytes))
  available_kib="$(df -Pk "${DEST}" | awk 'NR == 2 {print $4}')"
  [[ "${available_kib}" =~ ^[0-9]+$ ]] || die "could not determine free disk space for ${DEST}"
  available_bytes=$((available_kib * 1024))
  required_bytes=$((remaining_bytes + HEADROOM_BYTES))
  (( available_bytes >= required_bytes )) || die \
    "insufficient disk: need ${required_bytes} bytes (remaining artifact + 5 GiB headroom), have ${available_bytes}"

  echo "pull ${URL}"
  if (( partial_bytes < OFFICIAL_BYTES )); then
    # Point-in-time path checks cannot defend against a malicious same-UID process
    # racing the launcher. The intended operating boundary is an exclusive host.
    validate_destination
    validate_leaf "${PARTIAL}" "partial download"
    curl --disable --proto '=https' --tlsv1.2 --location --fail --retry 8 --retry-delay 15 --continue-at - \
      -A 'hizrianraz-laguna-spark-pack' --output "${PARTIAL}" "${URL}"
  else
    echo "complete partial already present; skipping network and verifying ${PARTIAL}"
  fi

  validate_destination
  validate_leaf "${PARTIAL}" "partial download"
  bytes="$(wc -c < "${PARTIAL}" | tr -d '[:space:]')"
  [[ "${bytes}" -eq "${OFFICIAL_BYTES}" ]] || die \
    "byte-size mismatch: got ${bytes}, expected ${OFFICIAL_BYTES}; partial retained at ${PARTIAL}"
  got="$(hash_file "${PARTIAL}")"
  echo "expected ${OFFICIAL_SHA256}"
  echo "got      ${got}"
  [[ "${got}" == "${OFFICIAL_SHA256}" ]] || {
    echo "FAIL-CLOSED: sha256 mismatch; partial retained at ${PARTIAL}" >&2
    exit 3
  }

  validate_destination
  [[ ! -e "${TARGET}" && ! -L "${TARGET}" ]] || die "target appeared during verification"
  publish_no_clobber "${PARTIAL}" "${TARGET}" || die "atomic no-clobber model publication failed"
  validate_leaf "${TARGET}" "published model"
  chmod 0400 "${TARGET}"
fi

sidecar_tmp="$(mktemp "${DEST}/.sha256.tmp.XXXXXX")"
marker_tmp="$(mktemp "${DEST}/.marker.tmp.XXXXXX")"
printf '%s  %s\n' "${got}" "${OFFICIAL_FILE}" > "${sidecar_tmp}"
{
  printf 'schema=saqs.gguf_verification/v1\n'
  printf 'file=%s\n' "${OFFICIAL_FILE}"
  printf 'repo=%s\n' "${REPO}"
  printf 'revision=%s\n' "${REV}"
  printf 'official_revision=%s\n' "${OFFICIAL_REV}"
  printf 'sha256=%s\n' "${got}"
  printf 'bytes=%s\n' "${bytes}"
  printf 'status=verified\n'
  printf 'diy_gguf=false\n'
  printf 'written_at=%s\n' "$(date -Iseconds 2>/dev/null || date)"
} > "${marker_tmp}"
chmod 0400 "${sidecar_tmp}" "${marker_tmp}"
publish_no_clobber "${sidecar_tmp}" "${SIDECAR}" || die "atomic checksum-sidecar publication failed"
sidecar_tmp=""
publish_no_clobber "${marker_tmp}" "${MARKER}" || die "atomic marker publication failed"
marker_tmp=""
echo "OK exact Q4 verified ${TARGET} · marker=${MARKER}"
