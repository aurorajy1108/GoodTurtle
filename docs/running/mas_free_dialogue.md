# MAS：共享聊天记录与独立 agent 会话

2026-11-04 新增策略 `free_dialogue`。A、B 共用一份公开聊天记录，各自使用独立模型会话；不是一个模型线程同时扮演两人。Host 和 grader 继续各自隔离。默认模型配置：Host `gpt-6.1-sol / medium`、grader `gpt-6.1-sol / high`、player 与默认 partner `gpt-5.6-luna / low`。旧冻结实验不会被新配置修改。

## 发言、反馈和会话

1. 当前 agent 看到汤面、自己的身份、双方职责、完整公开聊天及剩余额度。
2. 它输出 `type`、`text`、`next_speaker`。`question` 直接询问 Host；`final` 交给 grader，控制器只公布四标签；`discuss` 给队友讨论意见；`pass` 带简短交接说明。
3. 控制器立即写入共享聊天；外部提交处理完再写入 Host 标签，然后才执行下一个 agent 动作。模型不能自行署名成队友或 Host。队友意见始终是猜测，不是已确认事实。
4. `adaptive` 按输出的 `next_speaker=A|B` 调度；可以交给队友，也可以自己连续追问。两人都能提问及交卷，专长不限制动作权限。

例：A讨论身份假设→B直接提问→Host回答→B追问→Host回答→A质疑并提出新假设。内部讨论不直接发给 Host；Host 仍只看公开提交与四标签历史，grader 不看团队讨论，防止用尚未提交的内容给分。

共享记录每条消息立即写入；**agent 下一次被调度时读取此前全部公开消息**，没有每4问才同步的延迟，也不需要对两个模型额外发“广播”调用。这仍是按序执行，不是两个 HTTP 请求同时抢答。新策略不使用 `--sync-interval`，该参数只管旧 `shared_buffer`。

默认 `session_mode=persistent`：A续接A自己的线程，B续接B自己的线程，Host/grader同理。每个角色首次收到完整必要上下文，后续传无损增量（共享聊天用 `append_shared_dialogue`）；Codex 使用明确 thread ID，Responses 使用 response ID，其余供应商在本地维护多轮 messages。下一道题新建会话。持续会话不保证历史 token 免费，实际 usage、缓存与估算费用照常记录。当前不支持中途恢复 `free_dialogue`；异常轨迹保留，重开需使用新输出目录。

## 角色和 ablation 参数

以下参数可用于 `scripts/experiment.py team`、`scripts/study_20261102.py`、`scripts/team_sweep.py`，仅在选择 `free_dialogue` 时影响求解行为。

| 参数 | 默认 | 可选值与含义 |
| --- | --- | --- |
| `--strategies` | 原四策略 | 选择新模式用 `solo,free_dialogue`；必须包含 solo 基线。原默认 `solo,solo_reflect,independent,shared_buffer` 保留 |
| `--dialogue-roles` | `complementary` | A investigator：身份、场景、时间线、主因及叙事整合；B critic：反例、替代解释、遗漏动机/因果、矛盾。`symmetric` 为两名同职责 generalist；`swapped` 交换 investigator/critic |
| `--dialogue-scheduling` | `adaptive` | 模型决定下一位发言者，包括自己；`alternating` 每条 agent 消息后强制换人，覆盖模型提议 |
| `--dialogue-max-discussion` | `4` | 每次外部提交前最多 discuss/pass 消息数，整数0–10；达到上限后下一次调用必须提问或交卷；0关闭内部讨论但仍共享问答 |
| `--dialogue-start` | `A` | 首位发言者 A 或 B，独立于角色配置 |

这些职责说明及实际角色映射都保存在 `dialogue_policy.json`。自适应模式不强制均衡参与，可能一人长期主导；分析时需查看双方发言量。比较角色分工时固定调度与讨论预算，比较调度时固定角色；交换角色和首位发言者可检查身份/先手效应。不要把不同 ablation 目录的同名条件直接合并；它们的配置和成本可能不同。

## 预算与费用

两人共享100次外部提交额度，最后一次必须 final；错误/不完整 final 算一次。沿用现有统计口径：`counted_questions=host_questions+rejected_finals`，正确交卷记录到 `submissions` 并结束，不再加一问。内部讨论不消耗外部额度，但每条都需要模型调用并产生 token 成本。默认每次外部提交最多5次玩家调用（4条讨论+1条外部动作），强制最后交卷时跳过讨论。

因此更自由的对话不必然更省 token 或更准确。比较 solo 时同时报告成功率、partial score、外部问数、模型调用数、tokens/缓存与估算费用。仅完成工程测试，尚未实测新策略性能。

## 运行与审阅

先做一组两局的 dry-run，零模型调用；每次用新目录：

```sh
python3 scripts/study_20261102.py --suite team --team-puzzles TS038 \
  --strategies solo,free_dialogue --repeat 1 --mode dry-run \
  --dialogue-roles complementary --dialogue-scheduling adaptive \
  --dialogue-max-discussion 4 --dialogue-start A \
  --out runs/api/ts038_free_dialogue_check
```

真实实验将 `--mode dry-run` 改为 `--mode run`，并选择新的 `--out`。`--repeat 3` 为每策略三局；`--mode plan` 只冻结计划。省略 config 参数使用 `configs/loop.codex.json`。如需旧 `shared_buffer` 比较，使用 `--strategies solo,shared_buffer,free_dialogue`，三者都是100次共享外部预算。

每次只改变一个因素，例如 `--dialogue-roles symmetric`（无互补分工）、`--dialogue-scheduling alternating`（固定调度）、`--dialogue-max-discussion 0`（无显式讨论）。其余参数保持一致，使用单独输出目录和相同题目/重复数；seed 控制实验顺序，不保证模型采样可重现。

逐局输出：

| 文件 | 内容 |
| --- | --- |
| `shared_dialogue.html` / `shared_dialogue.jsonl` | A、B及Host全部公开消息；JSONL包含角色、外部回合、请求与实际下一发言者 |
| `dialogue_policy.json` | 协议版本、双方职责、调度、讨论预算、初始发言者 |
| `dialogue_metrics.json` / `result.json` 中 `dialogue_metrics` | 分角色提问/交卷/讨论/交接次数和内部消息总数 |
| `trajectory.html` | 原外部问答与评分轨迹，含共享聊天链接 |
| `api_calls.jsonl` / `token_costs.csv` / `cost_summary.json` | 包括所有内部讨论调用的模型输入、用量、缓存及费用估算 |

公开聊天 HTML 只显示聊天内容；研究目录里的原 trajectory 和 API 日志包含私有汤底/评分，仅供研究者审核，不能给 player 阅读。
