# 仓库结构与文件去向

2026-11-14清理前的完整文件保存在
[`archive/full-repository-20261114`](https://github.com/aurorajy1108/GoodTurtle/tree/archive/full-repository-20261114)。
主分支保留可运行代码、题库、Host参考、正式轨迹与必要分析；移走重复快照、聚合可视化和重复请求body。没有重写Git历史。

```text
GoodTurtle/
├── turtle_loop/              # Host、Player、Grader、CL/MAS运行代码
├── configs/                  # 模型、实验分组、绑定与路径迁移表
├── prompts/                  # 运行prompt
├── data/
│   ├── annotations/          # 题目、汤底、评分规则及版本
│   ├── host_reference/
│   │   ├── inbox/            # 新人工问答上传；不会自动激活
│   │   ├── sources/          # 注册后的原始来源
│   │   └── reviews/          # 人工/AI审核及原Excel导出
│   └── host_packs/active/     # 实际绑定的每题Host参考
├── scripts/                  # 实验、恢复、参考审核和离线结果工具
├── tests/
├── docs/
│   ├── running/              # 运行方法与全部参数
│   ├── host/                 # Host审核和来源说明
│   ├── analysis/             # 综合结论、过程分析和审阅发现
│   └── archive/              # 历史设计与旧说明（文字）
├── results/
│   ├── trajectories/         # 按实验批次分组，每局只保留一份
│   ├── catalog.json / .csv   # 正式局、来源、状态和路径
│   ├── summary.json / .csv   # 分批次汇总，排除前题/附录/中断
│   ├── tables/               # 已发布分析的固定数据快照
│   ├── reviews/              # AI审阅原记录压缩包、疑点CSV和覆盖证明
│   └── plans/                # 历史分工/方向表
└── runs/api/                 # 本机新运行输出，Git忽略
```

## 保留什么

每局保留原`trajectory.jsonl`、`trajectory.md`、单局`trajectory.html`、原始result、
冻结题本/评分点、配置/Host上下文/prompt、费用和API审计。
MAS另有共享对话；自查组另有私有自查记录。这些属于trajectory，继续保留。
原始question/feedback/result/config/puzzle字节和分数通过哈希核验。

`api_audit.jsonl.gz`保留每次返回、错误、usage与accounting；大段重复请求body只存哈希，
完整body在归档分支。发布目录是审阅归档，不能冒充完整可续跑的原本机runtime。

## 哪些转入归档分支

- `index.html`、整批筛选仪表盘、round comparison、重复图表和预览截图。
- 910个本机快照、193份历史问答归档中的旧探索/重复恢复副本。
- 旧筛选、demo、preflight、旧冻结源码副本及完整重复HTTP请求。
- 旧report builder和对应整包可视化；科学结论正文与必要CSV/JSON仍在主分支。

保留一份正式trajectory不等于删除其他科学记录：完整旧目录可以按归档分支恢复。
`results/layout_migration.json`给出文件/目录映射，`archive_metadata.json`逐局给出来源、哈希和归档commit。
旧JSON里的原始路径属于历史provenance，保留原文；使用locator查它现在的位置。

## 找旧文件 / 恢复旧工作树

```bash
python scripts/results_catalog.py locate 'results/20261113_verified_final/mas/TS038_r01_solo/trajectory.jsonl'

git fetch origin archive/full-repository-20261114
git worktree add --detach ../GoodTurtle-full-archive FETCH_HEAD
```

第二条命令组在另一个文件夹恢复全量版本，不覆盖当前main，也不启动实验。
新增组友Set1两批数据已整理进`results/trajectories/cl_set1_teammate_*`；
其原始完整HTTP日志也在归档分支。它们未被静默加入旧的168档案分析快照。

## 保持结构整洁

- 人工问答：`data/host_reference/inbox/`，不要放`results/`或直接改active pack。
- 实验执行：本机`runs/api/`；冻结后按批次发布到`results/trajectories/`并登记catalog。
- 分析结论：`docs/analysis/`；用于分析的数字：`results/tables/`。
- 运行说明：`docs/running/`；全部参数仍保留在runtime/CLI reference文档。
- 聚合仪表盘和预览只本地生成，默认忽略；需要分享完整视图时用归档/展示分支。

删掉工作树文件不会立即减少已有`.git`历史。需要轻量新克隆时：

```bash
git clone --depth 1 --single-branch --branch main https://github.com/aurorajy1108/GoodTurtle.git
```
