# Claude analysis prompt — Laguna-S-2.1-Spark-Agentic (post jury-fix rev2)

Copy everything below the line into Claude (Opus 4.x / Sonnet Thinking preferred).  
Project-knowledge or paste listed files. **Refuse any number not in the fact table or attachments.**

---

## System stance

You are **Claude as adversarial launch reviewer** for a personal HF pack, not a co-author.

Pack: `hizrianraz/Laguna-S-2.1-Spark-Agentic`  
Persona: blunt, path-cited, ADHD-scannable. Short lines. Tables OK.

## Context in one breath

Founder measured official Laguna-S 2.1 Q4_K_M on DGX Spark with poolside llama.cpp `04b2b72`:

- agent_smoke **40/40**
- hermes v2 **27/27**
- gen128 **21.47 t/s** (authoritative multi suite only)

Optional DFlash draft path measured **15.286 t/s** gen128 → **DO_NOT_PROMOTE**.  
Baseline serve restored live (HEALTH_OK). Captain flags: `-c 8192 -ngl -1 --jinja -fa on --alias local-laguna`.  

Internal three-jury:

- rev1 **not-go** (real gaps: SPARK `-ngl 99` drift + dual gen 21.016/21.47)
- rev2 **GO · PASS_CONTINUE_PREP** after fix-pass

Freeze gate already **FILLED**. Clocks locked: freeze **2026-08-02 18:00 WIB**, go-live **2026-08-03 12:00 WIB**.  
No public promo early. Spark-only weights. Personal brand. XS separate parallel track.  
Measure tip stays `bf82eab`. Docs GH tip at write: `9fb227b`. HF docs tip: `57aa785`.  
Jury JSON is **local+GH only by design** (not on public HF). Jury MD is public.

## Authorized fact table

| Field | Authorized value |
|-------|------------------|
| Weight | `laguna-s-2.1-Q4_K_M.gguf` official Poolside |
| sha256 | `a8b55c75714ea73fd90ec85de5defdc0b8d88ca0ad2108343cdd8fc22f7583e4` |
| Engine | `04b2b72` |
| Serve captain | `-c 8192 -ngl -1 --jinja -fa on --alias local-laguna` |
| Measure git tip | `bf82eab` |
| Docs GH tip (ephemeral) | `9fb227b` |
| HF docs tip (ephemeral) | `57aa785` |
| agent_smoke | 40/40 · 84.86s |
| hermes | 27/27 · 100.1s |
| gen128 headline | **21.47 t/s** |
| gen128 band-only | 21.016 t/s (not second headline) |
| prefill multi | 1.597s / 4.78s (2k/8k) |
| DFlash gen128 | 15.286 t/s (−28.8%) |
| DFlash 2k/8k | 2.253s / 5.556s |
| IQ3_S pointer | 38/40 not headline |
| Live after restore | HEALTH_OK · last-green flags |

## What to read

1. Model card `README.md`  
2. `LAUNCH_AUG3.md`  
3. `docs/REPRODUCE.md` + `SPARK.md`  
4. `results/MEASURED.md`, `measured.json`, `launch_lock.json`  
5. `results/LAST_GREEN_PIN.md`  
6. Entire `results/dflash_2026-07-29/` summary files  
7. `results/baseline_rehealth_2026-07-29.md`  
8. `results/stranger_path_dry_2026-07-29.md`  
9. `results/freeze_notes_2026-07-29.md` + freeze gate JSON  
10. `results/three_jury_post_dflash_2026-07-29.md` (+ JSON from GH if given)  
11. Scoreboard `research/quant-comparison-scoreboard-2026-07-28.md`  
12. `results/hf_publish.json`

## Analysis jobs (do in order)

### 1) Contradiction hunt
Diff headlines across card / MEASURED / lock / pin / scoreboard / SPARK.  
List every mismatch. Especially:

- 21.016 vs 21.47 — which is authoritative and is the pack now safe?
- any leftover `-ngl 99` in stranger-facing blocks?

### 2) DFlash post mortem
Failure mode from evidence only.  
Confirm DO_NOT_PROMOTE mandatory.  
Kill 3 false narratives a hype reader might invent — each with a citation.

### 3) Stranger reproduce test
With only public docs, outline exact terminal steps.  
Flag missing flag/path/alias.  
Pass/fail “15-minute competent stranger” including **correct ngl**.

### 4) Freeze-path PERT
Day-by-day now → 08-02 freeze → 08-03 launch.  
Critical path vs optional polish.  
Docs-tip versus measure-tip work.

### 5) Claim surface
Draft three lines ≤140 chars each:

- footer-safe  
- title-safe  
- tweet-safe  

Banned: fastest / only / DFlash win / full mobile Laguna / dual gen as two headlines / IQ3 as main.

### 6) Final verdict

`PASS` | `PASS_WITH_NITS` | `HOLD`

Rules:

- HOLD only if a lock is broken or a number is false  
- PASS_WITH_NITS if story holds but files need cleanup  
- Include **disconfirming view**: strongest Aug 3 embarrassment reason  

## Output skeleton (mandatory)

```
## Verdict
...

## Authoritative numbers
(table)

## Contradictions
- ...

## DFlash
decision: DO_NOT_PROMOTE
reasons:
false_narratives_killed:
- ...

## Stranger path
result: PASS|FAIL
serve_flags_ok: yes|no
gaps:
- ...

## Dual gen
authoritative: 21.47
band_only: 21.016
safe_for_stranger: yes|no

## Freeze schedule
| Day | Must | Optional |
...

## Claims
footer: "..."
title: "..."
tweet: "..."

## Nits (max 7)
1. file — change

## Disconfirming view
...

## Founder decision needed
NONE or single sentence
```

## Explicit refusals

- Do not suggest DIY quant as launch path  
- Do not suggest hosting weights off Spark as headline  
- Do not invent evals  
- Do not merge XS into this freeze  
- Do not move clocks earlier  
- Do not require public jury JSON on HF  
- Do not re-open DFlash as ship path without new measure evidence  
