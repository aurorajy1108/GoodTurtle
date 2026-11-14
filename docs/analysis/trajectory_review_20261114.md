# GoodTurtle 本机与组友实验联合审阅（2026-11-14）

> 本文是清理前已经发布的固定分析快照；随后收到的两批组友Set1结果单列在[最新结果目录](../../results/README.md)，未静默混入本文样本。

**目前最可靠的结论是：CL 能改变搜索方向，但没有带来完整解答成功；MAS 能在个别轨迹中修正角色理解，却没有跨批次稳定优于单 agent。自查组的较高成绩伴随更多实际计算量，尚不能归因于合作或自查机制本身。**

本次只做读取、统计和审阅，未启动付费实验，未更改原 Host 回答、原评分或 active Host reference。两名 subagents 分别审阅本机 CL＋历史 Set2、组友 Set2 v17；主 agent 审阅本机 MAS、April MAS 和 extra2，并整合校验。以下全部是 AI 审阅，不是人工 gold。

## 1. 当前进度、审阅范围与去重

|来源|物理档案|已记录提问/交卷|完成情况|
|---|---:|---:|---|
|本机 CL Set1 固定 A、四重复|39|3,889|3 个 A＋36 个 B，全完成|
|本机 TS038 2×2、四重复|16|1,410|15 完成；1 局在 36 次提交后中断|
|组友 Set2 v17|38|3,800|3 个 A＋35 个 B，全完成|
|组友 Set2 历史 round1/round2|24|2,400|6 个 A＋18 个 B，全完成|
|组友 April TS038＋extra2|14|1,132|12 个完整目标局＋1 个重复 A＋1 个技术失败|
|合计|131|12,631|每个已记录问题/交卷均有对应审阅|

范围是本轮正式 CL/MAS 批次与远端最新正式结果（以及解释它们所需的历史 Set2），**不包含十月份题目筛选、Host 训练参考和十一月初 preflight/pilot 的全部旧轨迹**。用于设定本次计算量上限的早期 MAS 探索局也不合并进新 2×2 的样本；其参考调用量不是本次实际调用量。这些都不是本次正式结果的独立重复。没有发现可归入本轮的远端正式 Set3、MAS TS002/TS014 结果；这不代表组友电脑上没有尚未上传的结果。

逐条核验 12,631 个原文、索引、类型、实际标签及已记录原评分，零缺项、零错配。原始 trajectory 整文件 hash 都不同，但 timestamped submission 与 API 解压内容证明：历史 round2 TS033 source 和 extra2 r02_source 是**同一份 A**，只多了 11 条 answer-reveal 记账事件。

因此是 **130 个唯一实验观察、12,531 次唯一提交**；其中 12 个唯一 A、118 个目标/单独求解观察。目标中 116 个完整结束、2 个技术中断。不能把恢复目录、重复上传的 A、公共 direct 控制再乘上前题种类，增加样本数。

本机 CL supervisor 已 completed；MAS 两个控制器均 requires_attention、active 为空。不同目录的汇总不是可直接相加的进度：本机 MAS 以 v2_partial 的 14 局，加 v3_actor_authorized 的 r04_mas 和 r04_mas_review 的最新状态重建为 15/16。r04_mas_review 在新 partner 响应读取时断流，尚未交卷，不能记 0 分或算失败。此前两次明确授权恢复只针对各自旧请求；新断流没有被冒用旧授权自动重试。本次审阅没有续跑。

## 2. CL Set1：重复完成，答案经验有帮助，完整 transcript 未稳定帮助

目标题始终 TS013；前题分别 TS015（positive 假设）、TS014（negative 假设）、TS028（irrelevant 假设）。每个前题只求解一次并揭晓完整官方答案，各 B 重复 4 次、独立新 100 次额度。原始角色前缀 hash 与 source response ID 验证了固定 A 重用；TS014/015/028 分别为 89/100/100 个提交对应的历史。B 没有沿用 A 的剩余额度。

- `direct`：没有 A。
- `answer_only`：A 的汤面与完整官方答案，不给 A 的整段问答。
- `session`：保留 A 的角色消息前缀、揭晓 A 的官方答案，再开始 B。

|A 题/假设关系|direct，n=4|answer_only，n=4|session，n=4|
|---|---:|---:|---:|
|TS015 positive|36.25%|56.25%|45.00%|
|TS014 negative|40.00%|33.75%|6.25%|
|TS028 irrelevant|36.25%|48.75%|31.25%|
|三块合计，每条件 n=12|37.50%|46.25%|27.50%|

以上是**原始末卷均分**，所有 36 个 B 均未完整解出，都用完 100 次提交。direct 三块各自是不同实际 rollout，表里按设计块展示，不代表它们接受了 A。四个 B 重复只检验同一个固定 A 前缀下的变异，不能当成四个独立 A。

TS015 的可迁移信息确实存在：它让 player 质疑 course 不一定是课程。answer_only 四局在 Q3/3/5/61 确认菜品，session 四局 Q2/7/2/2；但识别双关不等于找齐“强制高桌晚宴—截止前报偏好—按时赴宴—三道菜—每道尝过—不喜欢—本人请求服务员收走剩菜”的完整因果链。这里可报告的是**早期语义突破**，不能报告完整成功提升。

完整 transcript 也携带错误线索和习惯：TS014→TS013 r01_session Q50 错肯定“另一人遮挡课程屏幕”，后半约 49 问都追屏幕/光线/眼镜，末卷 0。TS015 r04_session Q6 错肯定“另一人先拿/选食物”，后 94 问长期围绕抢食和票据。它们是有具体早期转折的失败，不能仅归为无原因的 sampling variance。

session 一共 55 次 FINAL，direct 和 answer_only 各 19 次。TS015 r02_session 单局 19 次近同交卷仍不补缺少的事实。这支持“重复提交与保留更多上下文不自动累积正确因果信息”的观察。

因为全部 B 都达到 100 次上限，提交数量的样本方差在各条件都是 0；这只是顶格截断，并不代表求解行为稳定。不能把失败局的 100 当作真实的“解出所需问题数”，或据此声称已解决高 variance。

## 3. 组友 Set2：有五重复新批次，不能与旧版直接合池

最新完整 Set2 材料在 `origin/publish/set2-v17-35-trajectories` 的父提交 `42897fd6253478a39bd7a2ec536045ab7260d039`。最新分支 head `b510011` 删除了冻结配置/题本/上下文，只留下轨迹；38 份 trajectory 与父提交逐字节相同。本次从父提交补齐旁证，没有拿当前 Host 替换历史 Host。只 pull main 会看不到这一分支的全部结果。

新批次采用 TS034 Host v17、scoring-v6、coverage-v2；目标 B=34。每个 A 固定一份，answer_only/session 各 5 次；**公共 direct 只有 5 次**，不是每个 A 各 5 次。

|A/条件|n|原末卷均分|样本 SD|完整成功|
|---|---:|---:|---:|---:|
|公共 direct|5|55.50%|24.77 个百分点|0/5|
|TS033 negative · answer_only|5|66.50%|14.75 个百分点|0/5|
|TS033 negative · session|5|27.00%|34.93 个百分点|0/5|
|TS035 positive · answer_only|5|23.00%|33.47 个百分点|0/5|
|TS035 positive · session|5|41.00%|33.62 个百分点|0/5|
|TS012 irrelevant · answer_only|5|33.00%|28.42 个百分点|0/5|
|TS012 irrelevant · session|5|56.00%|31.30 个百分点|0/5|

这批最重要的反例是：标作 negative 的 TS033，仅答案条件均分反而最高；positive TS035 并未稳定提高 TS034。**positive/negative/irrelevant 是预设关系假设，不能当作实验已经测出的效应。** TS033 的“谁是人质”具有直接角色反转关系；TS035 的共性主要是父亲对后续危险的担忧，机制联系较弱。结果可能来自答案引发的重新检验，也可能来自固定源局质量、噪声、Host 误答与评分边界；这些因素本批未被逐个隔离。

35 个 B 的 96 份 FINAL 都没有完整写出财富/唯一家人等必要叙事。部分分的疑点即使修正，也不足直接宣布新增完整成功。典型问题：

1. TS035 session r05 FINAL77/88/100 已说告知女儿“不付款”、保护她并接受自身危险，grader 因未另写“不来”只给 C3 半分；冻结 grading_notes 接受 not paying OR staying away，存在可定位的过严评分。
2. TS012 answer r05 FINAL100 虚构“付款才让绑匪知道女儿身份”，v17 明确否定这类线索，却获 C2 半分。
3. TS033 answer r05 FINAL56 只说父亲不能离开，grader 推出父亲就是人质而给 C1 半分；行动不能不能替代明确角色断言。
4. 不少局 Q30 得到 police custody OR otherwise safe 的 yes，随后约 60 问锁定警方保护。这里大半是 player 将 OR 错误收窄，并不是 Host 已确认警方。

历史 Set2 两轮 18 个 B 均无完整成功；各轮 Host v12/v13、评分点和新 v17 不同。extra2 四个 B 也都未成功，answer_only .50/.15、session .40/.20；本包没有新 direct。它们适合展示具体失败链，不适合和 v17 的五重复合并，制造一个貌似更多重复的统一实验。

## 4. MAS：局部有互补，整体优势没有稳定证据

### 本机 TS038，同上限 2×2

|条件|完整结束/计划|成功|原末卷均分|样本 SD|平均提交数|
|---|---:|---:|---:|---:|---:|
|单 agent|4/4|0/4|25.00%|35.36 个百分点|100.00|
|单 agent＋自查|4/4|2/4|81.25%|23.94 个百分点|94.00|
|双 agent|4/4|1/4|52.50%|41.13 个百分点|87.75|
|双 agent＋自查|3/4|0/3|41.67%|38.19 个百分点|82.33|

共同上限是 100 次外部提交、225 次 solver 生成、77,696 solver 输出 token。实际 solver 平均输出分别约 **5,487 / 50,300 / 14,621 / 74,982 token**。单 agent 自查用了普通单 agent 约 9.17 倍实际输出；双 agent 自查完成局在输出额度耗尽后，于 81–84 次外部提交结束。应写成“相同计算量上限”，不能写成实际计算量严格相同。

还要保留批次差异：前两次与后两次 controller/recovery 不完全相同；单 agent 自查前两次 2/2 成功、后两次 0/2。四次汇总可描述，却不足证明稳定优越性。

协作确有可定位机制：mas r02 Q37 排除“作者另有其人”，Q44 建立伪造，Q51 成功；mas r01 也是 B21 笔迹→A22 伪造→B28 谋杀。它们说明换角度与实体归属修正能帮助求解。

但共享记录也会放大错误：mas r01 Q38 把可能暴露误肯定成已经识破，随后约 60 问围绕已破案细节；mas r03 的“列表/栏目”yes 被读成具体表格，约 70 问浪费；mas_review r03 把 split identity 举例当成分裂人格事实。两个 agent 同意一项假说不等于那项假说获得新证据。

### April 的四重复 TS038，单独看旧版

|条件|n|原末卷均分|成功|平均提交数|
|---|---:|---:|---:|---:|
|solo|4|87.50%|2/4|83.00|
|free_dialogue|4|62.50%|2/4|73.25|

这是 Host v9、coverage-v2，计算量限制与本机新 2×2 不同。成功局 MAS 是 57/36 次，solo 是 87/45 次，MAS 个别成功更快；但把 0 分失败局算回去，就没有整体更好。不能只选择成功轨迹比较效率，也不能和本机 v14/unified-v3 混成 n=8 的同质实验。

## 5. 最值得保留的跨轨迹 findings

### F1：早期错误常有几十问的后果，variance 并非全是随机波动

最常见链条是：早期含混/错误 yes → 玩家将具体解释写入“已确认事实” → 后续只枚举该框架内部细节 → 最终遗失正确机制。TS013 的遮屏、TS034 的男友人质、TS038 的真实分手或已被识破均有逐问证据。后续重复次数应与早期转折标注一起分析，而非只增加均值的小数位。

### F2：关系迁移有层级：词义、场景、角色、因果链、完整叙事

TS015→TS013 的词义迁移很清楚，完整叙事成功却是 0。TS033→TS034 的角色反转会诱发固化，也可能提醒玩家检查默认身份。不能把一个单一 partial score 当成所有层级都改善；报告可另外列第一次确认核心词义/真实人质/笔迹失败的提交位置，以及其后的偏离。

### F3：四标签通道会放大复合问的歧义

`A or B → yes` 只保证至少一个分支成立；`A and B → no` 不会逐个排除两部分；`such as / e.g.` 不是已证实示例。TS033 source Q8 的“不是自己的钱，但有义务交赎款”得 M 合理，player 却只否定前半后放弃赎款。TS034 的“loved one，例如 boyfriend”同样不能确立 boyfriend。应把 Host 命题判定、问句写法问题、player 过推分开记。

### F4：角色与认知状态比表面关键词更容易失稳

TS038 必须区分实际写字者=凶手、伪信名义作者=妻子、未指定的后续读者；TS034 必须区分当前父亲被绑、未来女儿送款风险、父亲害怕、绑匪客观计划及实际结局。现有 prompt 已写过部分区分，但具体 trajectory 仍有违反；“写进 prompt”与“经验证可靠”不等价。

### F5：评分释义会改变结果，原始分必须保留

本机同版 TS038 中 spouse/partner 有时被当 wife 忠实释义，有时只能半分；r04_mas 最终正确找到谋杀与伪造，却因写“女人/配偶”被判三项零分。英文汤底第一人称明确 my wife，却未明确叙述者是男性；rubric 自行写 his/he。此处必须让人工决定性别是否属于必要事实，不能在实验后悄悄放宽，让某一组获利。

本机 15 个完成 MAS 均通过结构发布审计，但自然语言打分仍有上述边界。结构正确、原分计算正确与语义公平是三层问题。

### F6：末卷退步与大量交卷是独立失败模式

extra2 answer r01 从 Q63 的旧分 1.0 到最终 .5；历史 TS035 A 从 .875 到 .625；本机 TS028 A 最佳 .9 最终 .75。玩家已知事实不自动进入本次交卷，原 grader 又只评分当前 FINAL。因此应同时报告末卷分、best score、完整成功；不能用 best 偷换最终结果，也不能悄悄用前文替它补分。

### F7：更多对话与自查不保证更多有效探索

自查组成本大幅增加、内部输出早耗预算，长 `<CoT>` 与普通输出中的推理也会进入 QUESTION。关闭 API thinking 不等于普通 text 一定没有推理。MAS 需要记录真正的 A/B 出手、转交和讨论，而不是只根据两个角色名字声称有分工。

## 6. Infra、来源与人工优先复核

1. **当前遗留中断**：仅本机 r04_mas_review 未完成；应在保留 36 次历史及已计成本的前提下处理新失联响应，未知生成/账单保持 unknown，不当 0、不重抽整局。这轮没有代为消耗新的 API。
2. **动作边界**：类型恢复能解析 QUESTION，不代表正文只有一个命题；多问、自我改口、队友指令和伪 user/context_update 都能被当 QUESTION。April technical 的 Q1/Q5、repeats56 MAS r01 多个 teammate-only 消息实际耗外部额度。需要把路由和问句语义分开验，而非把所有内容错误归给 JSON 格式。
3. **评分版本**：全局有 9 次 score=1 而 complete=false，涉及 3 局，均在旧 coverage-v2：历史 Set2 两局、extra2 answer r01。旧规则确有分点评分与独立完成要求，不能称新统一规则又失效，也不能事后把第一个 score1 直接改成成功并截短已发生轨迹。
4. **模型来源**：冻结配置请求 Host/Grader=deepseek-v4-pro、thinking enabled/high，Player/Partner=deepseek-flash、thinking disabled；不能根据当前 README 或早先 6.1-sol/medium 的意图反推历史配置。另历史 Set2 有 7 次、v17 有 5 次实际 Codex formatter 辅助调用（requested gpt-6.1-sol/low，returned model 未独立确认）。这些辅助被内容不一致/空值守卫拒绝，未接纳成提交，但确实调用过且必须保留来源/成本。不可写成所有辅助均为 DeepSeek。
5. **可复现归档**：v17 trim 删除冻结上下文；恢复须引用上述父提交。保留本次 global inventory 的 commit、puzzle/Host/prompt/controller/trajectory hash，并注明重复 A。原始 api_cost 已知小计不等于实际账单，未知调用不可隐去。
6. **人工优先看**：TS038 性别/妻子/配偶边界；Set2 v17 C3 not pay 与 not come 同义接受；从行动不能推断人质身份的 C1；TS038 实际/名义作者近同问翻转；TS013 遮屏 Q50 与他人 first Q6。不要把全部 AI 标记无区别灌回 active Host。

审阅共标记 265 条 suspect、456 条 ambiguous。**721 是物理归档上的审阅标记数，含复合问、玩家过推与评分边界，含重复 A 的重复审阅；不是 721 个确证 Host 错误，更不是 Host 准确率。** 默认 ok 只表示本次阅读未发现足以改判的明确冲突，不证明已有人工作答。

下一步建议先对上述会影响分组比较的少数评分/身份问题作统一人工裁定并冻结规则；把旧、新协议分别报告，保留失败个案。若继续扩样，要说明是同一固定 A 下增加 B 重复，还是增加独立 A 前缀；两者回答不同问题。本机 n=4、v17 n=5 的 SD 仍大，但现有资料不足给一个有保证的“再跑几次就合理”数字。

## 7. 如何查证本报告

- [逐问交互页面](https://github.com/aurorajy1108/GoodTurtle/blob/c4ccc67eef8c09aa0c6987a464f468718f5015f4/reports/20261114_joint_trajectory_review/index.html)：按批次/局名、问题/交卷、suspect/ambiguous、关键词筛选；每条有原问、原标签、审阅理由、建议与原始 grader 证据。完全本地，无外部资源。
- [所有问题审阅 CSV](https://github.com/aurorajy1108/GoodTurtle/blob/c4ccc67eef8c09aa0c6987a464f468718f5015f4/reports/20261114_joint_trajectory_review/all_question_reviews.csv)；[疑点 CSV](../../results/reviews/20261114/review_questions_only.csv)；[完整 JSONL](../../results/reviews/20261114/question_reviews.jsonl.gz)。
- [全局来源与一致性核对](../../results/reviews/20261114/global_inventory.json)；[去重证据](../../results/reviews/20261114/global_dedup.json)；[按版本和批次分层统计](../../results/reviews/20261114/global_metrics.json)。不要用其中跨全部异质题目计算的库存均值作科学结论。
- 逐批详细 findings：[本机 CL](reviews/local_cl.md)、[本机 MAS](reviews/local_mas.md)、[Set2 v17](reviews/coworkers.md)、[历史 Set2](reviews/coworker_legacy_set2.md)、[April/extra2](reviews/coworker_other.md)。

每局逐条 review 文件均可由上述子报告及全局 inventory 定位。页面与 CSV 验证原文/标签一致，浏览器验证了 131 个局入口、筛选、部分局无 FINAL、桌面与手机显示，零 JavaScript 错误。重新打包页面可运行 `python scripts/results_catalog.py check`（需要本机原冻结来源仍在）；当前生成的 HTML 已自带所有用于展示的数据，打开无需源码、服务端或 API key。
