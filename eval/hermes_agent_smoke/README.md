# hermes_agent_smoke v2

Hermes-**class** agent tool smoke for Laguna OpenAI-compatible serve.

- **Not** a Nous Research endorsement or Hermes Agent product claim.
- Name = tool-agent runtime shape (OpenAI `tools` / multi-turn repair).
- Reuses judges + prior-arg sanitization from `eval/agent_smoke/`.

## Suite

| Field | Value |
|-------|--------|
| Cases | **27** |
| Version | 2 |
| Ship min | **24/27** (~89%) |
| Stretch | **27/27** |
| Headline ship bar for launch lock | still **agent_smoke 40/40** (v1) |

Categories: terminal · files · web · multi_tool · multi_turn · error_repair · no_invented · browser · memory_cron · args_strict · safety

## Run

```bash
# assumed local Spark serve with --jinja
python eval/hermes_agent_smoke/run_hermes_smoke.py \
  --base-url http://127.0.0.1:8000/v1 \
  --model local-laguna \
  --out results/hermes_agent_smoke.json
```

Optional: `--limit N`, `--ids term_01,files_01`, `--temperature 0`.

## Claims rule

Do **not** put a pass fraction on the card until `results/hermes_agent_smoke.json` exists from a real Spark run.
Until then: suite is fixed and shippable; headline remains agent_smoke **40/40**.
