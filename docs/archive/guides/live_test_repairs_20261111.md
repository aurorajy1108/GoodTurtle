# 11月11日真实 API 小量测试：问题与修复

使用本地 `.env.local` 的 DeepSeek 凭据启动实测，文件权限600并被Git忽略，凭据不进入日志或仓库。本轮不是150局正式实验；目标是检查4局CL、2局MAS及其故障恢复。完整流程仍需等实际输出验收，不把离线通过或少量诊断等同于Host永不出错。

## 已发现并处理

| 问题 | 实测证据 | 修复/边界 |
| --- | --- | --- |
| TS015将“横渡河流”与“沿路线行进”混淆 | 原pilot第34问的复合命题被答yes | 保留原13条参考及原汤底，增加5条AI复核的方向边界；该问按现有mixed规则为yes and no。原pilot42问保留、标记非干净成绩，不静默改标签 |
| MAS把协议占位词当成真实首行 | 多次输出ACTION NEXT=B，而非QUESTION/DISCUSS等具体动作 | 新响应契约逐个列出完整可复制首行；独立新会话的四种动作均一次返回合法格式 |
| 已生成MAS交卷因外层占位词而无法提交 | 已生成ACTION NEXT=B、FINAL及完整正文，重试后仍停止 | 只在内层类型和外层NEXT均明确且一致时逐字规范化；不从无类型的自由文字推断动作 |
| 一个任务失败联动中断另一个任务，造成恢复缺口 | MAS停止时CL第39问已生成但Host未答 | 增加明确取消场景的原请求恢复。恢复保留39问，补发完全相同的Host请求；未收到usage的旧请求费用仍未知，不能记0 |
| 运行中汇总页计数落后 | 批次表只在整局结束更新，而逐局result持续正确 | campaign读取逐轮原子更新的result.json；新运行已验证实时问题数及token随轮更新 |
| DeepSeek价格未匹配 | token/cache usage正常，但金额未知 | 补充两个实际返回的模型别名，采用官方高峰参考价并明确低峰半价；原冻结记录不改写，可另建复算sidecar |

新TS015条目明确标为AI复核、非人工确认，见 [复核记录](../../../data/host_reference/reviews/ts015_20261111_crossing_guard.json)。上下文变更纳入50题版本迁移检查，原始题库与rubric不变。

## 核验与当前数据范围

- 原20条Host开发诊断通过。TS015修复后，另外6条边界诊断全部通过；旧诊断只有2条输入受影响，补测2条也通过，另18条按序列化输入完全一致复用。
- 新首行契约在两个独立持续会话中分别实测QUESTION、DISCUSS、PASS、FINAL，4次全部有效，无规范化或纠正调用。此为合成协议canary，不是题目成绩或人工参考轨迹。
- CL恢复实际核对：原API记录完整保留，恢复后的首个Host请求body与中断前完全一致。
- MAS恢复实际核对：保留两个agent的原始消息链及26次外部提交；第一个新模型调用是Grader，不是Player。错误/不完整交卷继续计1次并允许后续提问。
- 新旧协议历史可能造成不同的格式行为；续接旧历史的结果与新会话诊断分别记录，不声称修复前后实验完全相同。
- 245项回归测试通过。恢复、预算与格式通过不代表Player一定能猜对，也不代表所有Host语义已完成人工审核。

## 有限恢复入口

仅对已停止、经过哈希与完整消息链校验的DeepSeek运行使用。计划模式不调用模型，实际执行需使用不同的新out目录并改为run。

```bash
source .env.local
python3 scripts/resume_study.py --from-study PATH_TO_STOPPED_CL_STUDY \
  --out NEW_CL_RECOVERY_DIR --recover-host-transport --mode plan

python3 scripts/resume_study.py --from-study PATH_TO_STOPPED_MAS_STUDY \
  --out NEW_MAS_RECOVERY_DIR --recover-dialogue-action --mode plan
```

`--recover-host-transport`现在也接受明确取消时、最后一条Host调用无任何已观察答复的情况。只重发同一请求；可能重复远端计费会被记录。Player的问题不重新生成，额度不重置。

`--recover-dialogue-action`仅支持完整保存在末尾的明确占位外壳动作：内层动作类型、正文、外层下一位speaker均存在且无冲突；公开轨迹必须与全部已提交问答一致，两位agent原始会话必须完整。无类型自由文字、冲突handoff、已执行动作、缺失历史、其他任意MAS中断仍拒绝恢复，不重新抽样。它不是通用free_dialogue重启。

## 费用复算

[官方价格表](https://api-docs.deepseek.com/quick_start/pricing/)核对日期为2026-11-11：

| 模型 | 高峰未缓存输入/百万token | 高峰缓存输入 | 高峰输出 |
| --- | ---: | ---: | ---: |
| deepseek-flash | $0.30 | $0.006 | $1.20 |
| deepseek-v4-pro | $1.32 | $0.044 | $3.96 |

低峰为一半；官方还定义UTC时段及中国法定节假日条件。运行时金额是明确标注的高峰参考估计，不猜节假日，不冒充账单。reasoning token已包含在output中，不重复计费。

```bash
python3 scripts/reprice_campaign.py --campaign CAMPAIGN_ROOT --out NEW_PRICE_REVIEW_DIR
```

逐调用usage、原价格快照和冻结实验不改写；输出新的pricing_snapshot、calls及summary。给出已知金额的高峰/低峰范围；若存在缺失usage的中断调用，全量金额仍为null，保留已知小计。多份恢复归档已包含前序调用，不能把旧归档与最新归档再相加。

本机实测轨迹入口为 `runs/api/20261111_live_testing/index.html`，20秒刷新。恢复后的CL/MAS分别位于 `20261111_live_smoke_v2_cl_resume01` 和 `20261111_live_smoke_v2_mas_resume01`；这些运行产物仍在本地，不因代码补丁自动发布。


## 第二轮实测修复

- TS038：明确区分实际书写者（叙述者）、冒充作者（妻子）、伪造信中的离家理由与未确定的实际收件人。保留旧参考，新增7条AI审核边界；不是人工标注或独立准确率评估。真实API诊断7/7通过。
- 旧MAS轨迹保留并标记诊断用途；修复语义后重新进行两局小量MAS测试，避免把已经观察到的错误Host反馈带入干净对照。
- 无类型Player自由文字不会被猜测为问题或交卷。在原持续会话中最多追加两次明确格式纠正；保留原回复、费用及消息链，不消耗未实际执行的问题额度。已有明确类型的动作不通过此机制重新生成。
- 已停止的无类型输出恢复入口：`python3.11 scripts/resume_study.py --from-study OLD --out NEW --correct-untyped-player --mode plan`；审核计划后改为`run`。必须通过历史、预算和完整调用链校验；不是任意失败的自动重跑。
- 248项回归测试通过，包括同槽纠正、纠正次数限制、持续会话恢复与已有CL格式兼容。技术测试通过不代表所有真实轨迹或Host语义均已验证。
- 当前干净MAS入口：`runs/api/20261111_live_smoke_v3_mas/tasks/mas-ts038-a`；CL继续原恢复归档，避免重复调用。
