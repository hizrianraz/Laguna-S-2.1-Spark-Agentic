#!/usr/bin/env bash
# Serve official Laguna-S-2.1 GGUF on DGX Spark via poolside llama.cpp (laguna).
# DGX Spark serve helper
set -euo pipefail

ROOT="${LAGUNA_ENGINE:-$HOME/src/llama.cpp-laguna}"
BIN="${ROOT}/build/bin"
MODEL="${LAGUNA_MODEL:-$HOME/models/laguna-s-2.1/laguna-s-2.1-Q4_K_M.gguf}"
# Default loopback; set LAGUNA_HOST=0.0.0.0 only when intentionally exposing LAN
HOST="${LAGUNA_HOST:-127.0.0.1}"
PORT="${LAGUNA_PORT:-8000}"
CTX="${LAGUNA_CTX:-8192}"
# MoE: keep default GPU offload full unless RAM pressure; override with LAGUNA_NGL
NGL="${LAGUNA_NGL:--1}"
PARALLEL="${LAGUNA_PARALLEL:-1}"
ALIAS="${LAGUNA_ALIAS:-local-laguna}"

export PATH="/usr/local/cuda/bin:/usr/bin:$PATH"
export LD_LIBRARY_PATH="${BIN}:${LD_LIBRARY_PATH:-}"

if [[ ! -x "${BIN}/llama-server" ]]; then
  echo "missing llama-server at ${BIN}/llama-server" >&2
  exit 1
fi
if [[ ! -f "${MODEL}" ]]; then
  echo "missing model ${MODEL}" >&2
  exit 1
fi

# SAQS residency min: ≥12 GiB free before warm (peak non-swapped ≤112 GiB is soak/receipt axis)
MIN_FREE_GIB="${LAGUNA_MIN_FREE_GIB:-12}"
if [[ "${SKIP_RESIDENCY_CHECK:-0}" != "1" ]]; then
  free_kib="$(awk '/MemAvailable:/ {print $2}' /proc/meminfo 2>/dev/null || true)"
  if [[ -z "${free_kib}" ]]; then
    # macOS / non-Linux hop — best-effort via vm_stat pages free+inactive
    if command -v vm_stat >/dev/null 2>&1; then
      page_size="$(pagesize 2>/dev/null || echo 4096)"
      free_kib="$(vm_stat | awk -v ps="$page_size" '
        /Pages free/ {gsub("\\.","",$3); f=$3}
        /Pages inactive/ {gsub("\\.","",$3); i=$3}
        END {printf "%d", (f+i)*ps/1024}
      ')"
    fi
  fi
  if [[ -n "${free_kib}" ]]; then
    free_gib=$(( free_kib / 1024 / 1024 ))
    if [[ "${free_gib}" -lt "${MIN_FREE_GIB}" ]]; then
      echo "FAIL-CLOSED: residency min — MemAvailable/free≈${free_gib} GiB < ${MIN_FREE_GIB} GiB (SAQS)" >&2
      echo "  override only with SKIP_RESIDENCY_CHECK=1 after intentional window" >&2
      exit 3
    fi
    echo "residency_precheck free_gib≈${free_gib} (min ${MIN_FREE_GIB})"
  else
    echo "WARN: could not read free memory — residency precheck skipped (set enforce host)" >&2
  fi
fi

# Default loopback; refuse bare 0.0.0.0 without EXPOSE_LAN=1
if [[ "${HOST}" != "127.0.0.1" && "${HOST}" != "localhost" && "${EXPOSE_LAN:-0}" != "1" ]]; then
  echo "REFUSE: HOST=${HOST} needs EXPOSE_LAN=1 (default loopback only)" >&2
  exit 3
fi

# Evidence bind honesty — engine/model hash receipt is not gate clearance
echo "engine=$("${BIN}/llama-server" --version 2>&1 | head -1)"
echo "model=${MODEL}"
echo "listen=${HOST}:${PORT} ctx=${CTX} ngl=${NGL} alias=${ALIAS}"
echo "honesty=evidence_bind_neq_gate · smoke_neq_headline · residency peak≤112GiB non-swap (soak receipt)"

exec "${BIN}/llama-server" \
  -m "${MODEL}" \
  --host "${HOST}" \
  --port "${PORT}" \
  -c "${CTX}" \
  -ngl "${NGL}" \
  --parallel "${PARALLEL}" \
  --alias "${ALIAS}" \
  --jinja \
  -fa on
