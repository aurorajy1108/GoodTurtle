# MAS四次重复：已完成结果快照

截止香港时间 2026-11-13T14:26:25+08:00。本计划16局，已完成10局；本次新增发布2局，其余旧结果按原文件链接引用，不重复归档。

| 条件 | 已完成/计划 | 完整成功 | 平均partial score | 已完成重复号 |
| --- | ---: | ---: | ---: | --- |
| solo | 3/4 | 0/3 | 8.33% | 1,2,4 |
| solo_review | 2/4 | 2/2 | 100.00% | 1,2 |
| mas | 2/4 | 1/2 | 75.00% | 1,2 |
| mas_review | 3/4 | 0/3 | 41.67% | 1,2,3 |

各条件重复次数尚不齐，均值仅描述已完成样本，不是四次重复的最终结论。正在运行或网络中断的6局列于[excluded.json](excluded.json)，不当作失败或0分。

[index.html](index.html)可浏览所有已完成MAS轨迹，[runs.csv](runs.csv)给出逐局结果。新发布局含完整公开问答、HTML、自查笔记、评分点、冻结输入、token/费用及精简API审计；每局`verification.json`记录结构核验与文件哈希。

CL Set1的39局和此前MAS结果已在[先前发布](../20261113_verified_final/README.md)中。本目录只更新MAS，不能把新旧目录重复加总。`included_games_cost_summary.json`恰好计算上述完成局一次，包含其失败尝试；未完成局和Host门禁不在该费用范围，缺失usage保持未知。

所有Host/Grader语义仍待人工复核，[已发现的指代与评分边界疑点](../20261113_verified_final/analysis.zh-CN.md)保留；本次不修改任何旧标签或成绩。完整HTTP请求历史留在本地，本发布的精简API审计不能重建被省略的重复request body。
