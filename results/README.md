# 实验结果与trajectory

主分支保留206份正式轨迹（含前题、附录与三局技术中断／评分冲突），按批次各存一份。原分和冻结设置不改写。

[全部逐局CSV](catalog.csv) · [机器可读目录](catalog.json) · [分条件汇总CSV](summary.csv) · [目录与归档规则](../docs/REPOSITORY_LAYOUT.md)

[最新分析：206局、新增39局及结论修订](../docs/analysis/latest_results_20261114.md)。本次新整合15局Set3答案条件；另外24局Set1此前已收录，现纳入正文分析。旧168档案分析表保留为历史快照，当前全量数字见[最新更新表](tables/20261114_latest_update/README.md)。

|批次|归档局数|完整结束|轨迹目录|
|---|---:|---:|---|
|April_TS038_v9|9|8|[Markdown索引](trajectories/mas_ts038_april_v9/README.md)|
|Set3_answer_only_20261114|15|14|[轨迹与分列得分](trajectories/cl_set3_answer_only_20261114/README.md)|
|Set1_unified|39|39|[Markdown索引](trajectories/cl_set1_unified/README.md)|
|Set2_extra2_v13|4|4|[Markdown索引](trajectories/cl_set2_extra2/README.md)|
|Set2_legacy_round1|12|12|[Markdown索引](trajectories/cl_set2_legacy_round1/README.md)|
|Set2_legacy_round2|12|12|[Markdown索引](trajectories/cl_set2_legacy_round2/README.md)|
|Set2_v17|38|38|[Markdown索引](trajectories/cl_set2_v17/README.md)|
|T22_T42_20261114|37|37|[Markdown索引](trajectories/ts022_ts042_20261114/README.md)|
|TS038_v14_2x2|16|15|[Markdown索引](trajectories/mas_ts038_v14/README.md)|
|cl_set1_teammate_20261111|12|12|[Markdown索引](trajectories/cl_set1_teammate_20261111/README.md)|
|cl_set1_teammate_20261113|12|12|[Markdown索引](trajectories/cl_set1_teammate_20261113/README.md)|

## 每局保存的内容

- `trajectory.jsonl`：完整原事件；`trajectory.md` / `trajectory.html`：直接读对话。
- `result.json`：原始分数、完成状态与计数。
- `config.json`、`prompts.json`、`puzzle_private.json`、`host_context.json`：冻结模型/提示/评分与Host事实（源有则保留）。
- `api_audit.jsonl.gz`、`cost_summary.json`、`token_costs.csv`：各次返回、错误、usage与费用；重复请求body只存哈希。
- MAS有`shared_dialogue.jsonl/html`；自查组有`self_review.html`和相应原记录。
- `archive_metadata.json`：原路径、文件哈希、完整归档分支和精简策略。

公开归档不是完整可续跑的原runtime；原HTTP body和检查点在[完整归档分支](https://github.com/aurorajy1108/GoodTurtle/tree/archive/full-repository-20261114)。不要把恢复副本当重复实验。

## 离线查找与核验

```bash
python scripts/results_catalog.py list --puzzle TS038
python scripts/results_catalog.py list --cohort Set2_v17 --condition session
python scripts/results_catalog.py check
python scripts/results_catalog.py summarize
python scripts/results_catalog.py locate 'reports/20261114_joint_trajectory_review/index.html'
```

|参数/命令|含义|
|---|---|
|`list`|输出已登记的逐局结果与目录|
|`--cohort`|按catalog中的suite全名过滤|
|`--puzzle`|按题号过滤，例如TS038|
|`--condition`|按条件名过滤，例如session|
|`check`|核验冻结文件、原结果/计数与gzip审计格式；不认证语义正确|
|`summarize`|更新summary.json/CSV；排除前题、附录、重复及未完成结果，按批次分开|
|`locate PATH`|输入仓库相对旧路径，返回当前位置或归档URL；不允许`..`|
|`-h` / `--help`|查看命令帮助|

## 分析与人工复核

- [旧新版综合分析](../docs/analysis/all_versions_20261114.md)与[固定分析表](tables/20261114_all_versions/)。
- [项目主线与过程证据](../docs/analysis/project_story_20261114.md)与[Set1过程表](tables/20261114_transfer_process/)。
- [轨迹审阅报告](../docs/analysis/trajectory_review_20261114.md)与[待复核CSV](reviews/20261114/review_questions_only.csv)。
- AI逐问审阅原记录压缩在`reviews/20261114/question_reviews.jsonl.gz`，不是人工gold。
- 新收到的两批组友Set1数据在`cl_set1_teammate_*`，保留原始状态；未静默混入旧168档案分析快照。

## 新结果放哪里

新运行先保存在本机`runs/api/`。正式发布时按批次放入`results/trajectories/COHORT/GAME/`，登记catalog并运行check；本机原始日志、完整请求、恢复副本和批次可视化不加入主分支。人工参考问答请放`data/host_reference/inbox/`，不放这里。旧导出脚本仍可用于本机归档，结果进入主分支前遵循此结构。
