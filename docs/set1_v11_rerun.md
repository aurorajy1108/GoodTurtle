# Set 1 修复后重跑（2026-11-10）

在已经export `DEEPSEEK_API_KEY`的终端执行：

```bash
bash /Users/aurorasun/Desktop/COMP1110/GP/GoodTurtle/scripts/start_set1_verified.sh
```

默认输出：`runs/api/20261110_deepseek_set1_v11_once`。可用第一个位置参数指定另一个**不存在**的输出目录；已有目录、日志或PID文件均拒绝覆盖。脚本从自身位置确定repo路径，不要求终端当前位于repo。key只从环境继承，不写入代码、配置、日志或快照。PID打印出来不代表API已成功访问，须检查输出状态和日志。

## 实际顺序与实验设置

1. 冻结代码、提示词、模型配置、完整数据、Host包和诊断题，保存SHA256；诊断与正式CL共用这个快照。运行中若快照变化，下一阶段拒绝执行。
2. 运行20个Host诊断问题，每题一次，使用配置中的Host模型和persistent会话协议。问题包括正确/错误因果、完成与未完成、部分吃过与全部吃完、irrelevant、mixed，以及先前错误反馈干扰。预期答案不作为独立字段发给模型。每个诊断题隔离会话，完整缓存轮换另有离线测试。
3. **20题全部通过**才启动12局CL；错标签、非法响应、传输失败或未跑完都停止。保留诊断结果与用量，不反复重抽标签直到通过。它是开发诊断，不是独立测试集的准确率估计。
4. A=15（positive）、14（negative）、28（neutral），固定B=13。16不参加，本批没有MAS，没有额外重复。
5. 每道A重新做一次，结束后无论成功与否均提供完整规范答案。同一道A的经验冻结后复用；不会挑成功A替换失败A，也不会复用旧批次的已污染轨迹。
6. 每个A分别对应B的direct、transcript+完整A答案、answer_only，共9局B，加3局A=12局。direct之间是独立新局，不复用同一份baseline结果；调度seed只影响顺序，不是模型采样seed。
7. 每局独立100次额度；错误/不完整交卷计1次，槽位100强制最终交卷。错误交卷公开反馈仍仅yes/no/yes and no/irrelevant。

当前默认模型来自`configs/loop.deepseek.json`：Host和Grader为`deepseek-v4-pro`、thinking enabled/high；Player为`deepseek-flash`、thinking disabled。Host每个普通问题一次判断；Grader只在交卷时调用。角色会话独立，公开聊天持续保留，A答案只进入转移条件的Player。

## 本次修复范围

- TS013/TS014的26条新参考答案和因果/角色/时间范围约束，版本`host-v11-set1-causal-20261110`。原人工标签与原始文件保留；新裁决明确标注assistant，未伪称人工标注。
- 普通自己的行为（叫服务员）与特指学术选课系统操作区分；尝过与吃完、完成得差与未完成、搭便车与行政裁决区分；“仅仅吃完就是全部解释”的问法不再完整肯定。未知短时间间隔按irrelevant处理。
- persistent Host/Grader将参考语义存入`reference_library`，只追加新内容，`active_example_ids`指明本轮检索结果。完整汤底不摘要，历史不删除，例子的原公共历史不截断，来源/审核元数据不进入运行时。缓存按角色/游戏/lane隔离，旧例不是新事实。
- 用旧13题99次Host调用离线回放，同样的完整参考内容与选择顺序均能还原；增量用户消息字符从146344降到73290（49.9%）。这是字符结果，不代表已测得相同的token或账单降幅。
- TLS连接阶段的一般SSL错误现在也能确认“HTTP请求尚未发出”并有限重试；证书错误不重试。未确认发送阶段的错误仍不盲目重发。失败调用仍进入审计和费用记录。
- 新运行时版本`single-cached-reference-session-v3`。旧批不能混入新Host包或新缓存协议继续当同一条件比较；旧档保持不变。旧批恢复须使用兼容的归档恢复代码。本次重跑全部新建。

## 看进度和结果

| 文件 | 内容 |
|---|---|
| 输出目录旁的`.launcher.log` | 启动器输出；Python启动失败首先看这里 |
| `status.json` | 当前阶段：host_gate、continual，以及停止/完成状态 |
| `host_gate.log` / `continual.log` | 对应阶段的stdout/stderr |
| `host_gate/results.jsonl`、`summary.json` | 每个诊断题的expected/actual和通过数 |
| `study/continual/index.html` | 每局HTML轨迹入口 |
| `study/continual/<run>/trajectory.html` | 提问、回复、交卷和私有评估审核视图 |
| `study/continual/<run>/result.json` | 局内最新问题数、提交数、得分、错误 |
| `study/continual/<run>/api_calls.jsonl` | 每次模型调用、模型、用量、缓存和传输诊断 |
| `cost_summary.json` | 阶段结束后的诊断+CL合计用量 |
| `run_manifest.json` | 精确参数、Host版本和快照哈希 |

阶段内以每局result和api_calls为最新状态；根目录费用汇总在阶段结束时更新。记录input/output/cached/reasoning tokens。没有该模型的可靠价格配置时，estimated/actual费用保留unknown/null，不把它显示成免费，也不猜测实际账单。

## Python入口与全部参数

```bash
python3 scripts/run_set1_verified.py --mode run \
  --out runs/api/20261110_deepseek_set1_v11_once
```

| 参数 | 默认值 | 含义 |
|---|---|---|
| `--out` | 必填 | 新输出根目录，不允许覆盖或旧prefix复用 |
| `--mode` | `plan` | plan只冻结/检查、不调用API；run执行诊断，通过后跑CL |
| `--config` | repo内`configs/loop.deepseek.json` | 三角色模型/思考设置、预算、上下文策略、可选价格配置；运行前要求相应环境凭据可用 |
| `--dataset` | repo内`data/annotations/turtle50_v4/private.json` | 完整私有题面/汤底/评分数据，冻结到本批，不传给Player |
| `--seed` | `20261102` | 调度顺序seed，不能保证模型输出可重复 |

本入口固定Set1、A白名单、固定前题、repeat=1、primary方向和`on-error=stop`，避免误跑多余组合。要改实验范围应使用`study_20261102.py`并单独报告。

`check_host.py`保留原参数：`--dataset`、`--config`、`--cases`、`--out`均必填；`--repeat`默认1；`--dry-run`仅验证/落盘不调用模型。它现在遵循config的session_mode，并记录诊断调用成本。未通过诊断时可先审核`host_gate/results.jsonl`对应题目，修改后用新目录重跑，避免把旧标签悄悄改成通过。
