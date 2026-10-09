# 实验复现与暂停续接

本仓库保存 host prompt、共享/题目专属示例、秘密答案、solver 指令、评分标准以及实跑日志。当前模型调用使用 Codex 的 collaboration 子 agent；`scripts/` 是标准库 Python 的资料准备、验证和汇总工具，并不是独立 OpenAI API 自动跑局程序。仅 clone 仓库不会自动获得模型调用能力或原会话。

## 本地准备

发布范围由 `data/release_scope.json` 限定为 eraser/pillow，两道题使用各自专属示例。其他题目数据与共享示例不在已发布的 `data/` 中，本地同名文件即使存在也不会被 `prepare.py` 加载。历史 run 中的完整冻结示例保持不变，因此当前生成的 host 与历史实验配置不同。非英语历史汇总脚本在缺少研究题库时从 run 内冻结输入读取题目元数据。

在仓库根目录使用 Python 3：

```sh
python3 scripts/prepare.py validate
python3 scripts/prepare.py host USER_PILLOW_001
```

第二条打印当前工作区版本的 host 消息，包含秘密答案，不能发送给 solver。复现某个历史 run 必须使用该 run 的 `host_context.txt`、`puzzle_private.json`、`shared_examples.json` 和 `grader_rubric.json` 等冻结输入，不能用后来修改的共享 prompt 替换。`manifest.json` 或输入清单记录哈希。

## 实际调用协议

1. 新建隔离的 solver/host 会话，按 run 的 config 选择模型与 reasoning effort。本轮 pillow 为 gpt-6-sol high solver、gpt-6.1-sol host，host effort 未显式覆盖。
2. solver 只接收 `solver_task.txt` 中的规则与公开汤面，不能接收 host、评分标准、最终答案或其他局记录。host 接收 `host_task.txt` 和冻结上下文。归档任务文件中的绝对路径是原环境记录，迁移时只调整文件位置，不改变冻结内容。
3. solver 每次输出一个 question 或 final JSON。普通问题交给 host；host 只能输出 yes/no/yes and no。实际转发原文保存在 `continuations.jsonl`。
4. final 由控制器按冻结 rubric 评分；错误/不完整时只返回 no 并继续。控制器私有评分和审核意见不能反馈给 solver。当前实验没有把 final 内容加入 host 历史；这会影响指向先前交卷的提问，已列为审核问题，复现时不能悄悄改变条件。
5. 每次保存 solver、host、final、grader 原始事件。计数提问 = 普通问题 + 错误交卷；总提交另外包含正确交卷。不得删除重复问题或不完整交卷。模型工具访问隔离在本轮是指令约束，不是操作系统级隔离。
6. 本轮不设问题或总提交上限。用户暂停优先于自动继续；基础设施失败单独记录，不能当作一次真实问题或伪造模型输出。

## 当前暂停点

三局 pillow unlimited 均已按用户要求暂停，需明确恢复授权后才调用模型：

- Run01：Q165 host 标签已保存，尚未发送该反馈给 solver。
- Run02：Q159 host 标签已保存，尚未发送该反馈给 solver。
- Run03：Q166 solver 问题已保存，尚未发送给 host。

以各局 `pause_checkpoint.json` 为准。原 agent 会话仍可用时可精确接续；换环境需要依据完整记录重建两边历史，并标记为重建上下文，不能声称与原会话状态完全一致。原模型 checkpoint、随机种子、采样参数和 token 用量未知，无法保证逐字重现同一轨迹。

## 仅重新生成报告（不调用模型）

```sh
python3 runs/2026-10-09_pillow_unlimited_01/build_report.py runs/2026-10-09_pillow_unlimited_01
python3 runs/2026-10-09_pillow_unlimited_01/build_report.py runs/2026-10-09_pillow_unlimited_02
python3 runs/2026-10-09_pillow_unlimited_01/build_report.py runs/2026-10-09_pillow_unlimited_03
python3 runs/2026-10-09_pillow_unlimited_summary/summarize.py
```

这些命令保持 paused 状态并生成结果、轨迹与审核表。已有人工审核表不覆盖，合并表只追加新回答。运行前有人工修改时建议保留备份。历史有上限实验仍按原始条件归档，不与本轮混合计算成功问题数。
