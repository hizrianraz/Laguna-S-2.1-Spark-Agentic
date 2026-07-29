# Dual roadmap — Laguna S (Spark) + Laguna XS (Mac)

Prepared 2026-07-28. Personal founder tracks only.  
Two roadmaps. One is never a rename of the other.

## North star split

| | **Roadmap A — S / Spark** | **Roadmap B — XS / Mac** |
|--|---------------------------|-------------------------|
| Model | Laguna-**S**-2.1 · 118B-A8B | Laguna-**XS**-2.1 · 33B-A3B |
| Host | **DGX Spark only** (weights) | Founder Mac ≤32G (weights candidate) |
| Default SKU | official S Q4_K_M ~96G | official XS Q4_K_M ~18.9G |
| Measured bar today | 40/40 + hermes 27/27 · ~21 t/s | **none** (disk evidence only) |
| Pack / freeze | `hizrianraz/Laguna-S-2.1-Spark-Agentic` · freeze Aug 2 18:00 · launch Aug 3 12:00 WIB | research parallel; optional later `laguna-xs-*` surface |
| Founder Mac role for S | **client → Spark :8000** | n/a |
| Coupling | — | **must not** delay or dilute A |

## Roadmap A — S / Spark (stand-behind)

### Done
- Official Q4 bind + sha256
- agent_smoke 40/40 · hermes v2 27/27 on Spark
- weight_host lock: `dgx-spark-only`
- founder_mac lock: `client-only-no-local-weights` for full S
- IQ3_S pointer 38/40 (not headline)
- Launch lock + personal HF surface

### To freeze (2026-08-02 18:00)
1. Clean tree + pushed tip for any final STAMP
2. README / MEASURED / matrix honest; no Mac-S weight claim
3. Client path smoke from Mac → Spark documented
4. No DIY GGUF unless measured win
5. No public promo before Aug 3 12:00

### Non-goals A
- Local full-S weights on ≤32G Mac
- Rebrand S as XS
- Community quants as founder headline

### Kill / hold A
- Dirty WT for “final”
- Conflicting jury on host honesty
- Loss of Q4 restore after alt smoke

## Roadmap B — XS / Mac (parallel research)

### Prepared (this session)
- Live HF probe: base sha `205dc65…` · GGUF sha `1a37c0…`
- Q4_K_M sha256 `1ac7079101fca5a6df8c5a7523a3c30ea7d1c0e4b1258090e7d6d4039287f6cb` · 18.882 GiB
- BF16 non-fit (62.3 GiB) pinned
- Host: Studio 32G live vs vendor “36G” gap noted
- Engine: poolside laguna fork / PR #25165 risk
- Locks: `results/xs_mac_track_lock.json`
- Notes: `research/Laguna-XS-2.1-Mac-Agentic-fit-2026-07-28.md`
- Matrix row + definition table updated

### Ordered next (founder-gated each step)
1. **Jury GO** on prepared XS path + dual roadmap (this consult)
2. **Founder go** to pull Q4 only → prefer WD_BLACK  
   ` /Volumes/HFR WD_BLACK SN850X/models/laguna-xs-2.1 `  
   (System Data ~40 Gi free — soft; external has room)
3. Build/verify Metal llama on laguna fork (or prove Ollama path)
4. Load proof: RSS + free RAM + ctx
5. Same-harness `eval/agent_smoke` → `results/sku_xs-official-q4km/`
6. Optional hermes-class 27
7. Fail list + delta vs **not** S headline (separate table)
8. Founder go before any public/HF claim sentence

### Non-goals B
- Pull BF16 on Mac
- DIY re-quant before official fails a real gate
- Phone/tablet from XS
- Any claim that XS results are S results
- Couping B dates into A freeze

### Kill criteria B
- Cannot load under 32G with usable ctx after OS+Hermes
- Engine cannot run XS without endless fork chase past freeze bandwidth
- Smoke << research bar and no learnable delta
- Disk pressure threatens S freeze work → **park B**

## Shared honesty rules

1. Name the model family every time: **S** or **XS**
2. Disk size ≠ runtime fit ≠ agent smoke
3. Poolside public benches ≠ founder hermes harness
4. Always restore S Q4 on Spark after any alt experiment
5. Analysis / jury ≠ ship clearance

## Artifact map

| Artifact | Roadmap |
|----------|---------|
| `results/launch_lock.json` | A |
| `results/MEASURED.md` · smoke JSON | A |
| `results/xs_mac_track_lock.json` | B |
| `research/Laguna-XS-2.1-Mac-Agentic-fit-2026-07-28.md` | B |
| `research/device-quant-matrix-aug3.md` | A+B (labeled rows) |
| `research/post-freeze-smaller-device-path.md` | A + community; B pointer |
| `research/roadmap-dual-s-and-xs-2026-07-28.md` | A+B (this file) |
| `prompts/*-dual-roadmap-*.md` | external analysis of both |

## One-line each

- **A:** Ship honest Spark S pack Aug 3; Mac is client.
- **B:** Prove whether official XS Q4 actually works on founder 32G Mac — separate surface, after pull+smoke, no story theft from A.
