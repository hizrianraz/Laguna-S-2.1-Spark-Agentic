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

## Measured (live Spark)

| Field | Value |
|-------|--------|
| Result | **27/27 (100%)** |
| Elapsed | **104.4 s** (post-restore); prior same-day 102.68 s |
| Model id | `local-laguna` |
| Base | Spark OpenAI-compatible `:8000` |
| Temp | **0.0** |
| Artifact | `results/hermes_agent_smoke.json` |
| When | 2026-07-28 ~23:57 WIB (post-restore lock) |

Meets ship_min and stretch. Does **not** replace agent_smoke 40/40 launch bar.

## Run

```bash
# assumed local Spark serve with --jinja
python eval/hermes_agent_smoke/run_hermes_smoke.py \
  --base-url http://127.0.0.1:8000/v1 \
  --model local-laguna \
  --out results/hermes_agent_smoke.json
```

Optional: `--limit N`, `--ids term_01,files_01`, `--temperature 0`.

## Protocol honesty

**one-response protocol** — tool JSON shape / multi-turn repair are **validated**, tools are **not executed**.
Smoke temperature for claim runs: **0.0** (never 0.7 card/default for tools).

## Claims rule

Pass fraction on the card only with `results/hermes_agent_smoke.json` from a real run.
Headline launch bar remains agent_smoke **40/40**.
