# Laguna-XS-2.1 · founder Mac ≤32G fit track

Status: **prepared research** (2026-07-28).  
Awaiting three-jury on prepared pack, then founder gates.  
**Not** the Aug 3 S pack headline. **Not** a measured ship claim.

Personal founder track only. Dual roadmap → [`roadmap-dual-s-and-xs-2026-07-28.md`](./roadmap-dual-s-and-xs-2026-07-28.md)

## Bottom line

| Track | Model | Host | Status |
|-------|--------|------|--------|
| **A · stand-behind** | Laguna-**S**-2.1 ~118B MoE Q4_K_M | **DGX Spark only** | measured 40/40 + hermes 27/27 |
| **B · Mac local candidate** | Laguna-**XS**-2.1 33B-A3B Q4_K_M | founder Mac ≤32G | **disk candidate** · **0 local smoke** |

Full **S** stays Spark-only. Mac is **not** “S via XS”.

## Live HF probe (2026-07-28)

### Base
- `poolside/Laguna-XS-2.1`
- sha: `205dc65dd4bda946c50da6b7522b215734fa107b`
- Shape (card): **33B total · 3B active/token · MoE**
- Poolside claim: “compact enough to run on a Mac with **36 GB** of RAM”
- Founder Studio coin: **32G** exactly (`hw.memsize` 34359738368) → **tighter than vendor 36G**

### Official GGUF
- `poolside/Laguna-XS-2.1-GGUF` sha `1a37c0a5fb8c7a18e6106decb6be6327d1b63fa6`

| File | Bytes | GiB | sha256 | Founder Mac ≤32G |
|------|------:|----:|--------|------------------|
| `Laguna-XS-2.1-Q4_K_M.gguf` | 20274300032 | **18.882** | `1ac7079101fca5a6df8c5a7523a3c30ea7d1c0e4b1258090e7d6d4039287f6cb` | **disk candidate** (runtime unproven) |
| `Laguna-XS-2.1-BF16.gguf` | 66930226304 | **62.334** | `d1d99abe30c37749ec1b1ae2681cec74caa550ac6243d2ea70b61b1ff9d187ca` | **non-fit** |

Upstream recommended default: **Q4_K_M**.

Safetensors base ~14 shards ≈ **~67G** class — non-fit on ≤32G.

### Engine dependency
- llama.cpp Laguna support: PR `ggml-org/llama.cpp#25165`
- Prefer `poolsideai/llama.cpp` branch `laguna` on Mac Metal — **do not assume stock brew llama runs XS**
- Ollama (`ollama pull laguna-xs-2.1`) = alt route until smoke

## Founder Mac envelope (Studio live)

| Fact | Value |
|------|-------|
| Model | Mac14,13 · M2 Max |
| RAM | **32G** exactly |
| System Data free (prep) | ~40 Gi · 91% used — **prefer WD_BLACK for pull** |
| WD_BLACK free | ~1.7 Ti |
| Full S Q4 | ~96G · **non-fit** |
| Full S IQ3_S pointer | ~48G · **non-fit** as local weight |
| XS Q4_K_M | ~18.9G disk · **candidate** |

Runtime RAM ≫ disk. Leave OS + browser + Hermes + KV headroom.  
**Disk-fit ≠ load-fit ≠ agent-smoke-fit.**

## Prep lock

`results/xs_mac_track_lock.json` — status `prepared_research`

## Honesty rules

**Say**
- “XS Q4_K_M is the official ~19G Mac-class GGUF for Laguna-**XS**-2.1”
- “Founder Mac client still talks to Spark for full **S**”
- “XS is a **separate** 33B-A3B model, not a quant of S”

**Do not say**
- “Laguna runs on Mac” without naming **XS**
- “S on Mac via XS”, “S-lite”, “S-Mac”
- Any t/s, agent_smoke, or Hermes pass for XS until same-harness JSON
- Poolside SWE-bench / Terminal-Bench as founder measured bar
- BF16 / safetensors base as Mac-local

## Measurement gate (before any claim)

1. Working engine on founder Mac · record commit
2. `sha256` matches lock after download
3. Load proof: RSS + free RAM after load · ctx used
4. Same `eval/agent_smoke` 40 (or named subset + disclaimer)
5. Optional hermes-class 27
6. Host labeled **Mac Studio 32G** (never as Spark)
7. Fail list + separate delta table (not diluted into S headline)
8. Founder go before any public/pack claim move

Results dir when measured: `results/sku_xs-official-q4km/`

## Suggested first pull (NOT run — needs founder go)

```bash
# ~19G → external SSD preferred
huggingface-cli download poolside/Laguna-XS-2.1-GGUF \
  Laguna-XS-2.1-Q4_K_M.gguf \
  --local-dir "/Volumes/HFR WD_BLACK SN850X/models/laguna-xs-2.1"
shasum -a 256 "/Volumes/HFR WD_BLACK SN850X/models/laguna-xs-2.1/Laguna-XS-2.1-Q4_K_M.gguf"
# expect 1ac7079101fca5a6df8c5a7523a3c30ea7d1c0e4b1258090e7d6d4039287f6cb
```

Do **not** pull BF16 on this Mac.

## Relation to Aug 3 S pack

| Item | Owner |
|------|--------|
| `hizrianraz/Laguna-S-2.1-Spark-Agentic` freeze/launch | **Roadmap A only** |
| XS Mac notes | this file + `xs_mac_track_lock.json` |
| multi_device_track | S community pointers; XS is **extra parallel** |
| XS may delay S freeze | **no** |
