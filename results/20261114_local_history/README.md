# 全部本机历史归档（2026-11-14）

[历史轨迹浏览](index.html) · [逐历史CSV](histories.csv) · [全部目录/快照清单](all_local_inventory.json) · [跨版本正式分析](../../reports/20261114_all_versions/analysis.zh-CN.md)

保存了本机 `runs/api` 扫描到的910个result快照及对应不同API审计。非simulation且有实际提交的轨迹，按完整submission/feedback事件去重成193份问答历史。历史状态为137 completed、36 error、15 interrupted、5 running；running仅表示当时写入的状态，不能据此断言现在仍有进程。含一个明确的scripted demo，不能计入模型性能。

`histories/<hash>/`保存原问题/Host回答、评分、HTML/Markdown、题本/评分点、配置/提示词、Host上下文（源存在时）、共享讨论/自查、token费用及恢复授权等。`archive_verification.json`列原文件哈希、所有别名和核验范围。完整原始文件保持原样。

`snapshots/`保存全部result快照，含模拟、零提交失败和被后续续跑替代的副本；不同API调用记录去重保存，清单指向相应`api_audit.jsonl.gz`。所有返回、错误、usage/accounting保留。重复HTTP请求body及内嵌会话前缀不进入发布包，以exact hash留证；完整原body仍在原本机目录。发布包不是完整HTTP请求重建或一键续跑备份。没有复制环境文件或密钥。

**193份历史、910个快照均不是独立实验样本数。** 同一局恢复前后、共享相同开头的分支、旧版本和技术测试都可能重复；费用也不能跨这些副本直接求和。正式分析只选择各实验的权威终版；中断、原A、附录与版本分别标记。原评分不因后来的Host修复而追溯更改。

离线重建（无模型调用，输出必须为新目录）：

```bash
python scripts/publish_local_history.py \
  --source-root /path/to/original/GoodTurtle \
  --out results/NEW_LOCAL_HISTORY
```

`--source-root`：保留原`runs/api`的仓库根；`--out`：新建发布目录。该脚本只归档与核对，不进行语义认证，不启动实验。
