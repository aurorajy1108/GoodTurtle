# 统一评分与结束条件（2026-11-11）

新实验默认使用 `data/annotations/turtle50_v5/private.json` 和
`coverage-v3-unified`：**有效评分 100% ⇔ complete=true ⇔ 本局立即结束**。
原先“评分点满分、完整叙事仍不完整”的两个独立标准已合并。

## 标注与程序

50题、161个评分点的权重、汤面、汤底及原 required_facts 不变。
所有原 completion_requirements 逐条映射进对应评分点，映射记录见
[completion_mapping.json](../data/annotations/turtle50_v5/completion_mapping.json)。
说明“哪些未知细节不必回答”的规则进入 grading_notes，不要求玩家补写免责声明。

Grader 判断事实覆盖与引用证据，程序据此计算每个点的 0/0.5/1 分值，
保留原半分前置条件，再用 Decimal 精确求加权总分。
`full_solution` 字段继续兼容现有接口，但其布尔值和 completion_note
由程序统一生成，不再作为独立否决条件。原模型输出及纠正记录保留在审计文件中。

关键矛盾导致对应点为零；无法定位的矛盾或真正的标注冲突令评分无效
（null），并进入 needs_review，暂停本局，不继续让玩家猜缺了什么。
普通错误/不完整交卷仍计一次问题，仅反馈四种允许标签之一；100次额度不变。

## 运行

现有命令保持不变，默认数据已更新为 v5；Host/Player/Grader 模型配置不变。

```bash
source .env.local
bash scripts/run_team_smoke.sh jiayang cl-set1-a,mas-ts038-a runs/api/smoke_unified_v3
```

只验证 Grader 的四个定向案例（无 Player rollout）：

```bash
source .env.local
python3.11 scripts/check_grader.py \
  --dataset data/annotations/turtle50_v5/private.json \
  --config configs/loop.deepseek.json \
  --cases configs/grader_regression_unified_v3.json \
  --repeat 1 --out runs/api/unified_v3_grader_check
```

参数：`--dataset` 新版私有评分数据；`--config` 模型配置（仅调用其中grader）；
`--cases` 提交和预期结果文件；`--repeat` 每例独立重复次数，默认1；
`--out` 必须为不存在的新目录；可加 `--dry-run` 只校验/保存输入、不调用API。
每次调用及修复调用都记录usage、token_costs.csv和估计费用，实际账单金额不冒充已知。

## 验证与旧结果

回归检查覆盖：完整答案即使附带旧 false 标志也立即结束；遗漏必答内容
不能满分；关键矛盾扣对应点；标注冲突暂停；所有50题完整覆盖均满分、
逐个必答事实缺失均非满分；CLI schema与旧 coverage-v2 行为兼容。
四个API案例检验TS013/TS038的完整叙事、遗漏、矛盾，属于定向回归，不是总体准确率。

旧 v4 数据与已有冻结实验不改写、不与新结果混合。需要历史复现可显式传
`--dataset data/annotations/turtle50_v4/private.json`，此时仍是旧协议，
不会声称其满分和完成一致。旧交卷若要按v5复审，应另建审计结果。


本机验证结果（2026-11-11）：258项回归测试通过；真实DeepSeek Grader四例4/4通过。
TS013完整叙事=1.0且结束，遗漏叙事=0.9且未完成；TS038完整叙事=1.0且结束，
关键矛盾=0.5且未完成。定向调用的高峰参考估计费用约$0.0743，非实际账单。
原始结果位于本机 `runs/api/20261111_unified_v3_grader_check/`，不自动公开原始API日志。
