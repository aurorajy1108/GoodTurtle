# 自动修复格式并续跑

当前已停止的Set1从这里继续，在已export `DEEPSEEK_API_KEY`的终端执行一次：

```bash
bash /Users/aurorasun/Desktop/COMP1110/GP/GoodTurtle/scripts/start_set1_auto_continue.sh
```

当前默认输出`runs/api/20261111_set1_auto_continue_v2`，第一个位置参数可指定其他不存在的目录，第二个位置参数指定停止的study或监督器根目录（默认`runs/api/20261111_set1_auto_continue`）。它会选择最新已落盘的续跑检查点，跳过未成功创建的下一份归档，并拒绝接管仍在运行或已完成的监督器。已完成的A14、目标13的94次问答、已通过的20题诊断均复用；首先处理已经生成但尚未提交的第95次交卷。原目录保持不变。启动后常见格式错误直接在局内处理，无需每次人工改代码或重开整局。

## 处理顺序

1. 原有严格解析和限定引号/换行修复优先。输出完整才处理，截断、拒绝、API错误不会伪装成一个问题。
   对重复JSON键，只有同一个键的所有值完全相同时才可合并，并保留完整动作；重复键值冲突或存在额外未知字段仍拒绝。第95次输出的两个type均为final，已按此规则离线验证，完整解答文字不变。
2. 识别`<｜end▁of▁thinking｜>`、`</think>`、`</analysis>`、`</解答过程>`，只解析最后一个结束标记之后的动作；也支持去掉完整的markdown JSON围栏。
3. 没有结束标记却有多个完整动作时，按事先固定的位置规则取**最后一个完整动作**，不是比较哪个问题更有希望。候选数、选择位置和原文哈希写入轨迹。损坏的额外对象不被静默丢弃。可在策略中设为`reject`禁用这种选择。
4. 仍需格式修复时调用独立的Codex格式器。只传原始Player输出和格式控制，不传当前题面、公开历史、汤底、评分或Host反馈。它必须返回原文中的完整动作；程序核验type及完整text值逐字一致，不能补充、缩短、改写问题或把question改成final。能否答对不参与选择。
5. 当前局继续使用Player原来的持续会话，保留原始assistant输出。格式器是隔离的临时调用，不替代Player，不让Player重新生成当前问题。

Codex调用复用本机已登录的CLI，使用只读沙盒、JSON输出schema和项目已有禁工具配置；这一调用方式符合[官方非交互模式文档](https://learn.chatgpt.com/docs/non-interactive-mode)。这里自动修复的是输出数据格式，不是让Codex随意修改实验代码、Host或评分标准。

## 限制与计费

- 每个无法本地修复的输出最多一次Codex调用；每局最多3次。超限、无法逐字证明恢复、Codex不可用、同一失败输出再次出现时停止并记录原因，不无限重抽。
- 默认最多3个续跑子进程。若局内处理仍意外停止，监督器只针对完整、未提交的Player格式错误创建下一份续跑归档。API、认证、截断、Host/评分异常、用户中断不作为格式错误重跑。
- 所有已完成局和当前额度保留。问题或错误交卷只有实际提交后按原规则计数；内部格式器调用不算一道问题，但单独记录其tokens、角色和费用。
- 原始输出、response ID、修复方法、修复后动作、控制器/策略哈希保留。Codex角色为`format_repair`；其费用包含在每局和批次统计中，实际账单未知时保持null。
- 后续归档包含前序调用，因此监督器只复制**最新续跑的累计费用**，不能把多个归档再相加。诊断费用只包含一次。
- DeepSeek仍用于Host/Grader/Player，Player thinking保持disabled；Codex只是额外的格式修复器。默认`gpt-6.1-sol / low`，通过CLI现有登录调用。`codex login status`可检查登录，本机已确认登录；未实测的模型服务访问或额度问题仍可能令格式器停止。
- 自动恢复不是质量认证：错误Host标签、错误解答、得分偏低不会触发重新抽样。正式统计应报告修复次数、类型和辅助调用成本；新增解析策略是显式的协议变更，不能当作完全未修改的旧实现。

## 参数

Python入口：

```bash
python3 scripts/auto_continue.py \
  --from-study runs/api/20261111_set1_auto_continue \
  --out runs/api/20261111_set1_auto_continue_v2 --mode run --max-continuations 3
```

| 参数 | 默认 | 含义 |
|---|---|---|
| `--from-study` | 必填 | 停止的单批次study、verified根目录或监督器根目录；不接管任意正在运行的进程 |
| `--out` | 必填 | 新监督器根目录；已有目录拒绝覆盖 |
| `--mode` | `plan` | plan只离线复制、校验，不调用Codex或实验API；run实际续跑 |
| `--max-continuations` | `3` | 最多续跑子进程数，范围1–10；不代表重复实验次数 |

策略位于`configs/player_format_repair.json`，冻结到新批次/自动续跑快照；不改变原三角色配置：

| 字段 | 默认 | 含义 |
|---|---|---|
| `protocol` | `player-format-v1` | 协议标识，只接受此版本 |
| `enabled` | `true` | 是否启用局内自动修复；false时保留严格停止行为 |
| `multiple_actions` | `last_complete` | 按位置取最后动作；`reject`拒绝无标记多动作 |
| `max_codex_calls_per_game` | `3` | 每局辅助格式调用上限，0–10；0只允许本地修复 |
| `max_raw_chars` | `100000` | 接受处理的原始输出长度上限，1–200000；不截断后修复 |
| `formatter.provider` | `codex_cli` | 复用现有provider适配器 |
| `formatter.model` | `gpt-6.1-sol` | 显式格式器模型ID |
| `formatter.reasoning_effort` | `low` | 格式器思考档位 |
| `formatter.timeout` | `180` | 单次CLI调用秒数上限 |
| `formatter.max_retries` | `0` | 额外底层重试数；默认不重复请求格式器 |

低层`resume_study.py --auto-player-format`同样可用，但不能与其他repair参数同时使用。它会保留并验证已生成动作，再将新格式模块和策略作为显式controller overlay写入副本；未知但完整的语法错误可等到run时由Codex处理，plan阶段不会发出辅助模型调用。

## 查看进度

- 根`status.json`：当前`active_dir`、最多次数、已用续跑次数、停止原因。
- 根`index.html`：跳转最新轨迹与费用；`events.jsonl`记录每次断点。
- `continuation_01/continual/<run>/trajectory.html`：原始问答、交卷与修复事件；后续归档编号递增。
- `continuation_01/continual/<run>/api_calls.jsonl`：所有调用，含`format_repair`用量和`format_source_response_id`。
- `continuation_01/continual_resume.log`及监督器`continuation_01.log`：运行与恢复日志。
- `cost_summary.json`：最近完成阶段的累计用量。阶段内以局内result/API日志为最新状态，不把旧汇总误报为实时成本。

首次自动续跑已成功恢复第61次输出，并推进到94次问答。第95次交卷重复type键后严格解析停止，Codex未被调用；现已补齐相同值重复键的兼容规则并准备从该交卷继续。仍然保留A14和全部94次问答，不重新跑60问、第61–94问或诊断。
