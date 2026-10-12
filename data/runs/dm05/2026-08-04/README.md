These records support the DM0.5 evaluation submitted in
[`data/results/dm05.json`](../../../results/dm05.json), using the
[DM05-Vla-Arena checkpoint reference](https://huggingface.co/Dexmal/DM05-Vla-Arena).

The evaluation was run on August 4, 2026. It covers all 170 VLA-Arena tasks:
60 at L0, 55 at L1, and 55 at L2, with seeds `7`, `42`, and `1000` and
10 episodes per task per seed. There are 99 suite/level/seed runs, 5,100
completed episodes, and 3,202 successful episodes. LIBERO was not evaluated.

| Metric | L0 | L1 | L2 |
| --- | ---: | ---: | ---: |
| SR (%) | 89.090909 | 53.636364 | 44.060606 |
| Safety CC | 1.904000 | 18.745333 | 22.520000 |

For each suite/level/seed, SR is successes divided by completed episodes,
and CC is total cumulative cost divided by completed episodes. The result
file averages these values over the three seeds. Level summaries average
SR over the 11 suites and CC over the five Safety suites. All 10 trials of
every task are present. `numEpisodes` and `numSuccesses` in the result file
sum all three levels and all three seeds for that suite.

LongHorizon contains 10 tasks at L0 and five at each other level. Pooling
all L0 episodes instead of averaging the 11 suites gives 88.333333% SR;
this is a different aggregation convention.

The records are derived from the final per-run `parallel_eval_*.json`
files. Each source file has a SHA-256 digest in `run_manifest.json`.
`episodes.csv` retains task IDs, episode indices, success flags, cumulative
costs, and recorded attempt counts. Its 5,100 episode IDs are unique within
their respective runs, and its totals agree with both the original JSON
and the accompanying final summary CSV files. Seven episodes record two
attempts; the other 5,093 record one. No final episode has a recorded error.

The earlier top-level batch summary snapshots include overlapping runs.
Even after selecting the latest batch snapshot for each run, five records
differ from the final per-run JSON: UnseenObjects L0 seed7, all three
LongHorizon L0 seeds, and LongHorizon L1 seed42. The submitted values use
the final per-run records throughout.

All 99 source JSON files record 16 evaluation workers and 10 trials per
task. A retained configuration for LongHorizon L0 seed7 records an action
horizon of 20, replanning every 10 steps, 256-pixel environment images,
10 initial wait steps, and initial-state selection mode `first` with
offset 0 and random offset disabled. That one configuration is not a
complete configuration archive for all 99 runs. The source artifacts do
not record the served weight hash or evaluator Git revision.

The Hugging Face model card at revision
`12e0ec028dca289cd53aa14bd487ff12b8cc0977` reports SR
`89.0% / 53.6% / 44.1%` and CC `1.9 / 18.75 / 22.52`.
Minor differences from the displayed figures reflect different rounding
conventions. The submitted result preserves the episode-derived precision.
The card was read through hf-mirror at the fixed revision above.

Recompute and verify the submitted values from the repository root:

```sh
python3 data/runs/dm05/2026-08-04/verify.py
```

If the original evaluation directory is available, also verify its hashes:

```sh
python3 data/runs/dm05/2026-08-04/verify.py --raw-root /path/to/evaluation
```
