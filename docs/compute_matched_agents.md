# TS038：solo/MAS × 显式自我复查

本轮是四条件、每条件两次的探索性实验，共8局。四组全部新运行，不混入旧的单agent自查结果。

| condition | 解题Player | 显式自查 |
| --- | ---: | --- |
| solo | 1 | 关闭 |
| solo_review | 1 | 开启 |
| mas | 2 | 关闭 |
| mas_review | 2 | 开启 |

四组使用相同的 **225次成功返回的Player生成上限、77,696个生成output token上限、100次外部提交上限**，两次重复的预算也相同。上限由两次既有MAS已观测使用量的最大值预先确定，不根据新实验成绩调整。历史未观测调用不虚构usage。早解出会停止；预算快耗尽时预留最终交卷。错误或不完整交卷占一次外部额度，第100次必须交卷。

Player统一为原配置DeepSeek Flash、thinking关闭。Host/Grader为原配置DeepSeek v4 Pro，原Host/Grader prompt、题目、参考包和评分保留。所有actor生成的运行时输出上限统一2,048 token（还受总剩余额度约束），普通生成至少预留1,024 token供最后交卷；剩余生成1次或剩余输出不足3,072 token时要求FINAL。

solo使用真实solo参考的基础prompt，不再从MAS参考继承角色描述。MAS中A为investigator、B为critic，二者均可提问、讨论或交卷。两名Player各有独立持续会话，共享公开聊天；adaptive调度遵循NEXT交接，最多4条内部DISCUSS/PASS后必须向Host行动。Host/Grader角色与Player信息隔离。

启用自查时，在外部槽位1–99按确定性的floor差分分配draft/review，最多每槽两个额外生成，note目标160词。一个槽位只有第一次solver决策获得这些复查；后续讨论和格式纠正不会重复获得额外复查。预算预留不足时跳过尚未执行的note。MAS中由当前发言者自查，笔记只保留在自己的模型会话内；另一人只看到之后明确共享的正式消息。公共讨论和私有复查均计入同一个A+B共享预算。

对比 `solo_review` 与 `solo`、`mas_review` 与 `mas`，观察显式自查效果；对比 `mas_review` 与 `solo_review`，观察相同可用预算下协作是否仍有额外收益。匹配的是调用/输出预算上限，不是保证实际input、output、缓存、费用或FLOPs相等；必须同时报告实际使用量。两次重复、一道题不能推出普遍结论。

旧 `20261112_ts038_self_review_matched_v2` 的实际代码只有一个Player，但基础prompt含MAS角色描述，与追加的单人规则冲突；旧原始日志和评分保留，不作为本轮四组中的干净对照。

运行方式：

```bash
python3.11 scripts/compute_matched_agents.py prepare \
  --reference runs/api/20261112_jiayang_supervised_v2/continuations/mas-ts038-a/attempt_01 \
  --out runs/api/20261112_ts038_compute_matched_2x2_v2
bash scripts/run_compute_matched_agents.sh runs/api/20261112_ts038_compute_matched_2x2_v2
```

- `prepare`只写冻结计划，不调用API；`--reference`是含TS038两次已完成solo/MAS的study目录，仅用于冻结输入和确定预算，不给Player展示历史答案或参考trajectory。
- `--out`在prepare时必须不存在；run时指向已准备的目录。不要重复prepare覆盖已有数据。
- shell只有一个参数：已准备目录。它从忽略的`.env.local`加载`export DEEPSEEK_API_KEY=...`，或沿用已export的key，不打印key。macOS运行期间阻止空闲休眠。
- 等价直接入口：`python3.11 scripts/compute_matched_agents.py run --out 输出目录`。
- 查看状态：`python3.11 scripts/compute_matched_agents.py status --out 输出目录`。
- `worker --game ... --resume`是内部调度入口；正常使用run，确保互斥锁和冻结文件校验生效。

任务顺序使用固定seed 20261112打乱，seed只控制顺序，不控制API采样。最多两局并行，同一局内actor顺序执行。`index.html`提供公共trajectory、MAS共享聊天、各actor私有复查和实时budget；`cost_summary.json`记录全部角色token及估算费用。`solver_phase_plan.json`保存每次调用前的payload和cap，便于恢复和审计。没有额外Codex格式化模型调用。

唯一明确action支持本地原文恢复。若既有配置为`multiple_actions=last_complete`，多个明确prefix也按同样规则原文取最后一个完整action，记录候选数、选取位置和原文SHA；不按答案质量选择，不重新生成，不允许把question改成强制final。配置为reject或末尾action不完整时仍暂停/受限纠正。

运行器每10秒检查进度，遇可验证的已有transport断点按原请求恢复，已返回的review不重生成；最多自动恢复3次。未知schema、截断、无法证明安全的请求等暂停并请求macOS通知，原始记录不删除或伪造。通知可见性由本机权限决定。
