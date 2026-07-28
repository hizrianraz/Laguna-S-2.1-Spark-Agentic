#!/usr/bin/env bash
# Serve official Laguna-S-2.1 GGUF on DGX Spark via poolside llama.cpp (laguna).
# personal DGX Spark serve helper
set -euo pipefail

ROOT="${LAGUNA_ENGINE:-$HOME/src/llama.cpp-laguna}"
BIN="${ROOT}/build/bin"
MODEL="${LAGUNA_MODEL:-$HOME/models/laguna-s-2.1/laguna-s-2.1-Q4_K_M.gguf}"
HOST="${LAGUNA_HOST:-0.0.0.0}"
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

echo "engine=$("${BIN}/llama-server" --version 2>&1 | head -1)"
echo "model=${MODEL}"
echo "listen=${HOST}:${PORT} ctx=${CTX} ngl=${NGL} alias=${ALIAS}"

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
