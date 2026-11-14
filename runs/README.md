# Local execution output

New runs write to `runs/api/`, which is ignored by Git. Do not commit API keys,
recovery copies or generated dashboards here.

Published, curated trajectories are in [results/trajectories](../results/trajectories/).
See [results guide](../results/README.md) for the catalog and current summaries.

All previously committed run folders, including full request logs and checkpoints,
remain on [`archive/full-repository-20261114`](https://github.com/aurorajy1108/GoodTurtle/tree/archive/full-repository-20261114).
Use `python scripts/results_catalog.py locate OLD_PATH` to find a moved artifact.
