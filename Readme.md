# GoodTurtle — COMP1110

English | [中文](README.zh-CN.md)

GoodTurtle studies in-context experience transfer (continual learning, or CL) and two-agent collaboration using lateral thinking puzzles. It includes **50 English puzzles and 161 scoring checkpoints**, configurable host, player and grader roles, trajectories, and experiment summaries.

**Current scope: one-repeat CL Set 1 and TS038 team experiments are authorized; other experiments remain paused.** Host behavior and scoring annotations still need validation; passing unit tests does not establish model accuracy. The default host is `gpt-6.1-sol` with medium reasoning; the grader stays `gpt-6.1-sol` with high reasoning, and the player and default partner are `gpt-5.6-luna` with low reasoning. Host answers use four labels: `yes`, `no`, `yes and no`, and `irrelevant`.

New optional MAS strategy: [`free_dialogue`](docs/mas_free_dialogue.md) gives two independent persistent agents one shared public chat, adaptive speaking order, and explicit role ablations. Select `--strategies solo,free_dialogue`; the existing four-strategy study default is preserved.

The [current five-set study](docs/study_20261102.md) defaults to a fixed target B per set and one frozen A trajectory per source puzzle within a batch. B starts a fresh 100-submission session on every repeat. Reverse positive directions require `--directions bidirectional` and are exploratory; `--source-policy per-repeat` explicitly restores regenerating A. The study launcher defaults to writing a plan only.

New runs use **one host judgment per question**, local retrieval of up to 6 reference Q&As (6000 characters), and a separate grader context with up to 3 precedents (3000 characters). Full story facts and scoring rules remain intact; provenance stays on disk. **Each game has persistent, isolated role sessions** with lossless context updates: Codex resumes explicit thread IDs, Responses chains response IDs, and other providers maintain local multi-turn messages. Set `session_mode: replay` for the stateless control. Session continuity does not make history free or guarantee equal results. Configure these options in [runtime parameters](docs/runtime_parameters.md); existing frozen runs retain their original policy. Interrupted persistent games fail closed and currently require a new labeled run.

New runs automatically export per-call `token_costs.csv`, per-game `costs_by_game.csv`, and `cost_summary.json` totals by role/model. USD values are standard API-equivalent estimates, including failed calls with reported usage; unknown usage/prices stay unknown. Codex subscription charges are not inferred from API prices. See [cost accounting and price configuration](docs/study_20261102.md#token-与费用记录自动启用).

## Where to start

| Task | Entry point |
| --- | --- |
| Upload a human host reference trajectory | [Upload inbox](data/host_reference/inbox/); [reference guide](data/host_reference/README.md) |
| Find archived human conversations and corrections | [Reference sources](data/host_reference/sources/) |
| Review findings | [Applied human review](data/host_reference/reviews/human_20261102/manifest.json); [Original annotations](data/host_reference/sources/human_review_20261102/); [Review history](data/host_reference/reviews/) |
| Run the five CL sets and five team puzzles | [November 2 experiment list, settings and commands](docs/study_20261102.md) |
| Inspect examples currently used by the host | [Active packs](data/host_packs/active/); [bindings](configs/host_bindings.json) |
| Run experiments | [Coworker quickstart](docs/coworker_quickstart.md) |
| Find commands and model parameters | [Runtime parameters](docs/runtime_parameters.md); [CL and two-agent experiments](docs/experiment_pipelines.md); [v7 control design](docs/host_repair_v7.md) |
| Find outstanding work | [Review checklist](docs/todo_human_review_20261027.md) |
| Find older versions and reports | [Archived documentation](docs/archive/README.md); [run directory guide](runs/README.md) |

## Repository layout

```text
configs/                  Model profiles, puzzle bindings, transfer pairs, path migration map
data/
  annotations/turtle50_v4/ Current 50-puzzle answers and scoring; v2/v3 are historical
  host_reference/         Human references; uploads do not automatically change the host
    inbox/                New uploads by TSxxx/source_id, or multi/ for multiple puzzles
    sources/              Registered messages, IDs, segments and normalized Q&A
    reviews/              Decisions, conflicts, revisions and evidence
  host_packs/
    active/               One runtime pack per puzzle
    archive/              Historical versions and candidates
    local/                Unpublished local research packs, ignored by Git
prompts/                  Current host, player, grader and review prompts
  archive/                Historical prompts
turtle_loop/             Game, shared buffer, CL, grading and provider implementation
scripts/                  Commands for running, importing, validating and reporting
tests/                    Offline regression and integration tests
runs/                     Experiment trajectories and frozen runtime snapshots
outputs/                  Deliverable reports, including Excel workbooks
docs/                     Current documentation and historical archive
```

## Upload a human trajectory

Run from the repository root:

```sh
python3 scripts/host_reference.py init \
  --puzzle TS032 --source-id 20261028_chat01 \
  --file /path/to/conversation.md
python3 scripts/host_reference.py validate
```

This creates `data/host_reference/inbox/TS032/20261028_chat01/` with the source trajectory and `source.json`. Omit `--file` to create a template; `--source-url` records a share link without fetching it. For a conversation covering multiple puzzles, pass `--puzzle TS032,TS034` to create a folder under `inbox/multi/`.

Check the role mapping and source before committing. **Uploading or pushing a trajectory does not add it to the host prompt.** Explicitly selected examples are added to the active pack after review. See the [reference guide](data/host_reference/README.md) for the full process.

## Run and validate

After configuring a model account, start with an offline preflight:

```sh
python3 scripts/play.py run \
  --dataset data/annotations/turtle50_v4/private.json \
  --puzzle TS032 --config configs/loop.codex.json \
  --dry-run --out runs/api/my_preflight
python3 -m unittest discover -s tests -q
```

`--dataset` selects the private dataset, `--puzzle` selects the puzzle, and `--config` selects the model profile. `--dry-run` makes no model calls; `--out` must name a new directory. When experiments resume, remove `--dry-run` as described in the quickstart. OpenAI, Anthropic and DeepSeek configurations are also supported.

Each game allows at most 100 submissions, reserving the last for a forced final. Wrong or incomplete finals consume a submission; successful finals are recorded separately. Outputs include `trajectory.html`, scores and call costs. Host private information must not be sent to the player. CL here transfers context, not model weights.

## Compatibility and history

The 2026-10-28 reorganization moved paths and updated bindings and navigation without changing the 50 puzzles, scoring, actual host contexts or historical runs. The previous README is preserved in the [historical snapshot](docs/archive/README_before_cleanup_20261028.md).

Use `python3 scripts/host_reference.py locate OLD_PATH` to locate paths recorded in older reviews or Excel files; mappings are in [repository_layout.json](configs/repository_layout.json). Existing runs retain their frozen snapshots.
