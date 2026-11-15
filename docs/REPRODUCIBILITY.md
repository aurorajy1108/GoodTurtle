# Reproducing the experiments

## Research questions

1. How does earlier puzzle experience affect a player's exploration and final explanation?
2. How do the source relation and experience format change that effect?
3. How do two cooperating players use shared evidence compared with one player?

The CL intervention retains information in the conversation; model weights remain fixed. MAS uses separate continuing player sessions sharing one public record.

Full published records are on [HF](https://huggingface.co/datasets/COMP1110-20261A-Group50/GoodTurtle-experiments). First run `python3 scripts/fetch_results.py` to restore the pinned release before validating games or rebuilding analyses.

## Reproduction levels

| Goal | Required resources | Entry point |
| --- | --- | --- |
| Read and validate existing outcomes | Python 3.11; no credentials | `python3 scripts/results_catalog.py check` |
| Rebuild catalog summaries | Python 3.11; no credentials | `python3 scripts/results_catalog.py summarize` |
| Check a schedule without model calls | Python 3.11 | README planning commands |
| Generate fresh model trajectories | Provider credentials and API budget | Quickstart, with `--mode run` |
| Inspect a historical condition | Published frozen per-game files | `results/catalog.csv` and the game's directory |

## Experimental controls

CL fixes the target puzzle and compares no prior game, answer-only experience and full dialogue. The primary design reuses a fixed source experience across target repetitions. Its complete solution is supplied before the target, and the target receives a fresh allowance of 100 external actions. The README explicitly selects source puzzles 15, 14 and 28 for Set 1; puzzle 16 is an optional alternative.

The primary MAS comparison explicitly selects `solo,free_dialogue`. The team shares one external-action budget. The two players have separate ongoing sessions and investigator/critic roles. Role and scheduling ablations are available as command-line options. Explicit reflection is a separate exploratory condition; its output usage is reported with its results.

Model profiles, host packs, scoring rules and conversation handling are part of each condition. Use the checked-in profile for a fresh experiment and the frozen configuration when examining a historical run. New runs use unified v5 scoring. Historical outcomes keep their original annotation and completion rules.

The source relation recorded during a run and a later analysis interpretation can differ. In particular, the report's revised Set 2 grouping treats TS033 as positive and TS035 as negative; the original catalog labels are retained. Keep this distinction when rebuilding that comparison.

## Outcome measures

- **Story score:** weighted coverage of required story facts and causal links.
- **Complete solution:** under v5, full weighted credit; older runs retain their original decision.
- **External actions:** questions and answer submissions, including incorrect/incomplete submissions.
- **Usage:** per-role input/output tokens and available cost estimates. Unknown prices or usage remain unknown.

Summaries separate batches, sources and scoring versions. Source games, interrupted games and recovery aliases are not additional completed target repetitions. The scheduling seed controls local ordering; it does not fix a remote model's sampled responses. Fresh API runs can therefore produce different trajectories.

## Published evidence

The catalog restored as `results/catalog.csv` locates each original game. [Results documentation](../results/README.md) describes record formats. Analysis tables and dated interpretations are in `results/tables/` and `docs/analysis/`. Published records support reading and recalculating outcomes; exact execution checkpoints and repeated request bodies may reside in the full historical archive.

Repeated trials and a fixed CL source control two sources of variation. The main study covers three CL targets and three MAS puzzles; broader puzzle and model coverage remains future work.
