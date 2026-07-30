# External seat — claude_cowork — 2026-07-29 evening WIB

**Seat:** claude_cowork (external adversarial)
**Evidence:** live HF + GH tips (no Spark/Mac disk runs this seat)

## Live verify (Manwë 2026-07-29 17:15 WIB)

| Surface | Finding |
|---|---|
| HF XS README | CONFIRMED S card: title Laguna-S-2.1-Spark-Agentic, base_model poolside/Laguna-S-2.1, tag measured, dgx-spark tags |
| HF XS launch_lock.json | CONFIRMED S lock: event Laguna-S-2.1-Spark-Agentic-hf-launch, measured_smoke 40/40 · 97.25s |
| HF XS API tags | base_model:quantized:poolside/Laguna-S-2.1 · measured · laguna-s-2.1 |
| HF XS sha / lastModified | 48773f8f… · 2026-07-29T06:55:47Z (=13:55:47 WIB) |
| GH XS tip 29e4b48 | HONEST: base Laguna-XS-2.1, tag unmeasured, B-track lock |
| HF S | OK at 57aa785 · measured S card |

## Verdicts (seat)

- **S:** PASS_WITH_NITS — numbers receipt-backed; cleanup nits; no lock break in S tree
- **XS:** HOLD_PREP until HF card+lock swap; then PREP_NITS

## Critical fix (executed / in flight)

Docs-only HF re-upload of XS `README.md` + `results/launch_lock.json` from GH tip (patched optional_future_surface).

## Ranked nits after bleed (S)

1. XS HF bleed (P0) — this fix
2. sha256sum -c 3-col trip (P0 stranger)
3. HF hf_publish.json stale on S
4. LAST_GREEN_PIN dead multi_throughput.json pointer
5. SPARK.md Jul-28 quote-21 table
6. freeze_gate hashes re-stamp at Aug 2
7. dflash tidy + drop LAUNCH 22.50 parenthetical

Full seat paste: external channel 2026-07-29 (claude_cowork dual pack).
