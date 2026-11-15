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

- 206 canonical games, including source and interrupted records with their original status.
- 20,076 external submissions.
- 4,937 shared-agent and private reflection messages, explicitly distinguished.
- Full original records in `results.tar.gz`; browsable `games`, `turns` and `messages` tables on HF.

[Summary CSV](summary.csv) · [Condition table](tables/20261114_latest_update/by_condition.csv) · [Source/condition table](tables/20261114_latest_update/by_source_condition.csv)

Historical cohorts retain original model, host, rubric and completion rules. Restore the records before rebuilding analyses. Live experiments are added in a later verified release after registration.
