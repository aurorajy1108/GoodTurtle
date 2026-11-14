# Analysis tables

[`20261114_latest_update/`](20261114_latest_update/README.md) contains the current 206-game inventory, separated condition/source summaries and notes on the 39 additions since the previous analysis. Rebuild with `python scripts/analyze_latest_results.py`.

`20261114_all_versions/` is the pinned 168-archive analysis population, not the latest catalog count. `20261114_transfer_process/` contains the 36-game Set1 process analysis and verbatim early turns. Outcomes remain original.

Offline rebuild: `python scripts/build_all_versions_summary.py` and `python scripts/analyze_transfer_process.py`. These generate CSV/JSON only. The old scientific figure and visualization builders remain on the full archive branch.
