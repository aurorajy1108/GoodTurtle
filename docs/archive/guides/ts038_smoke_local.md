# TS038 本地两局试跑与实时网页

只跑 `solo,free_dialogue` 各一次，作为流程检测，不计入正式重复。
Host/Grader、Player/Partner 沿用 `configs/loop.deepseek.json`，预算为每局100次外部提交。
双 agent 使用互补分工、自适应交接、A先发言、每次外部提交前最多4条内部消息。

在 GoodTurtle 仓库根目录先做零调用检查，输出目录必须全新：

```bash
python3 scripts/run_ts038_smoke.py --mode dry-run \
  --out runs/api/ts038_my_dry
```

真实执行，可沿用已export的 `DEEPSEEK_API_KEY`；若key只保存在本地 `.env`，显式传 `--env-file .env`：

```bash
python3 scripts/run_ts038_smoke.py --mode run --env-file .env \
  --verified-dry-run runs/api/ts038_my_dry \
  --out runs/api/ts038_my_live
```

启动器只向子进程注入凭据，不修改 `.env`、配置或系统设置。默认使用 `/etc/ssl/cert.pem` 验证证书，并选择项目已有的DeepSeek直连模式。
可用 `--ca-file PATH` 指定其他可信CA文件，或 `--proxy-mode system` 选择系统代理。证书验证始终开启。
`smoke_provenance.json` 保存commit、工作区状态、连接设置；`snapshot_hashes.json` 保存实际实验代码、题库、prompt及配置的冻结哈希。

另一个终端启动只读网页：

```bash
python3 scripts/serve_progress.py --batch runs/api/ts038_my_live/team --port 8765
```

打开 <http://127.0.0.1:8765>，每2秒读取最新轨迹。横轴为外部提交序号，纵轴为实际交卷得分；普通提问不产生评分，暂无评分与0分分开显示。
页面还显示当前题目、策略、运行状态、额度、A/B发言与共享聊天、token及已知费用。
本地服务仅监听loopback，只提供指定批次的实验文件。`Ctrl+C` 停止网页服务不会停止另一个终端里的实验。

## 2026-11-12 流程检测记录

- `ts038_smoke_live_20261112`：第一次请求因Python默认CA缺失而停止，无有效提交。
- `ts038_smoke_live_20261112_tls_retry01`：启用可信CA和直连后，Player与Host成功返回；2次提问后B复制了提示中的 `ACTION NEXT=A` 占位符，格式纠正仍失败，批次停止。
- `ts038_smoke_live_20261112_contractfix01`：提示改成可直接执行的完整首行列表，例如 `DISCUSS NEXT=A`。保留严格解析，不猜测旧输出的动作类型；新批次独立冻结，不恢复旧MAS会话。

异常批次及费用记录保留；不得把不同版本的尝试当作正式重复合并。所有批次均发生错误即停止，`free_dialogue`不支持局中恢复。
