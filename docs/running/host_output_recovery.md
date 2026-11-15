# Host输出格式恢复与断点续跑

这次修复只处理接口输出和会话恢复，不修改汤底、Host参考问答、四种标签的含义、评分点或已经返回的有效回答。

## 新实验自动生效的规则

- 唯一、完整的标签可做本地格式归一化，例如`NO.`、`Answer: yes`、`exactly no.no`。重复内容必须是同一个标签；正文解释、`yes/no`、`no…yes`等不猜测。
- DeepSeek Host返回`finish_reason=stop`但正文为空时，只重试当前Host请求。请求body、会话位置、Player问题保持一致；空回复不加入模型的assistant历史。
- 同一道待答问题最多累计3次空回复尝试，包含重启前已经发生的空回复；profile的`max_retries`还可能进一步降低本次调用的自动重试次数。不会通过重启重置这个上限。
- 拒绝、截断、工具调用、不同标签冲突、鉴权/余额问题不走这个空回复重试路径。
- 正常问题仍只有一个有效Host标签。不会为核对答案调用第二位Host；原始API输出、空回复usage和所有费用均保留。
- Player不重问，不重做已完成的游戏，不重置100次外部提交额度。MAS的两名Player会话、公共buffer和私有复查笔记一起恢复。
- Host或Grader读取响应时断连，且本地没有收到可用正文、response ID或usage时，可校验断点后原样重发该请求。一次请求累计3次读取失败后停止，跨重启计数；Player读取失败不自动重新采样。已收到有效标签或评分时不会再请求新的判断。
- 读取中断可能已经产生远端费用，原调用保留为`cost_status=unknown`，恢复记录标注`possible_duplicate_remote_charge=true`，不会按免费重试计算。
- DeepSeek发生`IncompleteRead`时，如果异常中保留的字节能严格解析为一个完整JSON对象，则直接执行原有响应校验并保留该次答案和usage，不重发。真正截断的JSON、仅有空白的响应仍视为读取失败。日志只额外记录片段字节数、SHA256和类型，避免泄露正文。

已保存且可以明确归一化的回答恢复时，不增加Host调用。空回复恢复时只增加必要的Host调用。不能从未展示给Player的reasoning内容猜测标签。

## 同事更新并运行

在自己干净的代码工作区切换到当前实验分支并更新：

```bash
git fetch origin
git switch fix/cl-session-prefix-compat-20261111
git pull --ff-only
```

用自己的`DEEPSEEK_API_KEY`环境变量或忽略的`.env.local`。新实验照原入口运行即可，新冻结快照自动带上恢复代码，例如：

```bash
bash scripts/run_compute_matched_agents.sh runs/api/ts038_robust_yourname_01
```

这会准备并开始四组×两次的真实API实验。模型和预算详见[自查对照说明](compute_matched_agents.md)。不要使用他人的输出目录或重复启动同一目录。

## 恢复已经停止的CL study

原study必须停止，且存在一个可校验的未完成游戏；`--out`必须是原目录之外的新目录：

```bash
python3.11 scripts/resume_study.py \
  --from-study YOUR_STOPPED_STUDY \
  --out runs/api/YOUR_CL_HOST_RECOVERY \
  --recover-host-output --mode run
```

- `--from-study`：含`study_plan.json`、`runtime_snapshot/`、`continual/`的最新单批次study，不是campaign总目录或单局目录。
- `--out`：新归档，保留原目录，复制原轨迹和已完成结果。
- `--recover-host-output`：选择本次受限恢复；不能与其他恢复flag同时使用。
- `--mode plan`：只校验并准备，默认不调用API；`--mode run`准备后执行原计划剩余部分。

未收到响应的网络中断使用同一入口的`--recover-transport`替代`--recover-host-output`；团队监督器会自动选择已通过校验的恢复方式。

对已有团队campaign，可继续使用自动监督器；它现在会识别该恢复模式：

```bash
bash scripts/run_supervised_campaign.sh YOUR_STOPPED_CAMPAIGN_OR_SUPERVISOR runs/api/YOUR_NEW_SUPERVISOR
```

## 恢复四组计算预算对照

```bash
python3.11 scripts/compute_matched_agents.py recover \
  --from-run YOUR_STOPPED_2X2_OUTPUT \
  --out runs/api/YOUR_2X2_HOST_RECOVERY
bash scripts/run_compute_matched_agents.sh runs/api/YOUR_2X2_HOST_RECOVERY
```

- `recover`只复制和校验，不调用API；原run必须为`requires_attention`或`interrupted`，且没有活跃worker。
- `--from-run`：含`plan.json`、`snapshot_hashes.json`和逐局目录的四组对照输出根目录。
- `--out`：原目录之外、尚不存在的新目录。只有可校验的断点才会授权，已完成的7局不会重跑。
- 后续bash只运行未完成游戏，复用原预算计划。不要再次叠加原目录的费用；新目录已包含所有历史调用。

`recovery_manifest.json`记录代码覆盖及哈希；逐局`host_output_recovery.json`是待处理检查点，成功后移除，授权与恢复事件保留在`trajectory.jsonl`。`api_calls.jsonl`保留原始输出，恢复后的公共label出现在`host_feedback`事件中。重复归档只是续跑副本，不是新实验重复。

## 人工决定在耗尽读取重试后继续

默认仍然不超过同请求3次读取失败。排查连接、确认无活跃worker后，操作人可显式申请**一次**额外窗口，最多再发生3次读取失败。它不会清空旧日志、usage、潜在费用或100次答题额度；自动监督不会自行申请这个窗口。同一局已有该授权时拒绝再次申请。

CL单批次：

```bash
python3.11 scripts/resume_study.py --from-study YOUR_STOPPED_STUDY \
  --out runs/api/YOUR_RENEWED_CL --recover-transport \
  --renew-read-window 'Operator continuation after connection diagnosis and pause' --mode run
```

CL团队监督器（先在终端export密钥或source忽略的`.env.local`）：

```bash
python3.11 scripts/supervise_campaign.py --campaign YOUR_STOPPED_SUPERVISOR \
  --out runs/api/YOUR_RENEWED_SUPERVISOR \
  --renew-read-window 'Operator continuation after connection diagnosis and pause'
```

MAS四组对照：

```bash
python3.11 scripts/compute_matched_agents.py recover --from-run YOUR_STOPPED_2X2_OUTPUT \
  --out runs/api/YOUR_RENEWED_2X2 \
  --renew-read-window 'Operator continuation after connection diagnosis and pause'
bash scripts/run_compute_matched_agents.sh runs/api/YOUR_RENEWED_2X2
```

`--renew-read-window REASON`必须填写简短原因，仅适用于已累计3次读取失败、且没有收到正文、ID或usage的DeepSeek Host/Grader请求；CL同时要求`--recover-transport`。监督器仅首次检查点使用此人工授权，此后仍遵守正常校验和上限。`transport_read_window.json`将原因、时间、原日志哈希和额外上限绑定到唯一原请求；不能用来放宽其他题目或角色的失败上限。

DeepSeek官方说明，非流式排队时可能发送空行保活，而不是模型答案：[连接保活机制](https://api-docs.deepseek.com/quick_start/rate_limit/)。本地配置600秒与观察到约31秒断流不同，现有证据不能确定是服务端还是网络中间层；不能把空白片段误认为有效回答或未知费用为零。

## 停止原因与限制

新自查游戏区分外部100次上限（`budget_exhausted`）和提前耗尽solver预算（`solver_budget_exhausted`）。这只修正元数据分类，不改变停止条件或分数。旧已完成结果保持原样，分析旧日志应结合实际提交数和剩余计算预算。

会话链、问题文本、原请求body、公共buffer或冻结输入对不上时拒绝恢复。未知输出仍会暂停告警，不能保证任何模型错误都能自动继续。macOS通知可见性取决于本机权限；完整状态与失败原因以输出目录里的`status.json`和`alerts.jsonl`为准。
