# 历史远端 Set2 round1 / round2 全轨迹审阅

这是AI逐问语义审阅，不是人工gold。只读 `/tmp/joint_coworkers/main/runs/2026-11-12_set2_round{1,2}` 的冻结档案，未改任何Host、原标签、谜底或分数，未调用API/启动实验。local_cl报告保持不变。

24局全部完成逐条阅读与JSONL记录：每局100提交，共2,400条，其中2,321 QUESTION、79 FINAL/evaluation。局名跨轮重复，因此game_id用`round1::`/`round2::`，另存original_game_id。逐局JSONL与合并all_reviews保留原文、原标签及评分；coverage记录索引和轨迹/题本/Host哈希。普通ok理由按已读命题与冻结故事作简明说明，争议逐条另写；没有为未读条目补ok。

## 冻结规则与两轮边界

- TS034：父亲是人质，富有女儿自由并接绑匪电话。父亲怕她独送款时两人被灭口；为保护唯一家人，他让她不要付钱/不要来，冒自己生命风险。妻子不是电话求情者/送款者，女儿不是已被囚人质；“另一个所爱之人”不能取代父亲本人。
- round1为`host-v12-ts034-fear-boundary-20261109`，round2为`host-v13-ts034-user-accepted-20261111`；谜底与scoring-v5相同，24份prompts完全同哈希。v13新增六个用户保留的精确旧问题及相应历史（Q001/003/042/060/075/093）。这些具体先例优先，**不代表**绑匪真有无条件杀父计划，也不能迁移到任意同义问题。报告对精确旧例保持原标签，把一般canonical顾虑标ambiguity，未覆盖用户保留判断。
- “父亲怕女儿独来被杀”可yes；“绑匪真实打算无论付不付都杀/一定不释放”是实质未定，不能从fear升级为事实；“父亲拒付因为已知自己必死”是错误替代动机，应no。未知实际未来不能随意答no来确认安全，亦不能答yes来确认灭口。
- 本批全部`coverage-v2`，有独立completion_requirements。评分点满分和完整解出是两回事；TS034的财富、唯一家人、两人灭口风险、明确不付/不来等仍可阻止complete。不得套用后来coverage-v3-unified的100%=解出规则。
- A冻结语义分别为TS012高温未烧焦+忘开抽风+敏感烟感；TS033 5000万赎款、仅100万真钞、白纸内芯真钞外皮、换最上层全真包；TS035疫病先死+无火葬场缺燃料林葬+每日扫墓掘尸射熊+怕其他尸体被吃。没有使用TS013晚宴规则。

## 原成绩与解题机制

|轮次|模式|局数|成功|末卷均分|最佳均分|FINAL次数|
|---|---|---:|---:|---:|---:|---:|
|1|source|3|0|0.2917|0.3750|14|
|1|direct|3|0|0.9000|0.9000|8|
|1|answer_only|3|0|0.4000|0.4000|3|
|1|session|3|0|0.2167|0.2667|14|
|2|source|3|0|0.4083|0.4083|10|
|2|direct|3|0|0.5000|0.5000|7|
|2|answer_only|3|0|0.7667|0.9000|11|
|2|session|3|0|0.5667|0.5667|12|

24局没有成功，18个B均耗尽100预算。出现score1但complete=false的B是round1 TS035 direct（Q87、Q100）以及round2 TS033 answer_only（Q64、Q77、Q85、Q100），合计6次满分FINAL；这些均不是success。例如round1 TS035 direct Q61已确认女儿富有，却FINAL Q87/100仍未写财富；round2 TS033 answer_only持续遗漏唯一家人和明确叮嘱，并用女儿“ready to die”的对等牺牲替换源只明确父亲愿冒险的叙事。

目标角色反转比泛泛“保护女儿”更关键：不少轨迹很早排除女儿人质，却不停枚举妻子、兄弟、祖父、情人、朋友而不测试父亲本人；另有轨迹确认父亲也被囚，却保留第二个人质。round1 TS033 session虽Q65/74/87/92已获独送款+见证灭口C2满分，仍把父亲写远端观察者，C1与自我牺牲C3失败；Q99/100又删灭口动机，最佳0.3降0.15。

正向TS035→TS034的answer_only两轮均0.85，但session为0.25与0，不能说正向关系稳定有效。标作负向假设的TS033→TS034在round2 answer_only反而1.0（未complete）、session0.85，而direct0.25；说明标签是user_hypothesis_not_measured，不能替代观察到的条件效果。TS012中性组session由0.25到0.85，但同时有Host版本、seed、格式恢复和运输差异，不构成单因素因果证据。A官方答案揭示并不保证玩家自己在A里解出，也不保证B完成。

## 可定位的Host误导与模态范围

- round1 `S2_TS012_TS034_TS012_TS034_r01_answer_only` Q38将“父亲也被囚”给M而非宽泛yes；Q58错肯定父亲被另一名不是女儿绑匪的囚禁者关在无出口房间，引出双重绑架、两个赎款的长支线。末卷虽说父亲人质，又把女儿写成已被绑，C1=0。
- round1 `S2_TS012_TS034_TS012_TS034_r01_session` Q55把女儿独送款可能遭害的命题答no；问句will harmed的确定结果应未定，而不是否定核心风险。Q69/71/92才重新建立女儿送款风险，但从未原子确认父亲=人质，末卷0.25。
- round2 `S2_TS012_TS034_TS012_TS034_r01_direct` Q18错yes父亲独送；Q47/62又错yes“父亲被监视不能去，所以只能让女儿替代送款”。Q86/87后才澄清女儿本就是索款对象，与父亲能否去无关，末卷仍另造朋友人质，0.4。
- round2 `S2_TS012_TS034_TS012_TS034_r01_session` Q5/28/49把非精确旧例泛化成父亲相信无论付不付必死；Q41/50/56连续FINAL保留该错误。Q67才纠正动机，仍8次FINAL停0.85。Q90/91只剩女儿这项新事实被保留，但见证灭口和财富未补。
- round2 `S2_TS035_TS034_TS035_TS034_r01_answer_only` Q85/86错yes另一动机/更大犯罪；Q90只肯定family member广类（女儿本来符合），玩家却过推为另一妻子/孩子。源唯一家人不应被错误细化成第二位亲属。
- round2 `S2_TS035_TS034_TS035_TS034_r01_session` Q21把女儿自由与支付pointless绑在一起全yes；Q80/81又把父亲不能亲自交款扩成付款不可避免地不可能。最后20问全追囚禁地点和不可能付款，始终未原子查父亲身份，末卷女儿人质+父亲另被囚、0分。
- round2 `S2_TS033_TS034_TS033_TS034_r01_session` Q52错否广义“女儿所爱的人”，因为例子只举男友/丈夫/孩子就排掉父亲；Q62错yes父亲去交款落入针对自己的陷阱。直到Q79/82才统一父亲人质，后3次FINAL停0.85。

## 末卷退步、评分边界与A问题

- round2 `S2_TS012_TS034_TS012_TS034_r01_answer_only` Q91为0.85；Q97错yes“送款才让绑匪定位并杀女儿”，Q100据此发明“女儿是真目标”，C2从半分归零，末卷0.45。
- round1 `S2_TS035_TS034_TS035_TS034_r01_source` Q70已写疾病席卷村庄、多死者，得0.875；Q85/89/95/99/100删回泛称illness，退0.625。这是真实遗漏，不可由之前对话替本次FINAL补回。
- round2同源TS035 Q87/91/94已说同一疾病使其他村民死亡并林葬，仍仅C1半分，Q100同义“illness killed many villagers”才被接受疫病全分，存在不必要依赖epidemic原词的评分不一致；已逐条标suspect，原分未改。
- 两轮TS012源局从未问抽风机是否开启或烟感敏感性；round2 Q33/93/96错误肯定pantry是misnomer或房间官方专名，引发数十问词义排查。冻结pantry本就是共享小厨房。炉具类型不明，不能任意肯定stove或否定microwave；“油烟直接触发fire alarm”是否应算烟感部分覆盖也有复核空间。
- 两轮TS033源局均没发现原现金包里有白纸内芯。round1 Q6已确认赎款却长期追厚度、少量加钱；round2 Q8将“非本人钱”与赎款义务合问得M后未拆，Q39/56错把假纸放在“新增现金”而非初始包，no正确。最后都给0；raw理由中的半分被controller按明确错因的contradictions覆盖归零，不能只看理由文字声称评分计算出错。
- round1 TS035 session Q95/98/100近同FINAL原分0.25/0.15/0.25，Q98的C3零分与另两次“拒付保护有、本人自牺牲缺”半分边界不稳。round1 TS035 answer_only末卷R1标covered却无wealthy，独立完成项应partial。round2 TS035 session末卷C2零分与v5独立危险事实的半分边界亦保留AI疑问；不擅改原分。

## 格式辅助、重试与档案去重

API gzip审计实际有player/deepseek-flash 2,424次、host/deepseek-v4-pro 2,354次、grader/deepseek-v4-pro 89次，另有7次codex_cli格式辅助，请求模型gpt-6.1-sol、reasoning low。CLI事件未报告actual returned model，应写requested pinned而非独立验证返回模型。这7次全部紧接error而未被接纳成submission：5次内容不一致/缺原文证明，2次空text。不能把API status=ok当格式修复成功，也不能把辅助实际调用从模型来源和费用审计删去。见forensics.json逐调用记录。

还有948次确定性格式抽取（945 unique_prefix_action及3次原文末段抽取），12次用户授权re-prompt不耗提交；39次source_answer_reveal包含恢复重放，绝不是39个独立A。round2 TS033 session继承103个player turns，仍只对应100个提交，额外含源局3次re-prompt。另有12个host transport recovery和1个player transport recovery，重放可能重复收费；本文只计最终每局一次，不虚称实际账单。

round1 TS033 direct在experiment_runs.imported_direct明确导入此前已发布baseline，轨迹SHA256 `63fd23fa8e0e6701683c38433a215f6865b12bd57c60cbad83168c27c34f3704`，早于A，且含恢复。若总报告还纳入旧TS034_direct包，必须按该来源去重；本次24局内部文本+label签名均独立，round2未复用round1游戏。旧_skipped.json保留历史source API error，并不说明最终24局缺失。

可见DSML/tool样式污染保留为玩家文本而非执行指令，例如round1 TS033 source Q88/97、session Q53/64、round2 TS033 session Q36；round1 TS033 direct Q71突然问“wallet drained but father still hooked on”被正确irrelevant。这些与真实formatter/重试应分别记录。两轮均非理想完全均匀实验：round2运输由系统代理改直连TLS且有重试，版本差异不能仅归于关系迁移。

## 逐局索引

|轮次/局名|首个关键确认|末卷/最佳|FINAL数|逐局备注|
|---|---:|---:|---:|---|
|[round1::S2_TS012_TS034_TS012_TS034_r01_answer_only](round1__S2_TS012_TS034_TS012_TS034_r01_answer_only.review.jsonl)|无原子确认|0.25/0.25|1|Q3女儿非人质与伪绑架混问得M未拆；Q38父亲被囚本应yes，Q58误造另一个囚禁者，使后60问修补双重绑架。Q93父亲被囚确认，仍末卷说女儿同时被绑，C1=0，总.25。|
|[round1::S2_TS012_TS034_TS012_TS034_r01_direct](round1__S2_TS012_TS034_TS012_TS034_r01_direct.review.jsonl)|18|0.85/0.85|4|Q2排除女儿人质、Q18父亲人质、Q40女儿独送风险、Q43自我牺牲、Q44女儿远离；首FINAL47 .85，Q88/98/100都只改写未补证财富、唯一家人、灭口两人。Q12/86强化确定死亡，但v5仍分别计独立保护事实，.85非解出。|
|[round1::S2_TS012_TS034_TS012_TS034_r01_session](round1__S2_TS012_TS034_TS012_TS034_r01_session.review.jsonl)|无原子确认|0.25/0.25|2|Q11复合OR曾包含父亲人质但玩家未原子复问；Q42女儿自由、Q49风险、Q69/71独来风险、Q92女儿送款已知；末卷缺父亲人质及自我牺牲，仅“supposed hostage” .25。Q55核心送款风险被no误导。|
|[round1::S2_TS012_TS034_TS012_TS034_r01_source](round1__S2_TS012_TS034_TS012_TS034_r01_source.review.jsonl)|4|0.25/0.25|4|Q4烹调、Q42油烟、Q66高温、Q86-87同房报警器；长期追炉具/油来源和加料时序，100问没问抽油烟机或烟感敏感度。四次FINAL均0.25。|
|[round1::S2_TS033_TS034_TS033_TS034_r01_answer_only](round1__S2_TS033_TS034_TS033_TS034_r01_answer_only.review.jsonl)|32|0.1/0.1|1|Q1排除女儿人质、Q32/37父亲人质但未统一人质=本人身份，后50余问枚举其他亲属。Q90 relative、Q97 daughterfather仍未消歧；末卷造另个人质+被囚父亲、保护绑匪收益错因，.1。|
|[round1::S2_TS033_TS034_TS033_TS034_r01_direct](round1__S2_TS033_TS034_TS033_TS034_r01_direct.review.jsonl)|26|0.85/0.85|2|这是round1预先发布direct baseline，仅在TS033块纳入一次，早于A且含恢复；不能当A训练后的独立direct。Q26/27逐字重复人质确认。Q51 .85后多问“为何部分错”绕确定必死却未问唯一亲属/富女儿/灭口，Q100仍.85。Q71题外wallet，后入v13六个用户精确保留例需特殊标识。|
|[round1::S2_TS033_TS034_TS033_TS034_r01_session](round1__S2_TS033_TS034_TS033_TS034_r01_session.review.jsonl)|无原子确认|0.15/0.3|9|Q34女儿向绑匪求情、Q37非女儿人质、Q52向女儿索款、Q55可牺牲人质；但一直未查父亲=人质。Q49错yes让Q60女儿现场，Q62修正远程后仍造独立loved one。Q65/74/87/92 .3，有灭口；Q99/100删见证人动机退.15。Q53/64 DSML污染保留。|
|[round1::S2_TS033_TS034_TS033_TS034_r01_source](round1__S2_TS033_TS034_TS033_TS034_r01_source.review.jsonl)|6|0.0/0.0|3|Q6赎款、Q41外观伪装、Q49人质、Q73同伙、Q91自保；但始终没查“钱非全真钞”的默认假设，故未问纸芯/真钞外皮/顶层换包。Q90/98/100真现金不足+堆厚错机制0，controller矛盾归零有依据，不把raw半分理由误当最终分。Q88/97有DSML污染。|
|[round1::S2_TS035_TS034_TS035_TS034_r01_answer_only](round1__S2_TS035_TS034_TS035_TS034_r01_answer_only.review.jsonl)|27|0.85/0.85|1|Q27/29父亲人质、Q62女儿远端、Q74保护、Q76/77女儿独送风险、Q92/93亲口拒付。Q78实际绑/杀no被误读无危险，Q79-98逐类探索伤害，Q100仍.85且财富覆盖标注有误。|
|[round1::S2_TS035_TS034_TS035_TS034_r01_direct](round1__S2_TS035_TS034_TS035_TS034_r01_direct.review.jsonl)|29|1.0/1.0|2|Q29/31父亲人质、Q44女儿送款、Q61富有、Q77风险、Q79灭口、Q84告知、Q86冒自己风险。Q87和100均score1但coverage-v2未完整，已知富有Q61在FINAL被丢失，唯一家人始终未问。Q81 DSML get_tools污染仅数据。|
|[round1::S2_TS035_TS034_TS035_TS034_r01_session](round1__S2_TS035_TS034_TS035_TS034_r01_session.review.jsonl)|无原子确认|0.25/0.25|3|Q54仅familymember而从未测父亲自己=人质；Q35错no阻女儿独送核心，直到Q80/81/89补风险。95/98/100近同FINAL .25/.15/.25，98的C3归零疑不稳。|
|[round1::S2_TS035_TS034_TS035_TS034_r01_source](round1__S2_TS035_TS034_TS035_TS034_r01_source.review.jsonl)|8|0.625/0.875|7|Q8死后食尸、Q10传染病、Q55掘尸、Q63其他病死村民已知；Q70到0.875，之后抛弃多死者疫病改illness，Q85-100回0.625；全程没问火葬场/燃料、每日扫墓，也末卷不写射熊。|
|[round2::S2_TS012_TS034_TS012_TS034_r01_answer_only](round2__S2_TS012_TS034_TS012_TS034_r01_answer_only.review.jsonl)|61|0.45/0.85|2|Q61父亲人质、Q64囚禁、Q83女儿独送、Q88父亲怕两人死、Q90自牺牲；Q91 .85后Q97误肯定“送款才能定位杀女儿”，末卷改绑匪真正目标为女儿，C2归零且拨号角色混乱，降.45。|
|[round2::S2_TS012_TS034_TS012_TS034_r01_direct](round2__S2_TS012_TS034_TS012_TS034_r01_direct.review.jsonl)|无原子确认|0.4/0.4|3|Q22女儿送款、Q32灭口、Q44父亲也被囚已知但从未统一父亲=人质；Q47/62错肯定“监视不能去所以替代女儿”。Q64 .4后虽Q86/90排除监视原因，Q94/100只去掉监视而保留另一朋友人质，仍.4。|
|[round2::S2_TS012_TS034_TS012_TS034_r01_session](round2__S2_TS012_TS034_TS012_TS034_r01_session.review.jsonl)|14|0.85/0.85|8|Q14/25/27父亲=人质清楚，Q43女儿送款，Q49无条件必死重要动机错yes让前3FINAL重复.85；Q67纠正后仍多次.85。Q90唯一家人、Q94/100纳入，终于保留新事实，但未问wealth/两人灭口。8次FINAL无完整解答。|
|[round2::S2_TS012_TS034_TS012_TS034_r01_source](round2__S2_TS012_TS034_TS012_TS034_r01_source.review.jsonl)|4|0.35/0.35|4|Q1烟、Q13油脂、Q38宿舍、Q74烟感已定位；Q33 misnomer错误yes后长期追“pantry官方名”，Q93/96再次加固。四次FINAL最高0.35，没问抽风机/敏感烟感/高温。|
|[round2::S2_TS033_TS034_TS033_TS034_r01_answer_only](round2__S2_TS033_TS034_TS033_TS034_r01_answer_only.review.jsonl)|6|1.0/1.0|5|Q6/30父亲人质早但反复确认，Q51女儿自由、Q58灭口、Q62自我风险。Q54 .75后Q64/77/85/100全部1却不complete：缺富有、唯一家人、两人灭口、明确叮嘱。末卷又从Q96泛化“女儿ready to die”未确立的对等牺牲，不改变分点满分但不完整。|
|[round2::S2_TS033_TS034_TS033_TS034_r01_direct](round2__S2_TS033_TS034_TS033_TS034_r01_direct.review.jsonl)|无原子确认|0.25/0.25|1|Q2排除女儿人质，Q27所爱、Q29父亲关心人质、Q79父亲实际目标，却始终没问父亲=人质；Q13/15把父亲财力能力错答为不能，末卷照写无法筹。Q75/87女儿送款正确，Q100另有人质+无效救援/损害家庭框架，.25。|
|[round2::S2_TS033_TS034_TS033_TS034_r01_session](round2__S2_TS033_TS034_TS033_TS034_r01_session.review.jsonl)|79|0.85/0.85|3|Q11女儿自由、Q12手机“揭示自由”使Q13-43枚举设备证据和假绑架；Q45非她人质，Q52错no所爱之人延迟父亲身份至Q79/82；Q86/89独送风险补齐。Q90/98/100三次.85，但仍无灭口动机财富唯一家人，反复声称不会释放。|
|[round2::S2_TS033_TS034_TS033_TS034_r01_source](round2__S2_TS033_TS034_TS033_TS034_r01_source.review.jsonl)|无原子确认|0.0/0.0|1|直到Q93-94才问钱给罪犯看到；Q8赎款/义务与非本人钱合问得M未拆赎款。Q39/56把假纸放“新增现金”，而非原包内芯，no正确。全局未发现绑架/纸芯/顶层换包，Q100沿公司混合现金错机制0。|
|[round2::S2_TS035_TS034_TS035_TS034_r01_answer_only](round2__S2_TS035_TS034_TS035_TS034_r01_answer_only.review.jsonl)|55|0.85/0.85|4|Q34父亲人质混合、Q55原子父亲身份、Q56送款、Q57自牺牲；Q58/59无条件必死yes让前2FINAL保留错误因，Q82纠正后Q83 .85。Q85/86又误指更大犯罪，Q90 family泛类被过推另一家人，但末卷100回保护女儿框架仍.85。|
|[round2::S2_TS035_TS034_TS035_TS034_r01_direct](round2__S2_TS035_TS034_TS035_TS034_r01_direct.review.jsonl)|84|0.85/0.85|3|Q23父亲与K同地、Q31父亲被囚、Q59同赎款犯罪，但一直把daughter默认人质，Q52/64“被囚在别处”no又误作位置线索。Q83/84才她替父求命/父亲人质，Q85-87独送风险。FINAL88 .85有父死D活确定结局，97/100逐步改成风险但仍漏灭口/唯一家人/财富。|
|[round2::S2_TS035_TS034_TS035_TS034_r01_session](round2__S2_TS035_TS034_TS035_TS034_r01_session.review.jsonl)|无原子确认|0.0/0.0|1|从未原子询问父亲=人质；Q21女儿自由被误推假绑架，Q37/41/44见证人方向正确但未查她需独送。Q80/81把不付当无法送的错误yes引最后20问拘禁地点，Q95父亲亦受害仍不统一身份。末卷写D人质+F另被囚、付款必害和无法付，原0分；C2归零保留复核。|
|[round2::S2_TS035_TS034_TS035_TS034_r01_source](round2__S2_TS035_TS034_TS035_TS034_r01_source.review.jsonl)|2|0.875/0.875|5|Q2死尸、Q17疫病、Q21掘尸、Q58已死多人、Q99群体死亡；无火葬场/燃料从未探，daily visit也缺。Q64 .625，Q87/91/94同疾病多死者仍半分疑偏严，Q100才承认忠实疫病释义升.875；Q61/90又把未定过去/未来讲实。|

本次AI裁定：{'ok': 2289, 'suspect': 52, 'ambiguous': 59}；这些疑点不是已证实Host错误数，尤其精确用户先例、无关细节、复合问、条件恐惧、实际未来与整体错因的区分须人工复核。所有原始评分保持。
