# PVBench resource-limited reproduction notes

Date: 2026-09-12 (Asia/Shanghai)

Repository commit: `e5982b988ff41c5d69537ef480425d0cdc3e384e`

## Host budget

- 20 logical CPUs, about 14 GiB RAM, 4 GiB swap.
- No NVIDIA GPU was detected. PVBench uses remote LLM APIs, so this is not a direct blocker; local compilation and functional tests are the limiting workload.
- The reproduction was intentionally serialized with `COLD_MAX_PROC=1` and a per-container limit of 2 CPUs / 4 GiB.
- About 722 GiB disk space remained after repository and V8 submodule checkout.

## Verified locally

- Repository and both submodules were checked out.
- The missing Git LFS payload for `htslib-gh-2063` was restored and its repository-declared SHA-256 matched.
- The dataset contains 209 vulnerability configurations across 20 projects.
- `jq-base` built successfully and `jq-gh-2825` completed the sanitizer, repair, developer-test, patched-test, and post-test checks with exit code 0. See `logs/jq-base-smoke.log`.
- `cpython-base` built successfully. For `py-pr-125015`, the run reached sanitizer reproduction and repair validation, then entered the first full functional-test attempt.
- Metrics were recomputed from the committed result artifacts. See `metrics.md` and `metrics.json`.

## Resource-fix resumption on 2026-09-15

- `php-base` rebuilt successfully after the earlier GitHub timeout, confirming that the clone failure was transient.
- `php-gh-12721` completed the sanitizer, repair, unpatched functional, patched functional, and PoC+ checks in 12 minutes 25 seconds.
- The first resumed `py-pr-125015` run revealed that its case-specific `test.sh` bypassed the common script and still ran `make test -j20`; that diagnostic run was stopped.
- The CPython image now applies a project-local `make` wrapper to common and case-specific scripts. Builds and CPython regrtest are both limited to four workers.
- The corrected `py-pr-125015` run completed all five validation stages in 30 minutes 58 seconds. Its cgroup peak was about 8.16 GiB under a 9 GiB limit, with no OOM or cgroup limit event.
- Both base services run one vulnerability at a time under a 6 CPU / 9 GiB hard container limit. PHP uses six build jobs and four test jobs; CPython uses four build and four regrtest jobs.

See `php-cpython-resource-fix.md` and the corresponding logs for the exact commands and evidence.

## Earlier stops or stages not attempted

### Full 209-case baseline sweep

The sequential sweep was stopped during `py-pr-125015` at `Testing ... 1/3`. The case had already run for roughly 20 minutes; the container was using about 3.7 GiB of its 4 GiB cap and the repository allows up to one hour per functional-test attempt with three retries. There are 33 CPython cases and 209 cases overall, so a complete fresh local sweep would likely require many hours or days on this host. The batch parent and container were stopped cleanly, and no PVBench container was left running.

This is recorded as `stopped-resource-budget`, not as a benchmark failure.

### PHP base image

`php-base` failed while its Dockerfile cloned `https://github.com/php/php-src.git`: GitHub port 443 timed out after about 132 seconds. This is an external network/download failure, not a PVBench test result. See `logs/php-base-build.log`.

### Fresh LLM-agent matrix

Not started because API credentials are not configured. The full matrix is also expensive: 209 cases x 5 repetitions x 2 repair agents x 2 models = 4,180 repair-agent runs, before generated-test work. A one-case API smoke test should be run before considering any larger subset.

## Repository reproducibility caveats

- The evaluation artifacts contain 208 cases per agent/model rather than all 209; `simdjson-issue-1273` is absent. Consequently the recomputed percentages are close to, but do not exactly equal, every rounded value in the README.
- Several Dockerfiles clone upstream project default branches during image build rather than pinning repository commits. Results may therefore vary over time, and builds require reliable external network access.
- Compose's `full` profile includes `litellm-postgres` but the `litellm` service itself only has the `litellm` profile. Start the proxy explicitly with the `litellm` profile before PatchAgent runs.
