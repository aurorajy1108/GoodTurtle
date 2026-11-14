# 新版本运行指南：CL 原始会话续接 + Player 纯文本协议

当前默认分支：`main`（11月13日已合入统一评分与恢复修复）。本版同时兼容新的返回格式与 CL 原始会话续接。Python 3.10+，实验 loop 只使用标准库，无需模型 SDK。以下命令在仓库根目录执行。

## 获取与配置

首次下载：

```bash
git clone --branch main \
  https://github.com/aurorajy1108/GoodTurtle.git
cd GoodTurtle
```

已有 clone：

```bash
git fetch origin
git switch main
git pull --ff-only
```

已在main时用 `git pull --ff-only`。保留自己未提交的改动，不使用强制覆盖。在启动实验的同一个终端设置 key；已经 export 的终端无需重设：

```bash
export DEEPSEEK_API_KEY='YOUR_OWN_KEY'
```

key 不加入 Git。默认配置 `configs/loop.deepseek.json`：Host/Grader 为 `deepseek-v4-pro`，thinking enabled、reasoning high；Player/默认 Partner 为 `deepseek-flash`，thinking disabled、不传 reasoning_effort。三者共用 DEEPSEEK_API_KEY，不自动替换模型。

辅助格式器沿用 `configs/player_format_repair.json` 的可选 Codex CLI 配置，本地不能恢复格式时才使用，最多每局3次并独立记账。无 Codex 的机器可在冻结新批次前将 `max_codex_calls_per_game` 设为0：本地修复仍启用，无法确定的输出停止待审，不假装已修复。

## CL Set1：计划与实际运行

先只生成计划，零模型调用，无需 key：

```bash
python3 scripts/run_set1_verified.py --mode plan \
  --out runs/api/my_set1_prefix_plan
```

实际运行必须用另一个新目录，在已 export key 的终端执行：

```bash
bash scripts/start_set1_verified.sh runs/api/my_set1_prefix_once
```

同一冻结快照先做20次 Host 诊断，全部通过才开始12局 CL：

| 阶段/条件 | 局数 | 内容 |
| --- | ---: | --- |
| source | 3 | A=15（positive）、14（negative）、28（neutral），各做一次，不选16 |
| direct | 3 | 各方向独立新会话，直接做 B=13 |
| session | 3 | 从固定 A 原始 Player 消息链分支，揭晓完整答案后做 B=13 |
| answer_only | 3 | 新会话只接收 A 汤面与完整答案，再做 B=13 |

每条件一次，repeat=1，无 MAS。A 失败也保留并揭晓答案，不筛选成功 A。每个 B 从0获得新的100次额度，不看到其他 B 的轨迹；第100次必须 FINAL。问题及错误/不完整交卷各消耗1次，成功交卷单独记录。

启动脚本仅有一个可选位置参数：新输出目录。省略时用 `runs/api/20261111_deepseek_set1_raw_session_once`。已有输出、日志或 PID 文件拒绝覆盖。脚本后台运行；要前台运行或自选配置：

```bash
python3 scripts/run_set1_verified.py --mode run \
  --config configs/loop.deepseek.json \
  --dataset data/annotations/turtle50_v5/private.json \
  --seed 20261102 --out runs/api/my_set1_prefix_foreground
```

| verified 参数 | 默认 | 含义 |
| --- | --- | --- |
| `--mode` | plan | plan只冻结；run先诊断再实验 |
| `--out` | 必填 | 新目录，拒绝覆盖；plan和run不共用同一目录 |
| `--config` | configs/loop.deepseek.json | 全角色模型配置，冻结后不变 |
| `--dataset` | data/annotations/turtle50_v5/private.json | Git中已有完整题库和评分，无需原Excel |
| `--seed` | 20261102 | 调度seed，不控制模型采样 |

通用入口及全部参数见 [五组实验文档](../archive/guides/study_20261102.md)。`--memory session` 是新默认；transcript 显式使用旧引用历史，card 为摘要，both 为 transcript+card。session 要求 persistent API Player；Codex CLI 跨题分支暂不支持，CL须选 transcript。

## MAS TS038：solo 和 free_dialogue 各一次

```bash
python3 scripts/study_20261102.py --suite team \
  --team-puzzles TS038 --strategies solo,free_dialogue --repeat 1 \
  --dialogue-roles complementary --dialogue-scheduling adaptive \
  --dialogue-max-discussion 4 --dialogue-start A \
  --config configs/loop.deepseek.json --mode run \
  --out runs/api/my_ts038_prefix_once
```

先检查计划时把 `--mode run` 改成 `--mode plan`，并使用另一个 out。

| 参数 | 示例值 | 含义 |
| --- | --- | --- |
| `--suite` | team | 只跑 MAS |
| `--team-puzzles` | TS038 | 只选38题 |
| `--strategies` | solo,free_dialogue | 单agent baseline + 共享聊天双agent，共2局 |
| `--repeat` | 1 | 每策略一次 |
| `--dialogue-roles` | complementary | A investigator、B critic；symmetric 两个generalist；swapped 交换分工 |
| `--dialogue-scheduling` | adaptive | 遵从 NEXT；alternating 强制交替 |
| `--dialogue-max-discussion` | 4 | 每次外部提交前最多4条 discuss/pass，0禁用讨论 |
| `--dialogue-start` | A | 初始说话者，可选B |
| `--config` | configs/loop.deepseek.json | 同上模型配置 |
| `--mode` | run | plan仅计划、dry-run零调用、run实际实验 |
| `--out` | 新目录 | 拒绝覆盖 |

A/B 各自保持独立持续会话、共享公开聊天，分工写入 prompt 和日志。两者共用100次外部提交额度；讨论不算问题，tokens仍记账。free_dialogue 暂不支持题内中断恢复，停止轨迹保留待审；不能重跑后冒充同一 rollout。

## 返回格式和兼容性

| 返回者 | 新模型输出 | 内部结构 |
| --- | --- | --- |
| 普通Player/非自由对话MAS | QUESTION 或 FINAL，换行后正文 | type、text |
| free_dialogue A/B | QUESTION NEXT=B、FINAL NEXT=A、DISCUSS NEXT=B、PASS NEXT=A，换行后正文 | type、text、next_speaker；强制最后交卷NEXT可省略 |
| Host | yes / no / yes and no / irrelevant | label |
| Grader | 原有严格评分JSON | checkpoints、覆盖要求、得分及私有判定 |

新 Player 可直接使用引号、反斜线和换行，无需 JSON 转义。DeepSeek Player/Partner 不请求 JSON mode，Grader 继续使用 JSON mode。旧 JSON 动作仍可解析，CL和恢复保留 assistant 原文。强制交卷提示按新旧协议分别要求 FINAL 或 type=final，避免相互矛盾。

完整文本围栏和明确结束思考标记可本地剥离；问题文字及类型不变。Player 预测的 feedback 不成为真实Host反馈。未知字段、冲突或截断不会被猜测修复。见 [返回协议](player_action_protocol.md)、[自动续跑](automatic_continuation.md)、[CL架构](cl_raw_session.md)。

Host/Grader 不继承 A，Player 不会收到 A 的私有评分或 B 答案。DeepSeek API仍逐轮发送累计 messages，缓存和usage决定费用；持续会话不意味着历史免费。

## 查看结果与恢复

CL verified入口的主要文件：

- `my_set1_prefix_once.launcher.log`、输出目录 `status.json`：启动、诊断及运行状态；PID不证明API已连通。
- `host_gate/summary.json`：20次开发诊断，不能当作独立Host准确率评估。
- `study/continual/index.html`、各局 `trajectory.html`：问答、交卷及反馈。
- `study/continual/experiment_runs.json`：状态、成功率、partial score及问题/提交数。
- 根目录 `cost_summary.json`：含诊断成本；各局 api_calls.jsonl、token_costs.csv 保存逐调用用量。
- `player_continuation.json` 和首次B调用的 inherited_session：A原始前缀、完整答案边界和恢复检查点。

MAS入口对应 `team/index.html`、各局 `shared_dialogue.html` 和 `dialogue_metrics.json`。费用含讨论、报告了usage的失败调用和格式辅助调用；未知价格/账单保持未知，不将API等价估算当作真实账单。

已停止的 DeepSeek 单批次 CL，且属于支持的完整 Player 格式断点，可以先离线准备恢复副本：

```bash
python3 scripts/auto_continue.py \
  --from-study runs/api/my_set1_prefix_once \
  --out runs/api/my_set1_prefix_recovery_plan --mode plan
```

实际恢复改为 `--mode run` 并使用另一个全新 out。`--max-continuations` 默认3，限制续跑子进程，不是实验重复次数。已生成动作、固定A、B剩余额度与历史成本保留；不重抽问题，不为成功率重跑。API/auth/截断等不会被当作格式问题无限重试。旧 transcript 批次不能中途切换成 session。

## 离线验证命令

```bash
python3 -m unittest discover -s tests

python3 scripts/study_20261102.py --suite all --sets 1 \
  --source-puzzles TS015,TS014,TS028 --memory session --source-policy fixed \
  --team-puzzles TS038 --strategies solo,free_dialogue --repeat 1 \
  --config configs/loop.deepseek.json --mode dry-run \
  --out runs/api/my_prefix_offline_check
```

后一条验证12局CL+2局MAS的调度、快照及输出，均为 dry_run，没有模型成绩。测试覆盖新旧格式、CL继承/分支隔离、额度重置、MAS交接、Grader接口和格式恢复；真实模型的遵从率仍需实际实验检验。

2026-11-11 验证记录：Python 3.11 与 3.14 均通过228项回归；Set1 verified计划确认为20次Host诊断+12局CL；12局CL+2局MAS的冻结快照dry-run通过。本轮未启动收费实验。
