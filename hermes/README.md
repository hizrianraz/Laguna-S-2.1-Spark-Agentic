# Hermes-class sample client

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
api_key  = $OPENAI_API_KEY   # same random secret as server-side LAGUNA_API_KEY
model    = local-laguna      # must match llama-server --alias
```

```bash
export OPENAI_BASE_URL=http://127.0.0.1:8000/v1
export OPENAI_API_KEY="$LAGUNA_API_KEY"
export OPENAI_MODEL=local-laguna
/usr/bin/python3 -I -S hermes/sample_client.py
```

Remote client → Spark (no local full-S weights on ≤32 GB class machines):

- `serve_spark.sh` is loopback-only and rejects every direct remote bind.
- Use an SSH tunnel for the simple remote-client case.
- Treat any TLS proxy or tailnet gateway as a separate surface requiring its own audit.

```bash
ssh -N -L 127.0.0.1:8000:127.0.0.1:8000 spark-user@spark-host

# In a second local terminal:
export OPENAI_BASE_URL=http://127.0.0.1:8000/v1
export OPENAI_API_KEY='<same-random-secret-configured-on-spark>'
export OPENAI_MODEL=local-laguna
/usr/bin/python3 -I -S hermes/sample_client.py
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

## Hermes-class smoke v4 (current hardened, unmeasured)

```bash
export OPENAI_API_KEY="$LAGUNA_API_KEY"
/usr/bin/python3 -I -S eval/hermes_agent_smoke/run_hermes_smoke.py \
  --base-url http://127.0.0.1:8000/v1 \
  --model local-laguna \
  --temperature 0
```

27 hardened cases (terminal/files/web multi-turn + repair).
See `eval/hermes_agent_smoke/README.md`.  
**One-response protocol** on most cases — tools validated, not executed.  
Temperature is fixed at **0.0**. This v4 catalog is **unmeasured** at SHA-256
`748f152eb8ceeedb4f04bef336263519bf5739f4e5e3027f3ec56d5ae080ad89`.
The historical **27/27** belongs only to locked v2 catalog SHA-256
`3275a4a570007fa8f948764a6873e055dc5a4a5ff257a1edc8bc342a02a8ddfc`
and `results/hermes_agent_smoke.json`; it does not transfer to v4. The command
above writes a new receipt and does not overwrite historical evidence.

Does **not** replace the historical **agent_smoke 40/40 format/routing** receipt.

## Layer B research suite (optional)

```bash
LAGUNA_LAYER_B_OUT="results/hermes_agent_smoke_layer_b_v3_$(date -u +%Y%m%dT%H%M%SZ).json" \
  ./scripts/measure_layer_b_v3.sh
```

35 cases (27 parent-shaped + 8 long-horizon / denser repair). The current helper
catalog is **unmeasured diagnostic-only** at SHA-256
`0502e626d92fa6845bfb66da87c877f86c4e05f19b30d1fe5d264c88277d9ceb`.
The historical **35/35** in **137.56s** belongs only to the older catalog SHA-256
`829fd838a83a73cf3f5d05310491a51420fdae7fa7618b1d62d4da444f4fa5e1`.
It does **not** transfer to the current bytes or move the locked v2 freeze score.

One-shot helper: `./scripts/measure_layer_b_v3.sh`  
(For a remote Spark, keep the helper on local port 8000 with
`ssh -N -L 8000:127.0.0.1:8000 spark`.)

Historical receipt path fields are labels from the machine that produced the
receipt, not selectors for current files. Score identity is bound to the suite
version and catalog SHA-256 above; never reattach a historical score by matching
only a filename such as `cases.json` or a receipt path.

Not a Nous endorsement.
