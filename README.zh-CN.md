[English](Readme.md) | 中文

# GoodTurtle — COMP1110

研究海龟汤中的上下文经验迁移（CL）与双 agent 合作。当前有 **50 道英文题目、161 个评分点**，支持可配置的 Host / player / grader、完整轨迹和实验统计。

**当前状态：实验暂停。** Host 与评分标注仍待人工确认；单元测试通过不代表模型回答已经可靠。默认请求 Host / grader `gpt-6.1-sol / high`，player `gpt-6-luna / high`。四种反馈：`yes / no / yes and no / irrelevant`。

## 我应该去哪里？

| 任务 | 唯一入口 |
| --- | --- |
| **上传人工 Host 参考 trajectory** | **[data/host_reference/inbox/](data/host_reference/inbox/)**；[上传与审核流程](data/host_reference/README.md) |
| 查找已归档的人工聊天、回改和原始反馈 | [data/host_reference/sources/](data/host_reference/sources/) |
| 查看／填写审核结论 | [data/host_reference/reviews/](data/host_reference/reviews/)；[Excel审核表](outputs/20261026_host_review/host_review_20261026.xlsx) |
| 看 Host 现在实际使用哪些示例 | [data/host_packs/active/](data/host_packs/active/)；绑定表 [configs/host_bindings.json](configs/host_bindings.json) |
| 同事开始跑实验 | [运行指南](docs/coworker_quickstart.md) |
| 查全部命令／模型参数 | [对局与模型参数](docs/runtime_parameters.md)；[CL / 双agent参数](docs/experiment_pipelines.md)；[v7对照设计](docs/host_repair_v7.md) |
| 下一步做什么、哪些要人工check | [TODO与审核清单](docs/todo_human_review_20261027.md) |
| 找旧版本、旧报告 | [历史文档](docs/archive/README.md)；[运行目录说明](runs/README.md) |

## 目录结构

```text
configs/                  模型配置、题目绑定、CL题对、路径迁移清单
data/
  annotations/turtle50_v4/ 当前50题汤底与评分标准；v2/v3供历史复现
  host_reference/         人工参考资料（上传不会自动改变Host）
    inbox/                按 TSxxx/source_id 收新上传；多题一份放 multi/
    sources/              已登记的完整原文、消息ID、分段与规范化问答
    reviews/              裁决、冲突、改写及来源证据
  host_packs/
    active/               当前50题实际加载的包，每题一个TSxxx.json
    archive/              以前的版本与候选包，保留来源/哈希供追溯
    local/                本地未发布研究包（Git忽略）
prompts/                  当前loop的host/player/grader/review提示
  archive/                历史提示（含旧三标签host）
turtle_loop/              对局、共享buffer、CL、评分、provider实现
scripts/                  运行、导入、验证和报告命令
tests/                    离线回归与集成测试
runs/                     模型实验轨迹；旧局和runtime_snapshot保持原样
outputs/                  可交付的Excel等报告
docs/                     当前操作/研究文档；archive/保存旧说明
```

## 上传一份人工 trajectory

在仓库根目录执行：

```sh
python3 scripts/host_reference.py init \
  --puzzle TS032 --source-id 20261028_chat01 \
  --file /path/to/conversation.md
python3 scripts/host_reference.py validate
```

得到 `data/host_reference/inbox/TS032/20261028_chat01/`，里面是原文 `trajectory.md` 和来源信息 `source.json`。没有文件时省略 `--file`，生成待填写模板；分享链接可加 `--source-url`（只记录，不自动访问）。一个聊天涉及多题时写 `--puzzle TS032,TS034`，目录自动放在 `inbox/multi/`。

检查角色映射和原文后，按正常Git流程提交这个文件夹。**放进inbox或push不等于进入Host prompt**：先审核，再将明确接受的示例整合到当前题的active包。完整流程和参数见 [Host reference指南](data/host_reference/README.md)。

## 运行与验证

从已配置模型账号开始，先离线预检：

```sh
python3 scripts/play.py run \
  --dataset data/annotations/turtle50_v4/private.json \
  --puzzle TS032 --config configs/loop.codex.json \
  --dry-run --out runs/api/my_preflight
python3 -m unittest discover -s tests -q
```

`--dataset` 指私有题库；`--puzzle` 指题号；`--config` 指模型配置；`--dry-run` 不调用模型；`--out` 必须为新目录。恢复实验后，按运行指南去掉 `--dry-run` 才会真正调用模型。接口也支持 OpenAI / Anthropic / DeepSeek 配置。

每局最多100次提交，第100次预留为强制final；错误或不完整final占一次，成功final另记。结果包含 `trajectory.html`、评分及调用成本。Host私有资料不得发送给player。CL当前是上下文经验迁移，不更新模型权重。

## 整理与兼容性

2026-10-28 整理只移动目录、更新绑定与入口；50题内容、评分、Host实际上下文及历史run不变。原有超长README完整保存在 [历史副本](docs/archive/README_before_cleanup_20261028.md)，完整参数另整理到当前指南。

旧审核/Excel中的路径保留为当时的来源记录，可用 `python3 scripts/host_reference.py locate OLD_PATH` 找新位置；映射见 [repository_layout.json](configs/repository_layout.json)。已有运行继续使用自己的冻结快照，不套用新目录重新解释旧结果。
