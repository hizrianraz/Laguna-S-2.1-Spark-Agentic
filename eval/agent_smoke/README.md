# agent_smoke v1 (launch bar)

Personal fixed tool-agent smoke for Laguna OpenAI-compatible serve on **Spark**.

- **Headline ship bar:** **40/40**
- Cases: **40** · version 1
- Protocol: **one-response** — tool JSON / multi-turn repair are **validated**, tools are **not executed**
- Claim temperature: **0.0**

## Measured (post-restore lock)

| Field | Value |
|-------|--------|
| Result | **40/40 (100%)** |
| Elapsed | **97.79 s** |
| Model | `local-laguna` |
| Temp | **0.0** |
| When | 2026-07-28 ~23:55 WIB |
| Artifact | [`results/agent_smoke.json`](../../results/agent_smoke.json) |

See also [`MEASURED.md`](../../results/MEASURED.md). Receipts include a `run_manifest` block (host, runner SHA, cases SHA, pack git HEAD).

## Run

```bash
# assumed local Spark Q4 serve with --jinja, alias local-laguna
python eval/agent_smoke/run_smoke.py \
  --base-url http://127.0.0.1:8000/v1 \
  --model local-laguna \
  --out results/agent_smoke.json
```

Optional: `--limit N`, `--ids repair_04,long_06`.

## Claims rule

Pass fraction on the card only with a real `results/agent_smoke.json` from this host + quant.
Do **not** transfer numbers to XS / Mac.
