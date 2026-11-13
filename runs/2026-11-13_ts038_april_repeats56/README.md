# TS038 正式扩展实验：April 重复5、6

四局均正常结束，每局最多100次外部提交；模型、提示词、题库与控制器复用正式重复3、4的冻结快照。

| 正式重复 | 条件 | 提交次数 | 最终评分 | 完整解出 |
| --- | --- | ---: | ---: | --- |
| 5 | free_dialogue | 100 | 0% | 否 |
| 5 | solo | 100 | 90% | 否 |
| 6 | free_dialogue | 36 | 100% | 是 |
| 6 | solo | 45 | 100% | 是 |

[逐局结果](formal_results.json) · [轨迹与统计](team/index.html) · [费用与token](team/cost_summary.json) · [冻结输入](runtime_snapshot/)

本地编号r01/r02分别映射全局重复5/6，见assignment.json；该扩展批次独立于预设重复1–4，合并分析时请使用formal_results.json中的global_repeat。API日志按仓库惯例无损gzip压缩，原始运行目录未修改。

冻结文件哈希、压缩前日志哈希和归档文件哈希见archive_manifest.json；精确模型价格未配置时费用保持未知。两种策略的少量重复仅描述本次记录，不据此推断总体优劣。
