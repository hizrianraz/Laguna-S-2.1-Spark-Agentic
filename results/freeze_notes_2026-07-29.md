# Freeze notes — 2026-07-29 (post-restore lock)

WIB night lock after Q4 restore + dual smoke reconfirm.

## Headline (unchanged identity)

| Field | Value |
|-------|--------|
| Stand-behind quant | **official Poolside Q4_K_M** |
| Host | DGX Spark GB10 only (full S weights) |
| agent_smoke | **40/40** · 97.79 s · temp **0.0** · ~23:55 WIB |
| hermes_agent_smoke | **27/27** · 104.4 s · temp **0.0** · ~23:57 WIB |
| Protocol | **one-response** (tools validated, not executed) |
| Mac ≤32G | **client → Spark** · no local full-S weights |
| Always | restore Q4 after any alt SKU |

## Provenance (receipts)

- `results/agent_smoke.json` + `run_manifest` (runner SHA, cases SHA, host)
- `results/hermes_agent_smoke.json` + `run_manifest`
- `results/measured.json` · `results/MEASURED.md`
- `results/hf_publish.json` refreshed (measurement lock; no weight re-upload this tick)

## Tooling closed this night

- `scripts/pull_official_gguf.sh` — fail-closed sha256 vs pack `SHA256SUMS`
- Smoke runners — fail-closed checksums paths + `run_manifest` block
- `.gitignore` — sku local dumps not auto-public; whitelist MEASURED + locks

## IQ3 pointer honesty

Unsloth UD-IQ3_S **38/40** on **older runner** (no sanitize / any_of_tools) · **not** headline · **not** founder-Mac claim · **not** Q4 runner-identical.

## XS (sibling)

Parallel pack `laguna-xs-2.1-mac` · disk candidate only · **0 Mac smoke** · must not dilute S freeze.

## Not claimed tonight

- DFlash
- HF weight re-upload
- New public freeze package beyond clean main tip + receipts
- XS load-fit or ship authority
