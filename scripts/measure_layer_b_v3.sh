#!/usr/bin/env bash
# Run Layer B hermes v3 suite against a live captain serve.
# Does NOT start GPU/weights. Does NOT rewrite launch_lock.json.
# Fail-closed if /v1/models is down.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BASE_URL="${OPENAI_BASE_URL:-http://127.0.0.1:8000/v1}"
BASE_URL="${BASE_URL%/}"
MODEL="${OPENAI_MODEL:-local-laguna}"
OUT="${LAGUNA_LAYER_B_OUT:-$ROOT/results/hermes_agent_smoke_layer_b_v3.json}"
CASES="$ROOT/eval/hermes_agent_smoke/cases_layer_b_v3.json"
UA="${LAGUNA_UA:-laguna-layer-b-measure/0.1}"

echo "pack=$ROOT"
echo "base_url=$BASE_URL model=$MODEL"
echo "cases=$CASES"
echo "out=$OUT"

if [[ ! -f "$CASES" ]]; then
  echo "missing cases: $CASES" >&2
  exit 2
fi

echo "probe /models …"
code="$(curl -sS -m 8 -o /tmp/laguna_models_probe.json -w '%{http_code}' \
  -H "User-Agent: ${UA}" \
  -H "Authorization: Bearer ${OPENAI_API_KEY:-sk-local}" \
  "${BASE_URL}/models" || true)"
if [[ "$code" != "200" ]]; then
  echo "serve down (HTTP ${code:-curl-fail}) at ${BASE_URL}/models" >&2
  echo "restore on Spark first:" >&2
  echo "  ./scripts/serve_spark.sh" >&2
  echo "  # or LAST_GREEN_PIN restore block" >&2
  exit 3
fi
echo "models ok: $(head -c 180 /tmp/laguna_models_probe.json)"
echo

python3 "$ROOT/eval/hermes_agent_smoke/run_hermes_smoke.py" \
  --base-url "$BASE_URL" \
  --model "$MODEL" \
  --cases "$CASES" \
  --temperature 0 \
  --out "$OUT"

echo
echo "wrote $OUT"
if command -v python3 >/dev/null; then
  OUT="$OUT" python3 - <<'PY'
import json, os
from pathlib import Path
p = Path(os.environ["OUT"])
d = json.loads(p.read_text())
n = d.get("passed", d.get("n_pass", d.get("n_ok", "?")))
t = d.get("n", d.get("n_total", d.get("total", "?")))
if (n == "?" or t == "?") and isinstance(d.get("results"), list):
    cases = d["results"]
    t = len(cases)
    n = sum(1 for c in cases if c.get("pass") or c.get("ok") or c.get("passed"))
elif (n == "?" or t == "?") and isinstance(d.get("cases"), list):
    cases = d["cases"]
    t = len(cases)
    n = sum(1 for c in cases if c.get("pass") or c.get("ok") or c.get("passed"))
print(f"summary: {n}/{t}  (freeze bar unchanged: hermes v2 27/27 + agent_smoke 40/40)")
print("do not rewrite launch_lock.json from this artifact")
PY
fi
