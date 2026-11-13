# Set 2 v17：Zhen Qi 的五次重复实验归档

[English](README.md) · [逐局轨迹入口](index.html) · [逐局CSV](runs.csv) · [35局图](figures/your_35.pdf) · [双方分批对照图](figures/comparison_53.pdf)

本目录包含 **35局TS034目标题B，以及3份固定来源A的完整轨迹**。七个条件各五局：共享direct基线，以及TS033、TS035、TS012的answer-only/session。续跑副本不增加样本数，原始模型分数不改写；35局均完成预算，但均未完整解出。

| 前题来源 | direct共享基线 | 只看官方答案 | 完整前题会话＋答案 |
|---|---:|---:|---:|
| TS033，原negative假设 | 55.5% | 66.5% | 27.0% |
| TS035，原positive假设 | 55.5% | 23.0% | 41.0% |
| TS012，原irrelevant假设 | 55.5% | 33.0% | 56.0% |

这些是最终交卷原始部分分均值，不是成功率。每类只固定一份A，不能推广为一般的正负迁移规律。direct总共五局，不按三行重复计数。

## 条件与归档边界

目标题冻结Host v17、评分v6，权重45/30/20/2/3，使用coverage-v2配合rubric_aligned_v1；不是main后来更新的unified-v3默认设置。Player为DeepSeek Flash、thinking关闭；Host/Grader为Pro、高thinking。逐局保存实际配置、提示、题面汤底、评分项与Host上下文，不修改活动系统规则。

session继承完整前题Player会话，并揭晓官方汤底；B额度重新计100次，Host/Grader独立。TS012揭晓的完整汤底含冻结Host补充设定，比dataset.answer更长，已核对；answer-only使用相同官方揭晓，不含历史问答。来源目录、transfer_boundary.json和前缀指纹明确记录这些关系。

每局100个预算槽不等于100条有效问答：TS012 answer-only R3第44槽、TS033 answer-only R3第67/76/87槽是四个无效动作，没有执行，也没有Host反馈。原文及消耗额度的明确干预通知都保留；这两局不从主统计删除，可单列敏感性分析。

网络/格式恢复保留原回复。direct R5第95槽仅识别已保存中文“最终”动作标记，正文包括金额错误原样保留。控制器实现存在恢复版本差异，因此不能声称所有局代码逐字节相同。历史格式辅助调用及其模型、错误、用量、费用仍保留，不描述为所有接口只有DeepSeek。

## 原始记录与复核分开

每局含JSONL/Markdown/HTML完整轨迹、原始result、配置提示、Host上下文、题目评分、费用和核验文件。原API返回、错误及计费记录按顺序完整保留在api_audit.jsonl.gz；重复完整请求正文留在本地，发布哈希，精简审计不能恢复完整HTTP请求。本包不是可直接续跑的运行时。

[离线复核报告](analysis.zh-CN.md)及review目录保存助手建议：新增14局共1365条Host问答、35次交卷，重点裁决32条Host和13条评分，另附之前context争议裁决。不是所有Host标签逐条独立认证，也不是用户已确认的人工金标准。建议不覆盖原分、原反馈，也不通过删除低分或争议局美化结果。

双方比较图引用main固定提交25f4cc4的18局组友结果；旧v5与本轮v6分开展示，不混算均值。组友原始轨迹不重复复制到本包。图中direct为便于对比在三个来源面板重复显示，统计仍只计一次。53局比较记录含组友固定GitHub链接。

费用未知保留unknown；已知子总额是API等价估计，不是真实账单。结构核验只证明记录、计数、分数运算及导出字节一致，不证明全部语义回答正确。本次无新API调用。

从仓库根目录离线核验：

```bash
python3 scripts/publish_set2_v17_archive.py --out results/20261113_set2_v17_zhen_qi --verify-only
```

导出与图像复现方式见英文README。你的35局原图逐字节保留；当前工作区的活动代码和其他实验均未混入此次发布。
