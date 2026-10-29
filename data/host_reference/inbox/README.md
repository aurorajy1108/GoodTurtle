# Upload human reference trajectories

English | [中文](README.zh-CN.md)

For one puzzle, use `TS032/20261028_chat01/source.json` and `trajectory.md` (text, JSON, JSONL and CSV are also supported). For a conversation covering multiple puzzles, use `multi/20261028_chat01/` and list all puzzle IDs in `source.json`.

Create a directory with `python3 scripts/host_reference.py init --puzzle TS032 --source-id 20261028_chat01`, then paste the complete conversation. Include the full record, not just a link or selected answers. Run `python3 scripts/host_reference.py validate` after filling it in.

See the [reference guide](../README.md) for the full process. Uploads remain in the inbox with pending status and **are not automatically added to the host**.
