# Three-jury consult — post-DFlash (2026-07-29) · rev2 fix-pass

**Packet:** `three_jury_post_dflash_2026-07-29`  
**Mode:** Manwë three-seat appellate · fix-if-not-go  
**Measure tip:** `bf82eab` · **Engine:** `04b2b72` · **Weight:** official Q4_K_M  
**Live Spark:** HEALTH_OK · flags match last-green (`-ngl -1` · jinja · fa on · alias local-laguna)

## Bottom line

**GO · PASS_CONTINUE_PREP**

Named jury gaps from rev1 are fixed in-tree this tick:

1. SPARK default serve / DFlash / llama-bench: `-ngl 99` → **`-ngl -1`**
2. Scoreboard [dual gen] closed: **~21.47** authoritative · 21.016 band-only
3. Stranger dry re-verified **PASS**
4. DFlash remains **DO_NOT_PROMOTE**
5. Ship clock still **2026-08-03 12:00 WIB** · freeze **2026-08-02 18:00 WIB**

Not freeze day. No claim expansion.

## Seats

### Fable5 — measure
- **PASS**
- 15.286 < ~21.5 forces DO_NOT_PROMOTE
- Baseline re-health HEALTH_OK after DFlash teardown
- Dual gen claim closed in scoreboard
- Caveat kept: no full 40/40 re-smoke on post-rename tip this window (measure remains tip-bound `bf82eab`)

### Sol5.6 — serve
- **PASS**
- Live captain = last-green flags (probed)
- SPARK stranger serve blocks now match captain
- DFlash off default path
- XS HF pending_open is OK (S can ship alone)

### Composer2.5 — pack/claims
- **PASS**
- Forbidden claims listed
- Stranger dry PASS after SPARK fix
- HF must re-tip after this commit (docs-only) — in next unblocked

## Lórien chair
Not re-queued this tick (prior timeout ≠ fail). Appellate stands.

## External
- ChatGPT: `prompts/chatgpt-analyze-laguna-s-2026-07-29.md`
- Claude: `prompts/claude-analyze-laguna-s-2026-07-29.md`  
Founder paste → return findings become extra seats.

## Allowed claims
- Spark agent_smoke **40/40** official Q4_K_M
- hermes **27/27**
- ~**21.5** t/s gen128 plain Q4 Spark (authoritative multi suite 21.47)
- official digest-bound Q4 (no bare re-upload)

## Forbidden
- DFlash speedup
- first/only Laguna quant
- best universal tok/s
- full Laguna phone
- IQ3 headline
- global HF top-10

## Next
1. Commit + push GH tip (this fix)
2. HF docs-only tip (SPARK + scoreboard + jury + stranger)
3. Run external prompts when ready
4. Optional T-3 polish only if external opens a real gap
