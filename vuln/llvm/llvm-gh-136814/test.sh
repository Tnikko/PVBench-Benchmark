#!/bin/bash -eu
build_jobs="${BUILD_JOBS:-16}"

mkdir -p build && cd build
cmake -G Ninja \
	-DCMAKE_BUILD_TYPE=Release \
	-DLLVM_ENABLE_PROJECTS="clang" \
	-DLLVM_TARGETS_TO_BUILD="X86" \
	-DLLVM_BUILD_TESTS=ON \
	-DLLVM_INCLUDE_TESTS=ON \
	../llvm
ninja -j"$build_jobs"
ninja -j"$build_jobs" check-all
