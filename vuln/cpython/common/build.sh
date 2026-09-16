#!/bin/bash -eu
build_jobs="${CPYTHON_BUILD_JOBS:-${BUILD_JOBS:-$(nproc)}}"

./configure --without-pymalloc
ASAN_OPTIONS=detect_leaks=0 make -j"$build_jobs"
test -f python
