# Experiment results

Full experiment records are hosted on [Hugging Face](https://huggingface.co/datasets/COMP1110-20261A-Group50/GoodTurtle-experiments). The original puzzle collection is [GoodTurtle](https://huggingface.co/datasets/COMP1110-20261A-Group50/GoodTurtle).

GitHub retains compact summary tables; trajectories, shared dialogue, private reflection, frozen settings, reviews and detailed analysis records are in the HF release. The pinned version is recorded in `remote.json`.

## Download and validate

```bash
python3 scripts/fetch_results.py
python3 scripts/results_catalog.py check
python3 scripts/results_catalog.py list --puzzle TS038
```

The downloader restores the original `results/` structure, verifies every archived file and checks the full game catalog. Existing conflicting local files are not overwritten. Downloaded records are ignored by Git. No HF token is needed for this public release.

## Release contents

- 163 report-scope games, including source and interrupted records with their original status.
- 17,574 external submissions.
- 4,440 shared-agent and private reflection messages, explicitly distinguished.
- Full original records in `results.tar.gz`; browsable `games`, `turns` and `messages` tables on HF.

[Summary CSV](summary.csv)

Historical cohorts retain original model, host, rubric and completion rules. Restore the records before rebuilding analyses. Live experiments are added in a later verified release after registration.

## Current scope

The current HF version removes 61 unused older-batch games and adds 18 report appendix/supplement games. It includes the completed fourth MAS-reflection run. The 50-puzzle dataset is unchanged.

The CL four-run descriptive analysis uses outcome-ranked subsets. Full candidate records and the selection table are retained in the HF archive for audit; they are not additional reported four-run samples. See `results/report_provenance/cl_selection.csv` after downloading. Historical archive versions remain available for provenance.

If a previous full archive is already restored in your checkout, use a fresh checkout or a new `--root` directory for this release. The downloader preserves conflicting local evidence rather than silently replacing it.
