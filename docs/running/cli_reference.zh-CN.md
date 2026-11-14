**评分更新：** 新实验默认 v5，100% 与 complete、结束条件完全统一；旧结果不改写。[运行与验证说明](unified_scoring_v3.md)。

[English](cli_reference.md) | 中文

# GoodTurtle — COMP1110

**鲁棒恢复更新：** [Host标签格式归一化、空正文限次重试及旧CL/MAS续跑方法](host_output_recovery.md)。保留原始回答与费用，不重问Player、不重置额度；已有断点请按指南复制到新目录恢复。

## 自查与MAS的计算预算对照（一键运行）

更新main后，在终端export自己的`DEEPSEEK_API_KEY`，或写入忽略的`.env.local`，然后执行：

```bash
bash scripts/run_compute_matched_agents.sh runs/api/ts038_review_yourname_01
```

选择一个新目录；不需要下载本机历史run。脚本直接使用仓库里的TS038、Host参考包和DeepSeek配置，冻结后运行普通单agent、单agent自查、普通MAS、MAS自查，每组2次、最多2局并行。每局统一上限225次Player生成、77,696个输出token、100次外部提交；MAS两人共享计算预算。Player为Flash且关闭thinking，Host/Grader沿用配置中的Pro。实际token、缓存、费用另行记录。

输出的`index.html`可查看轨迹、公共对话、私有自查与统计。[全部参数和恢复方式](compute_matched_agents.md)。若只想准备计划而不调用API：`python3.11 scripts/compute_matched_agents.py prepare --out 输出目录`。

**11月13日结果发布：** [CL Set1四次重复](https://github.com/aurorajy1108/GoodTurtle/blob/c4ccc67eef8c09aa0c6987a464f468718f5015f4/results/20261113_verified_final/README.md)，直接打开[HTML轨迹索引](https://github.com/aurorajy1108/GoodTurtle/blob/c4ccc67eef8c09aa0c6987a464f468718f5015f4/results/20261113_verified_final/index.html)。CL已完成39/39局；[MAS已续跑完成8/8局](https://github.com/aurorajy1108/GoodTurtle/blob/c4ccc67eef8c09aa0c6987a464f468718f5015f4/results/20261113_mas_completed/README.md)，保留原截断私有笔记，剩余局在第84次提交以0%结束。结构、会话和费用核验通过，Host/Grader语义仍待人工复核。只汇总最新归档，避免续跑重复计数；[此前阶段分析](../archive/results/cl_set1_20261112/interpretation.zh-CN.md)保留作历史记录。

**MAS补至四次重复：** [最新已完成结果快照10/16局](https://github.com/aurorajy1108/GoodTurtle/blob/c4ccc67eef8c09aa0c6987a464f468718f5015f4/results/20261113_mas_r1r4_progress/README.md)，可直接打开[HTML轨迹](https://github.com/aurorajy1108/GoodTurtle/blob/c4ccc67eef8c09aa0c6987a464f468718f5015f4/results/20261113_mas_r1r4_progress/index.html)。本次新增单agent第4次（0%，100次提交）、MAS自查第3次（75%，81次提交）；未完成局单列，不进入成绩均值，旧局通过链接引用而非重复加总。

**组友远端结果分析：** [Set2两轮＋April的TS038正式实验](../archive/results/teammates_20261113/analysis.zh-CN.md)，固定main提交`6afda1c`核验28个唯一完成局。归档使用coverage-v2，Host、格式辅助模型和计算预算与当前默认配置不同，当前应分组报告而非直接合并。

**真实API测试修复：** [TS015方向判定、MAS首行契约、保存动作续跑、实时计数和DeepSeek费用](../archive/guides/live_test_repairs_20261111.md)。实测仍在进行，未宣称整批已通过。

**团队运行：** [三组CL+三道MAS，两人各两次的一键脚本](team_campaign_20261111.md)：6局小量测试、个人批跑、限并发全员150局与去重汇总。

**11月13日main同步：** 统一评分、鲁棒恢复、组友dashboard和归档已合并到main。[版本核对与旧实验边界](../archive/guides/main_sync_20261113.md)。pull后只有新准备的实验采用新版；已有冻结实验保留原代码和评分，不混算。

## 当前团队一键运行

使用 `main` 分支，在仓库根目录、已export自己 `DEEPSEEK_API_KEY` 的终端执行。各人的task IDs、全部参数、输出与合并方式见上面的团队指南。

```bash
git fetch origin
git switch main
git pull --ff-only
```

Jiayang的小量测试：4局CL＋2局MAS，最多1个槽位运行：

```bash
bash scripts/run_team_smoke.sh jiayang cl-set1-a,mas-ts038-a
```

Jiayang的正式实验：每条件两次重复，共21局CL＋4局MAS，最多2个槽位并行：

```bash
bash scripts/run_team_batch.sh jiayang cl-set1-a,mas-ts038-a 2
```

仅当一位协调人统一执行全员、其他人不另行启动时使用：

```bash
bash scripts/run_team_batch.sh coordinator all 4 runs/api/team_all_formal_v1
```

全员共150局，最多4个槽位并行：CL Set1–3共126局，MAS 38/2/14共24局。每个实验两人各跑两次，a/b是人工执行槽，不是模型Agent A/B。Set3第二人、MAS14第二人须各从候选中选一位；不要重复启动同一槽位。每个B独立100次额度，每个执行槽内部固定A并揭晓其完整答案；已有输出目录拒绝覆盖。

**11月11日新版本：** [CL会话续接与新返回格式运行指南](run_session_prefix_v1.md)，含新分支获取、Set1/TS038命令、参数、成本和恢复边界。

**历史Set1续跑：** `start_set1_auto_continue.sh`针对旧归档，不是新团队实验的启动命令。新批次停止后按[团队指南](team_campaign_20261111.md)对具体CL task恢复，保留额度、动作和费用；机制见[恢复说明](automatic_continuation.md)。

**11月10日Set1修复后重跑：** 在已export `DEEPSEEK_API_KEY`的终端执行`bash scripts/start_set1_verified.sh`。先冻结输入并跑20题Host诊断，全部通过才启动12局全新CL；本入口不跑MAS、不追加重复。已修复Host因果边界，并将持续会话中的参考内容按ID缓存。见[全部设置、参数和结果位置](../archive/guides/set1_v11_rerun.md)。

**当前默认DeepSeek：** `configs/loop.deepseek.json`中Host/Grader为 `deepseek-v4-pro / high`，Player/默认MAS partner为 `deepseek-flash / thinking disabled`。可选隔离格式修复器另行配置，没有Codex时如何只用本地修复见[团队指南](team_campaign_20261111.md)；供应商配置见[运行说明](deepseek.md)。

研究海龟汤中的上下文经验迁移（CL）与双 agent 合作。当前有 **50 道英文题目、161 个评分点**，支持可配置的 Host / player / grader、完整轨迹和实验统计。

**当前安排：CL Set1–3与MAS 38/2/14，两人各两次。** 收费对局须显式执行run脚本才启动。Host与评分标注仍待人工确认，单元测试通过不代表模型回答已经可靠。GPT模型设置保留在显式Codex配置中，不是当前团队脚本的默认设置。四种反馈：`yes / no / yes and no / irrelevant`。

11月3日起新批次：每个普通问题只调用一次Host；本地检索最多6条参考（6000字符），grader单独使用精简上下文、最多3条判例（3000字符）。每局每角色持续独立会话，增量更新上下文；Codex按thread ID续聊，Responses按response ID续聊，其余API本地维护多轮messages。可用 `session_mode: replay` 做独立重放对照。完整汤底、评分规则和当前对话历史仍保留，来源与审核元数据只存磁盘。持续会话不等于历史免计费；一般persistent中断不自动恢复；完整返回且仅有已支持的元数据或可确定修复的问题引号错误的DeepSeek单玩家响应，可在明确标记的新副本中恢复，见[恢复限制](deepseek.md#字符串text_note及一次性续跑)。配置见[完整参数](runtime_parameters.md)，设计与限制见[当前研究方案](../archive/guides/study_20261102.md)。旧冻结实验保持原策略。

新增可选 MAS 策略 [`free_dialogue`](mas_free_dialogue.md)：两名独立持续会话的 agent 共用公开聊天记录，自主选择提问、讨论、交卷和交接，并支持角色分工 ablation。用 `--strategies solo,free_dialogue` 选择；原四策略默认计划保留。

## 我应该去哪里？

| 任务 | 唯一入口 |
| --- | --- |
| 当前三组CL＋三道MAS的团队运行 | [分工、小量测试、个人正式跑、全员并行与汇总](team_campaign_20261111.md) |
| **上传人工 Host 参考 trajectory** | **[data/host_reference/inbox/](../../data/host_reference/inbox)**；[上传与审核流程](../../data/host_reference/README.md) |
| 查找已归档的人工聊天、回改和原始反馈 | [data/host_reference/sources/](../../data/host_reference/sources) |
| 查看／填写审核结论 | [data/host_reference/reviews/](../../data/host_reference/reviews)；[Excel审核表](../../data/host_reference/reviews/exports/20261026_host_review/host_review_20261026.xlsx) |
| 看 Host 现在实际使用哪些示例 | [data/host_packs/active/](../../data/host_packs/active)；绑定表 [configs/host_bindings.json](../../configs/host_bindings.json) |
| 同事开始跑实验 | [运行指南](coworker_quickstart.md) |
| 查全部命令／模型参数 | [对局与模型参数](runtime_parameters.md)；[CL / 双agent参数](experiment_pipelines.md)；[v7对照设计](../host/host_repair_v7.md) |
| 下一步做什么、哪些要人工check | [TODO与审核清单](../host/todo_human_review_20261027.md) |
| 找旧版本、旧报告 | [历史文档](../archive/README.md)；[运行目录说明](https://github.com/aurorajy1108/GoodTurtle/blob/c4ccc67eef8c09aa0c6987a464f468718f5015f4/runs/README.md) |

## 目录结构

```text
configs/                  模型配置、题目绑定、CL题对、路径迁移清单
data/
  annotations/turtle50_v5/ 当前50题统一评分与完成标准；v2/v3/v4供历史复现
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

检查角色映射和原文后，按正常Git流程提交这个文件夹。**放进inbox或push不等于进入Host prompt**：先审核，再将明确接受的示例整合到当前题的active包。完整流程和参数见 [Host reference指南](../../data/host_reference/README.md)。

## 运行与验证

从已配置模型账号开始，先离线预检：

```sh
python3 scripts/play.py run \
  --dataset data/annotations/turtle50_v5/private.json \
  --puzzle TS032 --config configs/loop.codex.json \
  --dry-run --out runs/api/my_preflight
python3 -m unittest discover -s tests -q
```

`--dataset` 指私有题库；`--puzzle` 指题号；`--config` 指模型配置；`--dry-run` 不调用模型；`--out` 必须为新目录。恢复实验后，按运行指南去掉 `--dry-run` 才会真正调用模型。接口也支持 OpenAI / Anthropic / DeepSeek 配置。

每局最多100次提交，第100次预留为强制final；错误或不完整final占一次，成功final另记。结果包含 `trajectory.html`、评分及调用成本。Host私有资料不得发送给player。CL当前是上下文经验迁移，不更新模型权重。

## 整理与兼容性

2026-10-28 整理只移动目录、更新绑定与入口；50题内容、评分、Host实际上下文及历史run不变。原有超长README完整保存在 [历史副本](../archive/README_before_cleanup_20261028.md)，完整参数另整理到当前指南。

旧审核/Excel中的路径保留为当时的来源记录，可用 `python3 scripts/host_reference.py locate OLD_PATH` 找新位置；映射见 [repository_layout.json](../../configs/repository_layout.json)。已有运行继续使用自己的冻结快照，不套用新目录重新解释旧结果。

Player 输出协议：新实验使用固定前缀，单 agent 与 MAS 的格式、兼容性和计数规则见 [player_action_protocol.md](player_action_protocol.md)。Host/Grader 格式保持不变。

CL 默认改为保留 A 原始角色消息、揭晓完整答案后续接 B；B 重新获得 100 次额度，每次重复从固定 A 前缀独立分支。[协议、对照与启动方式](cl_raw_session.md)
