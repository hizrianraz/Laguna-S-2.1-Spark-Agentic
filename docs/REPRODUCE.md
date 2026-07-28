# Reproducible method — Laguna-S-2.1 Spark pack

Personal reproducible method.

## Pins (card freeze)

| Item | Value |
|------|--------|
| Base model | `poolside/Laguna-S-2.1` |
| Base revision | `00af5a51782109b587a3b3bbf11875e566036fa7` |
| Official GGUF repo | `poolside/Laguna-S-2.1-GGUF` |
| GGUF revision | `fc4e481289523cf7d0df668da6d1d391616141ca` |
| Default weight | `laguna-s-2.1-Q4_K_M.gguf` |
| Q4_K_M sha256 | `a8b55c75714ea73fd90ec85de5defdc0b8d88ca0ad2108343cdd8fc22f7583e4` |
| Engine | `github.com/poolsideai/llama.cpp` branch `laguna` |
| Hardware | DGX Spark GB10 only |

## Steps

1. Read OpenMDW-1.1 on the base model card/LICENSE. Accept constraints before redistribute.
2. Build engine per `SPARK.md` (CUDA `121` → `121a`, `llama-server`).
3. Record `git rev-parse HEAD` of the engine tree into `results/engine_sha.txt`.
4. Download official GGUF (not a DIY re-quant unless you will measure a real delta):

```bash
huggingface-cli download poolside/Laguna-S-2.1-GGUF \
  laguna-s-2.1-Q4_K_M.gguf \
  --revision fc4e481289523cf7d0df668da6d1d391616141ca \
  --local-dir ~/models/laguna-s-2.1
sha256sum -c SHA256SUMS
```

5. Serve (`SPARK.md`), confirm `curl /v1/models` → 200.
6. `llama-bench` @ prompt 2048 and 8192; save stdout to `results/llama_bench_q4km.txt`.
7. `python scripts/bench_server.py --ctx-mark 2k --ctx-mark 8k`.
8. `python eval/agent_smoke/run_smoke.py --out results/smoke_q4km.json`.
8b. Optional Hermes-class: `python eval/hermes_agent_smoke/run_hermes_smoke.py --out results/hermes_agent_smoke.json`.
9. Populate the tables in `SPARK.md` from those files only — never invent.
10. Publish pack (docs + results + scripts). **Host GGUF binary only if you have a measured unique artifact**; otherwise ship digests + download commands (S5).

## Personal HF publish surface

- User: `hizrianraz` (personal)
- Repo id: `hizrianraz/laguna-s-2.1-spark`
- Card framing: personal measurements only; no org product claims

## DIY quant policy

Only if:

1. Official/Unsloth GGUF cannot load or is >10% worse on agent_smoke pass rate or tg tok/s at same ctx, **and**
2. You publish method + imatrix/source commit + full sha256 + smoke numbers

Otherwise: official GGUF + Spark delta docs only.
