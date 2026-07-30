# hermes_agent_smoke

Hermes-**class** agent tool smoke for Laguna OpenAI-compatible serve.

- **Not** a Nous Research endorsement or Hermes Agent product claim.
- Name = tool-agent runtime shape (OpenAI `tools` / multi-turn repair).
- Reuses judges + prior-arg sanitization from `eval/agent_smoke/`.

## Suites

| Contract | Source / artifact | Cases | Catalog SHA-256 | Status |
|----------|-------------------|------:|----------------|:-------|
| **Historical v2 (locked)** | `results/hermes_agent_smoke.json` | **27** | `3275a4a570007fa8f948764a6873e055dc5a4a5ff257a1edc8bc342a02a8ddfc` | Historical **27/27** only; immutable launch-lock evidence |
| **Hardened v4 (current)** | `cases.json` | **27** | `748f152eb8ceeedb4f04bef336263519bf5739f4e5e3027f3ec56d5ae080ad89` | **Unmeasured**; suite-only authority, never release clearance |
| **Historical Layer B v3** | historical measured catalog | **35** | `829fd838a83a73cf3f5d05310491a51420fdae7fa7618b1d62d4da444f4fa5e1` | Historical **35/35**, research-only |
| **Current Layer B v3 diagnostic** | `cases_layer_b_v3.json` | **35** | `0502e626d92fa6845bfb66da87c877f86c4e05f19b30d1fe5d264c88277d9ceb` | **Unmeasured**; diagnostic-only |

The v2 and historical Layer B scores belong only to their listed catalog
hashes. They do not transfer to the hardened v4 or current Layer B bytes.
Historical receipt path fields are machine-local labels, not selectors for the
current files; version plus catalog SHA-256 defines the score identity.

Historical format/routing regression bar: **agent_smoke 40/40** (v1); smoke is not a headline.

The 27-case v4 categories are: terminal · files · web · multi_tool · multi_turn · error_repair · no_invented · browser · memory_cron · args_strict · safety

v3 adds **long_horizon** (+ denser multi_turn / error_repair): tool→obs→next-tool chains after 1–2 prior hops.

### Layer B new case ids (v3 only)

- `long_01` … `long_05` — multi-hop continue (search→read→run, terminal→calc, write→read, empty-search recover, gather→memory)
- `repair_03` — invalid prior JSON args repair
- `turn_05` — prose guess then force tool
- `turn_06` — finish second half of multi-goal after first tool obs

## Measured (live Spark) — locked historical v2 freeze bar

| Field | Value |
|-------|--------|
| Result | **27/27 (100%)** on **v2** |
| Elapsed | **~100–104 s** |
| Model id | `local-laguna` |
| Base | Spark OpenAI-compatible `:8000` |
| Temp | **0.0** |
| Catalog SHA-256 | `3275a4a570007fa8f948764a6873e055dc5a4a5ff257a1edc8bc342a02a8ddfc` |
| Artifact | `results/hermes_agent_smoke.json` |
| When | 2026-07-28/29 (see `results/launch_lock.json`) |

## Measured (live Spark) — historical Layer B v3 research only

| Field | Value |
|-------|--------|
| Result | **35/35 (100%)** on **v3** (=27+8) |
| Elapsed | **137.56 s** |
| Model id | `local-laguna` |
| Weight | official `laguna-s-2.1-Q4_K_M.gguf` |
| Path | Spark serve `127.0.0.1:8000` → SSH tunnel Mac `:18000` |
| Temp | **0.0** |
| Catalog SHA-256 | `829fd838a83a73cf3f5d05310491a51420fdae7fa7618b1d62d4da444f4fa5e1` |
| Artifact (local, gitignored) | `results/hermes_agent_smoke_layer_b_v3.json` |
| Receipt (tracked) | `layer_b_v3_live_receipt.json` |
| When | 2026-07-29 ~18:49 WIB |

**Not a freeze-bar move.** Do not rewrite `launch_lock.json` hermes fields from v3.

## Run

```bash
# Future hardened v4 regression run — historical v2 authority remains immutable
export OPENAI_API_KEY="$LAGUNA_API_KEY"
/usr/bin/python3 -I -S eval/hermes_agent_smoke/run_hermes_smoke.py \
  --base-url http://127.0.0.1:8000/v1 \
  --model local-laguna \
  --cases eval/hermes_agent_smoke/cases.json

# Layer B expansion (research / post-measure) — does not move freeze bar
LAGUNA_LAYER_B_OUT="results/hermes_agent_smoke_layer_b_v3_$(date -u +%Y%m%dT%H%M%SZ).json" \
  ./scripts/measure_layer_b_v3.sh
```

The hardened v4 default is a new UTC-dated receipt. Existing files, symlinked output
paths, and the locked historical authority filenames are rejected.

Optional: `--limit N`, `--ids term_01,long_01`, `--temperature 0`.

One-shot helper (fail-closed if serve down; does not start GPU):

```bash
./scripts/measure_layer_b_v3.sh
# For a remote Spark, create an SSH forward first; the runner remains loopback-only:
# ssh -N -L 8000:127.0.0.1:8000 <spark-host>
# OPENAI_BASE_URL=http://127.0.0.1:8000/v1 ./scripts/measure_layer_b_v3.sh
```

Offline judge dry-run (no server): load `agent_smoke.judge` against synthetic tool_calls (see receipt).

Static result browser (local file drop): [`../smoke_viewer.html`](../smoke_viewer.html).

## Protocol honesty

**one-response protocol** — tool JSON shape / multi-turn repair are **validated**, tools are **not executed**.
Smoke temperature for claim runs: **0.0** (never 0.7 card/default for tools).

Judges already support: `tool_call`, `any_of_tools`, `any_ok_tools`, `no_extra_tools`, `content_contains` + `sanitize_messages_for_server` for broken prior args.

## Claims rule

- Freeze / launch lock quotes **only** locked historical v2 `results/hermes_agent_smoke.json` at catalog SHA `3275a4a570007fa8f948764a6873e055dc5a4a5ff257a1edc8bc342a02a8ddfc`.
- Hardened v4 and current Layer B have no measured score yet; neither a smoke nor a bench receipt sets `release_green` or `gate_clearance`.
- Do not rewrite `launch_lock.json` hermes fields from a v3 run.
- Historical format/routing receipt remains agent_smoke **40/40**; path safety is not proven.
- Pass fraction on the card only with a real run artifact.

## Layer B intent

Expand regression coverage for multi-turn-shaped and long-horizon-shaped prompts **without** touching weights or Aug 3 freeze claims.
Retrain / full agentic SFT stays **parked** (separate post-freeze decision).
