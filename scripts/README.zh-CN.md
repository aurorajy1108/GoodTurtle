[English](README.md) | 中文

# 脚本入口

团队正式分工及新一键脚本见 [campaign指南](../docs/running/team_campaign_20261111.md)：`run_team_smoke.sh`小量测试，`run_team_batch.sh`每人两次重复/限并发，`team_campaign.py`列计划、dry-run和去重汇总。

| 用途 | 入口 |
| --- | --- |
| Player格式自动修复、有限续跑监督 | `auto_continue.py`；当前Set1用`start_set1_auto_continue.sh`，见[说明](../docs/running/automatic_continuation.md) |
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
| 已发布结果索引、校验、汇总与旧路径查找 | `results_catalog.py list / check / summarize / locate` |
| 重建固定分析表，不生成仪表盘 | `build_all_versions_summary.py`、`analyze_transfer_process.py` |
| 旧三标签原型 | `prepare.py`、`summarize_pilot.py`；旧筛选脚本见[归档分支](https://github.com/aurorajy1108/GoodTurtle/tree/archive/full-repository-20261114/scripts) |

新同事先读 [运行指南](../docs/running/coworker_quickstart.md)。旧原型不作为当前四标签实验入口。每个脚本的 `--help` 列参数；完整参数说明见docs。

## Set 1 修复后的一键试跑

在已export `DEEPSEEK_API_KEY`的终端执行`bash scripts/start_set1_verified.sh`。先用同一冻结快照做20题Host诊断，通过后才跑12局CL（A=15/14/28，B=13，direct/session/answer_only，每条件一次）；不跑MAS。可用唯一位置参数指定新输出目录。新版本参数、CL/MAS命令和返回协议见[新分支运行指南](../docs/running/run_session_prefix_v1.md)，历史诊断背景见[重跑说明](../docs/archive/guides/set1_v11_rerun.md)。
