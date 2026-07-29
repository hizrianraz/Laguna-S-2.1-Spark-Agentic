# Laguna Spark HF launch lock — 2026-08-03

Status: **LOCKED** · measure tip + model card + lock set filled `2026-07-29T14:43:26+07:00`  
Repo: https://huggingface.co/hizrianraz/Laguna-S-2.1-Spark-Agentic  
Timezone: WIB (UTC+7)

**Dual launch:** co-ships with `Qwen3-Coder-Next-Spark-Agentic` at the same go-live.  
This pack remains the **sole flagship measured** claim (40/40). Qwen uses the same harness; no trade of S freeze quality.

## Freeze window

| When | Action |
|------|--------|
| Now → Aug 2 18:00 WIB | Build + measure only |
| Aug 2 18:00 WIB | Content freeze (no new claims without re-measure) |
| Aug 3 09:00 WIB | Preflight |
| Aug 3 12:00 WIB | **GO LIVE** (card + announce ready state) |
| Aug 3 18:00 WIB | Post-launch verify + brief |

## Launch definition of done (all required)

1. HF model public: `hizrianraz/Laguna-S-2.1-Spark-Agentic`
2. Card shows fixed scoreboard row for Spark + official Q4_K_M
3. Official digests in `SHA256SUMS` match LFS metadata
4. Stranger path works: pull official Q4 → serve → smoke
5. Measured artifacts on HF (not only local): `results/measured.json`, `server_bench.json`, `agent_smoke.json` (+ receipt)
6. agent_smoke headline honest:
   - Min ship: **≥38/40 (95%)**
   - **Current measured: 40/40 (100%)** · **84.86s** live tip 2026-07-29 13:22 WIB · pack `bf82eab`
7. Gen throughput quote (sole headline): **~21.47 tok/s** @ 128 completion from multi suite in `results/measured.json`
8. Clear disclaimer: independent · not first quant · not Poolside/Nous affiliate
9. No DIY GGUF unless it beats a scoreboard cell (default: **bind official only**)
10. Launch receipt JSON written + card updated same day
11. **Freeze gate filled:** model card + **S-only** locks (`results/freeze_gate_model_card_lock_set_2026-07-29.json`) — XS lock is parallel research, not S freeze set

## Live tip (binding until weights/runners change)

| Field | Value |
|-------|--------|
| Measure tip (provenance) | `bf82eab5fd6c1fb04e863f0c4b05b5658dec4aee` — docs tip may advance after |
| Engine | poolsideai/llama.cpp `04b2b72` |
| Quant | official Q4_K_M · sha256 `a8b55c75714ea73fd90ec85de5defdc0b8d88ca0ad2108343cdd8fc22f7583e4` |
| agent_smoke | **40/40** · 84.86s · runner `3bb81080…` |
| hermes v2 | **27/27** · 100.1s · runner `20c1e52a…` |
| gen128 quote | **21.47 t/s** (do not headline short single-shot or pre-smoke spikes) |
| Artifacts | `results/measured.json` · `MEASURED.md` · smokes |

Re-smoke only if weights, runners, or serve flags change. Fresh same-harness green may refresh elapsed without claim change.
## Non-goals (hard)

- Org / company product branding on this surface
- Re-hosting official GGUF without measured win
- Side-quest models under this tag
- Fake 100% smoke or unverified tok/s
- X/public brand push beyond HF card before launch
- Local S weights on Apple Silicon ≤32 GB class
- XS inside S freeze artifact

## Daily clock (WIB)

| Day | Date | Theme | Exit gate |
|-----|------|-------|-----------|
| T-6 | Jul 28 | Lock + HF gap close | measured JSON on HF, launch file live |
| T-5 | Jul 29 | Smoke harden + freeze-gate fill | **DONE** — 40/40 · 27/27 · card+locks filled |
| T-4 | Jul 30 | DFlash / serve sweep | **DONE early 2026-07-29** — DFlash **DO_NOT_PROMOTE** (15.286 vs ~21.5); baseline re-health HEALTH_OK; stranger dry PASS; scoreboard row live |
| T-3 | Jul 31 | Card polish | **DONE early 2026-07-29** — Layer B live **35/35** research receipt; stale “no live claim” wording cleared; freeze bars untouched |
| T-2 | Aug 1 | Buffer / second measure | optional Unsloth abort/keep only if free |
| T-1 | Aug 2 | Freeze 18:00 | final push; no claim changes after freeze |
| T-0 | Aug 3 | Launch 12:00 | go-live receipt; 18:00 verify brief |

## Contingency

Smoke gate clear: **40/40 measured** on tip `bf82eab`. Hold that bar through freeze; if a later re-run slips, ship last green with named fails (never invent).  

If Spark down at launch: freeze last green MEASURED row; do not invent numbers.  
If HF token dies: restore HF write token from local secret store only; never paste token in chat.

## Announce text (draft — edits OK)

> Independent DGX Spark agent-runtime pack for Poolside Laguna-S-2.1: measured OpenAI-compatible serve, fixed agent smoke **40/40**, Hermes-class **27/27**, ~21.5 t/s @128, official Q4_K_M digests (no bare re-upload).  
> https://huggingface.co/hizrianraz/Laguna-S-2.1-Spark-Agentic

## Authority

Independent pack surface. Docs/results may be pushed to this HF repo.

## Quant compare + smaller-device path (Aug 3 accelerated)

- Scoreboard: `research/quant-comparison-scoreboard-2026-07-28.md`
- Device matrix: `research/device-quant-matrix-aug3.md`
- Path notes: `research/post-freeze-smaller-device-path.md`
- Pull helper: `scripts/pull_sku.sh <sku_id>`
- Headline remains Spark **official Q4_K_M** measured row
- Smaller SKUs ship as **pointers + optional same-harness delta** — promote to scoreboard only at ≥ official−2
- Apple Silicon ≤32 GB: **client → Spark only** for full S; XS = parallel unmeasured track
- No bulk third-party LFS rehost; no public promo before Aug 3 12:00 WIB

## Hermes-class smoke v2

- Suite path: `eval/hermes_agent_smoke/` (27 cases; ship_min 24)
- Does **not** replace launch bar `agent_smoke` 40/40
- **Measured tip 2026-07-29: 27/27** in 100.1s · artifact `results/hermes_agent_smoke.json`
- Card lists **27/27 hermes_agent_smoke** alongside **40/40 agent_smoke**
- Layer B research (**35** = 27+8): live **35/35** · 137.56s · 2026-07-29 · receipt `eval/hermes_agent_smoke/layer_b_v3_live_receipt.json` — **not** a freeze-bar field
- **Public promo** (X / social / “top trending” push): still wait until **2026-08-03 12:00 WIB**

## Promo timing (lock)

| Surface | When |
|---------|------|
| HF pack docs + measured artifacts | now → freeze (keep honest) |
| Soft profile link (GH bio / HF details) | optional now, factual only |
| Public launch / announce / trending push | **Aug 3 12:00 WIB**, not before |
