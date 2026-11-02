# Host reference review — 2026-10-30

This revision adds reviewed references to the active Host and preserves the source
conversations separately. It does not start new games, alter recorded performance,
or claim a measured improvement in Host accuracy.

## Active changes

| Puzzle | Change | Key boundary |
| --- | --- | --- |
| TS031 | 28 examples added | Remove eraser → refill inside mechanical pencil → write; no invented external supporting apparatus |
| TS035 | 32 examples added | Fear versus confirmed future event; rare attacks versus zero risk; avoid contradictory rankings of grief and harm to remains |
| TS038 | 42 examples added | Writer versus forged author/recipient; concealment versus alibi; preparing a note versus sending additional messages |
| TS033 | 1 existing label corrected | Adding genuine notes conceals fake bundles; the high ransom amount does not validate the wrong causal explanation |

These four packs and their bindings now use `host-v8-reviewed-20261030`.
The primary and independent-review prompts also remind the Host to preserve
modality, referents and evidence in the opening. All other pack contents and
the dataset scoring rubrics remain unchanged.

The 102 added examples contain 81 original questions and 21 explicit standalone
rewrites. Original wording and replies remain in provenance and in the audit.
They have empty example histories because the selected wording is self-contained;
the full hundred-turn histories are not repeatedly pasted into the Host prompt.
Cases with unresolved meaning are withheld in their original form. A corrected
standalone rewrite being active does not certify the original question/label.

The active Host loads these examples for its current puzzle through
`configs/host_bindings.json`. This is prompt context, not weight training and not
retrieval over the inbox. Both verification passes receive the updated context.

## Audit coverage and review artifact

[Download the workbook](../outputs/20261030_host_reference_audit/host_reference_audit.xlsx).

- 109 previously active user-history examples checked against the current stories.
- All 300 actions in the new TS031/035/038 runs reviewed: 278 questions and 22
  incomplete/incorrect final submissions. Each run used all 100 actions. Finals
  are kept as evaluation records, not imported as ordinary Host question examples.
- 689 visible actions in 17 inbox uploads checked, including non-label responses,
  controls and unanswered tails. Those uploads have not been activated wholesale.
- 180 current review flags: these include semantic ambiguity, unsupported details,
  contradictions and protocol problems, **not 180 established errors**.
- 44 earlier shared-conversation issues are carried forward on a separate sheet.
  This is not a new complete certification of all older raw shared messages.

Start with **本轮疑点**, filter priority **高**, and fill the yellow human decision,
label and note columns. Each flagged row includes the question, original reply,
proposed label if decidable, reason, puzzle opening, full current Host solution and
source. **三题逐条审核**, **Active人工参考** and **Inbox逐条记录** preserve ordering
and stable IDs for reading surrounding turns. **Active变更** lists the actual
new/corrected questions. Blank proposed labels mean split/rephrase or adjudicate,
not that a correction has been silently supplied.

Examples to prioritize: TS007's `mammal=no`; TS015's aircraft branch; TS042's hammer
branch despite the knife-throwing solution; TS002's arm replies under the required
strict hand/arm distinction; TS035's contradictory answers to nearly identical
questions about emotional distress; TS038's unsupported later communications.

One earlier TS038 flag about disappointment is retracted: the opening explicitly
says “You've disappointed me so much”. TS035 Q70 was actually **no**, not yes;
the workbook records the original value and compares it with Q68=yes.

The supplied `6ae46825` ChatGPT share was previously inaccessible (403); no new
messages from that URL are claimed as evidence in this audit.

## Provenance and reproducibility

The display term is “reviewed reference Q&A / 已审核参考问答”. Model-generated
sources remain identified in provenance; review does not turn them into human
authorship or human confirmation. `human_confirmed` remains false. The user-supplied
originals, old audit reports, old Excel and frozen run snapshots are unmodified.

`data/host_reference/reviews/audit_20261030/` contains:

- `baseline/`: the 50 pre-review active packs and bindings, frozen for comparison.
- `activation.json`: all 103 changes, originals, selected examples, source hashes
  and before/after context hashes for all 50 puzzles.
- `review.json`: all 1,098 reviewed records and source coverage.

To rebuild a new workbook without overwriting someone's filled-in version:

```sh
python3 -m pip install openpyxl
python3 -m scripts.audit_host_references_20261030 --out /tmp/host_review_copy.xlsx
```

| Option | Meaning |
| --- | --- |
| `--out PATH` | New XLSX path; defaults to the published 20261030 workbook; refuses an existing file |
| `--preview` | Also generate representative PNG previews next to the workbook; requires Pillow and macOS PingFang font |
| `-h`, `--help` | Show help |

The exporter regenerates the machine-readable `review.json` from frozen inputs
and the active revision manifest; it does not read human edits from Excel or modify
Host packs. Do not edit that generated JSON as a replacement for a new review.
`scripts.activate_host_review_20261030.py` is the already-applied, one-time activation
script; it refuses to run again when its manifest exists. Future human decisions
should be recorded and applied as a **new** version, preserving this one.

Validation: `python3 -m unittest discover -s tests -q` passes 100 offline tests.
Tests verify original source hashes, reconstruct the frozen pre-review contexts,
check all current bindings, ensure every adopted example reaches the runtime Host,
and preserve actual provenance and unanswered/control records. The XLSX exporter
round-trips full flagged questions/reasons and verifies row counts and cached
summary counts; representative workbook previews were inspected.

An independent held-out Host label evaluation is still needed to measure accuracy.
Replaying the newly added few-shot examples would not be such a measurement.
