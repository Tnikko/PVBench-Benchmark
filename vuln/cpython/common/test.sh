#!/bin/bash -eu
build_jobs="${CPYTHON_BUILD_JOBS:-${BUILD_JOBS:-$(nproc)}}"

./configure --without-pymalloc --with-pydebug
make -j"$build_jobs"
make test -j"$build_jobs"
