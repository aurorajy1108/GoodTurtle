# 当前提示词

`loop_host_v1.txt`、`loop_host_review_v1.txt`、`loop_player_v1.txt`、`loop_grader_v1.txt` 是当前四标签loop加载的提示。实际版本还需结合冻结运行快照，不能只看文件名v1。

`archive/`保存旧三标签提示，不用于当前运行；`host_system_v0.5.1.txt`仅供旧prepare.py兼容。人工问答不上传这里，而是到 `data/host_reference/inbox/`。
