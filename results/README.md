# 实验结果入口

最新汇总：[中文综合分析](../reports/20261114_all_versions/analysis.zh-CN.md) · [正式轨迹HTML索引](../reports/20261114_all_versions/index.html) · [分条件CSV](../reports/20261114_all_versions/condition_summary.csv) · [逐局来源CSV](../reports/20261114_all_versions/formal_inventory.csv)。

|目录|内容|如何使用|
|---|---|---|
|[20261114_local_history](20261114_local_history/README.md)|910个本机结果快照、193份去重问答历史，含旧实验、失败和续跑检查点|完整归档；不能把这些历史全部当独立正式样本|
|[Set2 v17](20261113_set2_v17_zhen_qi/README.md)|35个B＋3个A，保留完整冻结旁证|公共baseline仅5次，不能乘以3个A|
|[T22/T42](20261114_t22_t42_session_free_dialogue/README.md)|31个主比较局＋6个附录局|T22五重复，T42只有一个baseline；附录不并入主比较|
|[Set1与早期MAS正式发布](20261113_verified_final/README.md)|39个CL，MAS早期完成项|历史发布；最终状态以最新inventory为准|
|[逐问AI审阅](../reports/20261114_joint_trajectory_review/summary.md)|截至第一轮审阅时的131份档案、12631条提问/交卷|不是人工gold；其后新增T22/T42的审阅覆盖在最新分析单列|

组友的Set2历史轮次、April TS038及extra2仍保留在`runs/2026-11-*`。所有旧评分保持，coverage-v2不被事后换算成新成功规则；技术中断不当作0分失败。部分相同轨迹在历史发布与本机完整归档同时出现，最新逐局inventory给出逻辑观察及重复标识。

拉取后即可离线看结果，不需要API key或重新运行实验：

```bash
git fetch origin
git switch main
git pull --ff-only
open reports/20261114_all_versions/index.html
```

`open`是macOS命令；其他系统直接在浏览器打开该HTML文件。需重新生成汇总时，在仓库根目录运行：

```bash
python scripts/build_all_versions_summary.py
```

这个脚本只读取已发布归档，无模型调用；重建JSON、CSV和HTML索引，保留中文分析文档及原始评分。原本机API目录已不再需要。重新归档原本机历史的两个参数见[本机历史说明](20261114_local_history/README.md)。
