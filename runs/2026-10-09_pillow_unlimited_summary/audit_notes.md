# Host 与实验流程审核疑点（已暂停）

以下为控制器的语义审查意见，尚非人工标签或准确率。试跑标签保持原样，不将意见反馈给 solver/host，也不在运行中修改 prompt。本记录对应用户要求暂停时的轨迹。

适用版本为每局冻结的 **HOST PROTOCOL v0.4**，不是后来修改的工作区共享 prompt。应优先检查 A01/A05/A09 的一致性和 A02 的示例设计；其余项目需要结合语境定标，并非已确认错答。

协议层限制：`yes and no` 同时承载“独立主张部分正确”“事实未指定”和“歧义”。这符合当前三标签规则，却不能让 solver 从单个标签辨别是哪一种原因。它可能增加提问成本，但本轮数据尚不足以定量归因，也不能把所有这种标签都算作 host 错误。

## A01：几乎等义的开场问题得到不同标签

- Run 01 Q1: “Was she arrested because one of the listed items concealed something illegal?” → **no**
- Run 03 Q1: “Was she arrested because something illegal was hidden inside one of the items she listed?” → **yes and no**

两题都是开场问题，无历史指代区别；均询问列出的某件物品内部藏有非法物品是否导致被捕。冻结资料和示例完全相同。标签差异值得优先核验：应明确隐藏于独立物品这一前提是否为错误解释，还是包装未定；当前三个标签承载的判断不稳定。不能据两条样本推算整体错误率。

## A02：专属示例 P074 本身存在解释风险

冻结 P074 将 “Was the severed hand placed inside a real pillow?” 标为 **yes and no**，以包装未知解释。但谜底的核心是手本身被她当作枕头；是否包布与是否放进独立真枕头是不同主张。

- Run 02 Q3: “Was the human body part hidden inside the pillow?” → **yes and no**

这与上一批有上限实验中反复出现的混淆相同。应在后续版本明确核心物品身份和容器关系，单独保留对包裹方式的未知回答。本轮保持该示例不变，以免中途改变实验条件。

## A03：枕头“损坏”的语境

- Run 01 Q10: “Was the pillow physically damaged?” → **yes**
- Run 01 Q11: “Did the pillow have a hole made by a bullet?” → **no**

第一问可以理解为 severing 造成身体损伤，因此 yes 有可辩护理由；但也可能强化“普通枕头损坏留下犯罪证据”的语境。需要结合后续轨迹判断，不直接把它标成错答。

## A04：limb 上位词与 hand 精确要求

- Run 03 Q38: “Was the object she called a pillow a severed limb?” → **no**
- Run 01 Q38: “Was a severed human limb inside the pillow?” → **yes and no**

第二题还包含 inside 前提，因此不能只看 limb 认定完全同义；但需要明确 hand 是部分上肢的自然语义如何处理。严格否定 arm 的近似替换，不意味着可以随意否定较宽泛的身体部分描述。

## A05：普通包装前提在长对话中漂移

- Run 01 Q35: “Did the pillow contain human remains?” → **yes**
- Run 01 Q44: “Did the pillow contain a severed human hand?” → **yes**
- Run 02 Q3: “Was the human body part hidden inside the pillow?” → **yes and no**
- Run 02 Q34: “Was the severed hand physically inside the item she called a pillow?” → **no**
- Run 03 Q11: “Did the pillow contain human body parts?” → **yes and no**
- Run 03 Q23: “Was the pillow's filling made from human remains?” → **no**
- Run 01 Q149: “Was the object she called a pillow actually a conventional soft pillow?” → **no**

这些问题不是逐字相同，也有不同前文，但 contain/inside/filling 与“手本身是枕头”的关系需要统一。Run 02 Final 1 在已获得手本身=枕头的 yes 之后，仍写成枕头藏手。后续需审查实例如何影响推断，不能仅凭模型最终猜中或猜错评 host。

Run 01 直到 Q149 才直接排除 conventional soft pillow；应将这一回答与本局 Q35/Q44 的 contain=yes 并列审查。前面的描述是否造成额外分支，是待验证的因果假设，不能把期间全部提问都算成由 host 错答造成。

## A06：时间与用途

- Run 02 Q26: “Had she used the severed hand as something to rest her head on?” → **yes and no**
- Run 02 Q49: 询问切下之前拿他的手垫头 → **yes**（完整原文见合并轨迹）。

前者可能指切下之后是否已经实际使用，后者是过去习惯。应核验时态解释，不直接判两个标签矛盾。故事明确的是手作枕头的关系及切下保留的目的，不要求捏造切下之后已经睡过觉。

## A07：离开角色与时点

- Run 02 Q50: “Was she leaving her partner behind when she reached the checkpoint?” → **yes**
- Run 02 Final 2（53 问后）: “She was leaving her romantic partner.”，随后正确恢复手作枕头和安检发现。

问题指定安检时点，回答可理解为她当时独自携带断手出行；最终解释却省略男方在公寓准备离开的前因，容易被读成她主动结束关系。不能把不同时间的 leaving 合并。缺少 R1–R4 足以判不完整，判分不依赖对这句含混表达的单独裁决。

## A08：动机的宽泛概括

- Run 01 Q51: “Did she cut off his hand in revenge for something he had done to her?” → **no**
- Run 01 Q55: “Did she sever his hand to prevent him from doing something?” → **yes**
- Run 01 Q56: “Did she cut off his hand to stop him from leaving her?” → **no**

直接意图是保留她称为枕头的手；背叛、拒绝挽留是背景。需要审查 host 是否对“报复”“阻止”进行了过度狭义或宽泛解读。Q55 的 yes 应能由固定故事支持，不能靠未说出的其他行为。后续 Q57/Q58 分别追查武器与联系别人，均 no；这些分支原样保留。

## A09：同局互补命题的时间状态不一致

- Run 03 Q87: “Was her partner already dead when she removed his hand?” → **yes and no**
- Run 03 Q91: “Was her partner alive when she severed his hand?” → **yes**
- Run 02 Q47: “Was her romantic partner alive when she cut off his hand?” → **yes**

在固定故事与常识下，Q87 与 Q91 针对同一个切手时点，互为相反状态，应该先统一能否推出当时活着。其间的公开问题未增加新的权威故事事实。切手之后是否死亡未定，不能自动推成切手之前生死未定。这是同局一致性优先审核项。

## A10：宽泛“纪念物”得到 yes

- Run 03 Q86: “Did she take the hand as a keepsake?” → **yes**

保留她称为枕头的手可被宽泛理解为保留与恋人有关的物品，但 keepsake 不能替代真正的 headrest 用途。Run 03 Final 2 同时写明 headrest 与 keepsake，核心用途已经恢复；不能仅因用了这个词额外判错。是否该 yes 过度扩展动机，需要人工定标。

## A11：先前同住与安检前紧接时点

- Run 03 Q79: “Had the woman and her partner been staying together immediately before the checkpoint?” → **yes and no**

汤底明确他们共享公寓，未说明安检距公寓事件多长时间。审核时要保留 immediately before 的限定；不要用“共同居住是 yes”机械覆盖含严格时间限定的新问题。另一方面，也需审查 host 是否对普通语境过于字面化，妨碍恢复本来明确的同住事实。

## A12：含“部分动机”的报复问法

- Run 02 Q93: “Was revenge for his decision to leave her part of her motive?” → **no**

与 A08 一起复核：这是问兼容的部分动机，而非把报复规定为唯一因果解释。故事明确她保留枕头的目的，是否足够否定报复成分，需要标注者统一，不能仅凭未写出就自动否定。

## A13：普通枕头假设始终无法排除

- Run 03 Q117: “Was there any conventional pillow in the luggage in addition to the severed hand?” → **yes and no**
- Run 03 Q121: “Was there a cloth or fabric pillow in the luggage?” → **yes and no**
- Run 03 Q131: “Did security find a soft, stuffed pillow in the suitcase?” → **yes and no**

这三条自身标签一致，但与 A02/A05 共同暴露建模问题：host 是否应把未指定的额外普通枕头视为开放事实，还是依据题目物品清单和指定的身份反转排除它？当前示例使 solver 无法通过改写问题排除普通枕头分支。此处首先是资料和标注规则的审核项，不能简单归责为模型没有遵循示例。

## A14：解剖边界与精确伤口不是同一要求

- Run 03 Q123: “Was his hand severed at the wrist?” → **yes and no**
- Run 03 Q130: “Was any part of his forearm still attached to the severed hand?” → **yes and no**

用户要求严格区分 hand 与 arm；这不自动要求精确到伤口位置或是否有极小段相邻组织。需要人工明确何种自然语言判断足以区分手与整条手臂。评分只要求切下 hand，不会因没有猜出伤口细节而否决完整叙事。

## A15：被捕原因与具体罪名的解释

- Run 03 Q126: “Was she arrested specifically for mutilating her boyfriend?” → **yes and no**

正常语境可把这理解为问伤害男友是不是被捕原因，故事应足以支持；也可能把 specifically 过窄地解释成未知的正式罪名。需要审查是否因法律精确性而把明确因果转为模糊标签。当前不能从这条回答断言真实罪名，也不应要求 solver 还原罪名。

## A16：严格评分的部分覆盖不能误读为全错

Run 02 Final 7（Q147 后）已经写到男方收拾行李、女方挽留、男方坚持离开、请求继续把手当枕头。其 R1–R4 的 `false` 表示“该复合要素尚未完整”，不表示这些已恢复部分都错误。

- “he insisted on leaving” 可以忠实表达拒绝挽留，不另外要求逐字出现 “did not look back”。
- 请求继续把手当枕头可表达保留枕头的请求，不要求逐字背诵原台词。
- 此次仍缺明确的当日背叛、共同公寓、含泪挽留与冷冷提出请求的完整叙事；拒绝这次交卷符合冻结的完整叙事要求。

原始评分记录保留，并补充私有审核澄清；上述解释未发送给 solver。人工审查应同时检查 grader 是否过于字面化，不能只检查 host。

## A17：分手原因与背叛事件的区别

- Run 03 Q158: “Is the reason her boyfriend ended the relationship essential to the explanation?” → **no**

冻结答案要求还原“他当天背叛她”，没有解释他为什么决定结束关系。因此不能直接把这个 no 判成否认背叛。但 solver 在寻找遗漏前因时，可能将其理解为无需进一步探索分手背景。应检查正常语境下 host 的判断是否足够贴合问意，并与后续问题联读；目前仅列为疑点，未确认错答。

## A18：host 未收到交卷内容，无法可靠解析“上次解释”

- Run 02 Q155: “Does my last final explanation contain an incorrect factual claim, apart from leaving out details?” → **yes and no**

当前实验把交卷发送给控制器评分，没有把交卷原文追加到 host 会话。因此 host 并不知道此处 last final explanation 的全文。该标签可能是恰当的歧义回退，不能直接归为 host 推理错误；但这是运行框架造成的上下文缺口，会使 solver 难以区分“遗漏”与“错猜”。原始 relay 已保存，可核对 host 实际看到的内容。本轮保留既定流程，不临时补上下文；后续协议应明确最终交卷是否进入双方公开历史，不能只增加 few-shot 而忽略这个问题。
