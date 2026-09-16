#!/usr/bin/env bash
set -euo pipefail

docker_bin="${DOCKER_BIN:-docker}"
registry="ghcr.io/tnikko/pvbench-env"
version="pvbench-green-20260916"

projects=(
  cpython
  exiv2
  hdf5
  hermes
  htslib
  icu
  jasper
  jq
  libtiff
  libxml2
  llvm
  mruby
  pcapplusplus
  php
  quickjs
  simdjson
  v8
  vim
  wabt
  wireshark
)

for project in "${projects[@]}"; do
  remote_image="${registry}:${project}-base-${version}"
  local_image="pvbench-${project}-base:latest"

  printf 'Pulling %s\n' "$remote_image"
  "$docker_bin" pull "$remote_image"
  "$docker_bin" tag "$remote_image" "$local_image"
done
