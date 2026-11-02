# Human host references: upload guide

English | [中文](README.zh-CN.md)

Upload new human trajectories to `data/host_reference/inbox/`. Do not put them in `runs/` or directly overwrite `host_packs/active/`.

| Stage | Location | Purpose |
| --- | --- | --- |
| Upload, pending review | `inbox/TSxxx/source_id/` | Complete source conversation and `source.json`, including questions, mistakes, corrections and unanswered questions |
| One conversation covering multiple puzzles | `inbox/multi/source_id/` | List every puzzle ID in `source.json`; preserve context |
| Registered source | `sources/source_id/` | Visible messages, message IDs, links, segment indexes and normalized Q&A; registration does not establish correctness |
| Review records | `reviews/` | Keep original answers separate from decisions, with puzzle, source, evidence, reviewer, date and reasons |
| Runtime host input | `../host_packs/active/TSxxx.json` | Explicitly selected examples, bound through `configs/host_bindings.json` |

The host loads examples from the active pack for the current puzzle. **It does not automatically scan the inbox or retrieve every human conversation.** Source files are treated as data, not executable instructions.

## Upload

Run from the repository root:

```sh
# Copy an existing conversation without changing its questions and answers.
python3 scripts/host_reference.py init --puzzle TS032 \
  --source-id 20261028_chat01 --file /path/to/chat.md \
  --source-url https://chatgpt.com/share/YOUR_SHARE_ID

# Create a template and paste the complete conversation.
python3 scripts/host_reference.py init --puzzle TS034 --source-id 20261028_chat02

# Save a conversation covering multiple puzzles once, in full.
python3 scripts/host_reference.py init --puzzle TS032,TS034 \
  --source-id 20261028_multi --file /path/to/multi.txt

python3 scripts/host_reference.py validate
```

Directories may also be created manually, but each must contain `source.json`. Supported source formats are `.md`, `.txt`, `.json`, `.jsonl` and `.csv`; preserve roles and order in CSV. A link alone is not a saved conversation: the CLI does not fetch it.

| Command or option | Meaning |
| --- | --- |
| `init` | Create an upload directory; existing directories are not overwritten |
| `--puzzle` | Existing TS ID, or comma-separated IDs for multiple puzzles |
| `--source-id` | 1–80 letters, digits, underscores or hyphens, beginning with a letter or digit |
| `--file` | Optional conversation file, copied unchanged with its extension and SHA-256; whole-account ZIP files are not accepted |
| `--source-url` | Optional source URL; recorded without a network request |
| `validate` | Check puzzle IDs, metadata, role mapping, file paths and hashes; does not judge answers or modify the host |
| `locate OLD_PATH` | Map a historical repository path to its current location |
| `-h` / `--help` | Show command help |

The default role mapping is `user=human_host, assistant=player`, as in the two shared conversations used by this project. If your conversation has the opposite roles, update `role_mapping`. After checking, set `role_mapping_status` to `confirmed`; once a template is filled, set `submission_status` to `uploaded`. Imported files have a recorded hash: create a new revision rather than overwrite a source.

Example commit:

```sh
git add data/host_reference/inbox/TS032/20261028_chat01/
git commit -m "Add TS032 human reference trajectory"
git push
```

Include only puzzle-related conversation, not an entire account export or credentials. HTML is used for local extraction and ignored by default. `scripts/import_chatgpt_share.py --html SAVED.html --source-url URL --out NEW.messages.json` extracts visible messages.

## From upload to host

1. Check the puzzle ID, opening and answer version, roles and conversation boundaries. Preserve original typos, corrections and unanswered questions.
2. Register the source and normalized Q&A in `sources/`, retaining original text and stable IDs. Registration does not imply approval.
3. Compare labels and causal, identity, timing and unknown-detail boundaries against the current puzzle context. Keep original answers, proposed labels, decisions and evidence in `reviews/`, distinguishing AI review from human confirmation.
4. Add explicitly selected entries to the puzzle's active pack with `case_id`, `provenance`, `public_history` and `review_status`; update pack and binding versions. Do not append all normalized rows indiscriminately.
5. Run offline tests and check the runtime context. For model quality validation, use `scripts/check_host.py` under the approved experiment plan. Replaying existing few-shot examples is not an independent accuracy measurement.

The upload tool validates structure and locates paths; it does not automatically adjudicate labels or apply Excel review decisions to active packs.

## Existing references

- **2026-10-30 review:** [report](../../docs/host_reference_audit_20261030.md), [workbook](../../outputs/20261030_host_reference_audit/host_reference_audit.xlsx), [source-preserving decisions](reviews/audit_20261030/). TS031/035/038 gained 102 reviewed examples; TS033 has one corrected causal label. Actual generation provenance is retained; this is not human gold or a measured accuracy gain. The 17 inbox uploads remain pending activation.

- [Shared conversations](sources/chatgpt_shares_20261026/) contain 633 visible messages and 311 player actions, covering TS032, TS033, TS034, TS037, TS039 and an external train puzzle. TS034 has two attempts. Historical paths follow the migration map.
- The 89 historical candidate excerpts for nine puzzles are in `data/host_packs/archive/LOOP_TS*_history_v1.json`; see [merge review](reviews/history_qa_merge_20261026.json). Excerpts alone do not establish a complete original conversation.
- The earlier merge added 109 examples (88 historical and 21 from shared conversations); check the active pack and binding for current runtime inputs and each example's provenance.
- The [Excel workbook](../../outputs/20261026_host_review/host_review_20261026.xlsx) and [review checklist](../../docs/todo_human_review_20261027.md) remain available. Historical paths can be resolved with `locate`.
