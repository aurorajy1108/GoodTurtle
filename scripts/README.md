# Scripts

English | [中文](README.zh-CN.md)

| Purpose | Entry point |
| --- | --- |
| Upload human references, validate the inbox, locate historical paths | `host_reference.py init / validate / locate` |
| Convert saved ChatGPT share HTML to visible-message JSON | `import_chatgpt_share.py` |
| Run games | `play.py` |
| Run CL and two-agent experiments | `experiment.py` |
| Run two-agent sweeps and freeze snapshots | `team_sweep.py` |
| Replay host or grader cases | `check_host.py` / `check_grader.py` |
| Render trajectory HTML | `render_trajectories.py` |
| Audit batch completeness | `audit_sweep.py` |
| Export an Excel review workbook | `export_host_review.py` (optional `openpyxl`; write to a new file rather than overwrite human edits) |
| Package or verify the private dataset and host packs | `experiment_bundle.py` |
| Historical three-label prototype and screening | `prepare.py`, `audit_screening.py`, `summarize_screening.py`, `summarize_pilot.py` |

Start with the [coworker quickstart](../docs/coworker_quickstart.md). The historical prototype is not the entry point for current four-label experiments. Use each script's `--help` for its options; see the documentation for complete parameters.
