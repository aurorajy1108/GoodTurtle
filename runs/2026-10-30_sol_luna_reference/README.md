# TS031 / TS035 / TS038：模型模拟参考问答

2026-10-30 用户指定：GPT-6.1-sol Host、GPT-6-luna Player，补充三题参考 trajectory。这是模型生成资料，不是人工 Host 原始聊天或已确认 gold。

- 每题 solo 一局，各自最多 100 次提交，最后一个名额必须最终交卷；错误或不完整交卷计一次并继续。
- Host / grader 请求 `gpt-6.1-sol`，player 请求 `gpt-6-luna`；reasoning 均为 high，使用现有 Codex CLI 登录。CLI 事件未报告实际模型时只能确认请求 ID。
- Host 保留 independent_then_adjudicate_v1：普通问题先独立判两次，有分歧再裁决；player 只见一条四标签回答。私有评分不展示给 player。
- 用已有 active Host 包和 v4 题库；冻结输入见 runtime_snapshot、snapshot_hashes.json。
- 新分享链接读取返回 HTTP 403，未能提取，因此没有将其内容加入本轮上下文。见 reference_provenance.json。
- 这不是 CL 或双 agent 对照，三题互不共享对话；不改动此前暂停的实验。

运行命令：

```sh
python3 scripts/team_sweep.py --dataset data/annotations/turtle50_v4/private.json --config configs/loop.codex.json --puzzles TS031,TS035,TS038 --repeat 1 --strategies solo --workers 3 --poll-seconds 10 --out runs/2026-10-30_sol_luna_reference
```

[全部轨迹 HTML](trajectories.html) · [进度](progress.json) · [计数校验](validation.json)

单题完整问答位于 `batches/TSxxx/TSxxx_r01_solo/trajectory.md`，机器记录为 trajectory.jsonl；原始模型调用为 api_calls.jsonl。运行状态以 result.json 为准。语义审核后才能挑选加入 active Host，不能自动将所有模型答案当作正确标签。

## 最终结果

三局均 completed / budget_exhausted，未完整解出。每题一局，所有失败交卷计数。

| 题目 | 普通问题 | 失败/不完整交卷 | 总提交 | 最终 partial score |
| --- | ---: | ---: | ---: | ---: |
| TS031 | 97 | 3 | 100 | 0.0 |
| TS035 | 84 | 16 | 100 | 0.625 |
| TS038 | 97 | 3 | 100 | 0.35 |

分数为模型判定，尚未人工确认。[审核疑点](audit_notes.md) · [导出核验](reference_export_validation.json) · [规范化参考问答](../../data/host_reference/sources/model_simulated_20261030/README.md)。
