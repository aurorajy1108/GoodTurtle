# 模型实验输出

这里保存自动实验的trajectory、grader输出、合作记录和运行快照，**不用于上传人工Host参考问答**。人工资料入口是 `data/host_reference/inbox/`。

- `runs/api/<batch>/`：当前loop、CL和双agent输出，默认Git忽略；需要对同事共享时按批次明确发布。
- `runs/2026-10-08_*`、`runs/2026-10-09_*`：早期实验档案，保留原目录和冻结内容。
- `runtime_snapshot/`：当时的代码/模型/数据/绑定快照；不因本次仓库整理而改写。

每批阅读 `index.html`、`trajectories.html` 或每局的 `trajectory.html`；先看result/status是否completed、interrupted、error或dry_run。不能从旧running字段直接推断当前进程仍在运行。

实验继续暂停。本次整理没有重新启动模型。重点待审批次和轮次见 [审核清单](../docs/todo_human_review_20261027.md)。
