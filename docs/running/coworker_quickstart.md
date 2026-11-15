# Quickstart

Run commands from the repository root with Python 3.11. Core experiments require no additional Python packages. All output paths below must be new.

## 1. Check the installation

```bash
python3 -m unittest discover -s tests
python3 scripts/fetch_results.py
python3 scripts/results_catalog.py check
python3 scripts/play.py demo --out runs/api/offline_demo
```

The demo is scripted and makes no model calls. It checks plumbing, not model performance.

## 2. Configure credentials and models

```bash
export DEEPSEEK_API_KEY='your-own-key'
```

The export can be run in any folder; launch the experiment in that same terminal. Never commit credentials. Default model settings are in `configs/loop.deepseek.json`: player thinking is disabled; host/grader thinking is enabled. The standard dataset is `data/annotations/turtle50_v5/private.json`. Host reference selection follows `configs/host_bindings.json`.

## 3. Plan a CL experiment

```bash
python3 scripts/study_20261102.py --suite continual --sets 1 \
  --source-puzzles TS015,TS014,TS028 --directions primary \
  --source-policy fixed --memory session --repeat 4 \
  --mode plan --out runs/api/set1_plan
```

| Option | Meaning |
| --- | --- |
| `--suite continual` | Run source-to-target experience comparisons. |
| `--sets 1` | Use Set 1 with target TS013; other study sets are selectable. |
| `--source-puzzles` | Source whitelist; this selects TS015, TS014 and TS028, leaving TS016 optional. |
| `--directions primary` | Keep the designated target fixed. `bidirectional` adds exploratory reverse positive directions. |
| `--source-policy fixed` | Solve each source once and reuse that exact experience across repeats. |
| `--memory session` | Continue the source's original player-role messages for the full-dialogue condition. |
| `--repeat 4` | Four fresh target games per scheduled comparison; source games are not repeated. |
| `--mode plan` | Save a plan without model calls. `dry-run` checks offline execution; `run` makes paid calls. |
| `--out` | New output directory; never overwrites an existing experiment. |

The plan lists the scheduled source games, baseline, answer-only and full-dialogue conditions. Inspect it before starting a large batch. To run, use `--mode run` and a new output path. The source answer is revealed even after an unsuccessful source attempt. Every target starts with a fresh 100-action quota.

## 4. Plan a MAS experiment

```bash
python3 scripts/study_20261102.py --suite team --team-puzzles TS038 \
  --strategies solo,free_dialogue --repeat 4 \
  --dialogue-roles complementary --dialogue-scheduling adaptive \
  --dialogue-max-discussion 4 --mode plan --out runs/api/mas_plan
```

`solo,free_dialogue` selects the single-player and shared-public-dialogue conditions. Both team players retain separate continuing sessions. `complementary` assigns investigator/critic roles; `symmetric` and `swapped` are role ablations. Adaptive scheduling follows the selected next speaker; `alternating` changes speaker after each message. At most four internal messages occur between host-facing actions, and the team shares the external-action quota.

Specify `--strategies` explicitly: the historical generic study default also schedules other strategies. [Team allocation and bounded parallel launchers](team_campaign_20261111.md) support larger campaigns. [Reflection pilot](compute_matched_agents.md) is a separate experiment.

## 5. Inspect output and recover interruptions

Local output includes `plan.json`, `status.json`, per-game trajectories/results, frozen settings and token/cost records. Optional HTML is generated locally and excluded from published results. Check `status.json` and the launcher log after startup: a process ID alone does not confirm API access.

Use the existing task's documented recovery command rather than starting a new experiment directory. [Automatic continuation](automatic_continuation.md) describes supported retries and checkpoints. Keep the original records when a request may have reached the provider.

Use `python3 scripts/study_20261102.py --help` for all scheduling parameters, and the [runtime reference](runtime_parameters.md) for model/provider configuration, timeouts, retries, sessions and context limits. No experiment is started by opening this repository.
