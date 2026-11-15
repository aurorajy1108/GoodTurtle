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
| List, verify and summarize published games; find an old result path | `results_catalog.py list / check / summarize / locate` |
| Rebuild current analysis and pinned historical tables without dashboards | `analyze_latest_results.py`, `build_all_versions_summary.py`, `analyze_transfer_process.py` |
| Historical three-label prototype | `prepare.py`, `summarize_pilot.py`; retired screening scripts are on the [archive branch](https://github.com/aurorajy1108/GoodTurtle/tree/archive/full-repository-20261114/scripts) |

Start with the [coworker quickstart](../docs/running/coworker_quickstart.md). The historical prototype is not the entry point for current four-label experiments. Use each script's `--help` for its options; see the documentation for complete parameters.
