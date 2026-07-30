# Evidence inventory

Evidence is scope-bound. A historical pass never proves a newer source tree or a
broader claim.

| File | Scope |
|---|---|
| `measured.json` | Historical July 29 multi-bench record at measure tip `bf82eab` |
| `server_bench.json` | Historical latency/generation samples; not a soak or concurrency study |
| `agent_smoke.json` | Historical 40/40 format/routing regression only; path safety not proven |
| `hermes_agent_smoke.json` | Historical 27/27 tools validated, not executed |
| `launch_lock.json` | Current self-authority freeze-candidate posture |
| `RELEASE_MANIFEST.json` | Current claim and release boundary |
| `hf_publish.json` | Time-scoped Hub observation only |
| `launch_receipt_aug3.json` | Expected target-host receipt; absent until a qualifying launch writes it |

`scripts/_stamp_accel_receipts.py` is now a read-only historical validator. It
checks locked artifact, runner, cases, row, and suite bindings; it cannot stamp,
rewrite, or transfer the old 40/40 and 27/27 scores to current source.

The current hardened v2 source has not been re-smoked. Until the source path
gates are independently audited and a target-host receipt exists,
`path_safety_proven=false` and `verified_runnable_day0=false`.
