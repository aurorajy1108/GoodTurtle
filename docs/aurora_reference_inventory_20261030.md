# 指定五组人工 trajectory 核对（2026-10-30）

已 fetch 并检查远端 `123fd30` 的文件正文和 source 元数据；工作区未 merge。共 20 道不同题目，13 道已有人工 Q&A 上传，另 6 道经用户指定暂用模型 trajectory；当前清单需补 1 道（16）。这里的“已上传”不表示游戏完成、标签正确或已绑定 Host。

| 组 | 已有人工问答上传 | 尚无人工问答（其中 45/46/47 暂用模型） |
| --- | --- | --- |
| set1 | 13、14、15、28 | 16 |
| set2 | 34、33、12 | 35 |
| set3 | 22、19 | 47、45 |
| set4 | 7、26、21 | 31 |
| set5 | 32、28 | 38、46、45 |

按用户最新要求，**45、46、47 暂用模型实验 trajectory**，31、35、38 也已完成指定模型的模拟问答，当前需补：**16**。这些暂用记录保留模型来源，不标成人工确认，也未自动写入 active Host。

## 已上传记录与质量边界

- 7：新上传的结构化历史包含 32 问及原始 JSON；不再只有 11 条片段。
- 12、14、15：记录最后一个 player 问题无回答；13 没有最终完整交卷。若还有后续消息需要补传；不能仅据文件判断整局已结束。
- 22、26、28：有规范化 Q&A 和最终提交，但不包含每个原始假设段落。
- 31：只有早期人工参考片段和模型运行记录，仍缺完整人工问答。
- 45、46、47：本次远端新增的是自动 DeepSeek 实验，Player/Host/grader 都是模型，不抵扣人工 trajectory 缺口。
- 35、38：此前新 ChatGPT 分享可能包含它们，但仍未读到内容，仓库没有相应人工归档。Notion 页面内容也未能读取。
- 所有新 inbox 上传仍待语义审核；此轮没有修改 Host 或启动实验。

## 来源索引

- [TS007](https://github.com/aurorajy1108/GoodTurtle/blob/123fd30c261c1056e55f3455a4816b67b8d1f703/data/host_reference/inbox/TS007/20261029_tiger_history/trajectory.md)
- [TS012](https://github.com/aurorajy1108/GoodTurtle/blob/123fd30c261c1056e55f3455a4816b67b8d1f703/data/host_reference/inbox/TS012/20261029_chat01/trajectory.md)
- [TS013](https://github.com/aurorajy1108/GoodTurtle/blob/123fd30c261c1056e55f3455a4816b67b8d1f703/data/host_reference/inbox/TS013/20261029_courses_gone/trajectory.md)
- [TS014](https://github.com/aurorajy1108/GoodTurtle/blob/123fd30c261c1056e55f3455a4816b67b8d1f703/data/host_reference/inbox/TS014/20261029_fail_course_group_project/trajectory.md)
- [TS015](https://github.com/aurorajy1108/GoodTurtle/blob/123fd30c261c1056e55f3455a4816b67b8d1f703/data/host_reference/inbox/TS015/20261029_fail_course_river/trajectory.md)
- [TS019](https://github.com/aurorajy1108/GoodTurtle/blob/123fd30c261c1056e55f3455a4816b67b8d1f703/data/host_reference/inbox/TS019/20261029_stairs_campus/trajectory.md)
- [TS021](https://github.com/aurorajy1108/GoodTurtle/blob/123fd30c261c1056e55f3455a4816b67b8d1f703/data/host_reference/inbox/TS021/20261029_chatgpt_6ae30251/trajectory.md)
- [TS022](https://github.com/aurorajy1108/GoodTurtle/blob/123fd30c261c1056e55f3455a4816b67b8d1f703/data/host_reference/inbox/TS022/20261029_chatgpt_6ae30235/trajectory.md)
- [TS026](https://github.com/aurorajy1108/GoodTurtle/blob/123fd30c261c1056e55f3455a4816b67b8d1f703/data/host_reference/inbox/TS026/20261029_chatgpt_6ae3021a/trajectory.md)
- [TS028](https://github.com/aurorajy1108/GoodTurtle/blob/123fd30c261c1056e55f3455a4816b67b8d1f703/data/host_reference/inbox/TS028/20261029_chatgpt_6ae2ff22/trajectory.md)
- [TS032 / 6adf3775_TS032_04](https://github.com/aurorajy1108/GoodTurtle/blob/123fd30c261c1056e55f3455a4816b67b8d1f703/data/host_reference/sources/chatgpt_shares_20261026/sessions.json)
- [TS033 / 6adf3775_TS033_03](https://github.com/aurorajy1108/GoodTurtle/blob/123fd30c261c1056e55f3455a4816b67b8d1f703/data/host_reference/sources/chatgpt_shares_20261026/sessions.json)
- [TS034 / 6adf3775_TS034_05](https://github.com/aurorajy1108/GoodTurtle/blob/123fd30c261c1056e55f3455a4816b67b8d1f703/data/host_reference/sources/chatgpt_shares_20261026/sessions.json)
- [TS034 / 6adf37d6_TS034_01](https://github.com/aurorajy1108/GoodTurtle/blob/123fd30c261c1056e55f3455a4816b67b8d1f703/data/host_reference/sources/chatgpt_shares_20261026/sessions.json)

## 45、46、47 暂用模型来源

2026-10-30 用户指定暂用。实验是每题单 Player 的 solo 试跑，Player、Host、grader 均配置为 `deepseek-flash`，thinking disabled，最多 100 次提交。每题一条初始运行；recovery 是回放和续跑，不是独立重复；没有 CL 或双 agent 对照。此批 Host 并非此前要求的 gpt-6.1-sol。

- [TS045](https://github.com/aurorajy1108/GoodTurtle/blob/123fd30c261c1056e55f3455a4816b67b8d1f703/runs/2026-10-29_deepseek_TS043-TS050/20261029_deepseek_recovery/TS045/trajectory.md)：已计数 76，总提交 77，待反馈 1；error / ProtocolError；最终分数 None。
- [TS046](https://github.com/aurorajy1108/GoodTurtle/blob/123fd30c261c1056e55f3455a4816b67b8d1f703/runs/2026-10-29_deepseek_TS043-TS050/20261029_deepseek_recovery/TS046/trajectory.md)：已计数 99，总提交 100，待反馈 1；error / ProtocolError；最终分数 None。
- [TS047](https://github.com/aurorajy1108/GoodTurtle/blob/123fd30c261c1056e55f3455a4816b67b8d1f703/runs/2026-10-29_deepseek_TS043-TS050/20261029_deepseek_recovery/TS047/trajectory.md)：已计数 100，总提交 100，待反馈 0；completed / budget_exhausted；最终分数 0.8。

45/46 是 grader 协议错误中断，不能把空分数视为零分；47 达到上限，最终 partial score 0.8，未完整解出。原始回复和错误保持不变，后续筛选为 Host 示例前需要语义审核。

## 本次新增：31、35、38

按用户要求使用 GPT-6.1-sol Host/grader、GPT-6-luna Player，均 reasoning high，每题一次100次提交。三局均正常耗尽预算，最终分数分别 0、0.625、0.35，未完整解出。不是人工对话，也未直接绑定为 Host gold。

[规范化来源](../data/host_reference/sources/model_simulated_20261030/README.md) · [完整 HTML](../runs/2026-10-30_sol_luna_reference/trajectories.html) · [审核疑点](../runs/2026-10-30_sol_luna_reference/audit_notes.md)。原来的“人工原文缺口”列保留来源类型区分；按暂用模型方案，这份清单只剩16。
