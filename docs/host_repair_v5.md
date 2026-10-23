# Host v5.1 与证据覆盖评分

本次修复针对 2026-10-23 审核发现的错误：核心事实被否认、错误预设被延续、时间顺序和人物知识混淆、评分遗漏条件仍给满分、矛盾标志不一致。数据和示例仍为 **AI 标注，待人工确认**。不把回归测试通过率称为全题库准确率。

## 运行方式与版本

新实验使用 `data/annotations/turtle50_v3/private.json`。模型配置方式、CLI 参数和 100 次提交上限不变，命令见 [运行指南](coworker_quickstart.md)。`configs/loop.codex.json` 请求 Luna high；没有自动切换 Astra。

所有 50 题均绑定 `LOOP_TSxxx_repair_v5.json`，共 1,148 条示例。新增 35 题使用来源事实、否定问法与无关细节的基础示例，这只能解决示例缺失，不能替代真实历史的可靠性验证。TS023/032/033/036/009 另有时间线、人物知识状态及标签边界。TS009 明确是小明放下鸡蛋，正常运作的雨刮器打破鸡蛋。

`verification_policy=independent_then_adjudicate_v1`：

1. Host 按故事和完整公开历史回答。
2. 同一 host 模型在新的调用中独立核验，第二次看不到第一次标签。
3. 两者不同时，第三次对照汤底裁决，可以选择候选以外的标签。

只向 player 返回最终一个 `yes / no / yes and no / irrelevant`，内部不泄露分析或缺失答案。两次独立调用仍共享同一模型的偏差，因此并非可靠性保证。每个普通提问需要 **2 次 host 调用，分歧时 3 次**；问题数只增加 1。调用、token 与耗时照常统计，额外的 `host_review` 事件记录候选标签和裁决结果。没有新增 CLI 开关；策略属于题目包并随 context hash 冻结，所有比较条件应使用同一版本。

## Grader 规则

v3 数据声明 `grading_protocol=coverage-v2`。除了原来的 checkpoint 和完成标志，grader 还必须提供：

- `fact_coverage`：每个评分点的必需事实，按 `covered / partial / missing / contradicted` 标注并附提交证据。
- `requirement_coverage`：每条完整叙事要求的覆盖情况。
- `contradictions`：矛盾原文、冲突的故事事实及受影响的评分点。

控制器校验 ID 完整且唯一、证据来自本次提交，并执行分数上限：漏项/部分覆盖不超过半分；矛盾评分点为零；全缺失为零；完整通关必须覆盖所有要求且无矛盾。它不会自动把模型给的低分提高，也无法代替语义正确性检查。原始评分和 `controller_corrections` 都保留。

证据允许按原顺序摘取多个原文片段、用省略号连接；大小写和标点可规范化，不允许换词或删掉句内否定。如果模型改述证据导致校验失败，最多增加一次**仅修复引用格式**的调用：只提供玩家提交、原文句子 ID 与待修引文；模型只能选择句子 ID，由代码提取原文，只允许修改证据文本，不能改变 credit、coverage status、矛盾标志或完成判断。仍不能匹配原文则报告协议错误，不通过重新抽样挑选有利评分。该调用计入 grader 成本，不增加玩家提问数。

TS023 明确拆出囚犯自己藏入棺材、狱警身份、贿赂、承诺挖出等要求。“狱警把囚犯放在自己的尸体旁”使 C1/C2 为零并阻止通关；C3/C4 独立评估。上下文中的 guard / prison officer / 帮助囚犯逃脱的 officer 接受为同一救援者角色的改述，避免无谓地因称呼扣分。只遗漏贿赂或挖出安排可以是半分，不能仍得 C2 满分。权重沿用 v2，评分边界已有修订，不能直接混合新旧成绩。

## 可复现检查

```sh
python3 -m unittest discover -s tests -v

python3 scripts/check_host.py --dataset data/annotations/turtle50_v3/private.json \
  --config configs/loop.codex.json --cases tests/fixtures/host_repair_v5.json \
  --repeat 2 --out runs/api/my_host_v5_check

python3 scripts/check_grader.py --dataset data/annotations/turtle50_v3/private.json \
  --config configs/loop.codex.json --cases tests/fixtures/grader_repair_v5.json \
  --repeat 2 --out runs/api/my_grader_v5_check
```

两个检查入口均支持：

| 参数 | 含义 |
|---|---|
| `--dataset PATH` | 必填。私有题库 JSON；grader 检查要求 coverage-v2 数据。 |
| `--config PATH` | 必填。原实验配置；host 检查使用 host，grader 检查使用 grader，`grader: "host"` 时复用 host 配置。 |
| `--cases PATH` | 必填。测试列表；host 格式为 id/puzzle_id/question/expected/可选 history；grader 为 id/puzzle_id/submission/expected。grader 的 expected 支持 complete、partial_score、material_contradiction。 |
| `--out PATH` | 必填且必须是新目录，保存输入、预期、配置、prompt、模型调用和结果。 |
| `--repeat N` | 默认 1，必须为正整数；独立重复次数，不是失败重试次数。 |
| `--dry-run` | 仅验证并保存输入，不调用模型。 |
| `-h / --help` | 查看帮助。 |

预期标签和评分不会传给模型。33 个 host 案例包含真实历史修复重放、15 个新措辞诊断、3 个合成错误历史和6个此前无示例题的抽查；11 个 grader 案例覆盖错误旧交卷、完整答案及仅漏贿赂。现在这些文件已公开为回归集，未来不能再声称是未见过的测试集。

## 记录与旧实验

`host_context.json` 的 context hash 现在包含评分规则的摘要；`result.json` 的 `evaluation_versions` 单独记录题面/汤底、rubric、prompt、控制器代码及 host context 哈希。代码/题库/绑定仍由 sweep 冻结。旧 runtime_snapshot 会继续使用旧实现；修改仓库不会替换其正在运行的 host。

旧 trajectory 和旧分数不覆盖。审核结果单独记录在本地 `runs/api/20261023_host_reliability/`，修复各轮（包括失败轮）位于 `runs/api/20261023_host_repair/`。受旧 host 错答影响的实验不能直接用于证明合作优劣；重新实验应使用新输出目录和完整版本记录。
