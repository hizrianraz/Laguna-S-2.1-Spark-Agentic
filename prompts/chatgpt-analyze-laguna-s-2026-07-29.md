# ChatGPT analysis prompt — Laguna-S-2.1-Spark-Agentic (post jury-fix rev2)

Copy everything below the line into ChatGPT (o3 / GPT-5 Thinking preferred).  
Paste listed file bodies as attachments or follow-ups. **Do not invent numbers.**

---

## Role

You are an independent technical auditor for a **personal** Hugging Face model pack:

`hizrianraz/Laguna-S-2.1-Spark-Agentic`

Not Ainfera company IP. Spark-only full weights. Founder: Hizrian Raz.

## Mission

Audit freeze/launch readiness **after**:

1. Optional DFlash (draft speculative) experiment → **DO_NOT_PROMOTE**
2. Internal three-jury rev1 **not-go** on real gaps
3. Fix-pass closed those gaps → three-jury rev2 **GO · PASS_CONTINUE_PREP**

Return hard judgments. No cheerleading.

## Hard facts (only these numbers are authorized)

| Item | Value |
|------|-------|
| Headline quant | official Poolside `laguna-s-2.1-Q4_K_M.gguf` |
| Q4 sha256 | `a8b55c75714ea73fd90ec85de5defdc0b8d88ca0ad2108343cdd8fc22f7583e4` |
| Host | DGX Spark GB10 |
| Engine | poolsideai/llama.cpp `04b2b72` |
| Serve captain | `-c 8192 -ngl -1 --jinja -fa on --alias local-laguna` |
| agent_smoke | **40/40** · 84.86s · temp 0.0 |
| hermes_agent_smoke v2 | **27/27** · 100.1s |
| gen128 (authoritative) | **21.47 tok/s** — quote this only as headline |
| gen128 (band sample) | 21.016 tok/s — **not** a second headline |
| Prefill in multi suite | 2k **1.597s** · 8k **4.78s** |
| Prefill band sample | 2k 1.022s · 8k 1.521s (earlier same-day; not dual claim) |
| Measure tip (smoke/weights) | git `bf82eab` — must not be confused with later docs tip |
| Docs GH tip at prompt | `9fb227b` (moves with docs; not measure tip) |
| HF docs tip at prompt | `57aa785` (docs-only; weights untouched) |
| DFlash gen128 | **15.286 tok/s** (−28.8% vs 21.47) · **DO_NOT_PROMOTE** |
| DFlash prefill | 2k 2.253s · 8k 5.556s (worse than baseline) |
| IQ3 pointer (not headline) | Unsloth UD-IQ3_S **38/40** |
| Freeze clock | **2026-08-02 18:00 WIB** |
| Public go-live | **2026-08-03 12:00 WIB** |
| Freeze gate | **FILLED** 2026-07-29 (model card + lock set) |
| Live baseline after DFlash teardown | HEALTH_OK · captain flags match last-green |
| diy_gguf | false |
| weight host | Spark-only |
| founder Mac | client-only, no local S weights |
| XS pack | parallel track, **not** inside S freeze |
| branding | personal-only |
| public promo before launch | **false** |
| Jury JSON on HF | **intentionally absent** (local+GH only by pack gitignore) |
| Jury MD on HF | present — `results/three_jury_post_dflash_2026-07-29.md` |

## Gaps closed in rev2 (verify docs still hold)

1. SPARK default serve / DFlash example / llama-bench no longer show `-ngl 99`; captain is `-ngl -1`
2. Scoreboard must not present 21.016 as equal headline to 21.47
3. Stranger dry re-PASS after SPARK align
4. DFlash still DO_NOT_PROMOTE
5. Clocks unchanged

## Locks you must not break in recommendations

1. No freeze before 2026-08-02 18:00 WIB  
2. No public promo before 2026-08-03 12:00 WIB  
3. No claiming DFlash speedup  
4. No inventing higher tok/s or smoke scores  
5. No full Laguna mobile claims  
6. No mixing XS into S freeze artifact  
7. Docs tip may move; **measure tip stays bf82eab** until weights/smoke re-run  
8. Do not treat 21.016 as a second headline gen claim  
9. Do not require jury JSON on public HF (design)  

## Attachments to analyze (paste contents)

Primary:

1. `README.md` (model card)  
2. `LAUNCH_AUG3.md`  
3. `SPARK.md`  
4. `docs/REPRODUCE.md`  
5. `results/MEASURED.md` + `results/measured.json`  
6. `results/launch_lock.json`  
7. `results/LAST_GREEN_PIN.md`  
8. `results/dflash_2026-07-29/STATUS.md` + `measured.json`  
9. `results/baseline_rehealth_2026-07-29.md`  
10. `results/stranger_path_dry_2026-07-29.md`  
11. `research/quant-comparison-scoreboard-2026-07-28.md`  
12. `results/freeze_notes_2026-07-29.md`  
13. `results/freeze_gate_model_card_lock_set_2026-07-29.json`  
14. `results/three_jury_post_dflash_2026-07-29.md` (+ JSON if available from GH, not HF)  
15. `results/hf_publish.json`  

## Questions (answer all)

### A. Integrity
1. Any two docs contradict on gen128 / smoke / sha256 / engine / ngl?  
2. Is DFlash rejection scientifically fair (same host, weight, engine family)?  
3. Could a reader confuse docs tip with measure tip and allege regression?  
4. Is dual-gen (21.47 vs 21.016) now safe for a stranger reader?

### B. Ship story
5. Single tightest sentence for HF card opening after Aug 3?  
6. Which 5 phrases are **banned** (overclaim risk)?  
7. Is stranger-path documentation enough for a non-founder to reproduce headline serve (flags included)?

### C. Risk → freeze
8. Top 5 residual risks ranked by freeze-day severity.  
9. What must be true on clean pushed HEAD at freeze (checklist).  
10. Anything that looks “done” but is only claimed?

### D. Competitive honesty
11. Versus Poolside/Unsloth/Bartowski GGUFs: real wedge vs vanity?  
12. Should IQ3 appear above or below the fold?

### E. Decision
13. Verdict: **SHIP_AS_PLANNED** / **SHIP_WITH_NITS** / **SLIP_FREEZE** — pick one.  
14. If NITS: max 5 bullets with exact file paths to fix before 08-02.  
15. If SLIP: what evidence failed and minimum fix.  
16. **Disconfirming view:** strongest reason Aug 3 still embarrasses.

## Output format (strict)

```
VERDICT: ...
ONE_LINE_STORY: ...
BANNED_PHRASES:
- ...
CONTRADICTIONS:
- ... or NONE
DUAL_GEN_SAFE: yes|no + why
STRANGER_SERVE_FLAGS: pass|fail + note
RISKS_TOP5:
1. ...
FREEZE_CHECKLIST:
- [ ] ...
NITS:
- path: ...
DISCONFIRMING_VIEW: ...
CONFIDENCE: high|med|low + why
```

No marketing. No new benchmarks. Cite paths.
