# TS038：计算预算匹配的单 agent 自我复查

目的：检验已有 MAS 优势能否被一个拥有额外复查预算的 Player 重现。只新增两局，不重跑已有 solo/MAS，也不重新标注原实验。

| 配对编号 | 单 Player 生成次数上限 | 生成 output token 上限 | 外部提交上限 |
| --- | ---: | ---: | ---: |
| 1 | 139 | 30,660 | 100 |
| 2 | 225 | 77,696 | 100 |

预算由对应 MAS 的 Player A+B **已观测成功返回**计算得出，包括格式错误的输出。第2局另有一个未观测完成的 actor 请求，不猜测其 token，也不给新 Player 虚构预算；保留未知费用提示。

一个 Player 使用 `deepseek-flash`、关闭 thinking，同一个持续会话完成 draft、review、action。复查显式区分公开证据和自拟假设，不模拟第二个 agent。额外调用通过确定性 floor 差分分配到第1–99个外部槽位，第100个槽位只交最终答案。最多每槽一个 draft、一个 review、一个 action。复查次数不取决于模型表现，不按成功筛选或更换种子。没有额外示例、参考 MAS 对话或私有评分注入。

错误/不完整交卷占一个外部问题额度；格式错误没有发给 Host，但每个已生成回复仍消耗 solver 调用和 output 预算。最多一次同槽格式纠正。计算预算不足会预留一次最终交卷并停止；提前正确解出也停止。不会为了消耗预算要求输出无意义文字。

这是**相同可用调用和生成 token 预算**，不保证两边实际 token 数、输入长度、缓存命中或费用相等。不能据此声称实现了严格等 FLOPs 或等美元计算量。必须同时报告实际使用量和预算利用率；只有两次、一个题目的结果属于探索性控制。

Host/Grader 的模型、参数、prompt、汤底、评分点、参考问答与原 MAS 冻结版本一致。控制器加入预算停止与复查检查点支持，并保留现有评分格式兼容修复；这些属于版本差异，需要在报告中披露。TS038 的妻子身份跨评分点重复、参考答案歧义等已知争议暂时保留，避免同时改变条件。

运行前在仓库根目录保存 `.env.local`（不要提交，权限建议 `chmod 600 .env.local`）：`export DEEPSEEK_API_KEY=...`。不要把 key 粘贴到聊天或命令输出。

```bash
cd /Users/aurorasun/Desktop/COMP1110/GP/GoodTurtle
python3.11 scripts/matched_self_review.py prepare \
  --reference runs/api/20261112_jiayang_supervised_v2/continuations/mas-ts038-a/attempt_01 \
  --out runs/api/20261112_ts038_self_review_matched
set +x
source .env.local
python3.11 scripts/matched_self_review.py run \
  --out runs/api/20261112_ts038_self_review_matched
```

`prepare` 仅写计划与不可变运行快照，不调用 API；`--reference` 指向含两局已完成 TS038 MAS 的冻结 study，不是单局目录。`--out` 在 prepare 时必须不存在。`run` 并行运行这两局；最多两名独立 Player 各做一局，彼此无信息共享。工作目录、模型密钥和原实验都不会混入 Player prompt。

```bash
python3.11 scripts/matched_self_review.py status --out runs/api/20261112_ts038_self_review_matched
```

准备完成后，也可以直接 `bash scripts/run_matched_self_review.sh 输出目录`：自动从忽略的 `.env.local` 载入 key，并在 macOS 运行期间阻止空闲休眠。它不会阻止关机或保证合盖后持续联网。

同一输出目录有互斥锁，避免重复启动。运行器每10秒更新 `status.json`、`index.html`、`experiment_runs.json`、全角色 `cost_summary.json`；每局另有 `trajectory.html`、`self_review.html`、`solver_compute.json`、逐调用 `api_calls.jsonl`。`comparison.md/json` 把新对照与原 solo/MAS 并列，同时显示实际预算利用率。token/价格是供应商 usage 与冻结价格表推算，不是账单实扣。

已证明的发送前网络错误或显式中断可按原请求续跑，已返回的 draft/review/action 不重复生成，quota 不重置；缺失评分证据可按既有逻辑补全，不能改变已返回的评分判断。最多每局自动恢复3次，其他异常暂停并记录 `alerts.jsonl`、请求 macOS 通知；通知可见性取决于本机权限。`worker --repeat 1/2 --resume` 是内部入口，应由 run 调度，避免绕过锁和快照验证。
