# PVBench committed-artifact metric reproduction

Repository commit: `e5982b988ff41c5d69537ef480425d0cdc3e384e`

Observed 209 dataset cases, but evaluation traces cover 208; every agent/model is missing `simdjson-issue-1273` (5 runs). Generated PoC+ artifacts cover 96 cases with three generated tests each.

| Tool | Model | Runs | Basic count | Basic % | README | Dev count | Dev % | README | Gen count | Gen % | README | FDR % | README |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| PatchAgent | Sonnet-4 | 1040 | 868 | 83.46 | 83.5 | 525 | 50.48 | 50.7 | 516 | 49.62 | 50.1 | 40.55 | 40.1 |
| PatchAgent | GPT-4.1 | 1040 | 793 | 76.25 | 76.4 | 467 | 44.90 | 45.2 | 460 | 44.23 | 44.5 | 41.99 | 41.7 |
| San2Patch | Sonnet-4 | 1040 | 427 | 41.06 | 41.3 | 222 | 21.35 | 21.6 | 211 | 20.29 | 20.7 | 50.59 | 49.8 |
| San2Patch | GPT-4.1 | 1040 | 392 | 37.69 | 37.9 | 209 | 20.10 | 20.2 | 203 | 19.52 | 19.6 | 48.21 | 48.2 |
| SWE-Agent | Sonnet-4 | 1040 | 301 | 28.94 | 29.0 | 212 | 20.38 | 20.5 | 199 | 19.13 | 19.6 | 33.89 | 32.3 |
| SWE-Agent | GPT-4.1 | 1040 | 147 | 14.13 | 14.4 | 85 | 8.17 | 8.4 | 82 | 7.88 | 8.3 | 44.22 | 41.3 |

Overall exact counts: basic `2928/6240`, Dev PoC+ `1720/6240`, Gen PoC+ `1671/6240`.
Calculated overall: basic `46.92%`, Dev `27.56%`, Gen `26.78%`, FDR `42.93%`; README reports `47.1%`, `27.8%`, `27.1%`, `42.3%`.

The committed artifacts reproduce the published trend but not every displayed rounded value. The report preserves exact counts instead of adjusting denominators to force a match.

Definitions:

- Basic: matching `:post.json` exists.
- Dev PoC+: matching `:post.json` has `result=true`.
- Gen PoC+: Dev passes and all three generated tests pass for cases with generated-test artifacts.
- FDR: `(Basic - Gen) / Basic`.
