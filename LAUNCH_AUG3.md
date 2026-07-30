# Laguna Spark — Aug 3 freeze candidate

- Authority scope: `Laguna-S-2.1-Spark-Agentic` only
- Candidate status: `READY_FOR_FREEZE_REVIEW`
- Clock status: `BLOCKED_until_2026-08-02_freeze_attestation`
- Historical measured path: true
- Audited static source path gates complete: true
- Path safety proven: false
- Verified runnable day 0: false
- Launch clearance: false
- Hero CTA: null

- Target listing: **2026-08-03 12:00 WIB**
- Content freeze: **2026-08-02 18:00 WIB**
- Earliest hero review: **2026-08-03 20:00 WIB**, only after freeze clearance
  and a valid target-host launch receipt.

This file does not authorize sibling releases, collection order, publication, or
promotion. Those decisions are external to this pack.

## Evidence boundary

The retained July 29 evidence belongs to historical measure tip
`bf82eab5fd6c1fb04e863f0c4b05b5658dec4aee`:

| Evidence | Historical result | Exact scope |
|---|---:|---|
| `agent_smoke` | 40/40 · 84.86 s | Format/routing regression only; path safety not proven |
| Hermes smoke v2 | 27/27 · 100.1 s | Tools validated, not executed |
| Generation | 21.47 tok/s | One short point: 67 prompt / 128 completion tokens |

The current hardened v2 source has **not** been re-smoked. Historical receipts
are preserved, but they do not establish current-source runnability, path safety,
long-horizon agent reliability, or launch clearance.

## Freeze requirements

- [x] Official Q4_K_M authority is immutable:
  `poolside/Laguna-S-2.1-GGUF@fc4e481289523cf7d0df668da6d1d391616141ca`.
- [x] Official artifact is bound to SHA-256
  `a8b55c75714ea73fd90ec85de5defdc0b8d88ca0ad2108343cdd8fc22f7583e4`
  and 96,031,829,760 bytes.
- [x] Historical receipts remain labeled by their original scope.
- [x] `hero_cta` remains null and public promotion is not authorized.
- [x] Complete and independently audit the current static source path gates.
  This source audit does not prove target-host path safety or runnability.
- [x] Confirm the canonical standard and release metadata on this source tree.
- [ ] Attest target-host quiescence and the single-model residency policy.
- [ ] Produce `results/launch_receipt_aug3.json` with the declared immutable
  Hub pack revision, launcher SHA-256
  `547ccf1f6f6cbae3fff15995ff4fecccbb876c3f6d5e015f6ab6a622ed9d4c2f`,
  target engine-binary digest, receipt schema `saqs.spark_launch_receipt/v3`,
  and a successful target preflight.
- [ ] Independently resolve that exact Hub revision, compare its
  `scripts/serve_spark.sh` SHA-256 with the receipt, and record the source-match
  review; the launcher deliberately sets `clears_freeze=false` in its receipt.
- [ ] Re-read the authorized remote head and file set after publication.

Until every unchecked item passes, `path_safety_proven=false`,
`verified_runnable_day0=false`, launch clearance remains false, and no hero or
trending campaign may begin.

## Target-host receipt boundary

The target receipt validates one target launch only after an independent source
match. The receipt cannot attest its own review and therefore does not clear the
freeze by itself. It does not rewrite the
historical July 29 scores or turn format/routing checks into tool-execution or
long-horizon-reliability evidence. A failed or contradictory newer run blocks
claim refresh until explained.

## Public wording if freeze clears

Use factual wording only: this is an independent DGX Spark deployment/evaluation
pack for the official Poolside Q4_K_M artifact. If historical numbers are shown,
label 40/40 as format/routing-only, 27/27 as tools-validated-not-executed, and
21.47 tok/s as a single short-generation point. Do not call the pack best,
winner, fully agentic, path-safe, or long-horizon-proven.
