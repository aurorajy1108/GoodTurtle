[English](README.md) | 中文

# 脚本入口

| 用途 | 入口 |
| --- | --- |
| 上传人工参考、检查inbox、找旧路径 | `host_reference.py init / validate / locate` |
| 已保存ChatGPT分享HTML→可见消息JSON | `import_chatgpt_share.py` |
| 单局/多题对局 | `play.py` |
| CL / 双agent实验 | `experiment.py` |
| 多题多次双agent批处理、冻结快照 | `team_sweep.py` |
| Host / grader回放 | `check_host.py` / `check_grader.py` |
| 生成全部trajectory HTML | `render_trajectories.py` |
| 分析批次完整性 | `audit_sweep.py` |
| 导出Excel审核表 | `export_host_review.py`（可选依赖openpyxl；生成到新文件，勿覆盖人工填写稿） |
| 打包/校验运行所需私有题库与Host包 | `experiment_bundle.py` |
| 旧三标签原型与筛选 | `prepare.py`、`audit_screening.py`、`summarize_screening.py`、`summarize_pilot.py` |

新同事先读 [运行指南](../docs/coworker_quickstart.md)。旧原型不作为当前四标签实验入口。每个脚本的 `--help` 列参数；完整参数说明见docs。
