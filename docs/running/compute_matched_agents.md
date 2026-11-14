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

同事pull后的一键运行（不需要本机历史run目录）：

```bash
bash scripts/run_compute_matched_agents.sh runs/api/ts038_review_yourname_01
```

先在终端export自己的`DEEPSEEK_API_KEY`，或保存到忽略的`.env.local`。给定目录不存在时，shell自动从仓库内的v5题库、参考包和DeepSeek配置冻结新实验，再启动API调用；已准备目录则直接运行。目录存在但没有计划文件时拒绝覆盖。

若先检查计划再启动，可分开运行（prepare不调用API）：

```bash
python3.11 scripts/compute_matched_agents.py prepare --out runs/api/ts038_review_yourname_01
bash scripts/run_compute_matched_agents.sh runs/api/ts038_review_yourname_01
```

本机复用历史冻结输入的可选方式：

```bash
python3.11 scripts/compute_matched_agents.py prepare \
  --reference runs/api/20261112_jiayang_supervised_v2/continuations/mas-ts038-a/attempt_01 \
  --out runs/api/20261112_ts038_compute_matched_2x2_v3
bash scripts/run_compute_matched_agents.sh runs/api/20261112_ts038_compute_matched_2x2_v3
```

- `prepare`只写冻结计划，不调用API。默认使用仓库输入，无需历史trajectory。
- `--dataset`：可选新实验题库JSON，默认`data/annotations/turtle50_v5/private.json`，必须包含TS038。本pilot只选取TS038及其绑定参考包。
- `--config`：可选新实验模型配置，默认`configs/loop.deepseek.json`，要求persistent、额度100、全部模型接口为DeepSeek，Player关闭thinking。
- `--reference`：可选，含TS038两次已完成solo/MAS的历史study目录，仅用于冻结输入和确定预算，不给Player展示历史答案或参考trajectory；不能同时传`--dataset`或`--config`。历史`runs/api`不随代码推送，同事直接用默认新实验模式。
- `--out`在prepare时必须不存在；run时指向已准备的目录。不要重复prepare覆盖已有数据。
- shell只有一个参数：新目录或已准备目录。它从忽略的`.env.local`加载`export DEEPSEEK_API_KEY=...`，或沿用已export的key，不打印key。macOS运行期间阻止空闲休眠。
- 等价直接入口：`python3.11 scripts/compute_matched_agents.py run --out 输出目录`。
- 查看状态：`python3.11 scripts/compute_matched_agents.py status --out 输出目录`。
- `worker --game ... --resume`是内部调度入口；正常使用run，确保互斥锁和冻结文件校验生效。

任务顺序使用固定seed 20261112打乱，seed只控制顺序，不控制API采样。最多两局并行，同一局内actor顺序执行。`index.html`提供公共trajectory、MAS共享聊天、各actor私有复查和实时budget；`cost_summary.json`记录全部角色token及估算费用。`solver_phase_plan.json`保存每次调用前的payload和cap，便于恢复和审计。没有额外Codex格式化模型调用。

唯一明确action支持本地原文恢复。若既有配置为`multiple_actions=last_complete`，多个明确prefix也按同样规则原文取最后一个完整action，记录候选数、选取位置和原文SHA；不按答案质量选择，不重新生成，不允许把question改成强制final。配置为reject或末尾action不完整时仍暂停/受限纠正。

运行器每10秒检查进度，遇可验证的已有transport断点按原请求恢复，已返回的review不重生成；最多自动恢复3次。未知schema、截断、无法证明安全的请求等暂停并请求macOS通知，原始记录不删除或伪造。通知可见性由本机权限决定。

11月13日补充：仅对预算控制器的私有draft/review，非空且`finish_reason=length`的正文可以保留为**不完整私有笔记**，继续生成原角色的action；不会补写或重新抽取该笔记。下一步phase payload明确标出这条笔记不完整、不是Host证据。原输出全文、finish_reason、生成次数和token费用保留且只计一次，仍受原225次/77,696 token/100次额度约束。另一名agent看不到私有笔记，除非原agent之后主动在公共讨论分享结论。

公开action、Host、Grader的截断，以及空白、拒绝或工具调用不适用此规则。旧中断局可用下列命令校验并保留既有笔记，已完成的其他7局不重跑：

```bash
python3.11 scripts/compute_matched_agents.py recover --from-run YOUR_STOPPED_2X2_RUN \
  --out runs/api/YOUR_PRIVATE_NOTE_CONTINUATION
bash scripts/run_compute_matched_agents.sh runs/api/YOUR_PRIVATE_NOTE_CONTINUATION
```

`private_note_recovery.json`绑定原调用、计划、会话和公共buffer的哈希。若它们对不上则拒绝恢复。恢复事件标记为保留不完整笔记的控制器修复；它不修改历史Host回答、Grader分数、模型或prompt文件，不代表语义疑点已经修复。新后续结果需要带此恢复说明，不混写成一次从未中断的原版本运行。

Host的唯一标签格式与空正文也有受限恢复。[更新、CL续跑和本四组对照的`recover --from-run`命令](host_output_recovery.md)。

## 从每条件2次补到4次，保留已完成结果

```bash
python3.11 scripts/compute_matched_agents.py extend \
  --from-run YOUR_COMPLETED_2X2_RUN \
  --total-repeats 4 \
  --out runs/api/ts038_r1r4_yourname
bash scripts/run_compute_matched_agents.sh runs/api/ts038_r1r4_yourname
```

- `extend`仅校验、复制和安排，不调用模型。`--from-run`必须为全部完成、无活跃worker的四组对照根目录；不得使用未完成、模拟或缺少条件的归档。
- `--total-repeats`为每条件的**总次数**，默认4，允许2–20且必须大于现有次数。原重复号必须连续且从1开始；四个条件每个重复各有一局。
- `--out`为尚不存在的新目录，不能位于原归档内。原归档不修改；旧结果、API调用、轨迹、配置及prompt文件逐字校验保留。
- 原来每条件2次时，只增加重复3、4，共8局；新计划为16局，其中8局已完成。运行器跳过旧局，最多2个worker并行执行新局。
- 新局使用原冻结模型配置、题目、评分、Host参考包和相同的计算预算；不会向新Player展示旧轨迹或答案。当前已测试的恢复控制器写入独立冻结快照，覆盖文件与哈希记入`extension_manifest.json`，注明新增重复的版本cohort。
- 四次仍是同一题的探索性重复；原Host指代与Grader语义边界未因增加重复而自动解决。统计中的expected、配对差和完成数根据实际计划计算，不再固定为2次/8局。
- `index.html`、`performance.json`、`cost_summary.json`覆盖新计划的全部16个唯一局；旧目录和扩展目录不可再次叠加计数或费用。

本机11月13日扩展：CL Set1已达每条件4次，不重跑；TS038四组对照从`20261113_ts038_compute_matched_2x2_v8_private_note`扩展至`runs/api/20261113_ts038_compute_matched_2x2_r1r4`，仅新增四条件的第3、4次。团队其他题目/其他人的执行槽需要各自的实际归档才能确认，不能把未同步的结果算作已完成。
