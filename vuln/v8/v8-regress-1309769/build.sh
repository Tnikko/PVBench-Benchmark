#!/bin/bash -eu

rsync -a /v8-dependencies/v8-regress-1309769/ .

gn gen out/debug_asan --args='
    is_debug=true
    is_asan=true
    is_lsan=true
    v8_enable_backtrace=true
    is_component_build=false
    symbol_level=2
'

retry_count=0
max_retries=10

while [ $retry_count -lt $max_retries ]; do
    if ninja -C out/debug_asan -j8 d8; then
        break
    fi

    retry_count=$((retry_count + 1))
    if [ $retry_count -ge $max_retries ]; then
        exit 1
    fi
    echo "Transient Ninja failure; retrying ($retry_count/$max_retries)" >&2
    sleep 2
done

test -f out/debug_asan/d8
