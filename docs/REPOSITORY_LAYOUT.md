# Repository layout

| Directory | Purpose |
| --- | --- |
| `turtle_loop/` | Engine, providers, role sessions, recovery and live monitoring |
| `configs/`, `prompts/` | Model profiles, host bindings and role instructions |
| `data/annotations/` | Versioned puzzles and scoring rules |
| `data/host_reference/` | Original conversations, review decisions and upload inbox |
| `data/host_packs/` | Reviewed per-puzzle runtime examples |
| `scripts/`, `tests/` | Experiment commands, analysis and offline verification |
| `docs/running/` | Operational guides and parameter references |
| `docs/analysis/` | Findings and trajectory analysis |
| `docs/archive/` | Dated designs and historical notes |
| `results/trajectories/COHORT/GAME/` | One canonical published record per game |
| `results/tables/`, `results/reviews/` | Derived tables and review evidence |
| `runs/api/` | Ignored local execution, resumable checkpoints and generated exports |

Full experiment records live on [Hugging Face](https://huggingface.co/datasets/COMP1110-20261A-Group50/GoodTurtle-experiments). `results/remote.json` pins a verified version; `python3 scripts/fetch_results.py` restores the original results tree for inspection and analysis. The trajectory/review directories in this layout describe the downloaded tree.

Read the [English quickstart](running/coworker_quickstart.md) to run experiments and the [results guide](../results/README.md) to inspect trajectories. Original research records retain their language and scoring version. The release does not rewrite original dialogue to make it look cleaner.

Generated result HTML is excluded. Text/JSON trajectories, shared discussion and reflection remain available. The single retained HTML file, `turtle_loop/web/progress.html`, is the runtime's local monitoring interface. The [HTML inventory](release/html_inventory.json) explains every decision.

The pre-cleanup snapshot is retained in Git history. Older full execution snapshots and dashboards are also on [archive/full-repository-20261114](https://github.com/aurorajy1108/GoodTurtle/tree/archive/full-repository-20261114). Resolve historical paths with:

```bash
python3 scripts/results_catalog.py locate 'results/20261113_verified_final/mas/TS038_r01_solo/trajectory.jsonl'
```

Original path strings inside frozen JSON are provenance, not instructions to move files back.
