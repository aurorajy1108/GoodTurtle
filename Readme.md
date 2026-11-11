# GoodTurtle — COMP1110

**Scoring update:** new runs default to v5 / `coverage-v3-unified`: 100% means solved and ends the game. All mandatory narrative facts are scored; historical v4 results stay unchanged. [Details and checks](docs/unified_scoring_v3.md).

**Team runs:** [Three CL sets and three MAS puzzles, two people × two repeats](docs/team_campaign_20261111.md): a six-game pilot, personal batches, bounded parallel execution of all 150 games, and deduplicated collection.

English | [中文](README.zh-CN.md)

## Current team quickstart

Use branch `fix/cl-session-prefix-compat-20261111`, run from the repository root, and export your own `DEEPSEEK_API_KEY` in the same terminal. [Task assignments, every parameter and result collection](docs/team_campaign_20261111.md).

```bash
git fetch origin
git switch fix/cl-session-prefix-compat-20261111
git pull --ff-only
```

Jiayang's small pilot: 4 CL games + 2 MAS games, one concurrent slot:

```bash
bash scripts/run_team_smoke.sh jiayang cl-set1-a,mas-ts038-a
```

Jiayang's formal batch: two repeats per condition, 21 CL + 4 MAS games, up to two concurrent slots:

```bash
bash scripts/run_team_batch.sh jiayang cl-set1-a,mas-ts038-a 2
```

Only ONE coordinator launches all team slots; others do not launch their own copies:

```bash
bash scripts/run_team_batch.sh coordinator all 4 runs/api/team_all_formal_v1
```

This schedules 150 games with up to four concurrent slots: CL Set1–3 (126 games) and MAS TS038/TS002/TS014 (24 games). Each experiment has two human execution slots, each running two repeats. The Set3 second operator and TS014 MAS second operator must each be assigned to one person from their listed candidates. Existing output directories are never overwritten. Each B has 100 fresh submissions; A is fixed within each execution slot, with its full answer revealed before B.

**2026-11-11 branch:** [Run CL session continuation and the new Player response format](docs/run_session_prefix_v1.md), including Set1 and TS038 commands, all relevant parameters, costs and recovery limits.

**Historical Set1 recovery:** `start_set1_auto_continue.sh` targets an archived stopped rollout, not the new team campaign. For a current stopped CL task use the task-specific recovery instructions in the [campaign guide](docs/team_campaign_20261111.md).

**November 10 Set 1 rerun:** [verified launcher and settings](docs/set1_v11_rerun.md). Run `bash scripts/start_set1_verified.sh` in the terminal with `DEEPSEEK_API_KEY`: freeze inputs, run 20 Host diagnostics, then start 12 fresh CL games only if every check passes. Host causal boundaries were repaired; persistent reference bodies are cached once per role session. No MAS or extra repeats in this launcher.

**Current DeepSeek defaults:** `configs/loop.deepseek.json` uses `deepseek-v4-pro / high` for Host/Grader and `deepseek-flash / thinking disabled` for Player/default MAS partner. The optional isolated format repairer is configured separately; see the [campaign guide](docs/team_campaign_20261111.md) for machines without Codex. See [provider setup](docs/deepseek.md).

GoodTurtle studies in-context experience transfer (continual learning, or CL) and two-agent collaboration using lateral thinking puzzles. It includes **50 English puzzles and 161 scoring checkpoints**, configurable host, player and grader roles, trajectories, and experiment summaries.

**Current study: CL Set1–3 and MAS TS038/TS002/TS014, two people × two repeats per experiment.** Scripts start paid calls only when explicitly run. Host behavior and scoring annotations still need validation; passing unit tests does not establish model accuracy. GPT model settings remain available through the explicit Codex configuration; they are not the team launchers' DeepSeek defaults. Host answers use four labels: `yes`, `no`, `yes and no`, and `irrelevant`.

New optional MAS strategy: [`free_dialogue`](docs/mas_free_dialogue.md) gives two independent persistent agents one shared public chat, adaptive speaking order, and explicit role ablations. Select `--strategies solo,free_dialogue`; the existing four-strategy study default is preserved.

The [current five-set study](docs/study_20261102.md) defaults to a fixed target B per set and one frozen A trajectory per source puzzle within a batch. Every B repeat has a fresh 100-submission budget; the session condition independently forks A's original Player messages, while direct and answer_only start new conversations. Reverse positive directions require `--directions bidirectional` and are exploratory; `--source-policy per-repeat` explicitly restores regenerating A. The study launcher defaults to writing a plan only.

New runs use **one host judgment per question**, local retrieval of up to 6 reference Q&As (6000 characters), and a separate grader context with up to 3 precedents (3000 characters). Full story facts and scoring rules remain intact; provenance stays on disk. **Each game has persistent, isolated role sessions** with lossless context updates: Codex resumes explicit thread IDs, Responses chains response IDs, and other providers maintain local multi-turn messages. Set `session_mode: replay` for the stateless control. Session continuity does not make history free or guarantee equal results. Configure these options in [runtime parameters](docs/runtime_parameters.md); existing frozen runs retain their original policy. General persistent interruptions fail closed. Complete saved DeepSeek solo replies with a supported metadata or narrowly repairable question-quote error can be recovered in an explicitly annotated copy; see [recovery limits](docs/deepseek.md#字符串text_note及一次性续跑).

New runs automatically export per-call `token_costs.csv`, per-game `costs_by_game.csv`, and `cost_summary.json` totals by role/model. USD values are standard API-equivalent estimates, including failed calls with reported usage; unknown usage/prices stay unknown. Codex subscription charges are not inferred from API prices. See [cost accounting and price configuration](docs/study_20261102.md#token-与费用记录自动启用).

## Where to start

| Task | Entry point |
| --- | --- |
| Run the current three CL sets and three MAS puzzles | [Assigned slots, smoke/formal/parallel scripts and collection](docs/team_campaign_20261111.md) |
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

Player 输出协议：新实验使用固定前缀，单 agent 与 MAS 的格式、兼容性和计数规则见 [player_action_protocol.md](docs/player_action_protocol.md)。Host/Grader 格式保持不变。

CL now defaults to original-role session continuation: finish A, reveal its full answer, then continue B with a fresh 100-submission budget. Repeated B games fork the same frozen A prefix. See [protocol, controls and launch commands](docs/cl_raw_session.md).
