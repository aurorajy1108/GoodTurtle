# 本轮审核疑点与局限

这是运行中识别的定性疑点，**不是对所有问答逐条完成的人工作答准确率审计**。原标签和原运行均未改写；AI 建议不是人工 gold。

## 待审核条目

### TS031 第 13 次提交

Was the eraser attached to the end of an ordinary pencil, as a pencil-top eraser?

原标签：`yes`；状态：待人工复核。

“ordinary pencil” 可泛指普通铅笔，也可能被玩家理解为木杆铅笔；Host 的 yes 不能视为确认木杆结构。需连同下一次失败交卷审核。

### TS035 第 8 次提交

Had bears already dug up and eaten other villagers’ buried dead before this incident?

原标签：`yes and no`；状态：待人工复核。

此前已有其他遗体被熊挖出是否属关键未知：Q8 为 yes and no，Q10/12 对类似既往事件为 irrelevant。复核标签边界一致性。

### TS038 第 12 次提交

Is the speaker worried because the draft reveals something they intended to keep secret from its recipient?

原标签：`yes`；状态：待人工复核。

问题预设有 intended recipient 并询问隐瞒；汤底是伪造妻子离家笔迹，未指定具体收件人。检查 yes 是否无意确认额外角色。

### TS038 第 30 次提交

Did the speaker write the draft to create or support an alibi for the killing?

原标签：`yes`；状态：待人工复核。

alibi 狭义指案发时不在现场，汤底只确立伪造妻子离家证据。检查此 yes 是否把一般掩饰犯罪混同为不在场证明；结合 Q31 的后续澄清审核。

### TS035 第 56 次提交

Would villagers’ distress come from discovering bears eating their deceased relatives, even though the bears posed no danger to living people?

原标签：`yes`；状态：待人工复核。

父亲不担心熊攻击活人不等于熊客观上对活人无危险。问题 even though bears posed no danger to living people 强加了绝对事实；原 yes 过度肯定。建议复核为 yes and no：亲属悲伤部分有依据，客观零风险未确立。 题面说 rarely attack unfamiliar living humans，不是 never attack。

### TS031 第 57 次提交

Did the pencil support the separate graphite indirectly, through another object or part, while A wrote?

原标签：`yes`；状态：待人工复核。

another object or part 的 part 可包括自动铅笔内部夹持部件，但宽泛 yes 被玩家继续解释为外部支架。审查问题范围与后续 Q58/59，不将其直接改写成对外部装置的肯定。

### TS035 第 68 次提交

Was the ongoing consequence he feared chiefly that other villagers would be traumatized by finding bears eating their buried relatives?

原标签：`yes`；状态：待人工复核。

Q68/Q70 将主要担忧设为亲属精神创伤，Q71 明确区分并说主要担忧尸体被吃，Host 都肯定。情感反应可合理推测，但不能忽略 chiefly/rather than 所要求的优先级；对照汤底复核。

## 已撤销的初步标记

TS038 Q86：一开始只按简短汤底误以为“对收件人失望”无来源；检查题面后发现其反复明确出现 You've disappointed me，已撤销该标记。完整审核必须同时看题面、汤底和公开历史。撤销前记录保留在 JSON，避免隐藏审核过程。

## Player 行为与评分边界

- TS031 在“笔尖不可用”及“支撑另一段石墨”的假设上逐步固化，最终编出外部导向装置，未还原取下橡皮、加入铅芯的机制。宽泛问题中的物件指代需要特别复核。
- TS035 多次重复交卷同一主线，遗漏疫情、燃料不足及每日扫墓等背景；只给四标签时，玩家未能定位这些遗漏。
- TS038 找到杀人后伪造离家字条和笔迹暴露，但没有确定死者为妻子。后续通信也不是参考答案确立的事件。
- 这三局每题仅运行一次，没有重复实验或模型间比较，不能据此宣称整体准确率或效率差异。
- final partial score 为未人工确认的模型评分；不采用最高历史分替代最后交卷分。
- 已归档模型模拟问答，不自动写入 active Host，来源不标为人工。
