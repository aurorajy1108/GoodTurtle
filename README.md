# GoodTurtle

Turtle Soup is a lateral-thinking game: a player reconstructs a hidden story by asking a host questions. GoodTurtle provides 50 English puzzles, reviewed host references, weighted scoring, and automated experiments on prior experience and two-agent cooperation.

A COMP1110 academic project by **Sun Jiayang, Zhen Qi, Sun Xueli, Qiu Tong and Amy Ou**.

## Research overview

We study how prior experience and cooperation influence interactive puzzle solving. CL experiments compare source relations and answer-only versus full-dialogue experience while keeping the target fixed. MAS experiments compare one player with two players sharing a public conversation. The repository includes the dataset, experiment code and original game records.

[Reproduction guide](docs/REPRODUCIBILITY.md) · [Dataset on Hugging Face](https://huggingface.co/datasets/COMP1110-20261A-Group50/GoodTurtle) · [Dataset card](data/DATASET_CARD.md) · [Published results](results/README.md)

## Start here

| Task | Location |
| --- | --- |
| Run a game or experiment | [Quickstart](docs/running/coworker_quickstart.md) |
| Browse published games | [Results](results/README.md) and [HF experiment tables](https://huggingface.co/datasets/COMP1110-20261A-Group50/GoodTurtle-experiments) |
| Find puzzles and scoring rules | [Dataset](data/README.md) |
| Add reference questions and answers | [Host reference guide](data/host_reference/README.md) |
| Change models or providers | [Runtime options](docs/running/runtime_parameters.md) |
| Understand the release structure | [Repository layout](docs/REPOSITORY_LAYOUT.md) |

## Installation and offline checks

Python 3.11 is recommended. The core runtime uses the Python standard library.

```bash
git clone https://github.com/aurorajy1108/GoodTurtle.git
cd GoodTurtle
python3 -m unittest discover -s tests
python3 scripts/release_check.py
```

No API key is needed to inspect the dataset or published results. Optional workbook-import tools use `openpyxl`; existing experiment data is already included.

## Run experiments

Set `DEEPSEEK_API_KEY` in the terminal that launches the experiment. Keep credentials outside tracked files. The ignored `.env.local` can also be used by launchers that explicitly load it; Python commands inherit the current environment.

The commands below **write plans without model calls**. Use a new output directory each time.

```bash
# CL Set 1: fixed target 13; positive 15, negative 14, unrelated 28.
python3 scripts/study_20261102.py --suite continual --sets 1 \
  --source-puzzles TS015,TS014,TS028 --source-policy fixed --memory session \
  --repeat 4 --mode plan --out runs/api/cl_set1_plan

# MAS: ordinary solo versus two independent players sharing public dialogue.
python3 scripts/study_20261102.py --suite team --team-puzzles TS038 \
  --strategies solo,free_dialogue --repeat 4 --mode plan \
  --out runs/api/mas_ts038_plan
```

To launch paid API calls, repeat the chosen command with `--mode run` and a different output directory. [Quickstart and parameter explanations](docs/running/coworker_quickstart.md).

The supplied DeepSeek configuration uses a Flash player with thinking disabled and Pro host/grader roles with thinking enabled. Other provider profiles are available in `configs/`. Each standard game allows 100 external actions, including incorrect or incomplete answer submissions; the last action is reserved for a final answer. New games use unified scoring: full credit and completion share the same criterion. Published historical games retain their original scoring rules.

CL compares no prior game, the earlier puzzle's answer, and its full dialogue. A source is solved once and reused across target repetitions; its complete answer is revealed before the next puzzle. Each target gets a fresh quota. In `free_dialogue`, two continuing player sessions share public messages immediately, with complementary investigator/critic roles.

## Read trajectories

Complete records are hosted on [Hugging Face](https://huggingface.co/datasets/COMP1110-20261A-Group50/GoodTurtle-experiments). Restore the pinned release before inspecting games:

```bash
python3 scripts/fetch_results.py
python3 scripts/results_catalog.py list --puzzle TS038
python3 scripts/results_catalog.py list --cohort Set2_v17 --condition session
python3 scripts/results_catalog.py check
```

Each published game contains `trajectory.jsonl`, readable `trajectory.md`, its original result, and the available frozen settings and usage records. Shared dialogue and private reflection are retained as text/JSON records. Generated HTML exports are excluded from the release. The live progress monitor remains runtime code.

## Repository

- `turtle_loop/`: game engine, providers, sessions, scoring and local monitoring.
- `configs/`, `prompts/`: model settings, host bindings and role prompts.
- `data/`: versioned puzzles, scoring annotations and host-reference sources.
- `scripts/`, `tests/`: experiment commands, maintenance and offline checks.
- `results/`: compact summary tables and the pinned HF release descriptor.
- Full trajectories/reviews are restored locally by `scripts/fetch_results.py`.
- `docs/`: current guides, analysis and dated historical documentation.
- `runs/api/`: ignored local output, checkpoints and optional visualizations.

English is the release's primary documentation language. Original conversations and dated research notes retain their source language. Human annotations, model-generated conversations and subsequent review decisions keep their original provenance.

The [full historical archive](https://github.com/aurorajy1108/GoodTurtle/tree/c4ccc67eef8c09aa0c6987a464f468718f5015f4) retains earlier dashboards and raw execution snapshots. See the [release cleanup record](docs/release/README.md) for the file-by-file HTML audit and validation.

## Citation and contributions

Citation metadata is provided in [CITATION.cff](CITATION.cff). Please cite the repository and relevant puzzle sources when using these materials. The [dataset card](data/DATASET_CARD.md) describes provenance and rights. See [CONTRIBUTING.md](CONTRIBUTING.md) for code, reference and result submission conventions.
