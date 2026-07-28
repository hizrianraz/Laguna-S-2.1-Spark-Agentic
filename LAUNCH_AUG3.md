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
   - Target: **≥38/40 (95%)** minimum ship
   - Stretch: **40/40** if fixed before freeze
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
| T-5 | Jul 29 | Smoke harden | repair_04 + long_06 diagnosed; fix or documented wontfix |
| T-4 | Jul 30 | DFlash / serve sweep | one scoreboard row with DFlash status final for launch |
| T-3 | Jul 31 | Card polish | stranger path re-run dry; REPRODUCE exact |
| T-2 | Aug 1 | Buffer / second measure | optional Unsloth abort/keep only if free |
| T-1 | Aug 2 | Freeze 18:00 | final push; no claim changes after freeze |
| T-0 | Aug 3 | Launch 12:00 | go-live receipt; 18:00 verify brief |

## Contingency

If smoke cannot reach 40/40 by freeze: ship **38/40 with named fails**.  
If Spark down at launch: freeze last green MEASURED row; do not invent numbers.  
If HF token dies: restore the personal Hugging Face write token from the local secret store only; never paste token in chat.

## Announce text (draft — edits OK)

> Personal DGX Spark agent-runtime pack for Poolside Laguna-S-2.1: measured OpenAI-compatible serve, fixed agent smoke, official Q4_K_M digests (no bare re-upload).  
> https://huggingface.co/hizrianraz/laguna-s-2.1-spark

## Authority

Personal founder surface only. Docs/results may be pushed to this HF repo.  
No company vault binding for this pack.
