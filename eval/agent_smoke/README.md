# agent_smoke v2 (future regression suite)

Personal fixed tool-agent smoke for Laguna OpenAI-compatible serve on **Spark**.

- **Historical format/routing bar:** **40/40** at measured tip `bf82eab`
- Cases: **40** · current cases version 2; historical `bf82eab` receipt version 1
- Protocol: **one-response** — tool JSON / multi-turn repair are **validated**, tools are **not executed**
- Claim temperature: **0.0**

## Measured (post-restore lock)

| Field | Value |
|-------|--------|
| Result | **40/40 (100%)** |
| Elapsed | **84.86 s** |
| Model | `local-laguna` |
| Temp | **0.0** |
| When | 2026-07-29 13:22 WIB |
| Artifact | [`results/agent_smoke.json`](../../results/agent_smoke.json) |

See also [`MEASURED.md`](../../results/MEASURED.md). Receipts include a `run_manifest` block (host, runner SHA, cases SHA, pack git HEAD).

The historical receipt is preserved byte-for-byte. Its `long_04` row chose the
correct `list_dir` tool but supplied `path=/`; the measured runner did not enforce
that argument value and did not fail an otherwise correct response solely for
additional tool calls. Therefore 40/40 means tool format/routing only, not path
safety. The current cases and scorer reject unsafe arguments and extra calls for
future runs. No re-smoke or retroactive score rewrite is implied.

## Run

```bash
# assumed local Spark Q4 serve with --jinja, alias local-laguna
export OPENAI_API_KEY="$LAGUNA_API_KEY"
/usr/bin/python3 -I -S eval/agent_smoke/run_smoke.py \
  --base-url http://127.0.0.1:8000/v1 \
  --model local-laguna
```

The default is a new UTC-dated receipt. Existing files, symlinked output paths,
and the locked historical authority filenames are rejected.

Optional: `--limit N`, `--ids repair_04,long_06`.

## Claims rule

Do not overwrite the historical `results/agent_smoke.json` authority. A future
score is claimable only from its own dated/current receipt on the same host + quant.
Do **not** transfer numbers to XS / Mac.
