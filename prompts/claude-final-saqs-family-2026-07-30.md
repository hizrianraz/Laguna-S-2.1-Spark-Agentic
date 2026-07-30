# FINAL external review — SAQS family — Claude seat (adversarial)
# Date: 2026-07-30 · Built: 2026-07-30T18:43:40+07:00
# Seat: adversarial proof · lock frets · stranger-serve failure hunt
# Partner seat: ChatGPT (product/claim) — separate prompt
# Mode: READ-ONLY. Return structured verdict. Do not soften.

---

## Mandate

You are the **hostile senior eng**. Assume the founder will paste your output next to ChatGPT's. Your job is to find **false numbers, lock breaches, and Aug-3 embarrassment modes** before freeze **2026-08-02 18:00 WIB**.

Default stance: **innocent until measured**. Only Laguna is measured. Qwen is probe. DeepSeek is scaffold.

---

## Immutable clocks

- Freeze **2026-08-02 18:00 WIB**
- List **2026-08-03 12:00 WIB** (all three cards)
- Laguna hero **2026-08-03 20:00**
- Qwen hero **2026-08-04 20:00** iff :8001 re-measure else **stay preview**
- DeepSeek **NO_HERO** (explicit freeze flip required)

---

## Locks (any breach → HOLD)

1. promo_pre / public_promo_before_launch = **false**
2. diy_gguf = **false**
3. smoke ≠ headline
4. verifier ≠ gate clearance
5. prep delivery ≠ freeze ≠ ship
6. DeepSeek NO_HERO + HOLD closed + no TYPE40 until release
7. ports 8000/8001/8002 isolation
8. DFlash DO_NOT_PROMOTE dual-gen headline
9. personal brand only
10. DSpark ≠ DGX Spark naming honesty
11. REAP25 labeled experimental · never "official DeepSeek on one Spark"
12. Founder gate-ask accept ≠ freeze clearance

---

## Accepted gate asks (founder 2026-07-30T18:43:40+07:00) — still not freeze

LAG-G1 KEEP `bf82eab` no re-smoke · LAG-G2 docs committed · LAG-G3 HF align at freeze  
QW-G1 preview list · QW-G2 remeasure-or-stay-preview · QW-G3 FP8 only  
DS-G1 NO_HERO · DS-G2 tip pushed · DS-G3 HOLD closed · DS-G4 explicit HERO only

---

## Forced numbers (treat as claims to verify consistency — do not invent extras)

### Laguna (flagship measured)

- Measure tip **bf82eab** (`bf82eab5fd6c1fb04e863f0c4b05b5658dec4aee`)
- Docs tip **a3ddac4** (receipts only; measure authority stays bf82eab)
- Smoke **40/40** · Hermes **27/27** · **~21.47 tok/s** gen128
- Q4 sha `a8b55c75714ea73fd90ec85de5defdc0b8d88ca0ad2108343cdd8fc22f7583e4`
- Live :8000 `local-laguna` sha **match** @ 2026-07-30T18:26:06+07:00
- engine poolsideai/llama.cpp `04b2b72`
- ship_min 38/40 · stretch 40/40

### Qwen (probe)

- Docs tip **a1ef94c**
- FP8 40/40 · ~80.4e9 bytes · resident · :8001 **off**
- agent_smoke probe **2/2** · ship_claim_allowed **false** · posture `preview_unverified`
- primary vLLM FP8 · tool_call_parser `qwen3_coder`

### DeepSeek REAP25 (NO_HERO)

- Docs tip **5214261** pushed main
- TYPE40 **absent** · :8002 off · HOLD closed
- ~85 GiB if ever · dual_download_default false
- status `scaffolding_hold_colist_unmeasured`

### Host

- free ≈ 1.1T · residency PROVEN_PARTIAL

---

## Attack surface checklist (you must touch each)

1. **Number drift** — lock vs MEASURED.md vs live sha vs tip KEEP  
2. **Claim leakage** — README/card/footer that upgrades smoke→SOTA or probe→ship  
3. **Naming lies** — DSpark, REAP25, official DeepSeek, Poolside wrap, Ainfera  
4. **Collection UX** — three equal heroes illusion  
5. **Serve stranger path** — clone → pull → serve flags → first tool call (Laguna)  
6. **Dual-gen** — any residual DFlash win narrative  
7. **Qwen mem** — dual-warm refused; hero-day single-port story coherent?  
8. **DeepSeek perishable honesty** — co-list with absent weights  
9. **Promo footguns** — anything that wants traffic before list floor  
10. **Freeze day** — dirty WT, HF lag, lock_set rehash gaps

---

## Required analysis blocks

### 1) Authoritative numbers table
Build a table of every public-facing number and its single authority path. Mark conflicts.

### 2) Contradictions
List real contradictions only. `NONE` if clean.

### 3) DFlash
- decision must be `DO_NOT_PROMOTE` unless you find new measure forcing reopen (you will not)
- kill false narratives in ≤5 bullets

### 4) Stranger path (Laguna Q4)
Pass/fail serve flags + gaps only.

### 5) Dual gen
Authoritative = 21.47 · band mentions only if evidenced · safe_for_stranger?

### 6) Claim surface
Draft three lines ≤140 chars:
- footer-safe
- title-safe
- tweet-safe  

Banned: fastest / only / DFlash win / full mobile / dual gen two headlines / IQ3 main / DeepSeek ready / Qwen ship / SOTA from smoke

### 7) Freeze schedule table
| Day | Must | Optional | Forbidden |

Cover 07-31 → 08-03 at minimum.

### 8) Verdict
`PASS` | `PASS_WITH_NITS` | `HOLD`

Rules:
- HOLD only if lock broken or number false
- PASS_WITH_NITS if story holds but files need cleanup
- Always include **disconfirming view**

---

## Output skeleton (mandatory)

```
## Verdict
PASS | PASS_WITH_NITS | HOLD

## Authoritative numbers
| claim | value | authority path | ok? |

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
safe_for_stranger: yes|no

## Qwen probe
preview_safe: yes|no
leak_paths:
- ...

## DeepSeek NO_HERO
colist_safe: yes|no
killed_claims:
- ...

## Residency
status: PROVEN_PARTIAL
ship_gate: no
notes:
- ...

## Freeze schedule
| Day | Must | Optional | Forbidden |

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
- Do not suggest HOLD_RELEASE / TYPE40 pull  
- Do not invent evals or re-smoke Laguna KEEP  
- Do not merge XS into this freeze  
- Do not move clocks earlier  
- Do not require public jury JSON on HF  
- Do not re-open DFlash ship path without new measure  
- Do not equalize three packs as measured  
- Do not treat founder gate-accept as freeze clearance  

Be shorter than you want. Cite paths. Prefer HOLD over cosplay optimism.
