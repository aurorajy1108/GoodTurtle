# Host实际使用的资料包

- **active/TSxxx.json**：当前每题一个包；完整50题的运行绑定见 `configs/host_bindings.json`。`version`字段保留原版本，不从文件名推测最新版本。
- **archive/**：历史包和候选包，原字节保留，用于追溯和历史审核；运行不会自动遍历该目录。旧89条历史候选位于这里，不能全当已确认标签。
- **local/**：本机原有、未发布研究包，保持Git忽略；不是运行依赖。

2026-10-28 active包从当时绑定的50个包原样复制，所有旧包归档。整理没有新增、删改Host事实或示例。更新active前需要明确审核，保留来源与版本；不要将聊天全文直接贴进包。

原始人工trajectory请上传到 [host_reference/inbox](../host_reference/inbox)，流程见 [reference指南](../host_reference/README.md)。历史audit中的旧路径可用 `python3 scripts/host_reference.py locate OLD_PATH` 查找，不需要复制出另一套旧目录。
