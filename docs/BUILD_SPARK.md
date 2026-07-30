# Build notes — poolside llama.cpp laguna on DGX Spark

Personal Spark build notes.

## Engine

```bash
git clone https://github.com/poolsideai/llama.cpp.git ~/src/llama.cpp-laguna
cd ~/src/llama.cpp-laguna
git checkout --detach 04b2b72cb54048ead292884adbe11f284e3ec950
```

## Patch (historical measured shape · Spark / GNU 13.3)

The retained engine receipt (`results/engine_sha.txt`) records exactly one local
source change: add `#include <cmath>` to `common/speculative.cpp`. That is the
only patch shape accepted by the strict launcher. Apply it after the detached
checkout and before compiling:

```bash
git apply <<'PATCH'
diff --git a/common/speculative.cpp b/common/speculative.cpp
--- a/common/speculative.cpp
+++ b/common/speculative.cpp
@@ -13,4 +13,5 @@
 #include <algorithm>
+#include <cmath>
 #include <cassert>
 #include <cstring>
 #include <iomanip>
PATCH
git diff --check
sha256sum common/speculative.cpp
# 3952ed9f2a415661d17cdedf4ebca4cccfb2d2a883a0e8b939b0bf1e0c1f48b9
```

This is a local host build compatibility change, not a model or inference
behavior claim. Older notes also described a broader `math.h` / global
`isfinite` alternative; that form is **not bound to the short measured engine
receipt and is rejected by `serve_spark.sh`**. If the exact patch above does not
compile on the launch host, stop and create a new engine/build receipt instead
of silently changing the launch profile.

Do **not** treat a failed UI-asset HF fetch during build as fatal — `llama-server` still links; only the optional embedded UI may stay stale.

## Configure

```bash
export PATH=/usr/local/cuda/bin:/usr/bin:$PATH
export CUDA_HOME=/usr/local/cuda
export CC=/usr/bin/gcc CXX=/usr/bin/g++ CUDAHOSTCXX=/usr/bin/g++
# GB10: sm_121a
cmake -S . -B build \
  -DGGML_CUDA=ON \
  -DCMAKE_CUDA_ARCHITECTURES=121a \
  -DCMAKE_BUILD_TYPE=Release
cmake --build build -j"$(nproc)" --target llama-server llama-cli llama-bench
```

If CMake translates `121` poorly, force `121a`.

## Verify

```bash
# Hashing is non-executing. Do not run the newly built binary or ldd before the
# operator has reviewed and bound its exact digest.
sha256sum ~/src/llama.cpp-laguna/build/bin/llama-server
# After the official Q4 is present, run hash-only discovery first:
#   : "${LAGUNA_EXPECT_PACK_REVISION:?set the authorized 40-hex Hub commit}"
#   export LAGUNA_EXPECT_PACK_REVISION
#   export LAGUNA_EXPECT_LAUNCHER_SHA256=547ccf1f6f6cbae3fff15995ff4fecccbb876c3f6d5e015f6ab6a622ed9d4c2f
#   printf '%s  %s\n' "$LAGUNA_EXPECT_LAUNCHER_SHA256" scripts/serve_spark.sh | sha256sum -c -
#   LAGUNA_PRINT_RUNTIME_PINS=1 ./scripts/serve_spark.sh
# Confirm that output matches the independently reviewed sha256sum, then export
# LAGUNA_EXPECT_ENGINE_SHA256. Only then run:
#   LAGUNA_PRINT_RUNTIME_PINS=2 ./scripts/serve_spark.sh
# Inspect the complete manifest and export LAGUNA_EXPECT_DSO_MANIFEST_SHA256.
# Phase 2 is the first discovery step allowed to invoke ldd; the final mode-0
# launch requires both reviewed values.
```

Measured: binaries present after this patch (`llama-server`, `llama-cli`, `llama-bench`).
