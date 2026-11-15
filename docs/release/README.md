# English release cleanup

**HF migration completed:** full records now live in [GoodTurtle-experiments](https://huggingface.co/datasets/COMP1110-20261A-Group50/GoodTurtle-experiments). The original cleanup below describes the archived evidence. The current GitHub tree keeps summaries and a pinned download descriptor; run `python3 scripts/fetch_results.py` to restore all records.

The public release uses a single `main` branch. Original development history and the pre-cleanup snapshot remain reachable from `main`. The existing experiment worktrees, credentials and report backups are untouched.

## Presentation audit

Every checked-in HTML file was inspected. [File-by-file inventory](html_inventory.json):

| Type | Files | Release decision |
| --- | ---: | --- |
| Rendered game trajectories | 191 | Remove; retain original JSONL and readable Markdown |
| Shared-dialogue pages | 23 | Remove; preserve JSONL and extract visible notes to Markdown |
| Private self-review pages | 16 | Remove; extract every visible note to Markdown; preserve API audit |
| Local live progress interface | 1 | Keep as functional runtime UI |

Eight reflection pages were empty templates from ordinary games; their Markdown replacements state that no reflection notes were present. The remaining reflection notes and all shared messages are retained in full.

The original HTML is recoverable from the parent commit. It is no longer included in the release tree. Generated local exports may still be produced when running experiments; Git ignores them.

## Data policy

The 206 catalog entries remain in their existing canonical cohort/game directories. No question, answer, score, completion flag, source identity, role assignment or token record was altered. Existing archive metadata now explicitly identifies removed presentations and their retained replacements. The catalog checker continues to verify the original scientific records and rejects missing replacement files.

Release navigation and the quickstart are English. Source conversations, raw model messages, annotations and dated research notes retain their original language. Translation is not applied to experimental evidence.

## Checks

```bash
python3 scripts/results_catalog.py check
python3 scripts/release_check.py
python3 -m unittest discover -s tests
```

Validation output is saved in `validation.json`. No model calls are needed for these checks. This cleanup does not incorporate unfinished runs or uncommitted experimental code from other worktrees.
