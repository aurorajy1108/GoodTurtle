# GoodTurtle — COMP1110

An auditable Turtle Soup puzzle dataset and Host/Player/Grader pipeline, with
continual in-context transfer and multi-agent experiments.

English | [中文](README.zh-CN.md)

|Task|Location|
|---|---|
|Run experiments|[Quickstart](docs/running/coworker_quickstart.md) · [Every runtime parameter](docs/running/runtime_parameters.md)|
|CL / MAS / self-review|[Experiment guide](docs/running/experiment_pipelines.md) · [Team commands](docs/running/team_campaign_20261111.md) · [Compute budgets](docs/running/compute_matched_agents.md)|
|Upload human reference Q&A|[`data/host_reference/inbox/`](data/host_reference/inbox/README.md)|
|Current Host inputs|[`data/host_packs/active/`](data/host_packs/README.md) and [`configs/host_bindings.json`](configs/host_bindings.json)|
|Trajectories and results|[Results catalog](results/README.md)|
|Research findings|[All-version analysis](docs/analysis/all_versions_20261114.md) · [Process evidence](docs/analysis/project_story_20261114.md)|
|Moved files and full archive|[Repository layout](docs/REPOSITORY_LAYOUT.md)|

## Run

Use Python 3.11. Credentials belong in your environment or the ignored local
environment file, never in tracked configuration. Provider/model options are in
[`configs/loop.deepseek.json`](configs/loop.deepseek.json); command-line options are in the
[runtime reference](docs/running/runtime_parameters.md).

```bash
python3 scripts/play.py --help
python3 scripts/experiment.py --help
```

For assigned studies, use the [team campaign guide](docs/running/team_campaign_20261111.md).
Each B has a fresh 100-submission budget; unsuccessful submissions count. Frozen
historical runs retain their original Host, scoring and configuration.

## Read existing results

No API key or model call is needed:

```bash
python3 scripts/results_catalog.py list --puzzle TS038
python3 scripts/results_catalog.py check
python3 scripts/results_catalog.py summarize
```

Open a game's `trajectory.html` or read `trajectory.md` / `trajectory.jsonl`.
Cooperation and self-review transcripts stay alongside the game. Summary tables
are Markdown/CSV/JSON; no aggregate visualization is required.

## Structure

`turtle_loop/`, `configs/`, `prompts/`, `scripts/`, `tests/` contain maintained code;
`data/` contains puzzles and Host references; `docs/` contains guides and analysis;
`results/` contains curated trajectories and tables. New local runs go to ignored
`runs/api/`. See the [layout guide](docs/REPOSITORY_LAYOUT.md).

The full pre-cleanup repository, visualizations, original request bodies and old
checkpoints remain on
[`archive/full-repository-20261114`](https://github.com/aurorajy1108/GoodTurtle/tree/archive/full-repository-20261114).
No Git history or original outcome was rewritten. AI review is distinguished from
human-confirmed annotations.

Detailed prior CLI notes remain in the [English](docs/running/cli_reference.md) /
[Chinese](docs/running/cli_reference.zh-CN.md) references; dated sections describe
their archived study, not a current progress counter.
