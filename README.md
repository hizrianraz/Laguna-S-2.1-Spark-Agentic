---
license: openmdw-1.1
license_name: openmdw-1.1
license_link: https://huggingface.co/poolside/Laguna-S-2.1/blob/00af5a51782109b587a3b3bbf11875e566036fa7/LICENSE.md
language:
  - en
tags:
  - deployment-pack
  - evaluation-pack
  - runtime-pack
  - laguna
  - laguna-s
  - laguna-s-2.1
  - poolside
  - moe
  - agentic-coding
  - coding
  - tool-use
  - function-calling
  - agents
  - dgx-spark
  - nvidia
  - cuda
  - llama.cpp
  - openai-compatible
  - measured
  - reproducible
  - not-a-model
---

# Laguna-S-2.1-Spark-Agentic

## Parameters

| | |
|--|--|
| **Total** | **~118B** (HF count 117.56B BF16) |
| **Active / token** | **~8B** |
| **Arch** | MoE · `LagunaForCausalLM` · 256 experts (top-10) + 1 shared |
| **Pinned measured deployment artifact** | Official Poolside **Q4_K_M** at `fc4e481289523cf7d0df668da6d1d391616141ca` · **96,031,829,760 bytes** (~96.0 GB / ~89.4 GiB) |
| **Measured serve context** | **8,192** tokens (the upstream maximum is not claimed here) |
| **Source** | [poolside/Laguna-S-2.1](https://huggingface.co/poolside/Laguna-S-2.1) |
| **This pack** | **runtime / evaluation pack only** — no weights here |

> HF native **Parameters** badge stays empty (no checkpoint in this repo) — size is the table above.
> No native **Model tree** edge is declared: Hugging Face relationship metadata does not have a deployment-pack relation.
> Full detail: [Model parameters](#model-parameters-upstream--not-this-pack).

**Measured DGX Spark deployment pack** for
[poolside/Laguna-S-2.1](https://huggingface.co/poolside/Laguna-S-2.1)
(118B total · ~8B active/token · MoE · agentic coding).

> This repository is a **runtime / evaluation pack**, not a model checkpoint and not a re-quant.
> Hugging Face may still list it under Models; treat it as a **runbook + harness + receipts**.

> **Freeze status:** `READY_FOR_FREEZE_REVIEW` source candidate, with clock
> `BLOCKED_until_2026-08-02_freeze_attestation`. The July 29 measured path is
> historical; the current hardened v2 source has not been re-smoked and is not
> verified `runnable_day0`. `path_safety_proven=false` until the audited source
> gates and a qualifying target-host receipt both pass.

> **Artifact identity:** the live Poolside `main` observed on 2026-07-31 still
> resolves to the measured `fc4e481…` revision. This pack nevertheless binds the
> exact 96,031,829,760-byte artifact and SHA-256 `a8b55c75…`; never replace that
> immutable identity with a moving branch. Any future upstream artifact change
> is a separate SKU and requires a new evidence run.

## Honesty / launch class

- **Pack:** `Laguna-S-2.1-Spark-Agentic`
- **Launch class:** historical format/routing smoke + local serve evidence; current source is a freeze candidate
- **Smoke ≠ headline:** agent_smoke validates tool-call *format/routing* on a live local endpoint. It is **not** a long-horizon reliability score, not a public leaderboard claim, and not gate clearance by itself.
- **Historical scorer boundary:** the locked `bf82eab` runner did not reject every extra tool call or the `long_04 path=/` argument. Hardened v2 does; v2 has not been re-smoked.
- **Verifier ≠ gate clearance:** a green smoke receipt is evidence of the smoke suite only.
- **diy_gguf:** false — the launch path uses the immutable official Poolside artifact.
- **Weights:** not in git. Pull scripts write outside the pack tree.
- **Loopback-only audited launcher:** `serve_spark.sh` accepts only `127.0.0.1` / `localhost` and rejects every direct remote bind. Remote access requires a separately audited SSH tunnel or TLS proxy; bearer auth alone is not transport encryption.
- **No public promo / campaign CTA:** `hero_cta` remains null until freeze
  attestation and a qualifying target-host launch receipt.
- **Smoke cases:** 40 (see `eval/agent_smoke/`).
- **Default port:** `8000`.
- **Engine:** `poolsideai/llama.cpp` at `04b2b72` (branch `laguna`).

## Positioning

**Unique contribution:** documenting how the **official** Poolside Q4_K_M behaved on a **single DGX Spark** under a pinned engine, fail-closed digest, fixed harness, and retained negative result (DFlash).

**Not coded as:** boutique quant producer, base-model trainer, or long-horizon agent reliability proof.

| | |
|--|--|
| **Role** | Historical measured deployment recipe; current-source freeze candidate |
| **Weights authority** | [poolside/Laguna-S-2.1-GGUF](https://huggingface.co/poolside/Laguna-S-2.1-GGUF) @ `fc4e481289523cf7d0df668da6d1d391616141ca` |
| **Optional mirror** | [hizrianraz/Laguna-S-2.1-GGUF](https://huggingface.co/hizrianraz/Laguna-S-2.1-GGUF) @ `510501dace2ff4e559644934a44c177ff8bd9f15` · byte-identical upstream · **not** re-quantized by this account |
| **Default quant** | Official Poolside `Q4_K_M` · 96,031,829,760 bytes (~89.4 GiB) |
| **Host** | NVIDIA DGX Spark (GB10) |
| **agent_smoke** | Historical `bf82eab`: **40/40** tool-format / routing **regression smoke** (see honesty section) |
| **Launch clock** | Target listing 2026-08-03 12:00 WIB · hero review no earlier than 20:00 WIB and only after freeze + target receipt · freeze 2026-08-02 18:00 WIB |
| **Affiliation** | Independent · not Poolside · not Nous Research |

Standard (SAQS): [`SPARK_AGENTIC_QUANT_STANDARD.md`](./SPARK_AGENTIC_QUANT_STANDARD.md)  
Launch calendar: [`LAUNCH_AUG3.md`](./LAUNCH_AUG3.md)

## Install the deployment pack

This is a real runtime pack, not a checkpoint. Set the immutable **final Hub
commit** supplied out-of-band by the release operator after an authorized
publication, download the canonical manifest, and
inspect `config.yaml` before running anything. A moving branch or dynamically
resolved latest tip is not accepted by this install path.

```bash
: "${LAGUNA_PACK_REV:?export the authorized 40-hex Hugging Face revision}"
[[ "$LAGUNA_PACK_REV" =~ ^[0-9a-f]{40}$ ]] || { echo "invalid pack revision" >&2; exit 2; }
printf 'pack_revision=%s\n' "$LAGUNA_PACK_REV"
hf download hizrianraz/Laguna-S-2.1-Spark-Agentic \
  config.yaml INSTALL.yaml SHA256SUMS LICENSE NOTICE SPARK.md docs/BUILD_SPARK.md \
  SPARK_AGENTIC_QUANT_STANDARD.md results/MEASURED.md results/launch_lock.json \
  results/engine_sha.txt \
  scripts/pull_official_gguf.sh scripts/serve_spark.sh \
  --revision "$LAGUNA_PACK_REV" \
  --local-dir laguna-spark-pack
cd laguna-spark-pack
chmod +x scripts/pull_official_gguf.sh scripts/serve_spark.sh
export LAGUNA_EXPECT_PACK_REVISION="$LAGUNA_PACK_REV"
export LAGUNA_EXPECT_LAUNCHER_SHA256="547ccf1f6f6cbae3fff15995ff4fecccbb876c3f6d5e015f6ab6a622ed9d4c2f"
printf '%s  %s\n' "$LAGUNA_EXPECT_LAUNCHER_SHA256" scripts/serve_spark.sh | sha256sum -c -

# The audited roots must preexist, be non-symlinked, current-user-owned, and
# not group/world writable. These exact roots are used by the default profile.
for trusted_root in "$HOME/src" "$HOME/models" "$HOME/.local/state"; do
  [[ ! -L "$trusted_root" ]] || { echo "symlinked root: $trusted_root" >&2; exit 2; }
  install -d -m 700 -- "$trusted_root"
done

# Required before pull/serve: install git, cmake, a GNU C/C++ toolchain,
# CUDA/nvidia-smi, curl, jq, Python 3, ldd/readlink, ss (or lsof), OpenSSL, and hf.
# Then build the exact engine revision + measured +<cmath>-only patch by
# following SPARK.md "Build" and docs/BUILD_SPARK.md. The strict launcher
# rejects a clean tree and alternative patch shapes.
export LAGUNA_ENGINE="$HOME/src/llama.cpp-laguna"
test -x "$LAGUNA_ENGINE/build/bin/llama-server"
./scripts/pull_official_gguf.sh

# Phase 1 is hash-only: it does not invoke ldd or execute llama-server.
engine_pin_output="$(LAGUNA_PRINT_RUNTIME_PINS=1 ./scripts/serve_spark.sh)"
printf '%s\n' "$engine_pin_output"
# Inspect/approve that binary hash against the reviewed target build before binding it.
export LAGUNA_EXPECT_ENGINE_SHA256="$(printf '%s\n' "$engine_pin_output" | awk -F= '$1=="LAGUNA_EXPECT_ENGINE_SHA256"{print $2}')"
[[ "$LAGUNA_EXPECT_ENGINE_SHA256" =~ ^[0-9a-f]{64}$ ]] || exit 2
unset engine_pin_output

# Phase 2 runs ldd only after the approved binary hash matches. Inspect the
# complete dependency manifest, then bind its digest for the final launch.
dso_pin_output="$(LAGUNA_PRINT_RUNTIME_PINS=2 ./scripts/serve_spark.sh)"
printf '%s\n' "$dso_pin_output"
export LAGUNA_EXPECT_DSO_MANIFEST_SHA256="$(printf '%s\n' "$dso_pin_output" | awk -F= '$1=="LAGUNA_EXPECT_DSO_MANIFEST_SHA256"{print $2}')"
[[ "$LAGUNA_EXPECT_DSO_MANIFEST_SHA256" =~ ^[0-9a-f]{64}$ ]] || exit 2
unset dso_pin_output

# Create the bearer only after both non-serving discovery phases are reviewed.
export LAGUNA_API_KEY="$(openssl rand -hex 32)"
export OPENAI_API_KEY="$LAGUNA_API_KEY"
./scripts/serve_spark.sh
```

`config.yaml` pins the official Poolside artifact revision, Q4 digest, measured
engine revision, secure serve defaults, and the historical `bf82eab` evidence authority.
`LAGUNA_PACK_REV` and the launcher digest must come from the release operator
after publication; this
candidate does not predict it. Do not substitute
`main`, a short hash, or a current-tip lookup. The strict serve writes a new
target-host launch receipt with the declared immutable pack revision and exact
launcher, engine-binary, and resolved dynamic-library digests. That receipt is
only a review candidate: an independent reviewer must compare its pack revision
and launcher digest with the authorized Hub commit before clearance. It does not
refresh the historical smoke or clear the freeze by itself.

---

## Download weights (authoritative = Poolside)

The launch path uses only the strict puller. It enforces the allowed root,
ownership, no-symlink/no-hardlink policy, host-local lock, exact bytes and
SHA-256, and atomic no-clobber publication:

```bash
./scripts/pull_official_gguf.sh

# Optional byte-identical mirror, only into a clean strict destination:
LAGUNA_ALLOW_ALTERNATE_SOURCE=1 \
LAGUNA_GGUF_REPO=hizrianraz/Laguna-S-2.1-GGUF \
LAGUNA_GGUF_REV=510501dace2ff4e559644934a44c177ff8bd9f15 \
  ./scripts/pull_official_gguf.sh
```

Do not substitute a direct `hf download --local-dir` in the launch workflow;
that bypasses the puller's filesystem and publication gates.
For a real mounted data volume, set `LAGUNA_ALLOWED_MODEL_ROOT` to its canonical,
non-symlinked model root and keep the exact `laguna-s-2.1/` child name.

This pack is **not** the bulk weight host. It publishes **serve pins, digests, and smoke harness**.

---

## Upstream relationship

```text
poolside/Laguna-S-2.1                 ← base (official)
├── poolside/Laguna-S-2.1-GGUF        ← official GGUF authority
├── hizrianraz/Laguna-S-2.1-GGUF      ← byte-identical mirror (not re-quant)
└── hizrianraz/Laguna-S-2.1-Spark-Agentic  ← this pack (runtime · measured)
```

The upstream model is linked in this card rather than declared through YAML
`base_model`, because Hub relationship metadata is reserved for checkpoint
relationships such as finetune, adapter, merge, and quantized. This pack is none
of those and hosts no weights. It also declares no `library_name: gguf` or
loadable inference pipeline.

---

## Model parameters (upstream · not this pack)

This repo hosts **no checkpoint weights**, so the HF native **Parameters** badge stays empty by design. Size = table above.
Sizes below are copied from the upstream base — not re-counted here.

| Field | Value | Source |
|-------|-------|--------|
| Architecture | MoE · `LagunaForCausalLM` | poolside config |
| Total parameters | **~118B** (HF safetensors count **117.56B** BF16) | [poolside/Laguna-S-2.1](https://huggingface.co/poolside/Laguna-S-2.1) |
| Activated / token | **~8B** | upstream card (118B-A8B) |
| Experts | 256 routed (top-10) + 1 shared | upstream card + config |
| Pack role | runtime / smoke harness only | this repo |

---

## Why this pack

1. Pinned Spark serve settings that clear tool-format smoke
2. Fixed harnesses you can re-run (no vibes)
3. Official digests for fail-closed verify
4. OpenAI-compatible client notes for tool-agent stacks
5. Negative results retained (DFlash slower — do not promote)

---

## Historical highlights (measured tip · 2026-07-29 13:22 WIB)

| Metric | Result |
|--------|--------|
| Host | NVIDIA DGX Spark (GB10) |
| Quant | Official `laguna-s-2.1-Q4_K_M.gguf` |
| Engine | `poolsideai/llama.cpp` @ `04b2b72` (branch `laguna`) |
| Serve context flag | `-c 8192` |
| agent_smoke | **40/40** · 84.86 s · temp 0.0 · **format/routing smoke** |
| hermes_agent_smoke v2 | **27/27** · 100.1 s · temp 0.0 · **one-response; tools validated not executed** |
| Generation throughput (sole short-gen headline) | **~21.47 tok/s** @ **128 completion** tokens (prompt 67) |
| Measure tip | pack `bf82eab` |

Artifacts:
[`results/MEASURED.md`](./results/MEASURED.md) ·
[`results/measured.json`](./results/measured.json) ·
[`results/agent_smoke.json`](./results/agent_smoke.json) ·
[`results/hermes_agent_smoke.json`](./results/hermes_agent_smoke.json)

---

## Honesty clock (read before quoting scores)

### What 40/40 and 27/27 are

Useful **tool-format and routing regression smokes** on a fixed case list.

Receipt language (hermes suite): **tools validated, not executed**.

### What they are not

- Not long-horizon agent reliability
- Not multi-turn tool-result continuation proof
- Not exact argument-value / schema-hard proof for every case
- Historical `long_04` called the correct tool with `path=/`; the retained bf82eab 40/40 score therefore does **not** prove path safety. Future cases reject that argument.
- Not SWE-bench / BFCL / Terminal-Bench substitutes

### Bench label correction (server_bench marks)

Recorded prefill marks were labeled **2k** / **8k** for convenience.
Actual prompt token counts on the receipt:

| Mark label | Actual `prompt_tokens` | Latency | Completion |
|------------|------------------------|---------|------------|
| `2k` | **836** | 1.597 s | 3 tokens ("OK") |
| `8k` | **3236** | 4.78 s | 3 tokens ("OK") |

Do **not** cite these as full 2K/8K filled-context prefill rates.

### Generation headline limits

- **~21.47 tok/s** is one short-gen point: **67 prompt / 128 completion** tokens
- Same-day suite also logged gen8 ~10.6 t/s and gen256 ~21.9 t/s
- Not a multi-seed soaked long-session figure; warm-rep / p50-p95 TTFT / peak RAM still to strengthen

External signal bar (future, not claimed): BFCL V4 · τ-bench · Terminal-Bench 2.

---

## Quick start

```bash
# 0) Precreate the exact audited roots; do not use symlinks/shared writable roots.
for trusted_root in "$HOME/src" "$HOME/models" "$HOME/.local/state"; do
  [[ ! -L "$trusted_root" ]] || { echo "symlinked root: $trusted_root" >&2; exit 2; }
  install -d -m 700 -- "$trusted_root"
done

# 1) Engine — pin the measured commit at the launcher's exact accepted child.
git clone https://github.com/poolsideai/llama.cpp "$HOME/src/llama.cpp-laguna"
cd "$HOME/src/llama.cpp-laguna"
git checkout --detach 04b2b72cb54048ead292884adbe11f284e3ec950
# Apply the exact +<cmath>-only patch in docs/BUILD_SPARK.md before building.
cmake -B build -G "Unix Makefiles" \
  -DCMAKE_BUILD_TYPE=Release \
  -DGGML_CUDA=ON \
  -DCMAKE_CUDA_ARCHITECTURES=121a \
  -DLLAMA_CURL=ON
cmake --build build -j --target llama-server llama-cli llama-bench

# 2) Weights — immutable upstream revision + atomic fail-closed verification
cd /path/to/this/pack
: "${LAGUNA_EXPECT_PACK_REVISION:?set the authorized 40-hex Hub commit}"
export LAGUNA_EXPECT_PACK_REVISION
export LAGUNA_EXPECT_LAUNCHER_SHA256="547ccf1f6f6cbae3fff15995ff4fecccbb876c3f6d5e015f6ab6a622ed9d4c2f"
printf '%s  %s\n' "$LAGUNA_EXPECT_LAUNCHER_SHA256" scripts/serve_spark.sh | sha256sum -c -
./scripts/pull_official_gguf.sh

# 3) Serve — two-phase target pins + one-model residency + auth + health
export LAGUNA_ENGINE="$HOME/src/llama.cpp-laguna"
engine_pin_output="$(LAGUNA_PRINT_RUNTIME_PINS=1 ./scripts/serve_spark.sh)"
printf '%s\n' "$engine_pin_output" # inspect before export
export LAGUNA_EXPECT_ENGINE_SHA256="$(printf '%s\n' "$engine_pin_output" | awk -F= '$1=="LAGUNA_EXPECT_ENGINE_SHA256"{print $2}')"
[[ "$LAGUNA_EXPECT_ENGINE_SHA256" =~ ^[0-9a-f]{64}$ ]] || exit 2
unset engine_pin_output
dso_pin_output="$(LAGUNA_PRINT_RUNTIME_PINS=2 ./scripts/serve_spark.sh)"
printf '%s\n' "$dso_pin_output" # inspect the complete manifest before export
export LAGUNA_EXPECT_DSO_MANIFEST_SHA256="$(printf '%s\n' "$dso_pin_output" | awk -F= '$1=="LAGUNA_EXPECT_DSO_MANIFEST_SHA256"{print $2}')"
[[ "$LAGUNA_EXPECT_DSO_MANIFEST_SHA256" =~ ^[0-9a-f]{64}$ ]] || exit 2
unset dso_pin_output
export LAGUNA_API_KEY="$(openssl rand -hex 32)"
export OPENAI_API_KEY="$LAGUNA_API_KEY"
./scripts/serve_spark.sh

# 4) Smoke — model id must match --alias
cd /path/to/this/pack
/usr/bin/python3 -I -S eval/agent_smoke/run_smoke.py \
  --base-url http://127.0.0.1:8000/v1 \
  --model local-laguna

# 5) Optional hermes-class suite (does not replace step 4)
/usr/bin/python3 -I -S eval/hermes_agent_smoke/run_hermes_smoke.py \
  --base-url http://127.0.0.1:8000/v1 \
  --model local-laguna \
  --out "results/hermes_agent_smoke_$(date -u +%Y%m%dT%H%M%SZ).json"
```

| Guide | Path |
|-------|------|
| Spark notes | [`SPARK.md`](./SPARK.md) |
| Reproduce | [`docs/REPRODUCE.md`](./docs/REPRODUCE.md) |
| Build | [`docs/BUILD_SPARK.md`](./docs/BUILD_SPARK.md) |
| Last-green pin | [`results/LAST_GREEN_PIN.md`](./results/LAST_GREEN_PIN.md) |
| Sample client | [`hermes/`](./hermes/) |

---

## License

Base model and official GGUF: **OpenMDW-1.1** (Poolside).

- Pack copy: [`LICENSE`](./LICENSE)
- Upstream: https://huggingface.co/poolside/Laguna-S-2.1/blob/00af5a51782109b587a3b3bbf11875e566036fa7/LICENSE.md

Retain notices. Pack scripts and eval harnesses are separate files with clear provenance.

---

## Base identity (pinned)

| Field | Value |
|-------|--------|
| Base model | `poolside/Laguna-S-2.1` |
| Base revision | `00af5a51782109b587a3b3bbf11875e566036fa7` |
| Architecture | 118B total · ~8B active/token · MoE |
| Official GGUF (authority) | `poolside/Laguna-S-2.1-GGUF` |
| Optional mirror | `hizrianraz/Laguna-S-2.1-GGUF` · **mirror only** |
| GGUF revision (upstream pin) | `fc4e481289523cf7d0df668da6d1d391616141ca` |
| Stand-behind quant | **official** `laguna-s-2.1-Q4_K_M.gguf` |
| Engine | `poolsideai/llama.cpp` · branch `laguna` · [PR #25165](https://github.com/ggml-org/llama.cpp/pull/25165) |

### Official GGUF digests (HF LFS metadata)

| File | sha256 |
|------|--------|
| `laguna-s-2.1-Q4_K_M.gguf` | `a8b55c75714ea73fd90ec85de5defdc0b8d88ca0ad2108343cdd8fc22f7583e4` |
| `laguna-s-2.1-Q8_0.gguf` | `d946b221d69f2c5f87a986952bcd3cfb75831e5a6a2184e626e361663e1bfe2b` |
| `laguna-s-2.1-F16.gguf` | `2036c9dcf70f59738d480d1da2a2a59c0a3a3c5bd4ab8c43a61d77fba031e1f8` |
| `laguna-s-2.1-DFlash-BF16.gguf` | `2ee8aa30338d6599bc7a8ce008cc57c56f2c2b2fdc21f6db9ecda203c751bfd4` |
| `laguna-s-2.1.imatrix` | `4a4f480f57a3251e3acfb1d35ffba64720662536135e4ca4f4d05b0732539be2` |

Pack verify file (GNU 2-column, Q4 default): [`SHA256SUMS`](./SHA256SUMS)

---

## Which quant to pull

| Goal | Artifact | Notes |
|------|----------|-------|
| **Default agent serve (Spark)** | Poolside **S Q4_K_M** | Measured format/routing smoke + short-gen point |
| Higher fidelity (Spark) | Poolside **S Q8_0** | More RAM |
| Speculative decode experiment | + Poolside **DFlash-BF16** | Measured slower · **DO_NOT_PROMOTE** |
| Full **S** on Mac ≤32 GB RAM | **No local S weights** | Use Mac as **client → Spark** only |

`diy_gguf: false`. Do **not** claim “first quant”. Mirror ≠ re-quant.

---

## Tool-agent wiring (OpenAI-compatible)

OpenAI `chat.completions` + `tools` / `tool_calls` shape.
**Not** a Nous Research product claim or endorsement.
“Hermes-class” in older notes = that wire shape only.

```bash
export OPENAI_BASE_URL=http://127.0.0.1:8000/v1   # /v1 required
export OPENAI_API_KEY="$LAGUNA_API_KEY"
export OPENAI_MODEL=local-laguna

/usr/bin/python3 -I -S hermes/sample_client.py

/usr/bin/python3 -I -S eval/agent_smoke/run_smoke.py \
  --base-url "$OPENAI_BASE_URL" --model local-laguna
/usr/bin/python3 -I -S eval/hermes_agent_smoke/run_hermes_smoke.py \
  --base-url "$OPENAI_BASE_URL" --model local-laguna \
  --out "results/hermes_agent_smoke_$(date -u +%Y%m%dT%H%M%SZ).json"
```

Agent loop contract (production agents; richer than current smoke):

1. POST messages + tool schemas
2. If `tool_calls` → execute **only** offered names → append `role=tool`
3. Repeat until final `content`
4. Sanitize invalid prior `function.arguments` JSON before re-send

Config snippet: [`hermes/config.example.yaml`](./hermes/config.example.yaml)

---

## Scoreboard (honest)

Freeze clock: **2026-08-02 18:00 WIB** — no new claims after freeze without re-measure.

| Host | Quant | Ctx flag | Gen tok/s (128 compl.) | agent_smoke | hermes v2 | Role |
|------|-------|----------|------------------------|-------------|-----------|------|
| DGX Spark GB10 | official Q4_K_M | 8192 | **~21.47** (short-gen) | **40/40 format smoke** | **27/27 validated-not-executed** | **Historical measured path** · engine `04b2b72` · tip `bf82eab` |

Ship minimum smoke ceiling historically used: **≥38/40** on this harness.
Historical result: **40/40**. The current hardened v2 source was not re-smoked.

Mandate: strengthen with multi-seed, actual tool execution, arg-value checks, warm TTFT stats — not ship day scope unless left green after freeze.

---

## Scope

**In scope**

- Measured Spark deployment packing
- Official weight pointers + digests
- Reproducible smoke harness + receipts

**Out of scope**

- Claiming this account quantized the weights
- Classifying this docs pack as a loadable GGUF model in prose
- Long-horizon agent SOTA claims from format smoke alone
- Fake or off-host benches labeled as Spark
- Local full-S weights on Mac hosts with ≤32 GB RAM
- Laguna hero announce / trending push before **2026-08-03 20:00 WIB**, before
  freeze attestation, or without a qualifying target-host receipt
- Using this pack to authorize or characterize other repositories' releases

---

## Attribution

| Component | Credit |
|-----------|--------|
| Model | Poolside Laguna S 2.1 © Poolside · OpenMDW-1.1 |
| GGUF | Poolside official conversions (authoritative) |
| Optional mirror | Byte-identical copy for bandwidth convenience only |
| Engine | poolsideai/llama.cpp `laguna` (+ upstream llama.cpp) |
| Pack, measurements, smokes | Independent work by [hizrianraz](https://huggingface.co/hizrianraz) |

## Disclaimer

Independent measurements on one DGX Spark.
Not affiliated with, endorsed by, or representing Poolside or Nous Research.

Updated: 2026-07-30 — self-authority freeze candidate; historical measured path;
current v2 not re-smoked; no checkpoint relationship · no quantized relation
