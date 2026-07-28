# Laguna Spark HF launch lock — 2026-08-03

Status: **LOCKED**  
Owner: personal (hizrianraz)  
Repo: https://huggingface.co/hizrianraz/laguna-s-2.1-spark  
Timezone: Asia/Jakarta (WIB)

## Freeze window

| When | Action |
|------|--------|
| Now → Aug 2 18:00 WIB | Build + measure only |
| Aug 2 18:00 WIB | Content freeze (no new claims without re-measure) |
| Aug 3 09:00 WIB | Preflight |
| Aug 3 12:00 WIB | **GO LIVE** (card + announce ready state) |
| Aug 3 18:00 WIB | Post-launch verify + brief |

## Launch definition of done (all required)

1. HF model public: `hizrianraz/laguna-s-2.1-spark`
2. Card shows fixed scoreboard row for Spark + official Q4_K_M
3. Official digests in `SHA256SUMS` match LFS metadata
4. Stranger path works: pull official Q4 → serve → smoke
5. Measured artifacts on HF (not only local): `results/measured.json`, `server_bench.json`, `agent_smoke.json` (+ receipt)
6. agent_smoke headline honest:
   - Min ship: **≥38/40 (95%)**
   - **Current measured: 40/40 (100%)** · 88.96s live reconfirm 2026-07-28 ~19:20 WIB (prior lock 97.25s)
7. Gen throughput quote: ~21 tok/s @ 128 completion (or fresher re-measure)
8. Clear disclaimer: personal · not first quant · not Poolside/Nous affiliate
9. No DIY GGUF unless it beats a scoreboard cell (default: **bind official only**)
10. Launch receipt JSON written + card updated same day

## Non-goals (hard)

- Org / company product branding on this surface
- Re-hosting official GGUF without measured win
- Side-quest models under this tag
- Fake 100% smoke or unverified tok/s
- X/public brand push beyond HF card

## Daily clock (WIB)

| Day | Date | Theme | Exit gate |
|-----|------|-------|-----------|
| T-6 | Jul 28 | Lock + HF gap close | measured JSON on HF, launch file live |
| T-5 | Jul 29 | Smoke harden | **DONE early Jul 28** — repair_04+long_06 closed; smoke **40/40** |
| T-4 | Jul 30 | DFlash / serve sweep | one scoreboard row with DFlash status final for launch |
| T-3 | Jul 31 | Card polish | stranger path re-run dry; REPRODUCE exact |
| T-2 | Aug 1 | Buffer / second measure | optional Unsloth abort/keep only if free |
| T-1 | Aug 2 | Freeze 18:00 | final push; no claim changes after freeze |
| T-0 | Aug 3 | Launch 12:00 | go-live receipt; 18:00 verify brief |

## Contingency

Smoke gate clear: **40/40 measured**. Hold that bar through freeze; if a later re-run slips, ship last green with named fails (never invent).  

If Spark down at launch: freeze last green MEASURED row; do not invent numbers.  
If HF token dies: restore the personal Hugging Face write token from the local secret store only; never paste token in chat.

## Announce text (draft — edits OK)

> Personal DGX Spark agent-runtime pack for Poolside Laguna-S-2.1: measured OpenAI-compatible serve, fixed agent smoke, official Q4_K_M digests (no bare re-upload).  
> https://huggingface.co/hizrianraz/laguna-s-2.1-spark

## Authority

Personal founder surface only. Docs/results may be pushed to this HF repo.  
No company vault binding for this pack.

## Quant compare + smaller-device path

- Scoreboard: `research/quant-comparison-scoreboard-2026-07-28.md`
- Mac/PC/laptop path: `research/post-freeze-smaller-device-path.md`
- Rule: no DIY/smaller SKU until official Q4_K_M bar holds post-launch.

## Hermes-class smoke v2

- Suite path: `eval/hermes_agent_smoke/` (27 cases; ship_min 24)
- Does **not** replace launch bar `agent_smoke` 40/40
- Card may list the suite; claim pass rate only after `results/hermes_agent_smoke.json` from live Spark
- **Public promo** (X / social / “top trending” push): still wait until **2026-08-03 12:00 WIB**

## Promo timing (lock)

| Surface | When |
|---------|------|
| HF pack docs + measured artifacts | now → freeze (keep honest) |
| Soft profile link (GH bio / HF details) | optional now, factual only |
| Public launch / announce / trending push | **Aug 3 12:00 WIB**, not before |
