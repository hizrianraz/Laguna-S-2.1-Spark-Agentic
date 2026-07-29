# Hermes-class sample client

Personal sample client for local Spark serve.

OpenAI-compatible client notes for **Hermes-class / tool-agent** runtimes against
local `llama-server` serving Laguna-S-2.1 on DGX Spark.

## Language

- **Hermes-class** / **tool-agent compatible** = speaks OpenAI `chat.completions`
  + `tools` / `tool_calls` shape common to agent stacks in that family.
- **Not** a Nous Research endorsement.
- **Not** Hermes Agent source, branding, or product affiliation.
- **Not** a third-party gateway product.

## Connect

```text
base_url = http://127.0.0.1:8000/v1
api_key  = sk-local          # llama-server ignores; keep placeholder
model    = local-laguna      # must match llama-server --alias
```

```bash
export OPENAI_BASE_URL=http://127.0.0.1:8000/v1
export OPENAI_API_KEY=sk-local
export OPENAI_MODEL=local-laguna
python hermes/sample_client.py
```

Mac client → Spark (no local S weights on ≤32G founder Mac):

```bash
export OPENAI_BASE_URL=http://<spark-tailscale-ip>:8000/v1
export OPENAI_API_KEY=sk-local
export OPENAI_MODEL=local-laguna
```

Stack-agnostic YAML sketch: [`config.example.yaml`](./config.example.yaml)

## Tool schema contract

Send tools as OpenAI function tools:

```json
{
  "type": "function",
  "function": {
    "name": "calc",
    "description": "…",
    "parameters": {
      "type": "object",
      "properties": {"expression": {"type": "string"}},
      "required": ["expression"]
    }
  }
}
```

Expect assistant messages with either:

- `content` final text, or
- `tool_calls[]` with `function.name` + `function.arguments` (JSON string)

Agent loop:

1. POST messages (+ tools)
2. If `tool_calls` → execute locally → append `role=tool` results
3. Repeat until final `content`
4. **Never** execute a name absent from the offered schema

Multi-turn repair (invalid prior args):

1. If a historical `function.arguments` string is not valid JSON, **do not** re-POST it raw
2. Replace with a sanitized object holding `_invalid_json_arguments` + `_raw` (see `eval/agent_smoke/run_smoke.py`)
3. Or drop/rebuild the broken turn and ask the model to re-issue the tool call

## Jinja / chat template

Serve with `--jinja` on poolside `laguna` llama.cpp so tool call formatting
matches the Laguna chat template. If tool_calls parse soft-fail, check server
log for template warnings before blaming the model.

Captain serve flags (must match last-green):

```text
-c 8192 -ngl -1 --jinja -fa on --alias local-laguna --parallel 1
```

## Failure → fix matrix

| Symptom | Check |
|---------|--------|
| empty tool_calls, prose only | temp→0, strengthen system “use tools”, confirm `--jinja` |
| invented tool names | smoke case `no_invented_tools`; tighten system prompt |
| JSON args invalid | repair turn in agent_smoke `error_repair`; sanitize priors |
| HTTP 500 on follow-up turn | prior tool args not valid JSON — sanitize before re-send |
| 404 /v1/... | `OPENAI_BASE_URL` must include `/v1` |
| model id mismatch | request model must match `--alias` (`local-laguna`) |
| slow / OOM agent loops | ctx 8192 agent day-to-day; do not jump to 256k without FSM |

## Hermes-class smoke v2 (freeze bar companion)

```bash
python eval/hermes_agent_smoke/run_hermes_smoke.py \
  --base-url http://127.0.0.1:8000/v1 \
  --model local-laguna \
  --temperature 0 \
  --out results/hermes_agent_smoke.json
```

27 fixed cases (terminal/files/web multi-turn + repair).  
See `eval/hermes_agent_smoke/README.md`.  
**One-response protocol** on most cases — tools validated, not executed.  
Claim temp **0.0**. Measured tip: **27/27**.

Does **not** replace the launch-bar **agent_smoke 40/40**.

## Layer B research suite (optional)

```bash
python eval/hermes_agent_smoke/run_hermes_smoke.py \
  --base-url http://127.0.0.1:8000/v1 \
  --model local-laguna \
  --cases eval/hermes_agent_smoke/cases_layer_b_v3.json \
  --out results/hermes_agent_smoke_layer_b_v3.json
```

35 cases (= v2 27 + 8 long-horizon / denser repair).  
Live research measure **2026-07-29:** **35/35** in **137.56s** on official Q4 (temp 0).  
Local artifact: `results/hermes_agent_smoke_layer_b_v3.json` (gitignored).  
Tracked receipt: `eval/hermes_agent_smoke/layer_b_v3_live_receipt.json`.  
DOES **not** move freeze lock numbers (v2 stays **27/27**).

One-shot helper: `./scripts/measure_layer_b_v3.sh`  
(If Spark serves loopback-only, tunnel: `ssh -L 18000:127.0.0.1:8000 spark`.)

Not a Nous endorsement.
