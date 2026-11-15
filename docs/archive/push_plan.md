# 已授权的推送范围

2026-10-09 用户确认推送先前清单，并要求 data 只包含 eraser 和 pillow。目标：`origin`，`https://github.com/aurorajy1108/GoodTurtle.git`，分支 main。推送前已检查远程无现有分支；使用普通首次提交与推送。

## data 发布白名单

- `data/release_scope.json`：仅允许 USER_ERASER_001 与 USER_PILLOW_001，禁用其他故事的共享示例。
- `data/host_packs/USER_ERASER_001.json`、`USER_PILLOW_001.json`：当前两题的答案、事实与专属示例。
- `data/host_dev/eraser_v02.json`、`eraser_v03.json`、`USER_PILLOW_001_draft.json`：两题历史开发资料。
- `data/public/puzzles.jsonl`：仅两题 ID 与公开汤面。

不发布 `data/private/candidates.json`、`data/host_examples.json`、`data/archive/`、`data/research/`、JP001–JP006 host 包或其他题目文件。它们仍保留在本地并被 Git 忽略。原混合公开题库也已在被忽略的 `data/local_only/` 中备份。

## 其他批准内容

先前清单中的 prompts、scripts、docs、Readme.md、.gitignore，以及所有橡皮/枕头/非英语筛选 run 均保留。既定 run 目录内后续生成的配套结果、检查点和输入清单一并归档，以保持轨迹与记录完整。新增加的无关资料文档或目录外文件不自动纳入。

**data 的限制不扩展到历史文档和 runs：这些目录仍可能包含其他题目的内容和冻结共享示例。** 本次不对历史轨迹、答案、审核标签或 prompt 快照进行删改。复现旧实验必须使用旧 run 的冻结上下文；当前发布配置的 host 只加载题目专属示例，不能冒充原 52 条共享示例配置。

运行所需的构建、校验、汇总脚本与说明均保留。模型调用仍依赖 Codex 子 agent，尚无独立 API 跑局程序。未发布研究题库时，历史筛选汇总脚本可从 run 的冻结输入读取元数据。

## 其他排除项

不纳入 `.git/` 内部文件、系统/执行缓存、虚拟环境、环境变量文件、密钥/令牌/登录凭据、仓库外临时脚本、IDE/Codex 私人配置和附件原件。`docs/push_manifest.json` 记录实际选中文件的路径、大小与 SHA256（自身排除递归哈希）。

## 实验继续保持暂停

提问计入错误交卷：Run01 165+4=169；Run02 159+7=166；Run03 166+7=173，第三局最后一问未发送 host。三局均恢复核心机制，完整叙事 0/3。暂停时均值 169.3333、总体方差 8.2222、样本方差 12.3333，并非成功解题次数统计。推送授权不等于恢复实验授权。
