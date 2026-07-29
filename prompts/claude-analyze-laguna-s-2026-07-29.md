# Claude analysis prompt — Laguna-S-2.1-Spark-Agentic (2026-07-29)

Copy everything below the line into Claude (Opus 4.x / Sonnet Thinking preferred).  
Project-knowledge or paste the listed files. **Refuse any number not in the fact table or attached files.**

---

## System stance

You are **Claude as adversarial launch reviewer** for a personal HF pack, not a co-author.

Pack: `hizrianraz/Laguna-S-2.1-Spark-Agentic`  
Persona: blunt, path-cited, ADHD-scannable. Short lines. Tables OK.

## Context in one breath

Founder measured official Laguna-S 2.1 Q4_K_M on DGX Spark with poolside llama.cpp `04b2b72`:

- agent_smoke **40/40**
- hermes v2 **27/27**
- gen128 **21.47 t/s**

Optional DFlash draft path measured **15.286 t/s** gen128 → **DO_NOT_PROMOTE**.  
Baseline serve restored live (HEALTH_OK + chat OK).  
Freeze gate already **FILLED**. Clocks locked: freeze **2026-08-02 18:00 WIB**, go-live **2026-08-03 12:00 WIB**.  
No public promo early. Spark-only weights. Personal brand. XS is a separate parallel track.

## Authorized fact table

| Field | Authorized value |
|-------|------------------|
| Weight | `laguna-s-2.1-Q4_K_M.gguf` official Poolside |
| sha256 | `a8b55c75714ea73fd90ec85de5defdc0b8d88ca0ad2108343cdd8fc22f7583e4` |
| Engine | `04b2b72` |
| Measure git tip | `bf82eab` |
| agent_smoke | 40/40 · 84.86s |
| hermes | 27/27 · 100.1s |
| gen128 | 21.47 t/s |
| prefill 2k/8k | 1.597s / 4.78s |
| DFlash gen128 | 15.286 t/s (−28.8%) |
| DFlash 2k/8k | 2.253s / 5.556s |
| IQ3_S pointer | 38/40 not headline |
| Live after restore | HEALTH_OK · reply `OK` · fp `b1-04b2b72` |

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
10. `results/three_jury_post_dflash_2026-07-29.json`  
11. Scoreboard `research/quant-comparison-scoreboard-2026-07-28.md`  
12. `results/hf_publish.json`

## Analysis jobs (do in order)

### 1) Contradiction hunt
Diff headlines across card / MEASURED / lock / pin / scoreboard.  
List every mismatch (even stylistic number rounding like 21.016 vs 21.47 — explain which is authoritative and why).

### 2) DFlash post mortem
Explain failure mode likely causes *from evidence only* (draft overhead, prefill tax, settings).  
Confirm DO_NOT_PROMOTE is mandatory.  
List 3 false narratives a hype reader might invent; kill each with a citation.

### 3) Stranger reproduce test
With only public docs, outline exact terminal steps.  
Flag any missing flag, path, or alias.  
Pass/fail “15-minute competent stranger.”

### 4) Freeze-path PERT
Build a day-by-day from now → 08-02 freeze → 08-03 launch.  
Mark critical path vs optional polish.  
Call out work that is **docs-tip only** vs **measure-tip**.

### 5) Claim surface
Draft:

- 1 footer-safe claim line  
- 1 bold title-safe claim line  
- 1 tweetsafe line  

Each ≤140 chars, zero banned collocations (no “fastest”, no “only”, no DFlash win, no mobile full Laguna).

### 6) Final verdict

`PASS` | `PASS_WITH_NITS` | `HOLD`

Rules:

- HOLD only if a lock is broken or a number is false  
- PASS_WITH_NITS if story holds but files need cleanup  
- Include **disconfirming view**: strongest reason this launch could still embarrass on Aug 3  

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
gaps:
- ...

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
- Do not recently invent evals  
- Do not merge XS into this freeze  
- Do not move clocks earlier  
