# Deep research — agentic quant + Hermes fit + HF trending

Date: 2026-07-28 18:47 WIB  
Scope: personal `hizrianraz/Laguna-S-2.1-Spark-Agentic` pack only  
Locks: launch_lock `diy_gguf=false`, official Q4_K_M only, min smoke 38/40, freeze 2026-08-02 18:00 WIB, launch 2026-08-03 12:00 WIB

## Bottom line

1. **Power for agents is not “a wilder GGUF.”** On Laguna-S-2.1 the competitive edge that survives scrutiny is: **official Poolside Q4_K_M (signal path protected) + fixed Hermes-shaped smoke + Spark-measured serve recipe.** DIY re-quants lose the launch lock unless they beat official by ≥10% on smoke or tok/s with full method disclosure.
2. **To be the most useful *agentic* Laguna pack for Hermes-class runtimes:** harden tool-call JSON validity, multi-turn repair, long-horizon multi-tool loops, and publish a Hermes local wiring playbook. That beats shipping another who-cares Q4.
3. **HF “top 10 trending” globally is not a realistic target for a personal digests-only spark pack.** Base `poolside/Laguna-S-2.1` is already on live trending. Realistic win: **#1 personal Spark + Hermes-class Laguna pack**, and rank inside the **Laguna-S-2.1 GGUF/quant search cluster** (today Unsloth leads third-party GGUF at 222 likes / 130k dl). Absolute global top-10 needs mass org reach or a novel binary people pull (not our S5 surface).

## Live field (measured 2026-07-28)

### Our surface
| Asset | State |
|-------|--------|
| HF `hizrianraz/Laguna-S-2.1-Spark-Agentic` | **0 likes, 0 downloads**, public, created today |
| Stand-behind weight | official `laguna-s-2.1-Q4_K_M.gguf` sha `a8b55c75…` |
| agent_smoke v1 | **40/40 (100%)** · 97.25s (2026-07-28 19:00 WIB); prior 38/40 was harness not weights |
| Claim style | personal measurements · digests · no bare GGUF re-upload |

### Laguna cluster (likes-ranked sample)
| Likes | DL | Id | Role |
|------:|---:|----|------|
| 777 | 67k | poolside/Laguna-S-2.1 | base (trending) |
| 222 | 130k | unsloth/Laguna-S-2.1-GGUF | Dynamic third-party GGUF leader |
| 157 | 90k | poolside/Laguna-S-2.1-GGUF | **official GGUF (our pin)** |
| 150 | 181k | poolside/Laguna-S-2.1-NVFP4 | official NVFP4 |
| 18 | 1.8k | jcbtc/…StrixKVSpine-V4-GGUF | AMD agentic spine + HermesAgent-20 claim |
| 13–12 | ~1–28k | CRACK / APEX / IQ4 community | mix lore / entropy / IQ |

### Global trending reality check
Live trending head includes org giants (Kimi-K3 ~7.4k likes, Unlimited-OCR, GLM-5.2, Inkling…). A personal pack does **not** enter that headroom via card polish alone.

## What “most powerful for agentic / Hermes” actually means

### Layer A — Weight / quant (mostly already decided)
Official Poolside Q4_K_M recipe (from their GGUF card):
- Routed experts: **Q4_K with imatrix**
- Signal path (attention, shared experts, embeddings): kept **Q8_0** (not smashed)
- Ships `laguna-s-2.1.imatrix` + recommended **llama-server --jinja**
- Optional DFlash draft for speculative decoding
- Context: GGUF metadata 256K recommended; 1M YaRN override available with quality caveats

Unsloth Dynamic 2.0 preaching:
- Selective layer precision; strong on Aider Polyglot / KL / MMLU-style anchors
- Actively patches **tool-calling chat templates** on newer models
- Wins downloads by **shipping many sizes** + brand distribution — not by Hermes-specific agent loops

Community agentic spine (Chadrock ROCmFP4 example):
- **Tensor protection** of expert-down “spine” + attention Q/O paths
- Claims on retained benches: Tool-Eval disputed-19 **70.18% vs 54.39%** baseline; **HermesAgent-20 77/100 vs 71**
- Hardware-specific (Strix Halo / ROCm). Not our Spark default; useful as **bench framing competitor**, not as standing weight.

Paper wake (agent inference, not GGUF fashion):
- Agentic loads ≠ chat: long prefixes, multi-turn tool trajectories, structured roles
- Sensitivity axes: temporal recency, modality, semantic role (user / tool / observation / reason)
- Research push is heavily **KV-cache / multi-agent cache pool / 4-bit KV** (TriAxialKV, PolyKV, UltraQuant, PLENA) and small-edge function calling (TinyAgent) — i.e. **serve + cache + schema**, not another random Q3.

**Implication for us under lock:** do **not** DIY-quant before freeze unless official fails load or loses ≥10% agent_smoke / tg. Power gain before Aug 3 is almost entirely **Layer B+C**.

### Layer B — Protocol fitness (Hermes-class)
Hermes Agent is toolset-heavy: terminal, files, web, browser, memory, cron, computer-use, delegation. It speaks OpenAI-compatible `chat.completions` + `tools` / `tool_calls`.

What kills agent quality under quant/runtime:
1. **Invalid tool-arg JSON** (our `repair_04` — server HTTP 500 parse error)
2. **Invented tool names** outside schema
3. **Dropped multi-tool / long-horizon** planning
4. Chat-template / `--jinja` mismatch → prose instead of structured calls
5. Temp/sampling too hot for tool routes
6. Runner / response-shape fragility (our `long_06` KeyError `'tool'`)

Own smoke categories already map to Hermes stress:
- `tool_select` / `args` / `multi_tool`
- `error_repair` (schema repair after bad args)
- `no_invented_tools`
- `long_horizon` multi-step
- `refuse` safety on tools

Gap vs Chadrock claim surface:
- No public **HermesAgent-20** or broader Tool-Eval disputed set in our pack
- No multi-turn tool→observation→tool loop scored end-to-end beyond single-response smoke
- No published tok/s @ agent-typical ctx (8k–32k) with tools attached

### Layer C — Runtime / Spark
Documented high-leverage stack:
- Engine: poolside `llama.cpp` branch `laguna` (+ isfinite patch as measured)
- Flags: `--jinja`, sensible ctx (8k agent day-to-day; 256k only when needed)
- Optional: DFlash draft GG UF if VRAM headroom
- Sampling for tools: temp 0–0.2 agent smoke; poolside long-ctx tip temp 0.7 top_p 0.95 only when exploring 1M rope
- Client: OpenAI base_url **must include `/v1`**, User-Agent set, strict tool schema, never execute unknown names

### Layer D — Distribution (HF trending mechanics)
Observed patterns that move Laguna quants:
1. **Binary people can pull** (Unsloth/official GGUF) → raw DL gravity
2. **Parent model already trending** → child repos ride search / “Tree” clicks
3. **Specific hardware story** (Strix Halo, Spark, MLX) with **tables + sha + repro**
4. **Named agent benches** (Tool-Eval, HermesAgent-20, Aider) with deltas
5. **Active discussions / collections / Spaces / blog cross-posts** within 24–72h of publish
6. Tags: `gguf`, `text-generation`, `base_model` relation, `license`, concrete hardware tags

Our S5 constraint: **digests + method, no 90GB re-host.** That lowers DL ceiling. Trending must come from:
- **Utility density of the card** (copy-paste Spark + Hermes path)
- **Cross-link from X / Reddit / Discord / HF discussions on parent + Unsloth threads**
- **Unique measured residue** no one else has (Spark GB10 numbers + Hermes-class smoke JSON)
- Optional later: Space that hits our public endpoint or notebooks that pull official weight via `huggingface_hub` (no repack)

## Honest competitive strategy

### Win condition A (recommended) — “best Hermes-class Laguna on Spark”
Measurable:
- agent_smoke ≥ **39/40**, stretch **40/40**
- New `hermes_agent_smoke` v2: 20–40 cases shaped like Hermes toolsets (terminal, read_file, web_search stubs, multi-turn repair)
- Card #1 section: **Hermes-class local wiring** (config keys, tool loop, failure matrix)
- Scoreboard row only from `results/*` files
- Secondary row: unlabeled comparison notes vs Unsloth UD-Q4 *if* re-measured on same harness (optional, post-freeze if time)

### Win condition B — “cluster top-10 Laguna quants by attention”
After launch fungal growth:
- Be in likes/DL top of *personal* third-party Laguna packs (today Chadrock 18 / CRACK 13 are the bar)
- Collection: “Laguna local agents”
- Reply with evidence on poolside + Unsloth Discussion spikes day-of

### Win condition C — global HF trending top-10
**Reject as primary KPI.** Requires org blast radius or weight host. Use only as aspirational side-effect if Poolside wave + a viral Spark clip align.

## Quant decision tree (locked)

```
Need new GGUF?
├─ Official Q4 loads on Spark and smoke ≥38/40 → NO. Ship digests + recipe.
├─ Official fails load or smoke/tg ≥10% worse vs alternative you can prove → YES DIY,
│    only with: method + imatrix commit + full sha256 + both smokes + REPRODUCE.md upgrade
└─ “Looking unique for HF” alone → NO (violates diy_gguf lock + integrity)
```

If DIY ever unlocks (post-launch research track):
1. Start from **official F16 or poolside imatrix**, not reverse Unsloth
2. Protect signal path ≥ Q8_0 (match first-party philosophy)
3. Build **agentic imatrix corpus**: tool-call transcripts, JSON schemas, multi-turn tool results, code+shell traces — not only wiki text
4. Candidate mixtypes: Q5_K_M (quality), IQ4_XS only if Spark memory forced; never hero a boutique name without harness delta
5. Run same agent_smoke + hermes_agent_smoke before any public claim

## Hermes-specific integration map

| Hermes need | Laguna pack lever |
|-------------|-------------------|
| OpenAI tools | llama-server `--jinja` + OpenAI `/v1` |
| Many tools / tool search | smoke with 8–20 schemas; stress no_invented |
| Terminal + files loop | multi-turn cases with tool role messages |
| Reliability under repair | close `repair_04`; add 2nd-order repair cases |
| Config discoverability | document `OPENAI_BASE_URL`, model id echo, timeouts |
| Skills / long sessions | measure kv/cache behavior @ 8k+; document ctx defaults |
| Honest branding | “Hermes-class / tool-agent compatible” — **not** Nous endorsement |

Sample client already at `hermes/sample_client.py` + `hermes/README.md`. Expand with:
- multi-turn repair demo
- hermes `config.yaml` snippet pointing at Spark
- failure→fix matrix from MEASURED.md

## Trending launch playbook (Aug 2 freeze → Aug 3 12:00 WIB)

### Pre-freeze (done or do)
- [x] Public scrub · positive only · personal framing
- [x] Diagnose + fix `repair_04` / `long_06` (harness; not weights)
- [x] Re-run smoke → **40/40**; MEASURED + measured.json from live files only
- [x] Add `research/` brief (this file)
- [ ] short public “Why official Q4 for agents” section on card
- [ ] Hermes wiring page on card (copy-paste)
- [ ] Tags + base_model relation clean
- [ ] SHA pins + engine sha frozen

### Launch hour
1. Meaningful card revisiontimestamp (mod time spike)
2. Short announcement paths founder owns (not Manwë codename): personal X after rename gate lifts; HF Discussion on **parent** Laguna-S-2.1 and Unsloth GGUF pointing to Spark measurements
3. Cross-link GitHub mirror ↔ HF
4. One clear hero metric: **40/40 agent_smoke on DGX Spark · official Q4_K_M · Hermes-class client**
5. Do **not** claim vs Chadrock HermesAgent-20 until we run the same harness

### 48h after
- Answer every HF comment with evidence
- Optional: Space “agent smoke viewer” (JSON render) — low cost engagement
- Watch Unsloth/Poolside threads for template bugs; patch docs same day

## Gap closure backlog (priority)

### P0 — quality residual
1. ~~`repair_04`~~ — **closed:** case poison `{not-json` in history → server HTTP 500; Hermes client sanitizes prior tool args (keeps `_raw` for judge)
2. ~~`long_06`~~ — **closed:** judge accepts `type: tool_call` + `any_of_tools` (no KeyError)
3. ~~Re-smoke~~ — **40/40 · 97.25s · 2026-07-28 19:00 WIB**; official Q4 only

### P1 — Hermes power
4. `eval/hermes_agent_smoke/` 20 cases (names only inspired by tool categories; no Hermes trademark claim)
5. Multi-turn tool observation tests
6. Card section + config snippet for Hermes local provider
7. Optional: side-measure Unsloth UD-Q4_K_XL on same harness (label third-party)

### P2 — attention
8. Launch-day parent discussions + collection
9. Spark chalkboard clip / blog (personal)
10. Space JSON explorer

### P3 — post-launch research (not launch blocker)
11. Agentic imatrix corpus design
12. Ablate Q5_K_M / spine-protect only if P0 saturation and DIY gate opens
13. DFlash speculative path on Spark if measured tok/s gain on agent loops

## What not to do
- Re-upload 68–96GB GGUF bare (S5 + lock)
- Invent smoke scores or competitor beats
- Claim Nous / Hermes endorsement
- Chase IQ3 “flex” that tanks tool JSON
- Spend freeze window on new quant fashion while 2 fails remain
- Promise global top-10 trending as a committed milestone

## Sources (live pulls)
- poolside/Laguna-S-2.1 + Laguna-S-2.1-GGUF model cards (official Q4 recipe, imatrix, DFlash, jinja)
- unsloth/Laguna-S-2.1-GGUF + Unsloth Dynamic 2.0 docs (template fixes, dynamic layer precision)
- jcbtc Chadrock ROCmFP4 card (HermesAgent-20 / Tool-Eval narrative)
- HF trending API + models search likes sort (2026-07-28)
- Local pack: README, SPARK, LAUNCH_AUG3, REPRODUCE, results/MEASURED, agent_smoke.json, launch_lock.json
- arXiv signals: TinyAgent (2409.00608), agent memory walls (2509.09505), TriAxialKV (2605.17170), PolyKV (2604.24971), UltraQuant (2606.20474)

## Verdict for founder intent

| Intent | Verdict |
|--------|---------|
| Most powerful **agentic** quantized Laguna *we* stand behind | **Official Q4_K_M + tighten agent/Hermes harness + Spark recipe** |
| Most powerful **DIY boutique quant** | Blocked by lock; only if measured ≥10% barrier |
| Top-10 **Laguna pack cluster** attention | Achievable with evidence card + launch distribution |
| Top-10 **global HF trending** | Not a primary commit; side-effect only |

Next single move: **P0 close the two smoke fails and wire Hermes multi-turn sample — not a new quant.**
