#!/bin/bash -p
{ builtin set +x; } 2>/dev/null
# Launch the Laguna Q4 measured-path candidate on one verified DGX Spark.
# This creates a target receipt; it does not refresh the locked bf82eab smoke.
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
  /usr/bin/printf '%s\n' 'FAIL-CLOSED: launch as one unprivileged user with matching real/effective IDs' >&2
  exit 126
fi

# Sanitize command and loader resolution before the first external command.
# Capture the bearer secret as a non-exported shell value, then remove inherited
# key names so no preflight tool or rejected candidate binary can observe it.
readonly CLEAN_PATH="/usr/local/cuda/bin:/usr/bin:/bin"
builtin export PATH="${CLEAN_PATH}"
builtin unset LD_PRELOAD LD_AUDIT LD_LIBRARY_PATH CDPATH ENV BASH_ENV TMPDIR TMP TEMP \
  PYTHONPATH PYTHONHOME PYTHONSTARTUP PYTHONINSPECT PYTHONWARNINGS PYTHONUSERBASE
for inherited_function in awk basename cd chmod cmp command curl date dirname echo env export git grep hostname jq kill ldd lsof mkdir mktemp nvidia-smi pgrep printf pwd python3 readonly readlink rm rmdir sed set sha256sum shasum sleep sort ss stat tr uname unset wc; do
  builtin unset -f "${inherited_function}" 2>/dev/null || true
done
API_KEY="${LAGUNA_API_KEY:-}"
builtin export -n API_KEY 2>/dev/null || true
builtin unset LAGUNA_API_KEY OPENAI_API_KEY

readonly ROOT="$(builtin cd "$(/usr/bin/dirname "${BASH_SOURCE[0]}")/.." && builtin pwd -P)"
readonly ENGINE_REV="04b2b72cb54048ead292884adbe11f284e3ec950"
readonly ENGINE_PATCHED_SOURCE_SHA256="3952ed9f2a415661d17cdedf4ebca4cccfb2d2a883a0e8b939b0bf1e0c1f48b9"
readonly MODEL_BASENAME="laguna-s-2.1-Q4_K_M.gguf"
readonly MODEL_SHA256="a8b55c75714ea73fd90ec85de5defdc0b8d88ca0ad2108343cdd8fc22f7583e4"
readonly MODEL_BYTES=96031829760
readonly RESERVE_BYTES=$((12 * 1024 * 1024 * 1024))
readonly MIN_TOTAL_MEMORY_KIB=$((115 * 1024 * 1024))

ENGINE_ROOT="${LAGUNA_ENGINE:-$HOME/src/llama.cpp-laguna}"
MODEL="${LAGUNA_MODEL:-$HOME/models/laguna-s-2.1/${MODEL_BASENAME}}"
for path_var in ENGINE_ROOT MODEL; do
  value="${!path_var}"
  while [[ "${value}" != "/" && "${value}" == */ ]]; do
    value="${value%/}"
  done
  printf -v "${path_var}" '%s' "${value}"
done
SERVER_BIN="${ENGINE_ROOT}/build/bin/llama-server"

HOST="${LAGUNA_HOST:-127.0.0.1}"
PORT="${LAGUNA_PORT:-8000}"
CTX="${LAGUNA_CTX:-8192}"
NGL="${LAGUNA_NGL:--1}"
PARALLEL="${LAGUNA_PARALLEL:-1}"
ALIAS="${LAGUNA_ALIAS:-local-laguna}"
HEALTH_TIMEOUT_S="${LAGUNA_HEALTH_TIMEOUT_S:-900}"
EXPECTED_ENGINE_BINARY_SHA256="${LAGUNA_EXPECT_ENGINE_SHA256:-}"
EXPECTED_DSO_MANIFEST_SHA256="${LAGUNA_EXPECT_DSO_MANIFEST_SHA256:-}"
EXPECTED_PACK_REVISION="${LAGUNA_EXPECT_PACK_REVISION:-}"
EXPECTED_LAUNCHER_SHA256="${LAGUNA_EXPECT_LAUNCHER_SHA256:-}"
PRINT_RUNTIME_PINS="${LAGUNA_PRINT_RUNTIME_PINS:-0}"
CLEAN_LD_LIBRARY_PATH=""
builtin export -n EXPECTED_PACK_REVISION EXPECTED_LAUNCHER_SHA256 2>/dev/null || true
builtin unset LAGUNA_EXPECT_PACK_REVISION LAGUNA_EXPECT_LAUNCHER_SHA256

die() {
  echo "FAIL-CLOSED: $*" >&2
  exit 3
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

validate_absolute_components() {
  local path="$1" label="$2" component
  [[ -n "${path}" && "${path}" == /* ]] || die "${label} must be a non-empty absolute path"
  component="${path}"
  while [[ "${component}" != "/" && "${component}" != "." ]]; do
    [[ ! -L "${component}" ]] || die "${label} contains a symlink component: ${component}"
    component="$(dirname "${component}")"
  done
}

validate_trusted_directory_chain() {
  local path="$1" label="$2" component owner mode
  validate_absolute_components "${path}" "${label}"
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

validate_regular_owned_single_link() {
  local path="$1" label="$2" links mode
  validate_absolute_components "${path}" "${label} path"
  [[ -f "${path}" && ! -L "${path}" ]] || die "${label} must be a regular non-symlink file: ${path}"
  [[ -O "${path}" ]] || die "${label} must be owned by the current user: ${path}"
  validate_trusted_directory_chain "$(dirname "${path}")" "${label} parent chain"
  links="$(link_count "${path}")"
  [[ "${links}" == "1" ]] || die "${label} must have exactly one hard link: ${path}"
  mode="$(stat_mode "${path}")" || die "cannot read mode for ${label}: ${path}"
  [[ "${mode}" =~ ^[0-7]{3,4}$ ]] || die "invalid mode for ${label}: ${path}"
  (( (8#${mode} & 0022) == 0 )) || die "${label} must not be group/world writable: ${path}"
}

validate_trusted_runtime_file() {
  local path="$1" label="$2" owner mode parent
  [[ -f "${path}" && ! -L "${path}" ]] || die "${label} must resolve to a regular file: ${path}"
  owner="$(stat_owner "${path}")" || die "cannot read owner for ${label}: ${path}"
  [[ "${owner}" == "0" || "${owner}" == "${EUID}" ]] || die "${label} must be root/current-user-owned: ${path}"
  mode="$(stat_mode "${path}")" || die "cannot read mode for ${label}: ${path}"
  [[ "${mode}" =~ ^[0-7]{3,4}$ ]] || die "invalid mode for ${label}: ${path}"
  (( (8#${mode} & 0022) == 0 )) || die "${label} must not be group/world writable: ${path}"
  parent="$(dirname "${path}")"
  validate_trusted_directory_chain "${parent}" "${label} parent chain"
}

validate_private_temp_file() {
  local path="$1" label="$2"
  [[ "$(dirname "${path}")" == "${runtime_dir}" ]] || die "${label} escaped the private runtime directory"
  validate_regular_owned_single_link "${path}" "${label}"
  [[ "$(stat_mode "${path}")" == "600" ]] || die "${label} must have mode 0600"
}

same_file() {
  /usr/bin/env -i PATH="${CLEAN_PATH}" HOME="${HOME}" LC_ALL=C /usr/bin/python3 -I -S - "$1" "$2" <<'PY'
import os
import sys
raise SystemExit(0 if os.path.samefile(sys.argv[1], sys.argv[2]) else 1)
PY
}

git_clean() {
  /usr/bin/env -i PATH="${CLEAN_PATH}" LC_ALL=C /usr/bin/git "$@"
}

publish_no_clobber() {
  /usr/bin/env -i PATH="${CLEAN_PATH}" HOME="${HOME}" LC_ALL=C /usr/bin/python3 -I -S - "$1" "$2" <<'PY'
import os
import sys
source, destination = sys.argv[1:]
try:
    os.link(source, destination, follow_symlinks=False)
except FileExistsError:
    raise SystemExit("receipt destination already exists")
os.unlink(source)
PY
}

for command_name in awk chmod cmp curl date dirname env git grep hostname jq kill ldd mkdir mktemp nvidia-smi pgrep readlink rm rmdir sed sleep sort stat tr uname wc; do
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
LAUNCHER_PATH="${ROOT}/scripts/serve_spark.sh"
validate_trusted_runtime_file "${LAUNCHER_PATH}" "Laguna launcher"
same_file "${BASH_SOURCE[0]}" "${LAUNCHER_PATH}" || die \
  "executed launcher must be the canonical pack path: ${LAUNCHER_PATH}"
[[ "${EXPECTED_PACK_REVISION}" =~ ^[0-9a-f]{40}$ ]] || die \
  "set LAGUNA_EXPECT_PACK_REVISION to the authorized immutable Hugging Face commit"
[[ "${EXPECTED_LAUNCHER_SHA256}" =~ ^[0-9a-f]{64}$ ]] || die \
  "set LAGUNA_EXPECT_LAUNCHER_SHA256 to the independently reviewed digest for that commit"
actual_launcher_sha256="$(hash_file "${LAUNCHER_PATH}")"
[[ "${actual_launcher_sha256}" == "${EXPECTED_LAUNCHER_SHA256}" ]] || die \
  "Laguna launcher SHA-256 mismatch"
readonly LAUNCHER_PATH EXPECTED_PACK_REVISION EXPECTED_LAUNCHER_SHA256 actual_launcher_sha256
ENGINE_ROOT="$(lexical_abs "${ENGINE_ROOT}")"
MODEL="$(lexical_abs "${MODEL}")"
ALLOWED_ENGINE_ROOT="$(lexical_abs "${LAGUNA_ALLOWED_ENGINE_ROOT:-$HOME/src}")"
ALLOWED_MODEL_ROOT="$(lexical_abs "${LAGUNA_ALLOWED_MODEL_ROOT:-$HOME/models}")"
for path_var in ALLOWED_ENGINE_ROOT ALLOWED_MODEL_ROOT; do
  value="${!path_var}"
  while [[ "${value}" != "/" && "${value}" == */ ]]; do value="${value%/}"; done
  printf -v "${path_var}" '%s' "${value}"
  validate_absolute_components "${value}" "${path_var}"
  case "${value}" in
    /|/home|/Users|/tmp|/tmp/*|/private/tmp|/private/tmp/*|/var|/usr|"${HOME}"|"${ROOT}"|"${ROOT}"/*)
      die "refusing broad, temporary, or in-pack ${path_var}: ${value}"
      ;;
  esac
  validate_trusted_directory_chain "${value}" "${path_var}"
done
[[ "${ENGINE_ROOT}" == "${ALLOWED_ENGINE_ROOT}/llama.cpp-laguna" ]] || die \
  "engine root must equal <LAGUNA_ALLOWED_ENGINE_ROOT>/llama.cpp-laguna: ${ENGINE_ROOT}"
[[ "${MODEL}" == "${ALLOWED_MODEL_ROOT}/laguna-s-2.1/${MODEL_BASENAME}" ]] || die \
  "model must equal <LAGUNA_ALLOWED_MODEL_ROOT>/laguna-s-2.1/${MODEL_BASENAME}: ${MODEL}"
SERVER_BIN="${ENGINE_ROOT}/build/bin/llama-server"
CLEAN_LD_LIBRARY_PATH="${ENGINE_ROOT}/build/bin:/usr/local/cuda/lib64:/usr/local/cuda/targets/sbsa-linux/lib"
readonly ENGINE_ROOT MODEL ALLOWED_ENGINE_ROOT ALLOWED_MODEL_ROOT SERVER_BIN CLEAN_LD_LIBRARY_PATH

[[ "$(basename "${MODEL}")" == "${MODEL_BASENAME}" ]] || die "model basename must be exactly ${MODEL_BASENAME}"
case "${ENGINE_ROOT}" in
  /|/home|/Users|/tmp|/tmp/*|/private/tmp|/private/tmp/*|/var|/usr|"${HOME}"|"${ROOT}"|"${ROOT}"/*)
    die "refusing broad, temporary-root, or in-pack engine path: ${ENGINE_ROOT}"
    ;;
esac
case "${MODEL}" in
  "${ROOT}"|"${ROOT}"/*) die "model must not be inside the deployment pack" ;;
esac
validate_absolute_components "${ENGINE_ROOT}" "engine root"
[[ -d "${ENGINE_ROOT}" && -O "${ENGINE_ROOT}" ]] || die "engine root must be an owned directory: ${ENGINE_ROOT}"
validate_trusted_directory_chain "${ENGINE_ROOT}" "engine root"
validate_trusted_directory_chain "${ENGINE_ROOT}/.git" "engine Git metadata"
validate_regular_owned_single_link "${SERVER_BIN}" "llama-server"
validate_regular_owned_single_link "${MODEL}" "model"

[[ "${PORT}" == "8000" ]] || die "measured launch profile reserves port 8000, got ${PORT}"
[[ "${CTX}" == "8192" ]] || die "measured launch profile requires ctx=8192, got ${CTX}"
[[ "${NGL}" == "-1" ]] || die "measured launch profile requires ngl=-1, got ${NGL}"
[[ "${PARALLEL}" == "1" ]] || die "measured launch profile requires parallel=1, got ${PARALLEL}"
[[ "${ALIAS}" == "local-laguna" ]] || die "measured launch profile requires alias=local-laguna, got ${ALIAS}"
[[ "${HEALTH_TIMEOUT_S}" =~ ^[0-9]+$ ]] || die "health timeout must be an integer"
(( HEALTH_TIMEOUT_S >= 30 && HEALTH_TIMEOUT_S <= 1800 )) || die "health timeout must be 30..1800 seconds"
[[ "${PRINT_RUNTIME_PINS}" =~ ^[012]$ ]] || die "LAGUNA_PRINT_RUNTIME_PINS must be 0, 1, or 2"

case "${HOST}" in
  127.0.0.1|localhost) HOST="127.0.0.1" ;;
  *) die "the audited launch path is loopback-only; use an authenticated tunnel or separately audited TLS proxy" ;;
esac
[[ "${EXPOSE_LAN:-0}" == "0" && -z "${LAGUNA_LAN_TRANSPORT:-}" ]] || die \
  "EXPOSE_LAN/LAGUNA_LAN_TRANSPORT are not implemented by this launcher; direct exposure is refused"
readonly NETWORK_PROFILE="loopback_only"

# Exact target identity: one arm64 DGX Spark with one GB10. A generic NVIDIA
# system is not allowed to mint a Spark target receipt.
arch="$(uname -m)"
[[ "${arch}" == "aarch64" || "${arch}" == "arm64" ]] || die "DGX Spark target must be arm64/aarch64; got ${arch}"
gpu_names="$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null)" || die "could not query GPU identity"
gpu_count="$(printf '%s\n' "${gpu_names}" | awk 'NF {n++} END {print n+0}')"
[[ "${gpu_count}" == "1" ]] || die "DGX Spark target must expose exactly one GPU; found ${gpu_count}"
gpu_name="$(printf '%s\n' "${gpu_names}" | awk 'NF {print; exit}')"
[[ "${gpu_name}" == *GB10* ]] || die "DGX Spark target must expose an NVIDIA GB10; got ${gpu_name}"

product_name=""
for product_file in /sys/devices/virtual/dmi/id/product_name /sys/firmware/devicetree/base/model /proc/device-tree/model; do
  if [[ -r "${product_file}" ]]; then
    product_name="$(tr -d '\000' < "${product_file}")"
    [[ -n "${product_name}" ]] && break
  fi
done
[[ "$(printf '%s' "${product_name}" | tr '[:upper:]' '[:lower:]')" == *"dgx spark"* ]] || die \
  "hardware product identity must contain DGX Spark; got ${product_name:-unavailable}"

[[ -r /proc/meminfo ]] || die "DGX Spark residency gate requires readable /proc/meminfo"
mem_total_kib="$(awk '/^MemTotal:/ {print $2; found=1} END {if (!found) exit 1}' /proc/meminfo)" || die "could not read MemTotal"
mem_available_kib="$(awk '/^MemAvailable:/ {print $2; found=1} END {if (!found) exit 1}' /proc/meminfo)" || die "could not read MemAvailable"
swap_total_kib="$(awk '/^SwapTotal:/ {print $2; found=1} END {if (!found) print 0}' /proc/meminfo)"
swap_free_kib="$(awk '/^SwapFree:/ {print $2; found=1} END {if (!found) print 0}' /proc/meminfo)"
for memory_value in "${mem_total_kib}" "${mem_available_kib}" "${swap_total_kib}" "${swap_free_kib}"; do
  [[ "${memory_value}" =~ ^[0-9]+$ ]] || die "invalid numeric memory state"
done
(( mem_total_kib >= MIN_TOTAL_MEMORY_KIB )) || die \
  "DGX Spark target receipt requires at least 115 GiB MemTotal; found ${mem_total_kib} KiB"

actual_engine_rev="$(git_clean -C "${ENGINE_ROOT}" rev-parse HEAD 2>/dev/null || true)"
[[ "${actual_engine_rev}" == "${ENGINE_REV}" ]] || die "engine source revision mismatch: got ${actual_engine_rev:-none}, expected ${ENGINE_REV}"
git_clean -C "${ENGINE_ROOT}" diff --cached --quiet --ignore-submodules -- || die "engine has staged tracked changes"
engine_status="$(git_clean -C "${ENGINE_ROOT}" status --porcelain=v1 --untracked-files=all --ignore-submodules=none)"
[[ "${engine_status}" == " M common/speculative.cpp" ]] || die \
  "engine worktree must contain only the unstaged measured patch; status=${engine_status//$'\n'/;}"
tracked_changes="$(git_clean -C "${ENGINE_ROOT}" diff --name-only --ignore-submodules --)"
[[ "${tracked_changes}" == "common/speculative.cpp" ]] || die \
  "measured engine source must contain only common/speculative.cpp; got ${tracked_changes:-clean tree}"
patch_lines="$(git_clean -C "${ENGINE_ROOT}" diff --unified=0 -- common/speculative.cpp | sed -n -e '/^+++ /d' -e '/^--- /d' -e '/^[+-]/p')"
[[ "${patch_lines}" == $'+#include <cmath>' ]] || die "common/speculative.cpp must match the measured +<cmath>-only patch"
validate_trusted_runtime_file "${ENGINE_ROOT}/common/speculative.cpp" "patched engine source"
actual_patched_source_sha256="$(hash_file "${ENGINE_ROOT}/common/speculative.cpp")"
[[ "${actual_patched_source_sha256}" == "${ENGINE_PATCHED_SOURCE_SHA256}" ]] || die "patched source SHA-256 mismatch"

# Hold the exact model and executable in read-only file descriptors. Hash and
# execute/load through those descriptors so later pathname replacement cannot
# swap in DFlash, a different GGUF, or another binary after preflight.
exec {server_fd}<"${SERVER_BIN}"
exec {model_fd}<"${MODEL}"
readonly SERVER_BOUND="/proc/$$/fd/${server_fd}"
readonly MODEL_BOUND="/proc/$$/fd/${model_fd}"
[[ -r "${SERVER_BOUND}" && -r "${MODEL_BOUND}" ]] || die "Linux /proc fd binding is unavailable"

actual_engine_binary_sha256="$(hash_file "${SERVER_BOUND}")"
actual_model_bytes="$(wc -c < "${MODEL_BOUND}" | tr -d '[:space:]')"
[[ "${actual_model_bytes}" == "${MODEL_BYTES}" ]] || die "model byte-size mismatch: got ${actual_model_bytes}, expected ${MODEL_BYTES}"
actual_model_sha="$(hash_file "${MODEL_BOUND}")"
[[ "${actual_model_sha}" == "${MODEL_SHA256}" ]] || die "model SHA-256 mismatch: got ${actual_model_sha}, expected ${MODEL_SHA256}"

# Phase 1 is deliberately hash-only: it never invokes ldd, the loader, or the
# candidate executable. An operator must review and bind this exact digest
# before phase 2 is allowed to inspect the dynamic dependency closure.
if [[ "${PRINT_RUNTIME_PINS}" == "1" ]]; then
  printf 'LAGUNA_EXPECT_ENGINE_SHA256=%s\n' "${actual_engine_binary_sha256}"
  printf '%s\n' 'next=review this hash, export it, then rerun with LAGUNA_PRINT_RUNTIME_PINS=2'
  exit 0
fi
[[ "${EXPECTED_ENGINE_BINARY_SHA256}" =~ ^[0-9a-f]{64}$ ]] || die \
  "set LAGUNA_EXPECT_ENGINE_SHA256 from hash-only LAGUNA_PRINT_RUNTIME_PINS=1"
[[ "${actual_engine_binary_sha256}" == "${EXPECTED_ENGINE_BINARY_SHA256}" ]] || die "llama-server SHA-256 mismatch"

# Bind the complete clean-environment DSO closure to an operator-attested
# digest. The candidate library directory is never exported to launcher tools;
# it is scoped only to ldd/version/final-server env -i calls.
serve_lock_dir=""
serve_lock_owned=0
runtime_dir=""
dso_manifest_file=""
dso_recheck_file=""
release_serve_lock() {
  if [[ "${serve_lock_owned:-0}" == "1" && -n "${serve_lock_dir:-}" ]]; then
    rmdir "${serve_lock_dir}" 2>/dev/null || true
    serve_lock_owned=0
  fi
}
release_runtime_dir() {
  if [[ -n "${runtime_dir:-}" ]]; then
    rmdir "${runtime_dir}" 2>/dev/null || true
    runtime_dir=""
  fi
}
cleanup_preflight() {
  [[ -z "${dso_manifest_file:-}" ]] || rm -f -- "${dso_manifest_file}"
  [[ -z "${dso_recheck_file:-}" ]] || rm -f -- "${dso_recheck_file}"
  release_serve_lock
  release_runtime_dir
}
trap cleanup_preflight EXIT
trap 'cleanup_preflight; exit 130' INT
trap 'cleanup_preflight; exit 143' TERM
trap 'cleanup_preflight; exit 129' HUP
build_dso_manifest() {
  local output="$1" ldd_output dependency resolved
  ldd_output="$(/usr/bin/env -i PATH="${CLEAN_PATH}" LD_LIBRARY_PATH="${CLEAN_LD_LIBRARY_PATH}" /usr/bin/ldd "${SERVER_BOUND}" 2>&1)" || \
    die "ldd failed for the pinned llama-server"
  [[ "${ldd_output}" != *"not found"* ]] || die "runtime dependency closure contains a missing library"
  while IFS= read -r dependency; do
    [[ -n "${dependency}" ]] || continue
    resolved="$(readlink -f "${dependency}" 2>/dev/null || true)"
    [[ -n "${resolved}" && -f "${resolved}" ]] || die "could not resolve dynamic dependency: ${dependency}"
    validate_trusted_runtime_file "${resolved}" "dynamic dependency"
    printf '%s  %s\n' "$(hash_file "${resolved}")" "${resolved}"
  done < <(printf '%s\n' "${ldd_output}" | awk '$2 == "=>" && $3 ~ /^\// {print $3} $1 ~ /^\// {print $1}' | sort -u) \
    | sort > "${output}"
  [[ -s "${output}" ]] || die "dynamic dependency manifest is empty"
}

# Use only the login manager's private runtime directory. An inherited TMPDIR
# can never choose where DSO manifests or bearer files are created.
runtime_parent="/run/user/${EUID}"
validate_trusted_directory_chain "${runtime_parent}" "private runtime root"
[[ "$(stat_owner "${runtime_parent}")" == "${EUID}" ]] || die "private runtime root must be current-user-owned"
[[ "$(stat_mode "${runtime_parent}")" == "700" ]] || die "private runtime root must have mode 0700"
umask 077
runtime_dir="$(mktemp -d "${runtime_parent}/laguna-launch.XXXXXX")"
[[ -d "${runtime_dir}" && -O "${runtime_dir}" && ! -L "${runtime_dir}" ]] || die "failed to create a private runtime directory"
[[ "$(stat_mode "${runtime_dir}")" == "700" ]] || die "private launch directory must have mode 0700"

dso_manifest_file="$(mktemp "${runtime_dir}/dso-manifest.XXXXXX")"
validate_private_temp_file "${dso_manifest_file}" "DSO manifest temporary"
build_dso_manifest "${dso_manifest_file}"
actual_dso_manifest_sha256="$(hash_file "${dso_manifest_file}")"

if [[ "${PRINT_RUNTIME_PINS}" == "2" ]]; then
  printf 'LAGUNA_EXPECT_DSO_MANIFEST_SHA256=%s\n' "${actual_dso_manifest_sha256}"
  printf 'dynamic_dependency_manifest:\n'
  sed 's/^/  /' "${dso_manifest_file}"
  exit 0
fi

[[ "${EXPECTED_DSO_MANIFEST_SHA256}" =~ ^[0-9a-f]{64}$ ]] || die \
  "set LAGUNA_EXPECT_DSO_MANIFEST_SHA256 from hash-gated LAGUNA_PRINT_RUNTIME_PINS=2"
[[ "${actual_dso_manifest_sha256}" == "${EXPECTED_DSO_MANIFEST_SHA256}" ]] || die "dynamic dependency manifest SHA-256 mismatch"

if ! version_output="$(/usr/bin/env -i PATH="${CLEAN_PATH}" LD_LIBRARY_PATH="${CLEAN_LD_LIBRARY_PATH}" "${SERVER_BOUND}" --version 2>&1)"; then
  die "llama-server --version failed: ${version_output%%$'\n'*}"
fi
grep -Fqi "${ENGINE_REV:0:7}" <<<"${version_output}" || die "llama-server --version does not identify ${ENGINE_REV:0:7}"

if (( ${#API_KEY} < 32 || ${#API_KEY} > 256 )) || [[ ! "${API_KEY}" =~ ^[A-Za-z0-9._~-]+$ ]]; then
  die "set LAGUNA_API_KEY to 32..256 random URL-safe characters"
fi

# Serialize every launcher owned by this user before residency/port checks and
# hold the directory lock for the complete server lifetime. mkdir is atomic and
# does not truncate or follow a predictable lock-file target.
# Fixed machine-level directory lock serializes compliant launchers across
# users and HOME values. A crash leaves an inspectable stale lock that an
# administrator must remove; the launcher never guesses that it is safe.
serve_lock_parent="/run/lock"
serve_lock_dir="${serve_lock_parent}/saqs-dgx-spark-model-residency.lock.d"
validate_absolute_components "${serve_lock_parent}" "host-wide serve lock directory"
[[ -d "${serve_lock_parent}" && ! -L "${serve_lock_parent}" ]] || die "trusted /run/lock directory is unavailable"
[[ "$(stat_owner "${serve_lock_parent}")" == "0" ]] || die "/run/lock must be owned by root"
validate_trusted_directory_chain "$(dirname "${serve_lock_parent}")" "host lock parent chain"
serve_lock_mode="$(stat_mode "${serve_lock_parent}")"
[[ "${serve_lock_mode}" =~ ^[0-7]{3,4}$ ]] || die "invalid /run/lock mode"
(( (8#${serve_lock_mode} & 0022) == 0 || (8#${serve_lock_mode} & 01000) != 0 )) || die \
  "/run/lock must be non-writable or root-owned sticky"
umask 077
mkdir "${serve_lock_dir}" 2>/dev/null || die \
  "another host model launch (or inspected stale lock) owns ${serve_lock_dir}"
serve_lock_owned=1

# Refresh mutable memory/swap state only after the host-wide lock is held; the
# earlier values established target capacity, not launch-time availability.
mem_available_kib="$(awk '/^MemAvailable:/ {print $2; found=1} END {if (!found) exit 1}' /proc/meminfo)" || die "could not refresh MemAvailable"
swap_total_kib="$(awk '/^SwapTotal:/ {print $2; found=1} END {if (!found) print 0}' /proc/meminfo)"
swap_free_kib="$(awk '/^SwapFree:/ {print $2; found=1} END {if (!found) print 0}' /proc/meminfo)"
for memory_value in "${mem_available_kib}" "${swap_total_kib}" "${swap_free_kib}"; do
  [[ "${memory_value}" =~ ^[0-9]+$ ]] || die "invalid refreshed memory state"
done
required_available_kib=$(((MODEL_BYTES + RESERVE_BYTES + 1023) / 1024))
(( mem_available_kib >= required_available_kib )) || die \
  "single-residency precheck needs model bytes + 12 GiB reserve (${required_available_kib} KiB); MemAvailable=${mem_available_kib} KiB"
swap_used_kib=$((swap_total_kib - swap_free_kib))
(( swap_used_kib == 0 )) || die "existing swap use is ${swap_used_kib} KiB; clear swap before launch"

for process_name in llama-server llama-cli ds4-server ollama; do
  set +e
  process_rows="$(pgrep -x "${process_name}" 2>&1)"
  process_rc=$?
  set -e
  if (( process_rc == 0 )); then
    die "another ${process_name} process is resident: ${process_rows//$'\n'/; }"
  elif (( process_rc != 1 )); then
    die "pgrep inventory failed for ${process_name} with status ${process_rc}: ${process_rows}"
  fi
done
set +e
process_rows="$(pgrep -f 'vllm|text-generation-(launcher|server)|sglang|pulsar-server' 2>&1)"
process_rc=$?
set -e
if (( process_rc == 0 )); then
  die "another known model runtime is resident: ${process_rows//$'\n'/; }"
elif (( process_rc != 1 )); then
  die "pgrep known-runtime inventory failed with status ${process_rc}: ${process_rows}"
fi
gpu_processes_before="$(nvidia-smi --query-compute-apps=pid,process_name --format=csv,noheader,nounits 2>/dev/null)" || die \
  "nvidia-smi compute-process inventory failed"
[[ -z "${gpu_processes_before}" ]] || die "GPU compute process already resident: ${gpu_processes_before//$'\n'/; }"

if command -v ss >/dev/null 2>&1; then
  set +e
  port_rows="$(ss -H -ltn "sport = :${PORT}" 2>&1)"
  port_rc=$?
  set -e
  (( port_rc == 0 )) || die "ss port inventory failed with status ${port_rc}: ${port_rows}"
  [[ -z "${port_rows}" ]] || die "TCP port ${PORT} is already listening"
elif command -v lsof >/dev/null 2>&1; then
  set +e
  port_rows="$(lsof -nP -iTCP:"${PORT}" -sTCP:LISTEN 2>&1)"
  port_rc=$?
  set -e
  if (( port_rc == 0 )); then
    die "TCP port ${PORT} is already listening"
  elif (( port_rc != 1 )); then
    die "lsof port inventory failed with status ${port_rc}: ${port_rows}"
  fi
else
  die "need ss or lsof for the required port preflight"
fi

echo "target_identity=product=${product_name} arch=${arch} gpu=${gpu_name} gpu_count=1 mem_total_kib=${mem_total_kib}"
echo "engine_revision_ok=${actual_engine_rev} binary_sha256=${actual_engine_binary_sha256} dso_manifest_sha256=${actual_dso_manifest_sha256}"
echo "model_sha256_ok=${actual_model_sha} bound_fd=true"
echo "residency_precheck=exclusive known_runtimes mem_available_kib=${mem_available_kib} reserve_after_model_gib=12 swap_used_kib=0"
echo "listen=${HOST}:${PORT} ctx=${CTX} ngl=${NGL} parallel=${PARALLEL} alias=${ALIAS} network_profile=${NETWORK_PROFILE}"
echo "authority=historical_bf82eab_format_routing_only; this run creates a separate target receipt"

server_pid=""
api_key_file=""
curl_config_file=""
wrong_curl_config_file=""
receipt_temp=""
cleanup_server() {
  local pid="${server_pid:-}"
  [[ -n "${pid}" ]] || return 0
  if kill -0 "${pid}" >/dev/null 2>&1; then
    kill -TERM "${pid}" >/dev/null 2>&1 || true
    for _ in {1..10}; do
      kill -0 "${pid}" >/dev/null 2>&1 || break
      sleep 1
    done
    kill -0 "${pid}" >/dev/null 2>&1 && kill -KILL "${pid}" >/dev/null 2>&1 || true
    wait "${pid}" >/dev/null 2>&1 || true
  fi
  server_pid=""
}
cleanup_all() {
  cleanup_server
  [[ -z "${api_key_file:-}" ]] || rm -f -- "${api_key_file}"
  [[ -z "${curl_config_file:-}" ]] || rm -f -- "${curl_config_file}"
  [[ -z "${wrong_curl_config_file:-}" ]] || rm -f -- "${wrong_curl_config_file}"
  [[ -z "${receipt_temp:-}" ]] || rm -f -- "${receipt_temp}"
  [[ -z "${dso_manifest_file:-}" ]] || rm -f -- "${dso_manifest_file}"
  [[ -z "${dso_recheck_file:-}" ]] || rm -f -- "${dso_recheck_file}"
  release_serve_lock
  release_runtime_dir
  api_key_file=""; curl_config_file=""; wrong_curl_config_file=""; receipt_temp=""; dso_manifest_file=""; dso_recheck_file=""
}
on_exit() {
  local rc=$?
  trap - EXIT
  trap '' INT TERM HUP
  cleanup_all
  exit "${rc}"
}
on_signal() {
  local rc="$1"
  trap '' INT TERM HUP
  cleanup_all
  trap - EXIT
  exit "${rc}"
}
trap on_exit EXIT
trap 'on_signal 130' INT
trap 'on_signal 143' TERM
trap 'on_signal 129' HUP

umask 077
api_key_file="$(mktemp "${runtime_dir}/api-key.XXXXXX")"
curl_config_file="$(mktemp "${runtime_dir}/curl-auth.XXXXXX")"
wrong_curl_config_file="$(mktemp "${runtime_dir}/curl-wrong-auth.XXXXXX")"
validate_private_temp_file "${api_key_file}" "API-key temporary"
validate_private_temp_file "${curl_config_file}" "curl-auth temporary"
validate_private_temp_file "${wrong_curl_config_file}" "wrong-auth temporary"
printf '%s\n' "${API_KEY}" > "${api_key_file}"
printf 'header = "Authorization: Bearer %s"\n' "${API_KEY}" > "${curl_config_file}"
wrong_key="SAQS_INVALID_BEARER_00000000000000000000000000000000"
[[ "${wrong_key}" != "${API_KEY}" ]] || wrong_key="SAQS_INVALID_BEARER_11111111111111111111111111111111"
printf 'header = "Authorization: Bearer %s"\n' "${wrong_key}" > "${wrong_curl_config_file}"
unset wrong_key
chmod 0600 "${api_key_file}" "${curl_config_file}" "${wrong_curl_config_file}"
API_KEY=""
unset API_KEY
# Revalidate names, then prove they still identify the held descriptors. The
# descriptor binding closes pathname replacement after the check; a malicious
# same-UID process that can mutate the already-open inode remains outside scope.
validate_regular_owned_single_link "${SERVER_BIN}" "llama-server"
validate_regular_owned_single_link "${MODEL}" "model"
same_file "${SERVER_BIN}" "${SERVER_BOUND}" || die "llama-server pathname changed after verification"
same_file "${MODEL}" "${MODEL_BOUND}" || die "model pathname changed after verification"
[[ "$(hash_file "${SERVER_BOUND}")" == "${actual_engine_binary_sha256}" ]] || die "held llama-server changed before launch"
[[ "$(hash_file "${MODEL_BOUND}")" == "${MODEL_SHA256}" ]] || die "held model changed before launch"
dso_recheck_file="$(mktemp "${runtime_dir}/dso-recheck.XXXXXX")"
validate_private_temp_file "${dso_recheck_file}" "DSO recheck temporary"
build_dso_manifest "${dso_recheck_file}"
[[ "$(hash_file "${dso_recheck_file}")" == "${EXPECTED_DSO_MANIFEST_SHA256}" ]] || die \
  "dynamic dependency closure changed immediately before launch"
cmp -s "${dso_manifest_file}" "${dso_recheck_file}" || die "dynamic dependency paths or bytes changed before launch"
rm -f -- "${dso_recheck_file}"
dso_recheck_file=""

# The model rehash is intentionally expensive. Refresh every mutable residency
# gate after it, immediately before exec, so the earlier snapshot cannot become
# a false clearance while another load starts or memory pressure changes.
final_mem_available_kib="$(awk '/^MemAvailable:/ {print $2; found=1} END {if (!found) exit 1}' /proc/meminfo)" || die \
  "could not read final pre-exec MemAvailable"
final_swap_total_kib="$(awk '/^SwapTotal:/ {print $2; found=1} END {if (!found) print 0}' /proc/meminfo)"
final_swap_free_kib="$(awk '/^SwapFree:/ {print $2; found=1} END {if (!found) print 0}' /proc/meminfo)"
for memory_value in "${final_mem_available_kib}" "${final_swap_total_kib}" "${final_swap_free_kib}"; do
  [[ "${memory_value}" =~ ^[0-9]+$ ]] || die "invalid final pre-exec memory state"
done
(( final_mem_available_kib >= required_available_kib )) || die \
  "final pre-exec memory fell below model + 12 GiB reserve: ${final_mem_available_kib} KiB"
final_swap_used_kib=$((final_swap_total_kib - final_swap_free_kib))
(( final_swap_used_kib == 0 )) || die "swap became active before exec: ${final_swap_used_kib} KiB"

for process_name in llama-server llama-cli ds4-server ollama; do
  set +e
  process_rows="$(pgrep -x "${process_name}" 2>&1)"
  process_rc=$?
  set -e
  if (( process_rc == 0 )); then
    die "runtime appeared before exec: ${process_name}: ${process_rows//$'\n'/; }"
  elif (( process_rc != 1 )); then
    die "final pgrep inventory failed for ${process_name} with status ${process_rc}: ${process_rows}"
  fi
done
set +e
process_rows="$(pgrep -f 'vllm|text-generation-(launcher|server)|sglang|pulsar-server' 2>&1)"
process_rc=$?
set -e
if (( process_rc == 0 )); then
  die "known runtime appeared before exec: ${process_rows//$'\n'/; }"
elif (( process_rc != 1 )); then
  die "final known-runtime inventory failed with status ${process_rc}: ${process_rows}"
fi
final_gpu_processes="$(nvidia-smi --query-compute-apps=pid,process_name --format=csv,noheader,nounits 2>/dev/null)" || die \
  "final pre-exec GPU process inventory failed"
[[ -z "${final_gpu_processes}" ]] || die "GPU process appeared before exec: ${final_gpu_processes//$'\n'/; }"
if command -v ss >/dev/null 2>&1; then
  set +e
  port_rows="$(ss -H -ltn "sport = :${PORT}" 2>&1)"
  port_rc=$?
  set -e
  (( port_rc == 0 )) || die "final ss port inventory failed with status ${port_rc}: ${port_rows}"
  [[ -z "${port_rows}" ]] || die "TCP port ${PORT} became occupied before exec"
else
  set +e
  port_rows="$(lsof -nP -iTCP:"${PORT}" -sTCP:LISTEN 2>&1)"
  port_rc=$?
  set -e
  if (( port_rc == 0 )); then
    die "TCP port ${PORT} became occupied before exec"
  elif (( port_rc != 1 )); then
    die "final lsof port inventory failed with status ${port_rc}: ${port_rows}"
  fi
fi

[[ "$(hash_file "${LAUNCHER_PATH}")" == "${actual_launcher_sha256}" ]] || die \
  "Laguna launcher changed before server launch"
/usr/bin/env -i \
  PATH="${CLEAN_PATH}" \
  LD_LIBRARY_PATH="${CLEAN_LD_LIBRARY_PATH}" \
  HOME="${HOME}" \
  LANG="C.UTF-8" \
  "${SERVER_BOUND}" \
  -m "${MODEL_BOUND}" \
  --host "${HOST}" --port "${PORT}" -c "${CTX}" -ngl "${NGL}" \
  --parallel "${PARALLEL}" --alias "${ALIAS}" --api-key-file "${api_key_file}" \
  --jinja -fa on &
server_pid=$!

deadline=$((SECONDS + HEALTH_TIMEOUT_S))
health_ok=0
while (( SECONDS < deadline )); do
  kill -0 "${server_pid}" >/dev/null 2>&1 || break
  if health_json="$(curl --disable --noproxy '*' --config "${curl_config_file}" --silent --show-error --fail --max-time 10 \
      "http://${HOST}:${PORT}/v1/models" 2>/dev/null)"; then
    if jq -e --arg expected "${ALIAS}" \
      '(.error == null) and (.data | type == "array") and (.data | length == 1) and (.data[0].id == $expected)' \
      <<<"${health_json}" >/dev/null; then
      health_ok=1
      break
    fi
  fi
  sleep 5
done
if (( health_ok != 1 )); then
  kill -0 "${server_pid}" >/dev/null 2>&1 && die "server did not become healthy within ${HEALTH_TIMEOUT_S}s"
  set +e; wait "${server_pid}"; server_rc=$?; set -e
  server_pid=""
  die "llama-server exited before health with status ${server_rc}"
fi

probe_payload='{"model":"local-laguna","messages":[{"role":"user","content":"Reply with one word: ready"}],"temperature":0,"max_tokens":1}'
unauth_code="$(curl --disable --noproxy '*' --silent --output /dev/null --write-out '%{http_code}' --max-time 10 \
  -H 'Content-Type: application/json' --data-binary "${probe_payload}" \
  "http://${HOST}:${PORT}/v1/chat/completions" 2>/dev/null || true)"
[[ "${unauth_code}" == "401" || "${unauth_code}" == "403" ]] || die \
  "unauthenticated protected endpoint returned HTTP ${unauth_code:-none}, expected 401/403"
wrong_auth_code="$(curl --disable --noproxy '*' --config "${wrong_curl_config_file}" --silent --output /dev/null --write-out '%{http_code}' --max-time 10 \
  -H 'Content-Type: application/json' --data-binary "${probe_payload}" \
  "http://${HOST}:${PORT}/v1/chat/completions" 2>/dev/null || true)"
[[ "${wrong_auth_code}" == "401" || "${wrong_auth_code}" == "403" ]] || die \
  "wrong-token gate failed: protected endpoint returned HTTP ${wrong_auth_code:-none}, expected 401/403"
protected_probe="$(curl --disable --noproxy '*' --config "${curl_config_file}" --silent --show-error --fail --max-time 120 \
  -H 'Content-Type: application/json' --data-binary "${probe_payload}" \
  "http://${HOST}:${PORT}/v1/chat/completions")" || die "authenticated one-token readiness probe failed"
jq -e --arg expected "${ALIAS}" '
  (.error == null) and (.model == $expected) and
  (.choices | type == "array" and length == 1) and
  (.choices[0].message | type == "object") and
  (.choices[0].message.content | type == "string" and length > 0) and
  (.usage.prompt_tokens | type == "number" and . > 0) and
  (.usage.completion_tokens | type == "number" and . > 0)
' <<<"${protected_probe}" >/dev/null || die "authenticated readiness probe returned empty or incomplete evidence"

post_mem_available_kib="$(awk '/^MemAvailable:/ {print $2}' /proc/meminfo)"
post_swap_total_kib="$(awk '/^SwapTotal:/ {print $2}' /proc/meminfo)"
post_swap_free_kib="$(awk '/^SwapFree:/ {print $2}' /proc/meminfo)"
for memory_value in "${post_mem_available_kib}" "${post_swap_total_kib}" "${post_swap_free_kib}"; do
  [[ "${memory_value}" =~ ^[0-9]+$ ]] || die "invalid post-health memory state"
done
reserve_kib=$((RESERVE_BYTES / 1024))
(( post_mem_available_kib >= reserve_kib )) || die "post-health reserve is below 12 GiB"
post_swap_used_kib=$((post_swap_total_kib - post_swap_free_kib))
(( post_swap_used_kib == 0 )) || die "server became healthy with swap in use"

gpu_processes_after="$(nvidia-smi --query-compute-apps=pid,process_name --format=csv,noheader,nounits 2>/dev/null)" || die \
  "post-health nvidia-smi compute-process inventory failed"
server_gpu_seen=0
while IFS=',' read -r gpu_pid gpu_process_name; do
  gpu_pid="${gpu_pid//[[:space:]]/}"
  [[ "${gpu_pid}" =~ ^[0-9]+$ ]] || die "invalid GPU process row after health"
  if [[ "${gpu_pid}" == "${server_pid}" ]]; then
    server_gpu_seen=1
  else
    die "foreign GPU compute process appeared after launch: pid=${gpu_pid} name=${gpu_process_name}"
  fi
done <<<"${gpu_processes_after}"
(( server_gpu_seen == 1 )) || die "llama-server PID ${server_pid} is absent from NVIDIA compute inventory"
[[ "$(hash_file "${LAUNCHER_PATH}")" == "${actual_launcher_sha256}" ]] || die \
  "Laguna launcher changed before receipt creation"

receipt_stamp="$(date -u +%Y%m%dT%H%M%SZ)"
receipt_root="${LAGUNA_RECEIPT_DIR:-$HOME/.local/state/laguna}"
while [[ "${receipt_root}" != "/" && "${receipt_root}" == */ ]]; do receipt_root="${receipt_root%/}"; done
receipt_root="$(lexical_abs "${receipt_root}")"
allowed_state_root="$(lexical_abs "${LAGUNA_ALLOWED_STATE_ROOT:-$HOME/.local/state}")"
while [[ "${allowed_state_root}" != "/" && "${allowed_state_root}" == */ ]]; do allowed_state_root="${allowed_state_root%/}"; done
validate_absolute_components "${allowed_state_root}" "allowed state root"
case "${allowed_state_root}" in
  /|/home|/Users|/tmp|/tmp/*|/private/tmp|/private/tmp/*|/var|/usr|"${HOME}"|"${ROOT}"|"${ROOT}"/*)
    die "refusing broad, temporary, or in-pack allowed state root: ${allowed_state_root}"
    ;;
esac
validate_trusted_directory_chain "${allowed_state_root}" "allowed state root"
[[ "${receipt_root}" == "${allowed_state_root}/laguna" ]] || die \
  "receipt directory must equal <LAGUNA_ALLOWED_STATE_ROOT>/laguna: ${receipt_root}"
validate_absolute_components "${receipt_root}" "receipt directory"
[[ "$(basename "${receipt_root}")" == "laguna" ]] || die "receipt directory basename must be laguna"
case "${receipt_root}" in
  /|/home|/Users|/tmp|/tmp/*|/private/tmp|/private/tmp/*|/var|/usr|"${HOME}"|"${ROOT}"|"${ROOT}"/*|"$(dirname "${MODEL}")"|"${ENGINE_ROOT}"|"${ENGINE_ROOT}"/*)
    die "refusing broad, model, engine, or in-pack receipt directory: ${receipt_root}"
    ;;
esac
mkdir -p "${receipt_root}"
validate_absolute_components "${receipt_root}" "receipt directory"
[[ -d "${receipt_root}" && -O "${receipt_root}" ]] || die "receipt directory must be owned by the current user"
chmod 0700 "${receipt_root}"
launch_receipt="${receipt_root}/launch_receipt_${receipt_stamp}.json"
[[ ! -e "${launch_receipt}" && ! -L "${launch_receipt}" ]] || die "launch receipt already exists: ${launch_receipt}"
receipt_temp="$(mktemp "${receipt_root}/.launch-receipt.tmp.XXXXXX")"

jq -n \
  --arg generated_at_utc "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --arg pack_revision "${EXPECTED_PACK_REVISION}" --arg launcher_path "${LAUNCHER_PATH}" \
  --arg launcher_sha256 "${actual_launcher_sha256}" \
  --arg host "$(hostname)" --arg product_name "${product_name}" --arg arch "${arch}" \
  --arg gpu_name "${gpu_name}" --arg engine_revision "${actual_engine_rev}" \
  --arg patched_source_sha256 "${actual_patched_source_sha256}" \
  --arg engine_binary_sha256 "${actual_engine_binary_sha256}" \
  --arg dso_manifest_sha256 "${actual_dso_manifest_sha256}" --rawfile dso_manifest "${dso_manifest_file}" \
  --arg engine_version "${version_output}" --arg model_path "${MODEL}" --arg model_sha256 "${actual_model_sha}" \
  --arg network_profile "${NETWORK_PROFILE}" --arg listen_host "${HOST}" --arg alias "${ALIAS}" \
  --argjson gpu_count "${gpu_count}" --argjson mem_total_kib "${mem_total_kib}" \
  --argjson model_bytes "${MODEL_BYTES}" --argjson port "${PORT}" --argjson context "${CTX}" \
  --argjson parallel "${PARALLEL}" --argjson final_preexec_mem_available_kib "${final_mem_available_kib}" \
  --argjson post_mem_available_kib "${post_mem_available_kib}" \
  --argjson post_swap_used_kib "${post_swap_used_kib}" --argjson server_pid "${server_pid}" '
  {
    schema: "saqs.spark_launch_receipt/v3",
    generated_at_utc: $generated_at_utc,
    host: {hostname: $host, product_name: $product_name, architecture: $arch, gpu_name: $gpu_name, gpu_count: $gpu_count, mem_total_kib: $mem_total_kib},
    authority: {
      historical_measure_tip: "bf82eab5fd6c1fb04e863f0c4b05b5658dec4aee",
      refreshes_historical_smoke: false,
      target_receipt_candidate: true,
      independently_source_bound: false,
      clears_freeze: false
    },
    pack_source: {
      declared_huggingface_revision: $pack_revision,
      launcher_path: $launcher_path,
      launcher_sha256: $launcher_sha256,
      launcher_digest_matched_operator_pin: true,
      independent_review_required: "compare revision and launcher SHA-256 with the authorized Hub commit before freeze clearance"
    },
    engine: {
      revision: $engine_revision, patch_profile: "spark_cmath_compat", patched_source_sha256: $patched_source_sha256,
      binary_sha256: $engine_binary_sha256, dynamic_dependency_manifest_sha256: $dso_manifest_sha256,
      dynamic_dependencies: ($dso_manifest | split("\n") | map(select(length > 0))), embedded_version: $engine_version,
      clean_loader_environment: true
    },
    artifact: {configured_path: $model_path, loaded_via_verified_fd: true, sha256: $model_sha256, bytes: $model_bytes},
    serve: {network_profile: $network_profile, listen_host: $listen_host, port: $port, alias: $alias, context: $context, gpu_layers: -1, parallel: $parallel},
    gates: {
      dgx_spark_gb10_arm64_identity: true, exact_model_identity_bound_fd: true,
      engine_source_patch_binary_and_dso_attested: true, dso_closure_revalidated_immediately_before_launch: true,
      absent_and_wrong_bearer_rejected: true,
      protected_auth_probe_with_positive_usage: true,
      final_preexec_residency_refresh: true, one_gpu_compute_process: true,
      zero_swap_post_health: ($post_swap_used_kib == 0), reserve_12gib_post_health: true,
      historical_format_routing_smoke_refreshed: false
    },
    safety_scope: {point_in_time_path_and_inode_binding: true, malicious_same_uid_in_place_inode_mutation: "outside_scope; exclusive host required"},
    observed: {final_preexec_mem_available_kib: $final_preexec_mem_available_kib, post_mem_available_kib: $post_mem_available_kib, post_swap_used_kib: $post_swap_used_kib, server_pid: $server_pid}
  }' > "${receipt_temp}"
chmod 0600 "${receipt_temp}"
publish_no_clobber "${receipt_temp}" "${launch_receipt}" || die "atomic no-clobber receipt publication failed"
receipt_temp=""

rm -f -- "${api_key_file}" "${curl_config_file}" "${wrong_curl_config_file}" "${dso_manifest_file}"
api_key_file=""; curl_config_file=""; wrong_curl_config_file=""; dso_manifest_file=""; dso_recheck_file=""
echo "health_ok=http://${HOST}:${PORT}/v1/models model=${ALIAS} protected_probe=positive auth_enforced_http=${unauth_code}"
echo "launch_receipt=${launch_receipt} copy to results/launch_receipt_aug3.json only after independent review"

set +e; wait "${server_pid}"; server_rc=$?; set -e
server_pid=""
trap - EXIT INT TERM HUP
cleanup_all
exit "${server_rc}"
