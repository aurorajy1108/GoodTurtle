# Host 与 dataset 的实施协议 v0.3

## 一、先固定可判定的故事世界

汤底是故事事实，不是让 host 自由发挥的提示。每题要有 opening、solution、canonical_facts、explicit_negatives、unknown_details。明确排除只写作者确定为假的情况，不能用长排除列表人为封死所有替代解法。未交代的附带细节保持 `yes and no`，同一游戏中不能临时补充。对汤底明确描述的用途、原因和解决机制，采用有限的故事解释约定：替换该用途的猜测判 `no`，不能虚构额外场景使所有错误机制都保留 `yes and no`。允许自然语义和最少的常识因果推断，但多个可选实现之间不能任意选一个当事实。

不要要求海龟汤仅凭汤面具有逻辑上唯一的解；更实际的要求是：经过合理提问可以区分主要解释，最终汤底自洽。若一个不同解释同样符合所有可见反馈，交人工复核；不要仅因它不逐字匹配答案就自动判错。若因此修改 canonical facts，应升级数据版本，并在受影响条件重跑，不能只重算分数。

`rubric` 每项有明确的 0 / 0.5 / 1 锚点。最终得分为 `100 * sum(scores) / K`；完整正确还要求没有实质矛盾。只猜中场景或故事机制不是完整解答。多余但无关的未证实细节与直接矛盾分开记，前者不应自动导致全错。

## 二、固定题库 host 的开发顺序（按最新目标调整）

目标是把已知 50 题主持准确。统一三标签规则，加每题完整汤底、事实表和专属示例；不要求不同题共享同一组专属示例，也不以跨题泛化为主要验收目标。

每题先准备约 40–80 条问答并人工确认，再做该题示例回放、新问法和多轮检查。错误用例允许进入该题示例库，修复后用新问法验证。详见 [逐题建设与验收](host_validation.md)。正式比较中，同一题的所有 solver 条件使用同一冻结 host 配置；不同题的资料包可以不同。host 知道目标答案本来就是任务设定，专属示例只交给 host，不交给 solver。

每次请求构建 `system prompt + shared demonstrations + active puzzle + target demonstrations + public history + question`。当前脚本生成消息模板，不是已上线的模型服务。`--shots` 仅改变共享示例数，专属示例全部保留。

每次逻辑查询都计入预算，包括重复和 `yes and no`。网络或非法格式错误单独记录，重试不得择优取标签；不得把非法输出默认为有效标签。保留原始轨迹、版本和排除/重跑原因。

## 三、“不能很快做出来”的操作化

这些是建议的开发期阈值；在首次正式筛选前确定，随后不要按结果移动门槛。

| 字段 | 首批建议 |
| --- | --- |
| baseline | 一个固定精确 model ID；记录 reasoning effort、temperature（若支持）、输出上限、seed（若支持） |
| condition | 无经验、无队友、无工具、无网络、无答案文件访问 |
| direct repeats | 3 次独立会话，只给 ID 和 opening，要求一个最终解释 |
| interactive repeats | 3 次独立会话，每次最多 H=50 次 host 查询 |
| quick threshold | q ≤ 10；direct 为 q=0，另行报告 |
| 建议入选 | direct 成功 ≤1/3，interactive quick 成功 ≤1/3，H 内成功 ≥1/3 |
| 全失败候选 | 双人独立 blind play 可解性复核后，才考虑少量保留 |

预算必须同时限制 solver 总输入/输出 token 和单轮输出；只限制问数仍可能允许无限思考/综合。首轮先测成本，再冻结共同 token 上限。重复实验共享配置，不共享记忆或上下文。

建议筛选专用 solver 在 q=0 和每次 host 回复后提交一个 `best_explanation`，允许不确定时留空；该字段仅供离线 grader，分数不给 solver，不额外请求一次模型调用。每个实际完成的中间解答都算其输出 token，避免免费采样。保持完整游戏到 H 或 solver 明确停止；记录最早一次经 grader/人工复核完整正确的 q。主实验是否采用这种协议也应预先固定，不能混用不同首解检测方式。

不要用“最终在第 50 问解出”推断前 10 问不会；必须有中间解答证据。没有完整轨迹或中间解答时，`first_complete_query` 保持 null，不能编造。出现 host 错误时，本轮不进入干净难度统计；保留原始轨迹并注明重跑。

筛选模型的精确版本尚未指定，因此本仓库 `screening.status` 均为 `not_run`，统计字段全部为空。一次对话里知道答案的作者/助手不能充当 answer-blind solver。

## 四、数据与上下文隔离

| 接收方 | 允许字段 |
| --- | --- |
| solver | puzzle_id、opening，以及实验允许的经验卡和公开问答 |
| host | opening、solution、canonical_facts、explicit_negatives、unknown_details、当前题专属问答、公开问答 |
| grader / curator | 完整故事、rubric、待评解释；grader 不看实验条件 |

`data/private/` 只是目录命名，不是访问控制。不要把本仓库整体挂载给拥有文件工具的 solver。用独立进程/隔离工作目录仅提供 public 导出；禁止 solver 的工具、检索、共享缓存接触答案。文件公开发布前完成实验，或明确讨论发布后的污染风险。

数据用途要区分：共享主持示例、专属主持资料、host 质量检查、solver source-memory、solver development、player-test。允许专属主持资料与 player-test 是同一道题；禁止其答案或 QA 进入 solver 的 prompt、工具或缓存。solver 的经验源题与目标题仍按故事家族隔离。若另外报告 untouched 外部 host benchmark，则不能用它来调 host。

M1/M2/M3 配对需另写来源故事并双人解释匹配关系。题目自己的机制标签不足以证明 M1 有效。首批不填虚假的经验卡、不把目标题汤底伪装成 source memory。

## 五、最少日志字段

保存 `run_id, puzzle_id, family_id, dataset_hash, prompt_hash, examples_hash, model_id, model_parameters, condition, repeat, timestamp, query_index, question, raw_host_output, validated_label, retry_index, solver_explanation, input_tokens, output_tokens, latency, grader_version, element_scores, first_complete_query, stop_reason, infrastructure_error, review_status`。

同一次 run 的 transcript 应包含全部请求/响应；字段为空要能区分 not_run、unknown 与 failed。不要记录 API key。原始日志只追加，排除/裁决记录另存，不覆盖失败轨迹。

## 六、仍需人工与模型完成的验收

脚本验证只能发现缺字段、重复 ID、非法标签、导出泄漏等工程问题，不能验证故事是否有趣、是否高难、是否曾公开出现，也不能证明 host 标签正确。建议先筛掉“藏了任意规则才难”的题，再增加候选；保留 2–3 条可行询问路径，以免唯一作者路径掩盖实际不可解性。

## 七、v0.3 三标签语义与版本比较

只输出 `yes` / `no` / `yes and no`，大小写与空格固定。`yes` 表示支持，`no` 表示反驳或错误核心机制；`yes and no` 包含部分正确、材料不足和有实质歧义等无法二分的情况。solver 不能把它直接理解为“方向部分正确”。全部正确的多步解释可答 `yes`，错误单一因果关系可答 `no`。详见 [当前规则](host_v03.md)。

所有逻辑 host 查询都计入预算，包括重复及非二分答复。非法格式作为 protocol error 记录，不自动映射成有效标签。

相对旧版，反馈语义已改变。不同版本的问数不可直接视为相同条件；正式比较中的 solver 必须共享同一协议、汤底与预算。若区分汤底补全、prompt 与示例变化的效果，应分别控制这些因素。

橡皮题用于构建专属主持资料，当前运行入口为 `data/host_packs/USER_ERASER_001.json`。建议标签仍待人工确认，不代表已通过模型验收；此前开发文件作为来源记录保留。旧 run 文件保持冻结。

## 八、交卷判错后继续（2026-10-08 更新）

`type=final` 表示提交解答尝试，不自动结束游戏。grader 根据冻结 rubric 判完整正确才结束；错误或不完整只向 solver 返回 `no`，不说明缺少哪些要素，不透露参考答案，然后在剩余预算内继续。Host 仍仅主持问题，最终判分不与 host 标签混淆。

本次恢复的橡皮局采用总计 50 次提交的明确预算：每个 host 问题和每次交卷各占 1 次，分别记录 `query_index`、`attempt_index` 与 `submission_index`。已有 3 问及 1 次错误交卷计为 4 次。预算用完或最终正确才结束；若在上限处提交的解答正确，仍算成功。最后一次是问题且尚未正式交卷，则记录未完成，不额外赠送解答尝试。

这是在第二局结束后应用户要求作出的协议修正，续局使用原 agent 上下文，单独保存为 `2026-10-08_eraser_02_continued`；不是独立新样本。旧局报告保留，以展示规则变更。今后正式实验需从开局统一告知此规则，不能把不同停止/预算协议的结果直接视为可比。

## 九、不限提交次数的完整叙事试跑（2026-10-09）

用户最新要求优先于前述有预算试跑：枕头题重新开三局，不设 host 提问数、交卷数或总提交数上限。配置 `max_questions=null`、`max_submissions=null`；不得在第 50 问或第 50 次提交强制结束、要求交卷或判失败。错误/不完整交卷只反馈 `no`，继续直至按冻结 rubric 完整答对；完整叙事与严格 hand/arm 要求保持不变。不能因为次数多而放宽评分或额外给提示。

所有问题和交卷仍计数，包括重复与 `yes and no`，但计数只用于报告。若运行被用户或真实基础设施问题中断，明确记录未完成及原因，不伪装成成功或预算内失败；不自行另设隐藏次数/时间上限。之前 50 次封顶的轨迹保留为历史条件。

2026-10-09 用户明确要求暂停这三局，并指定**每次错误交卷也算一次提问**。主指标为 `普通问题数 + 错误交卷数`，同时保留普通问题数、所有交卷数、总提交数和待回答数，便于复核。已生成并保存但尚未发送给 host 的问题单独标记，当前主计数包含该次问题；正确交卷保留在总提交数中，不归入错误交卷。暂停局只报告当前消耗的描述统计，不能把它们当作解题成功的 mean/variance。

本次保持旧 host 输入与评分标准不变，使用新独立 solver/host 上下文；保存每局原始轨迹、冻结输入、评分事件、人工审核表及三局合并轨迹。只对已完整答对的局统计成功所需问数；三局未全结束时不能报告三局最终 mean/variance。报告总体与样本方差的分母，host 语义疑点单列。
