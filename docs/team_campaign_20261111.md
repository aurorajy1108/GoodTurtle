# 团队运行：3个CL set、3道MAS，两人各两次

真实API小量测试新发现与有限恢复边界见 [11月11日修复记录](live_test_repairs_20261111.md)。其中新增MAS保存动作恢复，不等于所有free_dialogue中断都可续跑。

分支 `fix/cl-session-prefix-compat-20261111`。默认Set1只选15，16保留可选。每个实验有a/b两个**人工执行槽**：a跑重复1、2，b跑3、4；这与MAS内部两个模型Agent A/B不同。

## 实验与分工

| 实验 | 目标B/题号 | 前题A（预设关系） | a槽执行人 | b槽执行人 | 每人局数 | 合计 |
| --- | --- | --- | --- | --- | ---: | ---: |
| CL Set1 | 13 | 15 positive、14 negative、28 neutral | Jiayang | Amy | 21 | 42 |
| CL Set2 | 34 | 35 positive、33 negative、12 neutral | Zhenqi | April | 21 | 42 |
| CL Set3 | 22 | 47 positive、45 negative、19 neutral | Shirley | Jiayang/Zhenqi **二选一** | 21 | 42 |
| MAS | 38 | solo / free_dialogue | Jiayang（Aurora） | April | 4 | 8 |
| MAS | 2 | solo / free_dialogue | Kelly | Shirley | 4 | 8 |
| MAS | 14 | solo / free_dialogue | Amy | Shirley/Kelly **二选一** | 4 | 8 |
| 总计 | | | | | | **150** |

CL每条A→B比较direct、session、answer_only，每条件共4次B；每人21局=3局A+3方向×3条件×2次B。三个set共126局CL，MAS共24局。A失败也保留实际轨迹并揭晓完整答案，不重抽成功A。每局B重新获得100次额度，第100次强制FINAL；问题和错误/不完整交卷各计1次。

**固定A的范围是每个执行槽。** 每人两次B复用自己的一份A，两个人共产生两份A前缀，每份对应两次B；不是四个独立A样本。报告保留前缀哈希、执行人及全局重复编号，便于分层分析。Smoke试跑不计入正式四次重复。

| 人员 | 已确定task IDs | 额外候选（协调后只选一人执行） |
| --- | --- | --- |
| Jiayang | cl-set1-a,mas-ts038-a | cl-set3-b |
| Amy | cl-set1-b,mas-ts014-a | — |
| Zhenqi | cl-set2-a | cl-set3-b |
| April | cl-set2-b,mas-ts038-b | — |
| Shirley | cl-set3-a,mas-ts002-b | mas-ts014-b |
| Kelly | mas-ts002-a | mas-ts014-b |

候选槽各只启动一次，**不要两位候选都跑**。任务不按姓名自动推断，命令必须显式选task ID。完整定义在 [配置](../configs/team_campaign_20261111.json)。

## 准备

```bash
git fetch origin
git switch fix/cl-session-prefix-compat-20261111
git pull --ff-only
```

在仓库目录运行，Python3.10+，loop使用标准库；在启动脚本的同一个终端export自己的DEEPSEEK_API_KEY。默认Host/Grader=Pro/high，Player/Partner=Flash/thinking关闭，新返回协议与会话实现不变。配置及可选格式器要求见 [版本指南](run_session_prefix_v1.md)。

查看精确清单，不调用模型：

```bash
python3 scripts/team_campaign.py list --preset full
```

## 一键小量测试

```bash
bash scripts/run_team_smoke.sh jiayang cl-set1-a,mas-ts038-a
```

选定CL槽只测positive前题：A一次、direct/session/answer_only各一次，**4局CL**；选定MAS槽solo/free_dialogue各一次，**2局MAS**。上述合计6局，并发1。额度仍为100，不缩短协议。其他人的测试替换姓名和自己的task IDs即可。

参数：`RUNNER TASKS [OUT]`。RUNNER仅作审计ID，不传给模型；TASKS为逗号分隔槽位。OUT默认 `runs/api/smoke_<runner>_<timestamp>`，已存在则拒绝覆盖。

## 一键正式跑：每人两次

下列命令分别由对应人员运行，**不是让每个人全部执行一遍**：

```bash
bash scripts/run_team_batch.sh jiayang cl-set1-a,mas-ts038-a 2
bash scripts/run_team_batch.sh amy cl-set1-b,mas-ts014-a 2
bash scripts/run_team_batch.sh zhenqi cl-set2-a 2
bash scripts/run_team_batch.sh april cl-set2-b,mas-ts038-b 2
bash scripts/run_team_batch.sh shirley cl-set3-a,mas-ts002-b 2
bash scripts/run_team_batch.sh kelly mas-ts002-a 2
```

协调后将候选task追加到相应人员TASKS。例如Zhenqi承担Set3第二槽时改为 `cl-set2-a,cl-set3-b`。

参数：`RUNNER TASKS [WORKERS=2] [OUT]`。每槽固定两次重复。WORKERS为同时运行的独立槽位批次（1–12），不并行发送同一局的问题；实际并发不超过任务数。OUT默认 `runs/api/full_<runner>_<timestamp>`，拒绝覆盖。脚本前台运行，保持终端开启；后台运行可先 `mkdir -p runs/api`，再用 `nohup bash scripts/run_team_batch.sh ... > runs/api/<unique>.launcher.log 2>&1 < /dev/null &`。

### 一台机器集中跑全员

只允许**一个协调人统一跑全部，其他人不再分别启动**时使用：

```bash
bash scripts/run_team_batch.sh coordinator all 4 runs/api/team_all_formal_v1
```

一次安排12个槽、150局，最多4个槽同时进行。建议小量验证后从4并发开始，不能保证增加并发会加速或不被限流。不要每个人都跑all，那会重复收费。模型、100次额度、会话和研究条件不会因并发改变。

选中CL Set1时，默认先做20次Set1 Host开发诊断，通过才执行任务；**不意味着验证了其他set/MAS的Host**。分布式运行时每人各做一次诊断；协调人all只诊断一次。诊断费用计入token统计，不计入游戏局数。

## 零费用计划与150局并行dry-run

```bash
python3 scripts/team_campaign.py start --preset full --runner coordinator \
  --tasks all --workers 4 --mode plan --out runs/api/team_formal_plan

python3 scripts/team_campaign.py start --preset full --runner offline \
  --tasks all --workers 4 --mode dry-run --out runs/api/team_formal_offline_check
```

plan仅冻结；dry-run真正验证调度和输出，但不调用模型、跳过收费诊断，全部标记dry_run，没有模型成绩。每次选全新OUT，不能用原plan目录覆盖运行。

## 汇总所有人结果

每人交付自己的**整个输出目录**，保留campaign.json、tasks和轨迹；将目录放在同一机器后：

```bash
python3 scripts/team_campaign.py collect \
  --inputs runs/api/jiayang_formal runs/api/amy_formal \
           runs/api/zhenqi_formal runs/api/april_formal \
           runs/api/shirley_formal runs/api/kelly_formal \
  --out runs/api/team_merged_v1
```

替换为实际目录。汇总零模型调用，global_repeat标明1–4，缺少槽位如实列出；不会把预期四次当作已完成四次。重复槽、不同代码/模型/汤底或positive选择、smoke/full、dry/live混用都会拒绝合并。

### 输出及异常

- `campaign.json / experiments.md`：精确任务清单、参数和冻结哈希。
- `status.json / <task>.log`：各槽状态、PID及日志。
- `index.html`：全部对局及trajectory链接。
- `experiment_runs.json / .csv`：姓名、task、全局重复号、问题/提交数量、partial score、成功及状态。
- `performance.json`：按题目/来源/条件的均值、样本方差、成功率、已完成重复编号和A前缀哈希；失败耗尽额度与成功解题问题数分别统计，API错误不作0分。
- `cost_summary.json`：逐角色/模型累计已记录token与估计成本，含诊断、格式辅助调用；未知账单保持未知。
- `tasks/<task>/continual或team/<run>/trajectory.html`：完整轨迹；MAS另有shared_dialogue.html。

默认一个槽失败会停止本机未启动任务并中断本启动器的其他进程组，保留费用和轨迹，不杀同事的独立进程。`--on-error continue`允许继续其他独立槽，但不重新生成失败局。CL可按 [恢复指南](automatic_continuation.md) 对 `tasks/<cl-task>` 创建恢复归档；合并前确认每槽只采用一个最终版本，原始与恢复拷贝不能都计数。free_dialogue暂不支持题中续跑。

## Python参数

`list`接受 `--preset smoke/full`（默认full）及 `--set1-positive 15/16/both`（默认15）。

`start`的全部参数：

| 参数 | 默认 | 含义 |
| --- | --- | --- |
| --preset | smoke | smoke每槽一次、CL只选positive；full每槽两次、CL三类来源 |
| --runner | 必填 | 审计ID：字母/数字/下划线/短横线，最多64字符 |
| --tasks | 必填 | 逗号分隔task IDs，或仅协调人用all |
| --workers | 2 | 同时执行的槽位批次数1–12 |
| --set1-positive | 15 | 16替换15；both两道都选，full全员从150增至164局，不与默认混合 |
| --config | configs/loop.deepseek.json | 全角色配置 |
| --dataset | data/annotations/turtle50_v5/private.json | Git内完整题库 |
| --seed | 20261111 | 调度种子，按槽偏移，不控制API采样 |
| --host-gate | auto | 含CL Set1先做20次诊断；none显式跳过 |
| --on-error | stop | stop停止本机其他任务；continue继续其他槽；失败槽内部始终停止 |
| --poll-seconds | 2 | 状态刷新间隔1–30秒 |
| --mode | plan | plan仅冻结；dry-run离线执行；run调用模型 |
| --out | 必填 | 新输出目录，拒绝覆盖 |

`collect`接受 `--inputs`后接一个或多个campaign输出目录、`--out`新汇总目录。各入口均支持`--help`。macOS/Linux/WSL可运行；原生Windows进程组终止未验证。

11月11日验证：234项离线测试通过；6局smoke与150局full均完成dry-run，full实测最高并发4，异常0；两份分开交付的结果合并后仍为150局且重复编号1–4，无遗漏槽位。本轮未启动收费实验。
