# PHP/CPython base environment repair

Date: 2026-09-15 (Asia/Shanghai)

Repository commit: `e5982b988ff41c5d69537ef480425d0cdc3e384e`

## Host and container budget

- Host: Intel Core i7-12700, 20 logical CPUs, about 14 GiB RAM, 4 GiB swap.
- Base cases remain serialized with `COLD_MAX_PROC=1`.
- Both containers use a 6 CPU / 9 GiB hard limit and a 4 CPU / 6 GiB reservation.
- PHP uses `BUILD_JOBS=6` and `TEST_JOBS=4`.
- CPython uses `CPYTHON_BUILD_JOBS=4` and `TEST_JOBS=4`.

## PHP result

The original image build failed while cloning `php-src` because GitHub port 443 timed out. A retry on 2026-09-15 cloned the repository and built `pvbench-php-base` successfully, so no clone retry logic was added.

`php-gh-12721` completed in 12 minutes 25 seconds with exit code 0:

- sanitizer trigger: pass;
- developer repair: pass;
- unpatched functional tests: pass;
- patched functional tests: pass;
- patched PoC+ tests: pass.

Observed container memory remained far below the 9 GiB limit; sampled usage peaked around 1.3 GiB.

## CPython diagnosis and result

The initial resource change only updated `vuln/cpython/common/test.sh`. `py-pr-125015` has a case-specific `test.sh`, so it continued to invoke `make test -j20`. The diagnostic run was stopped after confirming this override path.

The corrected image prepends `/workspace/cold/compiler` to `PATH`. Its `make` wrapper:

- replaces every Make job count with `CPYTHON_BUILD_JOBS`;
- preserves existing CPython `TESTOPTS` exclusions;
- injects `-j${TEST_JOBS}` into CPython regrtest options;
- applies to both common and case-specific scripts without editing every benchmark case.

The corrected `py-pr-125015` run completed in 30 minutes 58 seconds with exit code 0. The regrtest parent was observed with `-j4`, and no more than four regrtest workers were active. Cgroup peak memory was about 8.16 GiB under the 9 GiB limit; `memory.events` reported zero `max`, `oom`, and `oom_kill` events.

## Evidence

- `logs/php-base-build-retry.log`
- `logs/php-base-php-gh-12721-resource.log`
- `logs/cpython-base-py-pr-125015-resource.log`
- `logs/cpython-base-build-resource.log`
- `logs/cpython-base-py-pr-125015-resource-v2.log`
- `status.tsv`

The complete 43-case PHP and 33-case CPython sweeps have not been started. At the observed per-case times, they remain multi-hour workloads and should continue serially.
