# Set3 answer-only — TS022, five repeats per source

[逐局得分 / Scores](scores.csv)

Fifteen independent target games: TS047 (hypothesized positive), TS045 (hypothesized negative), and TS019 (irrelevant), five repeats each. These labels are experimental hypotheses, not observed effects. Each Player receives only the fixed source opening and revealed source answer in a fresh target session; no source dialogue is inherited. Source A and baseline games were not rerun. The first three pilot games are included exactly once, followed by twelve additional games.

All games used a 100-interaction budget. Player: `deepseek-flash`, thinking disabled, max output 8192; Host/Grader: `deepseek-v4-pro`, thinking enabled/high, max output 32768. Host: `host-v9-human-20261102`. Grading: `coverage-v3-unified`, C1/C2/C3 weights 50/30/20. Target context SHA256: `5d44680f053ed1c15963a67180e489f6280a408a8977dbd1a644f7f922badcfc`. Fixed source games and the matching session condition are archived in [the earlier Set3 batch](../ts022_ts042_20261114/README.md).

**14 games completed online; one reached 100 submissions with an unresolved online grading conflict. No game was solved online.** For TS047 repeat 3, the original Grader checkpoints imply 35%, while its coverage completion implies 50%. The controller rejected their inconsistency. The assistant's [separate offline adjudication](reviews/TS047_r03_final_review.md) gives 50%, unsolved, under the previously declared broad partial-credit rule. It is not human gold or an accepted online grade. Original `result.json` remains `error` with a null final score; no additional model call was made to replace the grade.

TS019 repeat 4 resumed from 89 completed interactions using the saved, verbatim typed question for interaction 90 under the existing `last_complete` policy. Its original calls were not regenerated; prior events and recovery events remain in the trajectory. Host, grading settings and budget were unchanged.

The three pilot games already had an assistant offline review: TS047 90%, TS045 40%, TS019 40% (online scores 90%, 40%, 0%). These are separately listed in `offline_final_score`; all other repeats except the disputed TS047 R3 have not been uniformly offline adjudicated. Do not mix selectively reviewed scores into an aggregate treatment mean. Catalog and global summary always use accepted raw online scores and exclude the errored game from completed-game means. Full discovery/Host-quality review of the twelve new games is not included here.

Only trajectories, scoring records, a small integrity manifest per game, and this score index are published. JSONL and original result files are byte-identical to the local run; Markdown is rendered from all 100 submitted actions and accepted feedback. No HTML, dashboards, full API request logs, runtime snapshots, recovery copies, credentials, or runnable-code changes are included. Cost columns are API usage estimates, not invoices.

## 归档说明

每种来源5局，共15局；前3局仅计一次。14局在线正常结束，另1局交互已结束但在线评分冲突。CSV分列保留在线原分与助手离线复核分；空白复核分表示尚未统一复核，不能混算。离线50%不表示解出画像误认的核心诡计。恢复局和评分冲突均保留原始事件，不作为新的独立重复。

| Source | Repeat | Online status | Online final | Offline final | Complete trajectory |
|---|---:|---|---:|---:|---|
| TS047 | 1 | completed | 90% | 90% | [trajectory](TS022_after_TS047_answer_only_r01/trajectory.md) |
| TS045 | 1 | completed | 40% | 40% | [trajectory](TS022_after_TS045_answer_only_r01/trajectory.md) |
| TS019 | 1 | completed | 0% | 40% | [trajectory](TS022_after_TS019_answer_only_r01/trajectory.md) |
| TS047 | 2 | completed | 90% | — | [trajectory](TS022_after_TS047_answer_only_r02/trajectory.md) |
| TS045 | 2 | completed | 40% | — | [trajectory](TS022_after_TS045_answer_only_r02/trajectory.md) |
| TS019 | 2 | completed | 25% | — | [trajectory](TS022_after_TS019_answer_only_r02/trajectory.md) |
| TS047 | 3 | error | — | 50% | [trajectory](TS022_after_TS047_answer_only_r03/trajectory.md) |
| TS045 | 3 | completed | 40% | — | [trajectory](TS022_after_TS045_answer_only_r03/trajectory.md) |
| TS019 | 3 | completed | 0% | — | [trajectory](TS022_after_TS019_answer_only_r03/trajectory.md) |
| TS047 | 4 | completed | 10% | — | [trajectory](TS022_after_TS047_answer_only_r04/trajectory.md) |
| TS045 | 4 | completed | 0% | — | [trajectory](TS022_after_TS045_answer_only_r04/trajectory.md) |
| TS019 | 4 | completed | 35% | — | [trajectory](TS022_after_TS019_answer_only_r04/trajectory.md) |
| TS047 | 5 | completed | 85% | — | [trajectory](TS022_after_TS047_answer_only_r05/trajectory.md) |
| TS045 | 5 | completed | 50% | — | [trajectory](TS022_after_TS045_answer_only_r05/trajectory.md) |
| TS019 | 5 | completed | 25% | — | [trajectory](TS022_after_TS019_answer_only_r05/trajectory.md) |
