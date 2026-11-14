# 206局更新与新增39局

[分析正文](../../../docs/analysis/latest_results_20261114.md)。无API调用、无在线重评分、无聚合HTML。

|文件|内容|
|---|---|
|[inventory.csv](inventory.csv) / [JSON](inventory.json)|206局原在线分、完成状态、前题/目标、协议、prompt/controller/context哈希与现有费用；未知费用留空|
|[by_condition.csv](by_condition.csv)|按批次、题目、条件汇总；仅primary目标局，技术错误不填0|
|[by_source_condition.csv](by_source_condition.csv)|进一步按A来源分组；公共baseline不复制到各来源|
|[new_first10_verbatim.csv](new_first10_verbatim.csv)|新增39局的390条前十次提交，保留原问和反馈|
|[new_final_submissions.json](new_final_submissions.json)|新增39局的原末卷与原评分；包含6局A，不冒充39个B|
|[new_target_qualitative_notes.csv](new_target_qualitative_notes.csv)|新增33个目标局逐局助手复核：恢复的解释、主要缺项与轨迹路径；不替代原分|
|[legacy_score_completion_mismatches.json](legacy_score_completion_mismatches.json)|旧协议13次100%但未完整的评分事件，涉及5局|
|[validation.json](validation.json)|样本计数、去重、审阅范围与零模型调用声明|
|[source_coverage.json](source_coverage.json)|核对过的9个远端分支及本次新增来源；不能确认组友未上传的本机结果|
|[publication_checks.json](publication_checks.json)|本次发布的356项测试、冻结文件哈希及链接检查摘要|

本次助手读取新增33个B末卷及前十问、6个A末卷和选定关键问答；未完成所有新增提交的逐问语义复核，不是人工gold。离线复核分继续保存在对应源批次，不替换本表在线分。

重建：`python scripts/analyze_latest_results.py`。之前`20261114_all_versions/`和`20261114_transfer_process/`仍是原样本范围的固定快照。
