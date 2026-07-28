# Build notes — poolside llama.cpp laguna on DGX Spark

personal · not Ainfera · not Neptune · not Fin · not Gate0

## Engines

```bash
git clone https://github.com/poolsideai/llama.cpp.git ~/src/llama.cpp-laguna
cd ~/src/llama.cpp-laguna
git checkout laguna   # pin: 04b2b72cb54048ead292884adbe11f284e3ec950
```

## Patch (measured required on this host)

`common/speculative.cpp` uses `std::isfinite` without `#include <cmath>`.
GNU 13.3 fails the build until that include is added (one line).

## Configure

```bash
export PATH=/usr/local/cuda/bin:/usr/bin:$PATH
export CUDA_HOME=/usr/local/cuda
export CC=/usr/bin/gcc CXX=/usr/bin/g++ CUDAHOSTCXX=/usr/bin/g++
# GB10: sm_121a
cmake -S . -B build   -DGGML_CUDA=ON   -DCMAKE_CUDA_ARCHITECTURES=121a   -DCMAKE_BUILD_TYPE=Release
cmake --build build -j"$(nproc)" --target llama-server llama-cli llama-bench
```

If CMake translates `121` poorly, force `121a`.

## Verify

```bash
export LD_LIBRARY_PATH=$HOME/src/llama.cpp-laguna/build/bin:$LD_LIBRARY_PATH
~/src/llama.cpp-laguna/build/bin/llama-server --version
# version: 1 (04b2b72)
```
