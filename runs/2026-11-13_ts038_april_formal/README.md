# TS038 正式实验：April / b 槽

正式重复3、4已完成，共4局；不包含smoke或技术中断尝试。

| 正式重复 | 条件 | 外部提交次数 | 最终评分 | 完整解出 |
| --- | --- | ---: | ---: | --- |
| 3 | free_dialogue | 57 | 100% | 是 |
| 3 | solo | 100 | 60% | 否 |
| 4 | free_dialogue | 100 | 50% | 否 |
| 4 | solo | 87 | 100% | 是 |

## 数据与检查

全部4局status=completed；原始状态、评分与轨迹保持不变。每局最多100次外部提交，最后一次强制交卷。双agent采用互补分工、自适应交接、A先发言、每次外部提交前最多4条内部消息。

[结果JSON](experiment_runs.json) · [结果CSV](experiment_runs.csv) · [统计](performance.json) · [费用与token](cost_summary.json) · [轨迹入口](index.html) · [冻结输入](tasks/mas-ts038-b/runtime_snapshot/)

API日志按本仓库惯例保存为api_calls.jsonl.gz，无损解压后字节与原文件一致。archive_manifest.json记录归档文件哈希和日志压缩前哈希；两批冻结输入均已逐文件核验。manifest、launcher和API记录中的绝对路径是原运行环境的审计信息，不代表当前clone的位置；浏览结果使用上面的相对链接。读取需原JSONL的工具前，可以在副本中用gzip解压，不必改动归档。

## 技术中断与版本

[technical_failure](technical_failure/)保留首次正式启动的完整记录和用量：完成7次外部提交后，合法JSON正文中的test:被纯文本动作恢复逻辑误判。本批修复为有效JSON优先解析，并使用新的冻结输入独立重开；没有从MAS中途恢复。技术中断未计作0分，也不计作已完成的正式重复。费用记录分别保留在两批cost_summary.json中。

动作首行也已从ACTION占位符说明改成具体可执行首行。模型、题库和提示词设置见冻结输入及formal_provenance.json；DeepSeek使用可信CA和直连，证书校验保持开启。

新增回归与相关测试通过；完整离线测试263/264通过，唯一未通过是本次未修改的TS034历史上下文哈希清单检查，详见[startup_verification.json](startup_verification.json)和[offline_tests.log](offline_tests.log)。

当前只有每种策略2次重复，不据此作策略优劣推断。精确模型价格未配置，费用与真实账单保持未知；token用量包含重复历史和缓存。
