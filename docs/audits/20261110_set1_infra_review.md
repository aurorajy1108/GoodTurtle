# Set 1 轨迹与恢复审核（2026-11-10）

审核对象：`runs/api/20261109_deepseek_set1_cl_quotes_resume04`。
本次判断由助手根据完整汤底、原始问答、请求消息链和代码复核，未新增模型评审或实验 API 调用。

后续更新：本记录描述修复前的v2试跑及当时的恢复验证。当前main已迁移到v3参考缓存协议，不能将新的恢复overlay套进这批v2归档；下文恢复命令仅适用于兼容的旧恢复版本。用户已选择修复后新批次重跑，当前入口与全部设置见[Set1 v11重跑说明](../set1_v11_rerun.md)。

## 结论

会话隔离、额度、A 答案揭晓、固定前题和基础记录符合当前设计；Host 的语义判断仍有足以改变搜索路径的错误。当前批次应保留为诊断试跑，不能当作已验证 Host 下的正式 CL 证据。恢复工程和更换 Host/参考答案是两件事：续跑须保持本局旧规则；修订规则后的正式比较应使用新批次。

## 已检查的实现

| 检查项 | 观察结果 |
|---|---|
| 持续会话 | 三局成功调用中，每个角色各有一个消息链 lane；不是每问重新建立独立聊天 |
| 当前汤底 | 逐次还原成功 Host 请求的 JSON delta，完整 canonical story 始终存在且未变 |
| 角色隔离 | 还原后的 Player 顶层只有 opening、visible_history、turn_control、可选 prior_experience；未发现私有评分/当前答案字段混入 |
| CL 前题 | A14 完成后揭晓完整答案；失败未触发重抽 A；answer_only 的 A 题面和完整答案在 B 中固定 |
| 对照 | direct 没有 prior_experience；各角色与其他游戏会话隔离 |
| 配额 | source=98普通问题+2错误提交=100；answer_only=99普通问题+1错误提交=100；direct=37普通问题+2错误提交=39，其中最后一个普通问题待回复 |
| Host 调用 | 三局分别98/99/37次 Host 请求，对应98/99/37个普通问题；最后一次失败。未发现每问多次判定 |
| Grader | answer_only 最终交卷输入3743 tokens；没有再发送完整聊天或全量 Host 参考库。direct 两次评分输入3688/4744 tokens |
| 模型 | Host/Grader=`deepseek-v4-pro`、thinking enabled/high；Player=`deepseek-flash`、thinking disabled。这是此批次冻结配置，并非早期的6.1 sol设置 |

机器核对明细：本地 `output/audits/20261110_set1_infra/checks.json`。这里只核对结构与可见字段，不等于证明全部自然语言判断正确。

## 关键语义疑点

| 游戏/提交序号 | 原问题与回复 | 审核判断与影响 |
|---|---|---|
| A14 / 32 | “Did the student's failing grade result from a decision by someone other than the student and other than the course instructor (such as an administrator or committee)?” → **yes** | **明确错误，应为no。** 汤底是其他组员搭便车，工作量使项目质量差而挂科，不是管理员/委员会另作决定。把“他人不做事”错当“另一个决定者”，引入不存在的角色。 |
| A14 / 94 | “Was the decision-maker a teacher or professor after all, rather than an administrator/committee?” → **yes** | 与32的角色判断直接冲突。94不能挽回之前的路径污染；不要把“最后又换回教师”理解为已经恢复完整因果链。 |
| direct13 / 18 | “Is the story's twist simply that the student confused the meaning of the word: the academic ‘course selection’ is irrelevant, and ‘all my courses were gone’ refers to the meal courses the student ate during the evening?” → **yes** | **不应完整肯定。** 已知不是“仅仅吃完了菜”的谜底，也没有学生自己混淆单词的情节。按当前拒绝错误核心解释的规则，建议no；需加入因果与“simply”边界案例。后续两次交卷却给混合反馈，使问答与解答判定不一致。 |
| direct13 / 2 | “Was the disappearance ... caused by something the student did themselves (such as accidentally dropping or deleting their course selections)?” → **no** | **范围有歧义，需明确边界。** 广义“本人做的事”包含主动叫服务员收走；但括号举的是错误选课操作。不能直接照搬旧例“own action or mistake in the course selection system → no”。应拆分这两个问题做回归校准。 |
| answer_only13 / 18 | “Did you submit your course selection ... shortly before the courses disappeared?” → **yes** | “之前表达菜品偏好”有依据，“shortly before”没有具体时间依据。需要校准主体事实与附带时间限定的规则，不能从这句确认一个当晚提交/系统处理机制。 |
| answer_only13 / 58 | “Did you submit your chosen dishes/menu, and the dishes all disappeared because someone else ... took or served them elsewhere?” → **yes** | “别人拿走”可指服务员，因而**不能仅凭这个yes判错**；但“served them elsewhere”不是汤底机制。此种宽泛析取使 Player 错把正确支路理解为错送/被别人吃掉；适合改写为更精确的校准题，不能把整个问题直接认作全部为假。 |

注意两个容易误判的正确/合理回复：

- answer_only13 / 94：问“服务员收走，例如在能吃之前清走”，Host=no。汤底是尝过后主动要求收走剩菜；不能直接改成yes。
- A14 / 5：问项目“did not complete”，Host=no。汤底是**完成得差**，不等于没完成。Player 应拆分“存在项目”与“没完成项目”。

## 架构与研究设计仍需改善的地方

1. **单次 Host 判断满足预算要求，但不能保证正确。** 保留一次调用，优先用上述因果/角色/范围的离线金标准回归集校准；不要以在线重复询问同一模型的多数票替代验证。本次没有更改 active pack 或本批 prompt，避免静默混入不同实验条件。
2. **轮换参考案例仍在持续消息链里累积。** 每轮发送本轮检索到的最多6例，变化时整个案例数组替换；旧消息仍留在 DeepSeek 请求中。answer_only Host 输入从3651涨到37232 tokens，A14从3272涨到30316。持续会话并不表示旧 token 不再处理；约97.4%的已记录输入 token 命中缓存也不等于免费。下一版本可用每局 case_id→语义缓存，只追加未见案例并给本轮 active IDs；必须测试“未激活旧例不是当前证据”和指代边界后再用。
3. **模型需要在脑内应用 JSON delta。** 本地可无损重建，不代表模型永远正确维护状态。这里不能将 Host 错误归因于 delta 已被证明损坏；实际请求中完整汤底一直可还原。当前失败也可能来自错误历史锚定、限定词/因果解析。需要固定问题的受控回归比较，而不是根据一次轨迹定因。
4. **仅有每条件一次，不能估计variance或迁移效应。** direct在第8次提交确认食物含义，answer_only到第54次才确认，表现出值得追查的学业框架固着；Host误导及抽样波动均可能解释，不能据此证明负迁移。direct未完成，也不能拿0.25中间分与0.55最终分作结论。
5. **100是截断上限，不是所有失败的真实解题难度。** 同时报成功率、最终/最好partial score、达上限比例；中断单列，不能算解题失败。完整实验后才能讨论重复次数和不确定性。
6. **固定A减少前题波动，但结论只针对这一份prefix。** transcript会保留A14中错误Host反馈；完整答案揭晓不必然让模型彻底忘记错误推理。answer_only没有旧问答，却仍激活学业语义。两条件应分开解释，后续可增加经审核的干净prefix对照。

## 为什么停止

- 时间：2026-11-09 17:27:05 香港时间。
- 游戏：`S1_TS014_TS013_TS014_TS013_r01_direct`。
- Player第39次提交完整、合法且已保存；Host第37次调用（前面有2次交卷）失败。
- 日志：`URLError`，内部`SSLError`，errno=1，`transport_category=tls`，`transport_phase=open`，`safe_pre_send_retry=false`。
- `open`包含建立连接、发请求和等响应头；现有证据**不能确认**发生在HTTP发送之前，也不能确定根因是代理、网络或服务端。没有HTTP状态码或返回文本；没有证据说明是额度、API key错误或问题上限。
- provider故意不自动重试无法确认发送阶段的请求，以免重复生成/计费；局内捕获APIError，批次`--on-error stop`终止后续实验。原persistent恢复入口又一律拒绝这种未获回复的传输中断，所以不能直接原命令继续。

## 本次实现的恢复入口

新增 `scripts/resume_study.py --recover-host-transport`，仅适用于可核验的DeepSeek三角色单玩家、最后一个Host请求无返回、恰有一个待反馈普通问题的情形：

- 在新目录复制归档，保留已完成A14及answer_only13；保持题目、prompt、rubric、模型和顺序不变。
- 验证所有已收到响应的角色消息链、已有Player动作和待反馈问题。
- 还原Player/Host/Grader各自消息；失败调用保留在审计和成本统计中，但不伪造成一条assistant回复。
- **发送前严格比较整个恢复请求body与原失败请求body。** 有差异直接拒绝，不消耗API。
- 先为保存的第39问取得Host回复，再生成第40次提交；不重新解A、不重生成39问、不重复扣题目额度。
- 标记`possible_duplicate_remote_charge=true`：原请求可能已在远端处理，重发仍可能另计费。不能承诺服务端exactly-once或费用为零。
- 不支持泛化恢复任意MAS、已收到但不喜欢的回复、缺失消息链或多次混杂失败。

验证：191项unittest通过；额外将本批真实第39问的整个请求离线重建、拦截比对通过，**未发出真实HTTP请求**。恢复检查副本位于`runs/api/20261110_deepseek_set1_cl_tls_recovery_check`。

可运行命令（会继续该批剩余条件，需在已export key的终端执行）：

```bash
cd /Users/aurorasun/Desktop/COMP1110/GP/GoodTurtle
python3 scripts/resume_study.py \
  --from-study runs/api/20261109_deepseek_set1_cl_quotes_resume04 \
  --out runs/api/20261110_deepseek_set1_cl_tls_resume05 \
  --recover-host-transport --mode run
```

`--from-study`是原停止批次，`--out`必须是不存在的新目录，`--recover-host-transport`显式启用上述限定恢复，`--mode plan`只复制/检查，`--mode run`才执行模型调用。本次尚未启动收费续跑，也没有推送代码。
