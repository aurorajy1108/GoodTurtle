# MAS TS038：8/8完成更新

本次仅续跑原mas_review第1局，保留79次提交及原不完整review；未重新生成笔记，未重跑其他7局。最终第84次提交，partial score为0%，未解出；剩余输出2,881 token，按原预算预留规则强制最终交卷，非技术报错。

| 条件 | 成功 | 平均partial score | 各次提交数 |
| --- | ---: | ---: | --- |
| solo | 0/2 | 12.5% | 100, 100 |
| solo_review | 2/2 | 100.0% | 76, 100 |
| mas | 1/2 | 75.0% | 100, 51 |
| mas_review | 0/2 | 25.0% | 82, 84 |

[runs.csv](runs.csv)及[runs.json](runs.json)含逐局trajectory链接；新完成局的[trajectory](TS038_r01_mas_review/trajectory.html)、[共享聊天](TS038_r01_mas_review/shared_dialogue.html)、[私有自查](TS038_r01_mas_review/self_review.html)可直接打开。原7局沿用上一发布的文件，不重复归档。

此次改变的是不完整私有笔记的恢复处理，过程、哈希和原调用费用均保留；不把它写成一次从未中断的原版本实验。模型、prompt文件、Host/Grader历史回答和计算上限不变。此前[语义复核疑点](../20261113_verified_final/analysis.zh-CN.md)仍未解决，因此不能据此作架构普遍优越性的结论。

`cost_summary.json`覆盖本轮8局全部角色及失败调用，未知费用不按零处理，不能再叠加旧恢复副本。逐局结构核验不等于人工语义认证。
