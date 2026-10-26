# Host 与对照设计修复 v7（2026-10-24）

状态：旧 v6 / CL 批次按用户要求暂停；本次不启动正式实验或真实模型回放。旧 `runtime_snapshot`、原始问答和评分不改写。暂停时的计数、分数及进程记录保存在各批次 `pause_snapshot.json`。不得把新旧版本直接合并。

## Host 的修改和限制

Host / grader 默认请求 `gpt-6.1-sol`，reasoning `high`；player / partner 为 `gpt-6-luna`，reasoning `high`。不自动换模型。Codex CLI 参数固定请求模型，事件流未独立确认实际服务模型。

公共答案仍只有 `yes / no / yes and no / irrelevant`。增强全局 host、独立复核、player 和 grader 提示；TS015、TS016、TS023、TS036 绑定独立 v7 packs，其余题保留原专属资料。题库、汤底、评分权重不变。

- TS023：预期有尸体不等于知道尸体是狱警；原计划用下一位在监狱死亡者的棺材，不是提前选择狱警的葬礼，也不限定死者必须是囚犯。具体缺氧机制、另设墓室、葬礼宾客离开时间未被确定。
- TS036：政治对手被毒杀不等于发生政府接管；国王原本已是国王。不能确认虚构的辩论、选举、政变或死亡先后。区分生前政治败亡和死后遗骨保存状况。
- TS015 / TS016：题面相同而答案不同，不跨题套用。TS016 的运动种类未指定，不能逐步把 golf 当作事实；关于运动种类的问法为 irrelevant，关于有比赛阻挡通行的宽泛问法为 yes。
- `yes and no` 不用于“发现问题里有一个真词”的情况；单一命题的未证实修饰词不自动构成两个独立分句。与解答无关的未知细节为 irrelevant。保留对真正独立混合命题／关键歧义的 mixed 标签，故四标签的信息限制仍存在。
- 独立审核使用相同模型，可能产生相关错误；同意不是事实证据。私有评分诊断不发送给 player，也不以“评分指出缺项”认定 player 已知该缺项。

`tests/fixtures/host_repair_v7.json` 是 29 个开发回归用例（26 个事实边界及 3 个错误历史恢复），标注由 AI 制作、待人工确认。有用例与 few-shot 重合，不能将通过率当作独立测量的准确率。

先离线检查，零模型调用：

```sh
python3 scripts/check_host.py --dataset data/annotations/turtle50_v4/private.json \
  --config configs/loop.codex.json --cases tests/fixtures/host_repair_v7.json \
  --repeat 1 --dry-run --out runs/api/v7_host_preflight
```

`--dataset` 是完整私有题库；`--config` 只使用 host profile；`--cases` 指定回归用例；`--repeat` 指每例重复数；`--out` 必须为新目录；`--dry-run` 只验证／快照、不调用模型。恢复真实回归需明确去掉 `--dry-run`。当前不自动执行。

## 双 agent 对照

默认策略改为 `solo,solo_reflect,independent,shared_buffer`。分别为每步 1、3、3、1 次 solver 调用：

| 比较 | 能回答的问题 | 仍未控制的差异 |
| --- | --- | --- |
| independent vs solo_reflect | 同为三调用，独立候选选择与自我评论修订的差异 | token、推理耗时、提案／修订算法不同，不能声称纯粹 agent 数量效应 |
| shared_buffer vs solo | 同为一次调用，角色轮换与延迟共享的差异 | 信息可见范围、角色提示不同 |
| independent vs solo | 额外推理调用加独立提案的综合收益 | 调用预算不相等 |

shared_buffer 两人交替，A 查身份／事件顺序／主因果，B 查假设／替代解释／缺失因果。每 `--sync-interval` 次完成提交发布双方问答；同步前仅分享对方已问问题文本（`unpublished_questions`），不分享其未同步答案或未同步 final。预约文本本身可能暴露探索方向，因此不能将此模式称为完全隔离。强制最后交卷前共享全部已有反馈。记录在 collaboration 和 shared_buffer 工件中。依旧可能出现语义重复，不承诺自动消除重复提问。

independent 仍为 A 提案、B 在不知道 A 提案的情况下独立提案、A 原样选择一个。相同模型不同角色不是两个不同训练实体；CLI 每次均为隔离调用，连续性来自传入上下文。

以下只进行离线预检，暂不启动正式实验：

```sh
python3 scripts/team_sweep.py --dataset data/annotations/turtle50_v4/private.json \
  --config configs/loop.codex.json --puzzles TS023,TS036 \
  --strategies solo,solo_reflect,independent,shared_buffer --sync-interval 4 \
  --repeat 12 --workers 2 --seed 20261024 --on-error continue \
  --dry-run --out runs/api/v7_team_preflight
```

这是 2 × 4 × 12 = 96 个计划游戏，dry-run 无模型费用。12 是 pilot 预算，不是显著性保证；四条件各位置平衡。`seed` 只控制调度，不是模型采样种子。其它 sweep 参数仍见 pipeline 指南。

## CL 四条件

仍是 in-context transfer，不更新模型权重。每个 block：玩相关 A，再玩控制源 C，随后按预定循环顺序执行四种 B：

| 条件 | B 得到的历史经验 |
| --- | --- |
| direct | 无 A / C 经验 |
| transcript | A 汤面＋公开问答＋完整标准答案 |
| answer_only | A 汤面＋完整标准答案，不给 A 问答 |
| unrelated | C 汤面＋公开问答＋完整标准答案，不给 A 的内容 |

A / C 成功或失败后都揭示各自完整答案；源运行错误不能伪装成有效学习经历。相关 A 发生运行错误／需审核时跳过该 block；C 发生运行错误／需审核时仅跳过 unrelated；未解出但正常结束不属于运行错误。每个游戏独立 100 次额度，第 100 次强制 final，错误／不完整 final 计一次；成功 final 单独记录，所以 `submissions` 可能比 `counted_questions` 多一。揭示源答案不消耗 B 额度。四种 B 使用相同 player 系统提示，仅经验输入不同。所有 B 都看不到 B 汤底、评分标准或私有分数。

```sh
python3 scripts/experiment.py continual --dataset data/annotations/turtle50_v4/private.json \
  --config configs/loop.codex.json --group G02 --pair TS015:TS016 \
  --memory transcript --source-feedback answer --controls answer_only,unrelated \
  --control-source TS041 --repeat 12 --seed 20261024 --on-error continue \
  --dry-run --out runs/api/v7_cl_preflight
```

此例 12 × (A + C + 4B) = 72 个计划游戏，零模型调用。TS041 仅为主题不同的候选控制源，不能先验保证它不产生迁移。正式研究应预先人工确认并跨 block 平衡多个 C；上下文长度没有严格匹配，不能把 transcript/unrelated 的差异完全归为语义相关性。`transfer_metadata.json` 记录输入字符数和历史长度，provider usage 记录 token；这不是 token 数匹配设计。

新增及相关参数：

| 参数 | 默认／取值 | 含义 |
| --- | --- | --- |
| `--controls` | 空；逗号分隔 `answer_only,unrelated` | 追加 B 对照，必须搭配 source-feedback answer；不重复指定 |
| `--control-source` | 无默认 | unrelated 必需，必须在题库、且不同于 A / B；不得给目标题当源答案 |
| `--memory` | transcript；可 card / both | 原有 A 问答或摘要条件；both 增加 card 条件，可能改变位置平衡所需重复数 |
| `--source-feedback` | answer；可 none | answer 在 A 结束后给完整答案；none 是明确的消融，不支持上述新增对照 |
| `--on-error` | continue；可 stop | continue 记录异常，继续其余独立条件／block；stop 退出。用户中断始终停止 |
| `--repeat` | 3，正整数 | 每个有向题对／每道 team 题的重复数；建议预先固定 pilot 预算 |
| `--seed` | experiment 为 0，sweep 为 20261023 | 调度顺序，不控制模型随机数 |
| `--dry-run` | 不设置则会真实调用 | 设置时只验证与生成计划；本轮所有命令均保留该标志 |

`control_contrasts.json` 额外报告 transcript−answer_only、transcript−unrelated；原 `contrasts.json` 为各条件−direct。源 A / C 不混入 B 的统计。错误局不填零、不当成失败，也不形成有效配对；缺失条件在报告／跳过记录中显式保留。除模型错误外，输入配置错误仍立即失败。

G02 同时存在“共享非学业双关策略”和“具体答案互斥”，negative 是研究假设不是标签真值。G07 的画像／窗户是近答案重复，适合正迁移 sanity check，不代表一般策略学习。报告应分别呈现各题对和方向，避免把同一个有向题对在多个 group 中当成独立样本。

## 容量错误与统计约束

Codex profile 增加可选 `max_retries`，默认 2，整数 0–5：仅在无任何生成内容、无工具调用且明确报告容量／rate limit 时，按 1、2、4、8、8 秒退避重试同一请求。每次尝试保留 api_calls 记录。格式错、已有部分输出、超时、低分或错误标签不重采样；不自动换模型。重试不增加游戏问数，但计入请求／成本记录。超过限制保留异常，按 on-error 策略继续。

主指标预先固定为最终 partial score，另报完整成功率、预算消耗和成功局解题问数。best score 仅可另列，不能事后替代最终分。100 问失败属于预算耗尽，不能当成已知解题时间；条件差异按同题／同重复编号计算，同时展示样本数、缺失数、token 和耗时。三调用对照只是调用次数匹配，不是 token／算力完全匹配。

正式扩样需先完成 pilot 和 Host 人工审核，再按目标效果／配对差值波动定样本量。更多重复不能消除错误 Host、题面歧义或评分偏差；不根据中途显著性随意停跑。

## 本轮验证记录

- 86 项单元／集成测试通过，包括四种 B 条件独立 100 次额度、错误 final 计数、强制最终提交、私有信息隔离、容量失败有限重试、部分输出不重采样、调度错误保留，以及共享预约不泄露未同步反馈。
- Host 回归集 29 例已通过输入／绑定离线预检；没有真实模型标签通过率。
- CL dry-run：4 个重复、24 个游戏计划；双 agent dry-run：2 题 × 4 条件 × 4 重复 = 32 个游戏计划。无真实模型调用，不是实验结果。
- 实际 Host 准确性、相似问法一致性、控制源相关性仍需人工审核及恢复后的独立模型回放。正式实验仍暂停。
