# 项目主线：经验与协作如何改变推理路径

> 本文保留原Set1过程分析。最新39局及补齐后的Set3见[更新分析](latest_results_20261114.md)，新增“已确认人像消失却未进入末卷”的跨题佐证；本页原36局数字保持不变。

项目的目标是提取可靠结论。六个建议只作为寻找证据的工具，不各自扩成一个实验，也不预设一定能证明“学会方法”“失败经历有益”或“CL更稳定”。根据已经完成的数据，建议保留两个核心研究问题。

**RQ1：前题经验能否帮助玩家进入正确解释，以及这种进展能否经反馈修正转化成完整答案？**

**RQ2：多agent与显式自查能否改善探索和纠错，其实际收益与计算开销是什么？**

这两问将题库、Host、自动实验框架与实证结果连接起来。项目的贡献包括可重复运行与审查的海龟汤实验平台，以及对上下文迁移和合作求解的探索性证据。没有更新模型权重，应将CL明确称为continual in-context transfer。

## 一、目前最扎实的过程结论

### 1. 相关经验改变了一个关键词的解释优先级，不能据此宣称学会通用策略

Set1中固定A=TS015，“course”在A中指河道；目标题TS013中指菜品。以下使用全部12个对应B，而非只选成功或高分局。每个条件四次B重复，但均只对应这一份固定A。

|条件|首次有汤底支持的菜品解释：四局提交序号|前10次内达到|中位序号|最终原分均值±样本SD|
|---|---|---:|---:|---:|
|direct|21 / 10 / 19 / 38|1/4|20|36.25% ± 14.36个百分点|
|answer_only|3 / 3 / 5 / 61|3/4|4|56.25% ± 6.29个百分点|
|session|2 / 7 / 2 / 2|4/4|2|45.00% ± 18.26个百分点|

这里的节点是**已有逐问AI审阅标出的、由冻结汤底支持的菜品词义问答**。它不是第一次提到任何食物词，也不是完成因果重建；没有将Host任意yes数量当进展。序号计所有外部提交，错误FINAL也占额度。

A中Q13询问是否非学科意义，Q20到水道、Q93到cross the river；B的session r01在Q1检查academic classes，Q2检查dishes/meals。这是可追踪的语义方向复用。答案内容是河道，B却切换到菜品，因此不只是逐字搬答案。

但是answer_only也明显提前：仅提供A答案已足以提示course有歧义。现有对照不能分开“这个词的语义启动”与“从A问答学会通用前提检查策略”。**可采用的结论是词义搜索优先级改变；策略习得仍无充分证据。**

### 2. 更早进入有效方向，不保证后续整合更好

session比answer_only更早、更一致地到达菜品解释，但终局均分更低。另一个维度也分离：session的节点序号样本SD为2.50次，answer_only为28.68次；终局分数SD却分别为18.26和6.29个百分点。**在这一固定A下，探索入口的一致性与终局分数的一致性并不相同。** n=4是描述，不是显著性或总体稳定性证明。

[固定A下，早期语义入口与最终分数可以分离（归档图）](https://github.com/aurorajy1108/GoodTurtle/blob/c4ccc67eef8c09aa0c6987a464f468718f5015f4/reports/20261114_transfer_process/semantic_entry_vs_final.png)

图中每个点是一局B，标号是本地重复编号；左侧横线为中位数，右侧为均值±样本SD，均非置信区间。A固定于两个有前题的条件，direct未收到A。CSV中direct的fixed_A仅标记设计块，不表示实际暴露。只展示预设positive来源TS015的条件个案，其他来源的全部36局数字在CSV中，不把此图推广为所有CL的规律。

看全部Set1，direct/answer_only/session最终有10/12、11/12、8/12局出现菜品解释节点，但36局都没有严格完整成功。原Grader对终卷C3“清走剩菜及相关因果/叙事”的信用为26局零分、10局半分，没有满分。C3包含细节门槛，不能只凭这个分布推断36局全都不懂因果；下面的具体反例提供更直接的解释。

### 3. 反馈有时改变局部问题，却没有改变主导解释

`TS015→TS013 r01_answer_only`：Q3已经是菜品。Q41问“all my courses were gone仅表示吃完晚餐吗”，Host答no；Q76、86、87、92、99又否定相近的“本人全部吃完导致消失”解释。Q100仍交“本人选好菜品，吃掉后全部消失”，C3=0，终分55%。

这不是词义没有突破，而是**已被相关反馈排斥的主导因果解释进入了末卷**。其中也有有效局部探索：Q24混合问后，Q25拆查吃饭与截止的关系；Q54确认是在截止后吃饭，Q91确认提前选菜。不能把整段概括为完全不利用反馈。更准确的是：局部时序更新没有带来主导解释的修正。

`r02_session`在Q7达到菜品，Q12达到有人清走；Q63确认宴前菜单选择。全局19次FINAL，最后仍把deadline称为误导，未完整表达清走不喜欢的剩菜这一因果链，终分35%。这里观察到的是外部问答和交卷的整合不充分，不推测模型隐含信念。

## 二、TS033→TS034：一个有力的“未验证前提锁定”案例

`TS034_TS033_session_r02` Q30：

> Does the father know that his daughter is already in police custody **or otherwise safe** at the time of the call?

Host答yes。此时能成立的是女儿当前自由安全，**OR并没有确认警方拘留**。

随后Q31–96连续66次得到no，大量问题都问女儿为什么在警方处、警方何时通知父亲。Q97仍交“父亲知道女儿在警方处，所以绑架是假的”，再次被no；Q98才换成危险/圈套解释，后面已只剩几次FINAL，未恢复完整角色关系。

不能写成“同一个假设被明确否定66次仍不改”：这些no多数否定的是整句具体情节，不在逻辑上逐个否定所有共同前提。真正可见的问题是，玩家将OR的一个分支升级为背景事实，此后不断修改细节，却没有原子回查“女儿真的在警方处吗”。

Q66还提到“after the earlier mugging incident”。TS033源题有被抢劫背景，TS034题面没有建立这件事。这是**源题细节被带入新题前提的可定位线索**，但仅凭一句提问仍不把整段行为全部归因为前题经验。

可以与TS015→TS013 r04_session的开场对照：Q1问courses是否是class enrollments而不是river routes，收到no后Q2改查菜品。这里把旧解释作为待检验候选；警方案例则在OR后反复使用一个尚未确立的前提。两种行为都存在于经验条件中，不能只依据“提到A的概念”就把迁移记为成功或失败。

这个案例支持“父假设未验证，反复枚举子解释”的行为机制；它不证明negative经验必然有害，也不证明该机制只存在于CL。

## 三、必须主动保留的反例与替代解释

1. **direct也会坚持错误解释。** TS015设计块的r04_direct在Q98得到no后，Q99/100仍写本人吃完所以消失。故“反馈整合失败”是这批玩家的一般限制，不能全部包装成负迁移。
2. **需隔离Host反馈疑点。** TS015 r04_session在Q2正确到菜品，Q6却被yes确认“另一人先拿/选走”，前次AI审阅将它列为与冻结故事不一致的疑点，尚非人工gold。若该疑点成立，后续分支也包含主持反馈污染，不能直接证明经验导致思维定势。
3. **会话较长与故事内容都可能起作用。** 现有session没有与它同长度、同角色格式的无关对话控制；answer_only也含A汤面和答案。两组不是严格的“知识vs纯策略”隔离。
4. **原分包含严格叙事要求。** 完整答案的缺项、真正错因和Grader释义边界应分别解释。原分保持不动，不把新增过程指标作为替代成功规则。
5. **一个失败A不能识别“从失败学习”。** TS015的A未解完整，但随后给了官方答案；answer_only也看了答案。B的改变可能来自答案提示，无法独立证明纠正失败经历本身有效。这个方向保留为后续问题，不作为当前主结论。

反例使项目结论更精确，而不会抵消已经观察到的路径变化。

## 四、六个建议最终如何取舍

|建议|本项目的处理|
|---|---|
|答案内容还是探索方法|采用为解释边界：有语义方向复用证据，没有独立的通用策略习得证据|
|起手方向|作为首个定量过程结果；按固定A组织，使用实际问答节点及原文|
|方向感与定势|采用经过核验的机制案例；区别OR过推、正确反馈后的坚持、Host污染|
|发现还是整合|并入主线：用早期节点与终卷事实/原评分对照，不再另开研究支线|
|表现稳定性|区分节点时间与终局分数；只作固定A下描述，不宣称总体方差已减少|
|失败经历是否有用|现有设计不能独立回答，移到future work|

不新增“问题里有rather than就算策略好”“no越多越顽固”“yes越多越接近答案”等简化计数，也不在事后试很多指标后只报告漂亮结果。案例是回顾性选择，不声称66次这类锁定在全部轨迹中有某个发生率。

## 五、形成有意义的项目结论

建议主文用三个层次组织：

1. **最终表现**：原始partial reconstruction score、严格完成率、所有提交数与成本。CL的100次顶格不是解出所需问题数；不要把partial score直接叫未经定义的accuracy。
2. **过程变化**：前题怎样改变候选解释的起点；正确线索是否进入后续问题和末卷。Set1提供完整36局的过程描述。
3. **机制案例与反例**：以TS033的警方前提锁定、direct的相似失败、Host误导对照，解释为何早期收益不总能兑现。

MAS作为第二研究问题，继续沿用[跨版本综合分析](all_versions_20261114.md)：个别轨迹有互补探索和实体纠错收益，也有共同固化；自查开销会挤占外部探索。不要把整个项目压在“MAS必须优于单agent”这一单一结论上，也不要把所有问题都归给Host。

**当前可以作为中心结论的表述：**

> 相关前题能够改变玩家进入问题的方式，但这种早期方向收益不保证转化为完整重建。轨迹表明，未被确立的前提可能在反复追问中固化，局部反馈更新也可能没有进入最终解释。相似失败在无前题的控制局中同样出现，说明经验提供的信息与玩家的反馈整合能力需要分别考察。

可用于英文报告的表述：

> Prior-puzzle context can alter the route into a lateral-thinking problem without ensuring complete reconstruction. In one fixed-source ambiguity case, the median first supported meal-course interpretation occurred at submissions 20, 4 and 2 in the direct, answer-only and session conditions, respectively. Earlier entry in the session condition did not yield a higher final score than answer-only. Retrospective cases show unverified premises being retained across repeated probes and relevant feedback failing to change the final explanation. Similar failures in direct controls prevent attributing these patterns solely to transfer.

这是一项关于**经验、搜索、反馈与解释整合如何相互作用**的探索性研究。工程平台和可审计轨迹使这些问题能够被具体检验；结果可以是条件性的、有正反案例的，不需要预先保证一个方法稳定获胜。

## 数据与复核入口

- [36局逐局过程指标](https://huggingface.co/datasets/COMP1110-20261A-Group50/GoodTurtle-experiments)及[九个固定A/条件汇总](https://huggingface.co/datasets/COMP1110-20261A-Group50/GoodTurtle-experiments)：沿用原分与上轮逐问语义审阅节点。
- [全部360条前十次提交原文](https://huggingface.co/datasets/COMP1110-20261A-Group50/GoodTurtle-experiments)：没有自动把关键词映射成策略标签。
- [六个案例原问/回答](https://huggingface.co/datasets/COMP1110-20261A-Group50/GoodTurtle-experiments)：包括direct反例与Host污染；不是人工gold。
- [构建/一致性验证](https://huggingface.co/datasets/COMP1110-20261A-Group50/GoodTurtle-experiments)。离线重建：`python scripts/analyze_transfer_process.py`；原绘图脚本和图表在完整归档分支保留。无API调用，不改实验或评分。
