# Laguna S measure-tip KEEP — 2026-07-30

**Decision: KEEP bind · no re-smoke this turn**

## Why keep

- Measure tip locked: pack `bf82eab` · smoke **40/40** · hermes **27/27** · gen128 **~21.47 t/s**
- Q4 sha256 `a8b55c75714ea73fd90ec85de5defdc0b8d88ca0ad2108343cdd8fc22f7583e4`
- engine `poolsideai/llama.cpp 04b2b72`
- Current WT tip `b82d33d` is docs/jury only — measure tip sticks until fresh Spark smoke on tip runner
- **Live residency now proven** (ssh 2026-07-30T18:26:06+07:00): :8000 `local-laguna`, Q4 sha match

## Policy

- smoke ≠ headline
- docs tip may move; measure tip does not tighten without new dated smoke
- `public_promo_before_launch=false`

## Next for re-smoke (optional pre-freeze)

1. Laguna Q4 already live on :8000
2. Run agent+hermes smoke vs tip runner **or** pin runner sha from bf82eab
3. Dated receipts only then move measure_tip

## Receipts

- `results/LAUNCH_LOCK.json`
- `../results/SPARK_RESIDENCY_PROBE_LIVE_2026-07-30.json`
