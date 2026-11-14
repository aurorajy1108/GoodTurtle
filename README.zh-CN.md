# GoodTurtle — COMP1110

海龟汤题库、Host/Player/Grader自动对话，以及上下文经验迁移（CL）和多agent（MAS）实验。

[English](Readme.md) | 中文

|要做什么|入口|
|---|---|
|开始运行|[组员快速开始](docs/running/coworker_quickstart.md) · [每个参数](docs/running/runtime_parameters.md)|
|运行CL / MAS / 自查|[实验pipeline](docs/running/experiment_pipelines.md) · [组员批跑](docs/running/team_campaign_20261111.md) · [计算预算](docs/running/compute_matched_agents.md)|
|上传人工问答|[`data/host_reference/inbox/`](data/host_reference/inbox/README.zh-CN.md)|
|实际Host参考|[`data/host_packs/active/`](data/host_packs/README.md) 和 [`configs/host_bindings.json`](configs/host_bindings.json)|
|实验traj、分数、费用|[结果与轨迹索引](results/README.md)|
|研究结论|[旧新版综合分析](docs/analysis/all_versions_20261114.md) · [项目主线和过程证据](docs/analysis/project_story_20261114.md)|
|找旧文件、恢复旧页面|[目录结构与归档分支](docs/REPOSITORY_LAYOUT.md)|

## 运行

使用Python 3.11。API key放在环境变量或Git忽略的本地环境文件，模型设置在
[`configs/loop.deepseek.json`](configs/loop.deepseek.json)。完整命令和全部参数见[运行参数](docs/running/runtime_parameters.md)。

```bash
python3 scripts/play.py --help
python3 scripts/experiment.py --help
```

正式分工批次见[团队运行说明](docs/running/team_campaign_20261111.md)。
B每题重新获得100次提交额度，错误/不完整交卷也计数。旧实验使用自己的冻结版本，不追溯改分。

## 查看已有结果

不需要API key，不会调用模型：

```bash
python3 scripts/results_catalog.py list --puzzle TS038
python3 scripts/results_catalog.py check
python3 scripts/results_catalog.py summarize
```

每局可打开`trajectory.html`，或看`trajectory.md`和`trajectory.jsonl`。
双agent公开对话与私有自查也保留。汇总使用Markdown/CSV/JSON，不再提交整批可视化页面。

## 文件归属

- 运行代码：`turtle_loop/`、`scripts/`；模型/分组/prompt：`configs/`、`prompts/`。
- 题库与评分：`data/annotations/`；人工上传与审核：`data/host_reference/`；active Host：`data/host_packs/active/`。
- 当前说明：`docs/running/`；Host说明：`docs/host/`；分析正文：`docs/analysis/`。
- 正式实验：`results/trajectories/`；汇总与审核：`results/tables/`、`results/reviews/`。
- 本机运行：`runs/api/`，不自动加入Git。

清理前完整目录、可视化、重复快照和完整请求日志在
[`archive/full-repository-20261114`](https://github.com/aurorajy1108/GoodTurtle/tree/archive/full-repository-20261114)。
原问答、评分和Host输入不改写，人工确认与AI建议分开记录。

之前的长版运行说明和参数表保留在[完整CLI说明](docs/running/cli_reference.zh-CN.md)。
其中带日期的实验进度是历史快照；最新结果位置以[结果索引](results/README.md)为准。
