# Set2 v17 coworker trajectories：独立逐问审阅

本组完成 **38/38局、3800/3800次提交** 的AI辅助语义审阅：3688个问题、108个FINAL、4个invalid。不是人工金标准，也没有修改原始标签、评分或运行代码。逐条JSONL给出原文、实际标签、判断和理由；没有为未读条目自动填ok。审阅先独立阅读冻结答案、host context/判例、共同prompts和按顺序的全部提交/反馈，再汇总结果，没有以组友旧analysis代替核验。历史Set2、April及extra2由主agent另组审阅，不计入本组覆盖。

结果为3596 ok、63 suspect、141 ambiguous。按动作拆分：问题3514 ok/51 suspect/123 ambiguous；FINAL 78 ok/12 suspect/18 ambiguous；invalid 4条均确认其无反馈、占quota的协议处理。它们是待复核标记数，不是已经验证的Host错误率；尤其ambiguous多涉及未知事实应no、irrelevant还是yes and no，以及单一限定命题和独立并列句的边界。

## 归档和可复现性

- 发布head固定为 `b510011bb93531a1bc737756ed4b8582b3591a5d`。该Trim提交仅留trajectory和简要索引，删除了每局 `puzzle_private.json`、`host_context.json`、`prompts.json`、`config.json`、`result.json` 和API审计等完整旁证，**只看最新head不足以独立核对标签与评分**。
- 完整旁证取自父提交 `42897fd6253478a39bd7a2ec536045ab7260d039` 的 `results/20261113_set2_v17_zhen_qi/`。38条trajectory与head逐byte全部一致，哈希及每局上下文哈希写入 `inventory.json`。可用 `git archive 42897fd6253478a39bd7a2ec536045ab7260d039 results/20261113_set2_v17_zhen_qi` 恢复旁证，不需要merge分支。
- 本次只读提取位于 `/tmp/joint_coworkers/set2_full/results/20261113_set2_v17_zhen_qi/`；报告本身记录commit和哈希，临时路径不是长期存档依赖。父提交API审计保留请求哈希但省略请求body；它能核对实际调用和响应，不能单凭该审计声称发布了全部原始HTTP请求。
- 35局B的冻结Host为 `host-v17-ts034-witness-timeline-20261112`，评分为 `ts034-scoring-v6-aligned-20261111`、`coverage-v2`、`rubric_aligned_v1`。权重45/30/20/2/3：身份、条件性两人灭口恐惧、保护拒付/传达/自风险、女儿富有、女儿唯一家人。不能与旧版粗检查点/额外叙事完成门槛直接合池。

## 可定位的Host问题

较明确的错误集中在角色、时间和因果范围，而不是所有长串no都错误：

- `TS034_none_direct_r01` Q24以yes确认“女儿知晓绑匪计划，所以父亲知道她无立即危险”的新增因果；Q98反而以no拒绝父亲确被拘、付款也使其受险的正确重述。
- `TS034_none_direct_r02` Q58以yes确认父亲另有一笔“separate ransom”，从唯一人质创造额外勒索情节。
- `TS034_TS012_session_r02` Q32以yes确认付款会暴露父亲已被绑的身份，但索款绑匪本来就扣押父亲；Q75把危险筹到钱和危险送款混同。
- `TS034_TS033_answer_only_r04` Q60是inclusive OR，后项“绑匪物理上接近父亲”有据，却回答no。
- `TS034_TS035_session_r02` Q39广义“父亲愿死而不付”被no拒绝，似把非穷尽的绝症/保险例子当成必要限定。
- `TS034_TS035_session_r04` Q33以yes确认“不交换钱便取消绑匪杀女动机”；v17明确保护来自自由女儿不赴会，不是付款使犯罪完成或新生杀意。

部分问题把“父亲担忧女儿将来来交款后可能成为证人”错写为“女儿已经见过绑匪”“绑匪实际必杀”“不论付款都必死”。这些不等价。反过来，不能见到anyway就把一个仅限定在付款分支的担忧，误读为付款和不付款两个分支都必死。所有此类逐问结论和不确定性见各局JSONL。

## 可定位的评分问题

- `TS034_TS012_answer_only_r04` FINAL99/100、`TS034_TS035_session_r03` FINAL78：grader理由承认保护拒付，只缺传达或完整自风险，却将C3给0；冻结half_credit明确允许保护拒付但欠这些部分，建议C3至少重核为0.5。
- `TS034_TS035_session_r05` FINAL77/88/100：已明确“instructs/tells her not to pay”，也明确护女并接受自身风险；grader却额外要求另说“not come”，把C3给0.5。冻结grading_notes允许not paying **or** staying away的忠实沟通释义，建议C3=1。仅此项会把该局最终原分0.70提高到0.80，仍不完成。
- `TS034_TS033_answer_only_r05` FINAL56只写父亲不能出门，未写被绑/人质。grader凭“implying he is the hostage”给C1半分，违反 `half_credit_requires C1.F1`；行动失能不能独立证明绑架身份，建议C1=0。
- `TS034_TS012_answer_only_r05` FINAL100的付款会“reveal that the daughter can identify him”是v17明确拒绝的替代因果，却给C2半分；应按中心因果矛盾重核C2=0。
- `TS034_TS033_answer_only_r04` FINAL98把“付款后仍可能被杀”的支付分支expectation称作unconditional。原文没有明确说不付款也必死，建议重审C2半分与material_contradiction；该局FINAL100后来确实加入regardless，两稿不能机械同判。

另18条FINAL标为ambiguous，主要是“knows/would”与“fears/might”的模态尺度、错误第三人质叙事对独立保护分的影响，以及推断沟通的尺度不一致。这些需要人工逐条裁定。没有统一重打3800条原标签，也没有把建议自动当新成绩。

## 实验协议、恢复和来源关系

38局均达到100提交、`budget_exhausted`、`success=false`，不是38个技术中断。四个invalid为 `TS012_answer_only_r03` Q44，以及 `TS033_answer_only_r03` Q67/76/87；没有Host/Grader事实反馈，但占提交quota，后者三次都有明确controller notice。最后一格仍为强制FINAL。源码A结束后3次官方答案揭示不占question quota，仅交给transfer player。

原API审计真实记录：DeepSeek-flash player成功3800次，DeepSeek-v4-pro Host成功3688次，Grader成功115次（108次评估加7次证据修复）；另有player transport_error13条、Host transport_error18条。Host每个问题是一调用策略，并非独立多模型多数裁决。

**真实formatter辅助调用为5次，不能描述为“完全没有其他模型介入”。** `api_audit.jsonl.gz`中role=format_repair、provider=codex_cli、requested model=gpt-6.1-sol、status=ok，returned_model未填。分布为TS012 answer_only r01一次、TS033 answer_only r03三次、direct r05一次。随后控制器均因内容变动/无逐字证明或空动作报ProtocolError；之后用有记录的无损抽取、invalid占quota或中文头别名恢复继续，没有把这些恢复当新独立repeat。逐次审计响应与后续error见 `formatter_calls.json`；202个本地format recovery事件不等于202次formatter模型调用。

16个error事件、50次reopen/restore、7个pending transport replay授权、2个pending Host replay授权、7次grader evidence repair均保留在 `recovery_events.json`。证据修复事件声明judgments_changed=false；这证明日志记录其未改评分，不证明原语义评分正确。本次审阅没有新API调用或实验。

**35个B仅对应3个A源局，不能把source重复计成15个A。** 每个A的5个session B复用同一个100-turn source_response_id和prefix_sha256；answer_only的5次重复也复用该A的opening+官方揭示答案。17个inheritance事件中两个是恢复时重复继承，实际目标session局仍15局。3个A均未独立解完，但随后都揭示官方答案；因此session带入的是完整失败A轨迹及揭示答案，answer_only带入官方答案，不能解释成各B前都重新独立成功学会了A。`source_reuse.json`记录每个前缀。

## 可以和不可以得出的结论

35个B共有96个FINAL，全部原评C4/C5=0；逐文也没有重建“富有且唯一家人”两项。因此即使接受上述部分分数修正，本组仍没有足以支持新增完成局的提交。原始最终分均值为：direct55.5%；TS012 answer_only33%/session56%；TS033 answer_only66.5%/session27%；TS035 answer_only23%/session41%。这些是未经重评分的描述值，不是迁移因果效应或显著性结论。

solver还反复把OR回答当作某个具体分支获确认。例如TS033 session r02 Q30“police custody OR otherwise safe”的yes，只支持女儿当前自由，却引出几十次“为什么警方保护她”的重复询问；TS035 answer_only r01从广义“其他保护办法”推成秘密救援后也长串重复。Host的很多no是在正确拒绝这些具体替代机制。观察到host错误不意味着全部失败都由host导致；观察到推理循环也不证明source迁移本身有稳定负效应。

完整逐条覆盖、原文/type/label一致性验证已通过38×100；`coverage.json`无未审条目，`flags.jsonl`汇总204条待复核记录。优先人工复核上述身份/因果硬例和C3规则违背，再以冻结版本离线重评分；保留原结果并单独报告修正敏感性，避免把不同版本、来源复用和技术恢复误当新的独立实验。
