# 最新轨迹整合与分析：2026-11-14 更新

本次核对可见远端全部分支，并合并 `publish/set3-answer-only-trajectories`。当前正式目录有 **206局、20,076次提交**：203局正常结束，3局技术中断或评分冲突。与上次正文的167个去重观察相比，增加39局，其中33局目标题、6局前题。相对于刚清理后的191局目录，本次新拉取15局Set3。恢复副本、相同源题和附录不额外算重复。

**最重要的更新：Set3现在出现了较明确的正相关答案提示收益，但不是完整成功，也不能归结为“完整会话一定更好”。** 新数据加强了“相关信息怎样进入、怎样在探索和交卷中被保留”的研究主线；它没有支持CL或MAS普遍有效的结论。

## 1. 现在有哪些新材料

|新增批次|局数|其中目标题|评分协议|本次用途|
|---|---:|---:|---|---|
|组友Set1，20261111|12|9|coverage-v2|独立历史批次，不并入本机统一评分重复|
|组友Set1，20261113|12|9|coverage-v2|同上；保留100%但未完成的原记录|
|Set3 answer_only，20261114|15|15|coverage-v3-unified|补齐TS022的答案条件；14份接受的在线终分、1份评分冲突|

新增39局的完整轨迹均在[结果目录](../../results/README.md)。[更新逐局表](https://huggingface.co/datasets/COMP1110-20261A-Group50/GoodTurtle-experiments)覆盖全部206局；[分来源汇总](https://huggingface.co/datasets/COMP1110-20261A-Group50/GoodTurtle-experiments)保留A、条件、评分版本和批次边界。上次的[固定分析快照](all_versions_20261114.md)仍保留，不能把其中167或113等旧计数当作当前总数。

覆盖说明：本次机械核验全部206局；阅读了新增33个目标局的末卷、前十次提交及选定关键问答，也阅读了6个新前题末卷。导出[390条前十次提交](https://huggingface.co/datasets/COMP1110-20261A-Group50/GoodTurtle-experiments)和[39份末卷及原评分](https://huggingface.co/datasets/COMP1110-20261A-Group50/GoodTurtle-experiments)。**没有完成新增3,852次提交的逐问语义审查，也没有把助手审阅称为人工gold。** 旧批次逐问审阅的既有覆盖范围不因此扩大。

## 2. Set3：相关答案提示的收益，现在比原先更清楚

目标题固定为TS022。表内为原始在线末卷分数，±后是样本标准差，单位均为百分点；源题标签是实验假设。公共baseline只计5局，不为三个A复制三次。

|来源 / 条件|已接受在线终分 / 归档局数|均分 ± SD|取值|完整成功|
|---|---:|---:|---|---:|
|直接做TS022|5/5|26.00% ± 13.87|10–40%|0/5|
|TS047 positive · answer_only|4/5|**68.75% ± 39.24**|90、90、10、85%；另1局冲突|0/4接受的终分|
|TS047 positive · session|5/5|27.00% ± 27.52|10–75%|0/5|
|TS045 negative · answer_only|5/5|34.00% ± 19.49|0–50%|0/5|
|TS045 negative · session|5/5|21.00% ± 20.12|0–40%|0/5|
|TS019 irrelevant · answer_only|5/5|17.00% ± 16.05|0–35%|0/5|
|TS019 irrelevant · session|5/5|28.00% ± 25.88|0–50%|0/5|

TS047和TS022共享“画像其实是窗户，画中人是真人”的反转，因此有强机制联系。新positive答案组的三个高分末卷明确恢复这一点；两个低分/冲突局没有恢复画像误认。此前仅有session的27%对baseline的26%，不足说明相关先例是否有用；现在应改为：**简洁、直接相关的先例答案在本批次更容易被转用于目标题，但并不稳定，完整会话中的同类信息未出现同等结果。**

优先看新答案批次内部：相同目标、相同prompts哈希下，positive组已接受终分高于negative的34%和irrelevant的17%。逐份末卷按“明确写出误认画像、实际窗户和窗外真人”的标准作助手定性复核，positive为3/5，另外两来源为0/10（含评分冲突局的末卷，但不将其变成在线评分样本）。这一内容证据与单看均分互补；[33局复核笔记](https://huggingface.co/datasets/COMP1110-20261A-Group50/GoodTurtle-experiments)保留每局判断。它仍不是人工金标准，也不是新的成功定义。

不能把68.75%当五局的均分。TS047 r03在第100次交卷后，在线checkpoints与覆盖明细给分不一致，控制器拒绝接受，原result仍为error/null。组友另存的助手离线裁决为50%，不是在线终分。若只作该缺失值0–100%的算术敏感性分析，五局均分在 **55–75%**；若单独采用该局50%的离线裁决则为65%。两者都要另标，不能与选择性复核的其他局拼成一个“正式修正后均分”。同批TS019 r01也有在线0%与离线40%的分歧，进一步说明不能择优换分。

**比较仍有实质限制：** TS022的story、grading和Host context哈希与旧session/baseline相同；但新答案组的prompts哈希不同，controller也并非全部一致。新便携包没有完整配置/prompt/request body，因此不能仅凭共同题本断言所有角色提示完全相同。均分差是重要描述性证据，尚不是只改变上下文形式的严格因果估计。末卷和实际早期问题为“相关信息被利用”提供了额外证据。

### 三个可追踪的过程发现

**相关先例能进入搜索，但不是每次都会被提取。** [TS047 answer_only r01](https://huggingface.co/datasets/COMP1110-20261A-Group50/GoodTurtle-experiments) Q5已经问“窗户被误认作picture”，获yes；Q23明确连接真人、窗户与picture。r02 Q20直接检验window/picture，获yes；r05 Q15连接窗户和真人，获yes。另两局虽也有同一A答案，却到终卷仍未恢复画像误认。这里不把宽泛OR问题的yes直接算成全部分支成立，也不只凭画像关键词自动标为机制突破。

**确认的事实可以在最后整合时丢失。** r01 Q90明确问“画中人的影像消失，露出窗户”，Host答yes；Q100末卷却只写清晨认出窗户，没有写人已离开，原C3半分、总分90%。这个案例比“只是没问到关键细节”更具体：外部反馈已经给出，末卷仍遗漏。

**抓到反转也不等于重建完整因果。** [r05](https://huggingface.co/datasets/COMP1110-20261A-Group50/GoodTurtle-experiments) Q35–37确认人已离开、画像为空；最终写出这些事实，却没有明确把“误认画像但感觉被盯着”接到“无法入睡”，原C2半分，总分85%。这与Set1“已确认菜品、却仍写吃完或例行清盘”的失败相呼应：发现机制和整合因果是两个不同环节。

## 3. 新增Set1：完整会话仍没有表现出一致优势

以下是两个新增旧协议批次，不是新版多了两次重复。每个条件每批只有3个B，分别对应三个来源；不是某个固定A下n=3。

|批次|direct，3局|answer_only，3局|session，3局|
|---|---:|---:|---:|
|20261111，旧协议|66.67%|56.67%|30.00%|
|20261113，旧协议|56.67%|50.00%|40.00%|
|原本机统一评分，12局/条件|37.50%|46.25%|27.50%|

新增两批里，session均低于本批direct和答案组；但答案组也没有超过本批direct。因此，**“答案摘要一定优于直接做题”不成立**。目前更稳妥的说法是：完整历史没有保证收益；相关内容、呈现方式和后续反馈利用共同决定效果。

拆到来源可见更具体的模式：TS014 academic-course的两个新session均为0%，末卷仍围绕学业选课记录、请求管理员清空等解释，没有转到菜品。TS015 positive的两个新session为35%和80%，能恢复菜品双关，但仍以例行服务或活动时间表解释清盘。TS028 irrelevant的答案条件也有75%的高分，说明单次高分不能证明来源关系标签正确，反之预设negative也不等于观察到负迁移。

保留必要反例：20261113的TS014设计块 **direct也为0%**，同样困在学业框架，故不能仅凭两个negative session的0分就断言是A导致了固化。新TS015 direct末卷也已恢复菜品反转。因此，将“学业先验锁定”作为可解释案例，而非已隔离的负迁移效应。

旧评分的问题仍需显式分开：[20261113 TS015 direct](https://huggingface.co/datasets/COMP1110-20261A-Group50/GoodTurtle-experiments)原分100%、success=false，完成说明仍列出了缺少嫌弃口味、本人请求清盘等细节。这是coverage-v2把分点评分和完整要求分开的历史产物，**不能据此宣布这局成功，也不能反推当前统一规则坏了**。全集已由9次/3局更新为 **13次/5局**“评分快照100%但不完整”，都保留原值。

## 4. 对CL整体结论的修订

目前主比较CL目标题为146局：145局有正常在线终分，1局在线评分冲突；**没有被在线接受的严格完整成功**。技术冲突不记0分，也不算解题失败的一个已评分样本。完整成功有明显地板效应，应同时报告partial reconstruction与轨迹事实。

现在可分三层陈述：

1. **信息进入搜索：有证据。** Set1 TS015使course更早转向非学业词义；新Set3三个positive答案局将画像/窗户/真人机制用于B。既有内容启发，也有跨题语义方向复用。
2. **反馈转化为完整答案：不可靠。** 新Set3 Q90确认的消失事实未进末卷；Set1已确认菜品仍错写因果。即使方向正确，保留和整合仍可能失败。
3. **完整历史比答案本身更有价值：没有获得一致支持。** 新Set3差值和Set1多个批次更符合简洁相关提示可能较有效的解释，但prompt/controller和长度等混杂仍在。不能把差异直接叫“从经验学会了通用方法”，也不能宣称长上下文是唯一原因。

“CL越跑越稳定”同样没有支持。Set3 positive答案已接受的4局SD达39.24个百分点，包含10%和90%；即使均分上升仍有明显失败分支。原Set1的入口时间稳定与终分稳定分离的[过程结论](project_story_20261114.md)仍成立。不要把更多局混在一起、得到更小的标准误，误写成玩家本身方差变小。

## 5. MAS本次没有新增独立局，结论保持有条件

当前远端新上传的是CL材料；本次没有新增可计为重复的MAS观察。原分析中的主比较仍为：

|题目/批次|单agent均分|双agent均分|范围限制|
|---|---:|---:|---|
|TS038 April旧版，各4局|87.50%|62.50%|旧协议，方向为负|
|TS038本机v14，各4局|25.00%|52.50%|0/4 vs 1/4严格成功|
|TS022，各5局|26.00%|36.00%|0/5 vs 1/5严格成功；baseline与CL共用，不重复算档案|
|TS042|50.00%（1局）|63.00%（5局）|单agent样本不足；两侧都有恢复核心机制的末卷|

显式自查也保持原结论：TS038 solo_review81.25%高于普通solo25%，但实际solver输出约9.17倍；MAS_review仅3局完成，均分41.67%，不能宣称严格匹配实际计算量后仍获胜。共用上限不等于共用实际token消耗。

因此MAS可以讨论“个别互补、纠错成功”与“共享错误前提”两种过程，不能写成稳定优于单agent；更不能把新的Set3答案提示收益当成MAS的新增证据。

## 6. 数据质量、成本及仍需核查的边界

- 全部206局提交顺序/数量、目录原分和原状态一致；20,076次提交包含错误FINAL，正常Host反馈均属于四个允许标签。此机械检查不证明每个回答语义正确。
- 3局异常单列：旧April TS038中断、本机TS038 r04_mas_review中断，以及新TS047→TS022答案r03评分冲突。最后一局交互已满100，属于评分未接受，不是没跑到最后。
- 新Set3 r03不能以助手离线50%悄悄覆盖原null；离线复核的其他个例同样单列。没有进行新的统一离线重评分。
- 新Set3 15局的catalog曾把共同Host context哈希填入observation字段。本次把“上下文哈希”和“带时间戳的原始提交指纹”分开，避免将15次独立轨迹误去重。原result和JSONL未变。
- 所有新局保留token记录，但不是所有局都有完整USD估价：两个旧Set1批次24局均无完整美元估计；新Set3为10/15局有估价，这10局合计约$4.85，**不是15局总账单**。本次分析没有调用付费模型，没有补造缺失费用，也没有将cached input按全价重算。
- 新Set3共享相同题本/评分/Host context，但新旧prompts哈希不同；角色prompt差异的完整定位需要原冻结prompt文件。发布包保留轨迹和评分记录，并不等于可完全续跑的runtime。

## 7. 报告应采用的主线

**建议中心结论：相关信息可以帮助玩家进入正确解释，但从已确认线索到完整因果叙事的转化仍不稳定。简洁答案提示在部分任务上比完整历史更有利；多agent协作也存在局部收益和共同固化。**

证据选择以三个连贯案例为主：Set1词义入口提前但终分不随之改善；新Set3三个positive答案局恢复画像反转、却遗漏失眠因果或人物离开；TS038个别协作纠错与额外计算开销。对照中相似失败、10%低分反例、旧协议不一致、prompt/controller差异同时披露。这样项目回答的是经验与协作怎样影响搜索和整合，而不是预先假定某方法一定赢。

可用于英文报告：

> Relevant prior answers sometimes helped the player recover the target mechanism, but this did not ensure complete narrative reconstruction. In the newly added portrait/window task, the positive answer-only condition averaged 68.75% over four accepted online grades, compared with 26% for the five direct controls; a fifth answer-only run ended in a grading conflict. Three answer-only final submissions recovered the portrait/window mechanism, while confirmed details could still be omitted from the final account. The corresponding session condition averaged 27%. Prompt and controller differences, small samples, and substantial dispersion limit a causal interpretation of these contrasts. Multi-agent findings remain task-dependent and require accounting for actual computation.

本次不新增付费实验、不修改Host或评分、不用事后机制审阅冒充正式成功率。可复核数字和原问答放在CSV/JSON/Markdown，不再生成聚合HTML。

## 离线复现

```bash
python scripts/results_catalog.py check
python scripts/results_catalog.py summarize
python scripts/analyze_latest_results.py
```

输出为 `results/tables/20261114_latest_update/`。`by_condition.csv`保留批次；`by_source_condition.csv`进一步保留A。`validation.json`给出全集、新增、异常与审阅范围；旧168档案分析快照保持不动。
