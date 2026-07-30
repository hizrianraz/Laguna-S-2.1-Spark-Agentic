#!/bin/bash -p
{ builtin set +x; } 2>/dev/null
# Run the non-authoritative Layer B suite against the loopback Laguna serve.
# This does not start weights and can never rewrite historical launch authority.
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
  /usr/bin/printf '%s\n' 'FAIL-CLOSED: measure as one unprivileged user with matching real/effective IDs' >&2
  exit 126
fi

readonly CLEAN_PATH="/usr/local/cuda/bin:/usr/bin:/bin"
readonly NON_AUTHORITATIVE_EXIT=4
builtin export PATH="${CLEAN_PATH}"
builtin unset LD_PRELOAD LD_AUDIT LD_LIBRARY_PATH CDPATH ENV BASH_ENV TMPDIR TMP TEMP \
  PYTHONPATH PYTHONHOME PYTHONSTARTUP PYTHONINSPECT PYTHONWARNINGS PYTHONUSERBASE
API_KEY="${OPENAI_API_KEY:-}"
builtin export -n API_KEY 2>/dev/null || true
builtin unset OPENAI_API_KEY LAGUNA_API_KEY

readonly ROOT="$(builtin cd "$(/usr/bin/dirname "${BASH_SOURCE[0]}")/.." && builtin pwd -P)"
BASE_URL="${OPENAI_BASE_URL:-http://127.0.0.1:8000/v1}"
BASE_URL="${BASE_URL%/}"
MODEL="${OPENAI_MODEL:-local-laguna}"
OUT="${LAGUNA_LAYER_B_OUT:-$ROOT/results/hermes_agent_smoke_layer_b_v3.json}"
readonly CASES="$ROOT/eval/hermes_agent_smoke/cases_layer_b_v3.json"

die() {
  echo "FAIL-CLOSED: $*" >&2
  exit 2
}

stat_owner() {
  stat -c '%u' -- "$1"
}

stat_mode() {
  stat -c '%a' -- "$1"
}

link_count() {
  stat -c '%h' -- "$1"
}

validate_private_file() {
  local path="$1" label="$2"
  [[ "$(dirname "${path}")" == "${runtime_dir}" ]] || die "${label} escaped the private runtime directory"
  [[ -f "${path}" && ! -L "${path}" && -O "${path}" ]] || die "${label} is not a current-user regular file"
  [[ "$(link_count "${path}")" == "1" ]] || die "${label} must have one hard link"
  [[ "$(stat_mode "${path}")" == "600" ]] || die "${label} must have mode 0600"
}

[[ "${BASE_URL}" == "http://127.0.0.1:8000/v1" ]] || die "Layer B is restricted to http://127.0.0.1:8000/v1"
[[ "${MODEL}" == "local-laguna" ]] || die "Layer B model must equal local-laguna"
[[ -f "${CASES}" && ! -L "${CASES}" ]] || die "missing or symlinked cases: ${CASES}"
if (( ${#API_KEY} < 32 || ${#API_KEY} > 256 )) || [[ ! "${API_KEY}" =~ ^[A-Za-z0-9._~-]+$ ]]; then
  die "OPENAI_API_KEY must be the 32..256 character URL-safe Laguna bearer"
fi
[[ -x /usr/bin/python3 ]] || die "missing trusted Python interpreter: /usr/bin/python3"
for command_name in chmod curl dirname env jq mktemp rm rmdir stat; do
  command -v "${command_name}" >/dev/null 2>&1 || die "missing required command: ${command_name}"
done

runtime_parent="/run/user/${EUID}"
[[ -d "${runtime_parent}" && ! -L "${runtime_parent}" && -O "${runtime_parent}" ]] || die \
  "trusted per-user runtime directory is unavailable: ${runtime_parent}"
[[ "$(stat_owner "${runtime_parent}")" == "${EUID}" && "$(stat_mode "${runtime_parent}")" == "700" ]] || die \
  "per-user runtime directory must be current-user-owned mode 0700"
runtime_dir="$(mktemp -d "${runtime_parent}/laguna-layer-b.XXXXXX")"
[[ -d "${runtime_dir}" && ! -L "${runtime_dir}" && -O "${runtime_dir}" ]] || die "invalid private runtime directory"
[[ "$(stat_mode "${runtime_dir}")" == "700" ]] || die "private runtime directory must have mode 0700"
probe_file="$(mktemp "${runtime_dir}/models.XXXXXX")"
auth_config="$(mktemp "${runtime_dir}/curl-auth.XXXXXX")"
api_key_file="$(mktemp "${runtime_dir}/api-key.XXXXXX")"
validate_private_file "${probe_file}" "models response temporary"
validate_private_file "${auth_config}" "curl-auth temporary"
validate_private_file "${api_key_file}" "API-key temporary"

cleanup() {
  trap '' INT TERM HUP
  rm -f -- "${probe_file:-}" "${auth_config:-}" "${api_key_file:-}"
  [[ -z "${runtime_dir:-}" ]] || rmdir "${runtime_dir}" 2>/dev/null || true
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
trap 'exit 129' HUP

printf 'header = "Authorization: Bearer %s"\n' "${API_KEY}" > "${auth_config}"
printf '%s\n' "${API_KEY}" > "${api_key_file}"
API_KEY=""
unset API_KEY
chmod 0600 "${auth_config}" "${api_key_file}"

echo "pack=${ROOT}"
echo "base_url=${BASE_URL} model=${MODEL}"
echo "cases=${CASES}"
echo "out=${OUT}"
echo "probe /models"
code="$(curl --disable --config "${auth_config}" --noproxy '*' --silent --show-error --max-time 8 \
  --output "${probe_file}" --write-out '%{http_code}' "${BASE_URL}/models" || true)"
[[ "${code}" == "200" ]] || die "serve down (HTTP ${code:-curl-fail}) at ${BASE_URL}/models"
jq -e --arg expected "${MODEL}" \
  '(.error == null) and (.data | type == "array" and length == 1) and (.data[0].id == $expected)' \
  "${probe_file}" >/dev/null || die "model inventory does not contain exactly local-laguna"
echo "models_ok=${MODEL}"

runner_rc=0
/usr/bin/env -i PATH="${CLEAN_PATH}" HOME="${HOME}" LANG="C.UTF-8" \
  /usr/bin/python3 -I -S "$ROOT/eval/hermes_agent_smoke/run_hermes_smoke.py" \
  --api-key-file "${api_key_file}" \
  --base-url "${BASE_URL}" \
  --model "${MODEL}" \
  --cases "${CASES}" \
  --temperature 0 \
  --out "${OUT}" || runner_rc=$?
[[ "${runner_rc}" -eq "${NON_AUTHORITATIVE_EXIT}" ]] || die \
  "Layer B runner returned ${runner_rc}; expected diagnostic exit ${NON_AUTHORITATIVE_EXIT}"

/usr/bin/env -i PATH="${CLEAN_PATH}" HOME="${HOME}" LANG="C.UTF-8" \
  OUT="${OUT}" CASES="${CASES}" /usr/bin/python3 -I -S - <<'PY' || die "Layer B receipt validation failed"
import hashlib
import json
import os
from pathlib import Path

EXPECTED_IDS = [
    "term_01", "term_02", "term_03",
    "files_01", "files_02", "files_03", "files_04",
    "web_01", "web_02",
    "multi_01", "multi_02", "multi_03",
    "turn_01", "turn_02", "turn_03", "turn_04",
    "repair_01", "repair_02",
    "noinv_01", "noinv_02", "noinv_03",
    "browse_01", "mem_01", "cron_01", "args_01", "args_02", "safe_01",
    "long_01", "long_02", "long_03", "long_04", "long_05",
    "repair_03", "turn_05", "turn_06",
]
EXPECTED_CASES_SHA256 = "0502e626d92fa6845bfb66da87c877f86c4e05f19b30d1fe5d264c88277d9ceb"

out_path = Path(os.environ["OUT"])
cases_path = Path(os.environ["CASES"]).resolve()
payload = json.loads(out_path.read_text())
results = payload.get("results")
catalog = payload.get("catalog")
if not isinstance(results, list) or [row.get("id") for row in results if isinstance(row, dict)] != EXPECTED_IDS:
    raise SystemExit("receipt must contain exactly the 35 pinned Layer B rows in order")
if not isinstance(catalog, dict):
    raise SystemExit("receipt catalog metadata is missing")
required_false = {
    "complete_catalog": payload.get("complete_catalog"),
    "authority_eligible": payload.get("authority_eligible"),
    "suite_authority_eligible": payload.get("suite_authority_eligible"),
    "suite_green": payload.get("suite_green"),
    "smoke_green": payload.get("smoke_green"),
    "release_green": payload.get("release_green"),
    "gate_clearance": payload.get("gate_clearance"),
    "meets_ship_min": payload.get("meets_ship_min"),
    "meets_ship_stretch": payload.get("meets_ship_stretch"),
    "contract.eligible": (payload.get("contract") or {}).get("eligible"),
    "request_profile_eligible": payload.get("request_profile_eligible"),
    "catalog.canonical_catalog": catalog.get("canonical_catalog"),
    "catalog.complete_catalog": catalog.get("complete_catalog"),
}
if any(value is not False for value in required_false.values()):
    raise SystemExit(f"non-authoritative receipt flags are invalid: {required_false}")
if payload.get("run_scope") != "diagnostic_non_authoritative":
    raise SystemExit("Layer B receipt must have diagnostic_non_authoritative scope")
if payload.get("suite") != "hermes_agent_smoke" or payload.get("version") != 3:
    raise SystemExit("Layer B suite/version mismatch")
if payload.get("n") != 35 or len(results) != 35:
    raise SystemExit("Layer B receipt must report exactly 35 rows")
passed = payload.get("passed")
failed = payload.get("failed")
if type(passed) is not int or type(failed) is not int or passed != 35 or failed != 0:
    raise SystemExit("Layer B wrapper succeeds only for an exact 35/35 result")
if any(row.get("pass") is not True for row in results):
    raise SystemExit("every Layer B result row must pass exactly")
if catalog.get("catalog_count") != 35 or catalog.get("selected_count") != 35:
    raise SystemExit("Layer B catalog counts must both equal 35")
if catalog.get("catalog_ids") != EXPECTED_IDS or catalog.get("selected_ids") != EXPECTED_IDS:
    raise SystemExit("Layer B catalog IDs do not match the pinned suite")
actual_cases_sha256 = hashlib.sha256(cases_path.read_bytes()).hexdigest()
if actual_cases_sha256 != EXPECTED_CASES_SHA256 or catalog.get("actual_sha256") != EXPECTED_CASES_SHA256:
    raise SystemExit("Layer B catalog SHA-256 mismatch")
if Path(catalog.get("actual_path", "")) != cases_path:
    raise SystemExit("Layer B receipt names the wrong catalog path")
total = payload.get("n")
print(f"summary: {passed}/{total} (non-authoritative Layer B; freeze bar unchanged)")
print("do not rewrite launch_lock.json from this artifact")
PY
echo "validated diagnostic receipt ${OUT}"
