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
model    = local-laguna      # any label; server may echo file stem
```

```bash
export OPENAI_BASE_URL=http://127.0.0.1:8000/v1
export OPENAI_API_KEY=sk-local
export OPENAI_MODEL=local-laguna
python hermes/sample_client.py
```

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

## Jinja / chat template

Serve with `--jinja` on poolside `laguna` llama.cpp so tool call formatting
matches the Laguna chat template. If tool_calls parse soft-fail, check server
log for template warnings before blaming the model.

## Escapes

| Symptom | Check |
|---------|--------|
| empty tool_calls, prose only | temp→0, strengthen system “use tools”, confirm `--jinja` |
| invented tool names | smoke case `no_invented_tools`; tighten system prompt |
| JSON args invalid | repair turn in agent_smoke `error_repair` |
| 404 /v1/... | base_url must include `/v1` |

## Hermes-class smoke v2

```bash
python eval/hermes_agent_smoke/run_hermes_smoke.py \
  --base-url http://127.0.0.1:8000/v1 \
  --model local-laguna \
  --out results/hermes_agent_smoke.json
```

27 fixed cases (terminal/files/web multi-turn + repair). See `eval/hermes_agent_smoke/README.md`.
Not a Nous endorsement.
