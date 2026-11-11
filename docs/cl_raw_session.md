# CL 原始会话续接协议（2026-11-11）

新实验默认 `--memory session`。迁移条件不再把 A 的问答压成 `prior_experience.history` 放进新 B 会话，而是保留 A Player 原始的 user/assistant 消息，揭晓 A 的完整答案，随后在同一条 Player 消息链继续 B。权重不更新，这是上下文迁移实验。

## 实际消息和隔离

```text
system: 同一份 Player 系统提示
user: A 题面、100 次额度
assistant: A 的原始提问
user: A 的公开 Host 反馈和下一轮控制
assistant: …A 的最后一次提问/交卷（原文保留）
user: puzzle_boundary（A 最后公开反馈、终止原因、完整标准答案）
      + B 新题面、空的 B 公开历史、从 0 开始的 100 次额度
assistant: B 的第一次提问/交卷
user: B 的公开反馈和下一轮控制
…
```

第一次 B user 消息中的 JSON delta 明确替换 opening、清空 visible_history、重置 turn_control，并增加 puzzle_boundary。A 原始消息仍留在历史中，不被改写为一段 user 引用。A 的最后一个反馈也补进 boundary，避免漏掉最后交卷的结果。揭晓使用 A 实际 Host 的完整 canonical_solution，不含评分表、示例或 B 答案。

Player 延续的是逻辑消息链。DeepSeek/Chat Completions/Anthropic 仍需逐次发送累计 messages；OpenAI Responses 使用同一前缀的 previous_response_id。服务端是否缓存和如何计费由实际 usage 决定；本改动不保证降低输入 token。

A、B 的 Host 和 Grader 彼此独立，B 只继承 Player 会话。B 的 Host/Grader 看不到 A 的聊天、答案、评分或修复器输出。

## 三个比较条件

| 条件 | B 收到什么 | Player 会话 |
| --- | --- | --- |
| direct | 仅 B | 全新 |
| session | A 原始角色消息、最后公开反馈及完整答案，再做 B | 从固定 A 前缀分支 |
| answer_only | A 汤面与完整答案，再做 B；无 A 问答 | 全新 |

三者使用相同 Player 系统提示。每个 B 独立计数：最多 100 次提交，第 100 次必须 FINAL；问题和错误/不完整交卷各消耗 1 次。A 即使用满 100 次，也不会占用 B 额度。成功交卷单独记录，符合原计数规则。

`--source-policy fixed` 仍表示每批每道 A 只解一次，即使失败也揭晓答案，不筛选成功 A。每次 B 都从同一份不可变 A 前缀独立分支，不把 B1 的问题或答案传给 B2。不同 source block 的 direct 仍是独立 baseline 样本。

## 运行

在已设置 DEEPSEEK_API_KEY 的终端，运行新 Set1 批次（20 次 Host 诊断通过后，A=15/14/28，B=13，3 局 A + 9 局 B，无 MAS，无重复）：

```bash
bash scripts/start_set1_verified.sh
```

默认输出 `runs/api/20261111_deepseek_set1_raw_session_once`。可传一个不存在的输出目录作为第一个位置参数。不会覆盖旧实验。计划后立即执行的入口会冻结代码、数据、提示和模型配置。

只准备、不调用 API：

```bash
python3 scripts/run_set1_verified.py --mode plan \
  --out runs/api/set1_raw_session_plan
```

通用入口：

```bash
python3 scripts/study_20261102.py --suite continual --sets 1 \
  --source-puzzles TS015,TS014,TS028 --memory session --source-policy fixed \
  --repeat 1 --config configs/loop.deepseek.json --mode plan \
  --out runs/api/set1_raw_custom_plan
```

`--memory` 可选 session（新默认）、transcript（旧引用历史）、card（摘要）、both（transcript+card）。旧条件须显式选择；不同协议单独统计。session 只接受 persistent API Player，且必须揭晓 A 完整答案；Codex CLI 的跨题分支暂不支持，选择 transcript，程序在任何模型调用前检查。题内 Codex 持续会话不受此限制。

模型依照配置：当前 DeepSeek Host/Grader=Pro/high，Player=Flash/thinking disabled。这里的协议修改不替换模型。

## 格式故障和审计

新 Player 使用 [prefix-v1](player_action_protocol.md)：`QUESTION` 或 `FINAL` 加换行正文，减少 JSON 转义错误。MAS 自由对话保留显式 NEXT 及讨论/交接类型。Host 仍仅四种标签，Grader 仍是严格评分 JSON。

旧 JSON 仍可解析。若 Player 私自输出 feedback/expected_feedback/expected_answer，只有值是四种标签且其他字段符合既有 schema 时才丢弃该预测字段，记录修复事件，并调用真正 Host。未知字段、冲突重复键、无法确认原意或截断不被猜测修复。既有本地/隔离格式器的限额、原文一致性检查、用量记录和停止条件见 [自动续跑](automatic_continuation.md)。格式器不会获取汤底或代替 Player 解题。

每局 `player_continuation.json` 保存 A 的 Player 调用和 boundary；`transfer_metadata.json` 标明 raw-role-session-v1 及哈希。第一次 B API 审计记录携带可独立恢复的 inherited_session；后续 B 调用不重复该检查点。它们是审计数据，不是额外 API 调用。B 的 api_calls/费用只累计 B 新调用；A 在 source 局统计一次，B 重新处理 A 前缀的输入成本仍按供应商 usage 统计。

恢复时校验角色、模型、端点、系统提示、消息顺序、原始回复、前缀哈希及 response lineage。受支持的 DeepSeek 格式断点可以复用已生成的 B 动作，不重新调用 Player、不重跑 A、不重置 B 计数。来源不匹配则停止。旧冻结批次保留原协议，不在中途切成 session。

回归覆盖原始角色前缀、重复分支隔离、五种 API 适配模式、A 用满 100 次后 B 重置、Host/Grader 信息隔离，以及 B 格式断点恢复；这些是离线模拟服务测试，不代替真实模型效果评估。
