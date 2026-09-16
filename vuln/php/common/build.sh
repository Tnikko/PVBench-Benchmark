#!/bin/bash -eu
build_jobs="${BUILD_JOBS:-$(nproc)}"

./buildconf
./configure
make -j"$build_jobs"
test -f sapi/cli/php
test -f sapi/phpdbg/phpdbg
