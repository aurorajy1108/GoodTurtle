# Contributing

Use a branch and keep changes focused on code, annotations, or experiment records. Describe the change and the checks run.

## Code

Use Python 3.11 and run:

```bash
python3 -m unittest discover -s tests
python3 scripts/fetch_results.py
python3 scripts/results_catalog.py check
python3 scripts/release_check.py
```

Planning and offline checks require no API credentials. Do not start paid experiments as part of a test. New runs and generated exports belong under ignored `runs/api/`.

## References and annotations

Submit source conversations through `data/host_reference/inbox/` with source identity and puzzle IDs. Follow the [reference guide](data/host_reference/README.md). Preserve original messages and distinguish original human answers, generated replies and later review. Activate reviewed examples through the existing binding workflow.

## Results

Publish each game once under `results/trajectories/COHORT/GAME/`. Retain raw questions, replies, original outcomes, frozen settings and available usage records. Register the game in the catalog and validate it. Corrections or regrading should be explicit derived records, preserving the original result. Do not count recovery copies as independent trials.

Keep credentials, machine-specific environment files and generated dashboards out of commits. English is the primary language for maintained documentation; source evidence keeps its original language.
