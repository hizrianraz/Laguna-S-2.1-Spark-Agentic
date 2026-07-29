# hermes_agent_smoke

Hermes-**class** agent tool smoke for Laguna OpenAI-compatible serve.

- **Not** a Nous Research endorsement or Hermes Agent product claim.
- Name = tool-agent runtime shape (OpenAI `tools` / multi-turn repair).
- Reuses judges + prior-arg sanitization from `eval/agent_smoke/`.

## Suites

| Suite | File | Cases | Ship min | Stretch | Freeze claim? |
|-------|------|------:|---------:|--------:|:-------------|
| **v2 (freeze)** | `cases.json` | **27** | **24/27** | **27/27** | **Yes** — launch lock artifact |
| **v3 Layer B** | `cases_layer_b_v3.json` | **35** (=27+8) | **30/35** | **35/35** | **No** until live measured |

Headline ship bar for launch lock: still **agent_smoke 40/40** (v1).

v2 categories: terminal · files · web · multi_tool · multi_turn · error_repair · no_invented · browser · memory_cron · args_strict · safety

v3 adds **long_horizon** (+ denser multi_turn / error_repair): tool→obs→next-tool chains after 1–2 prior hops.

### Layer B new case ids (v3 only)

- `long_01` … `long_05` — multi-hop continue (search→read→run, terminal→calc, write→read, empty-search recover, gather→memory)
- `repair_03` — invalid prior JSON args repair
- `turn_05` — prose guess then force tool
- `turn_06` — finish second half of multi-goal after first tool obs

## Measured (live Spark) — freeze bar

| Field | Value |
|-------|--------|
| Result | **27/27 (100%)** on **v2** |
| Elapsed | **~100–104 s** |
| Model id | `local-laguna` |
| Base | Spark OpenAI-compatible `:8000` |
| Temp | **0.0** |
| Artifact | `results/hermes_agent_smoke.json` |
| When | 2026-07-28/29 (see `results/launch_lock.json`) |

v3 Layer B has **no live Spark claim** in this pack tip until a real run writes `results/hermes_agent_smoke_layer_b_v3.json`.

## Run

```bash
# Freeze / claim path — v2 only
python eval/hermes_agent_smoke/run_hermes_smoke.py \
  --base-url http://127.0.0.1:8000/v1 \
  --model local-laguna \
  --cases eval/hermes_agent_smoke/cases.json \
  --out results/hermes_agent_smoke.json

# Layer B expansion (research / post-measure) — does not move freeze bar
python eval/hermes_agent_smoke/run_hermes_smoke.py \
  --base-url http://127.0.0.1:8000/v1 \
  --model local-laguna \
  --cases eval/hermes_agent_smoke/cases_layer_b_v3.json \
  --out results/hermes_agent_smoke_layer_b_v3.json
```

Optional: `--limit N`, `--ids term_01,long_01`, `--temperature 0`.

Offline judge dry-run (no server): load `agent_smoke.judge` against synthetic tool_calls (see receipt).

## Protocol honesty

**one-response protocol** — tool JSON shape / multi-turn repair are **validated**, tools are **not executed**.
Smoke temperature for claim runs: **0.0** (never 0.7 card/default for tools).

Judges already support: `tool_call`, `any_of_tools`, `any_ok_tools`, `no_extra_tools`, `content_contains` + `sanitize_messages_for_server` for broken prior args.

## Claims rule

- Freeze / launch lock quotes **only** v2 `results/hermes_agent_smoke.json`.
- Do not rewrite `launch_lock.json` hermes fields from a v3 run.
- Headline launch bar remains agent_smoke **40/40**.
- Pass fraction on the card only with a real run artifact.

## Layer B intent

Expand harness toward Hermes multi-turn / long-horizon dominance **without** touching weights or Aug 3 freeze claim surface.
Retrain / full agentic SFT stays **parked** (separate post-freeze decision).
