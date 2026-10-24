# Continual learning 与双 agent 实验

入口：`python3 scripts/experiment.py`，Python 3.10+，仅标准库。复用现有 host/player/grader API 配置、四标签协议、100 次预算、HTML/Markdown/JSONL 轨迹及私有评分。所有命令从仓库根目录运行。当前实现是 **in-context continual learning / experience transfer**，没有梯度更新或模型参数训练；A→B 是最小两任务序列，不测长期遗忘。

## 数据与评分

仓库已发布 `data/annotations/turtle50_v4/private.json`：TS001–TS050，共 50 题、161 个评分点，经过三位 AI 独立提案及裁定。clone/pull 后即可使用，无需另取数据包。每题包含：

- `completion_requirements`：完整叙事必须覆盖的清单，供 host／grader 使用，player 不可见。
- `rubric[].points / full_credit / half_credit / zero_credit`：百分制满分值与满分、半分、零分规则。程序仍按 `weight × credit` 输出 0–1，乘 100 得百分制。
- `grading_notes`：不可过度要求的细节、hand/arm 等边界。
- `annotation_status`：标记 AI 审核且待人工确认，不能视为人工金标准。

人工阅读同目录的 `review.md`，权威运行输入为 `private.json`。原 XLSX 未改写，其 SHA-256 保存在 source 字段。所需 host packs 已一起入库；完整标注不再受旧的 eraser／pillow 发布范围限制。

TS040 是 [Puzzle Prime: Unconscious and Bleeding](https://www.puzzleprime.com/puzzles/brain-teasers/lateral/unconscious-and-bleeding/) 的简短英文转述：窃贼扔砖砸窗，砖反弹使其昏迷。记录了来源和待复核状态，未验证难度，未自动加入关系组。

`partial_score=1` 仍不足以自动判成功：grader 还需确认完整叙事、无关键矛盾。不得拼接多次 final 获得满分。判据未量化的参考叙事细节仍通过完整解答清单检查。模型判分与 host 标签都必须人工审核。

## A→B 对照

```sh
export OPENAI_API_KEY='你的 API key'
export OPENAI_MODEL='账号可用的准确 API 模型 ID'

# 默认 G07 的两个方向：TS022→TS047，以及 TS047→TS022。
python3 scripts/experiment.py continual \
  --dataset data/annotations/turtle50_v4/private.json \
  --config configs/loop.openai.json --group G07 --repeat 3

# 限定一个方向，并先做不调用模型的检查。
python3 scripts/experiment.py continual \
  --dataset data/annotations/turtle50_v4/private.json \
  --config configs/loop.openai.json --group G01 --pair TS012:TS017 \
  --repeat 3 --dry-run

# 全部 28 个关系组；建议先完成小批 host 人工审核再运行。
python3 scripts/experiment.py continual \
  --dataset data/annotations/turtle50_v4/private.json \
  --config configs/loop.openai.json --group all --repeat 3
```

每个 group / A / B / repeat 构成一个 block：

1. 新会话完成 A，最多 100 次。无论 A 答对还是耗尽预算，结束后都揭示 A 的完整标准答案；保留真实失败轨迹，不改写成成功。答案揭示不算提问。
2. 在新会话直接做 B（direct），没有 A 的任何信息。
3. 在另一新会话做 B（transcript），每轮提供 A 的完整公开提交、四标签反馈以及结束后揭示的完整标准答案。A 的模型私有推理、rubric、分数、题号、family、关系标签均不传入；B 的标准答案始终不可见。
4. 比较同一 block 的两个 B；每局 B 都有完整独立预算。B 条件的运行顺序随机化，互相不共享 B 的轨迹。

根据当前实验要求，默认 `--source-feedback answer`：A 结束后提供 **A 的完整标准答案**，永远不给 B 的答案。`--source-feedback none` 仅作为显式选择的历史消融条件，必须与 answer 分开报告。A 不必成功，源局成功与否留在 contrasts 中用于分层分析。完整答案写入 `source_answer_reveal.json` 和源 trajectory 的 `source_answer_reveal` 事件，计数不变。

可选 `--memory card` 将 A 的允许信息总结成不超过 300 词的经验卡，随后让 B 看卡；默认 answer 模式还会在卡旁单独提供未经摘要或截断的 A 完整答案，防止摘要遗漏；`--memory both` 同时包含 direct / transcript / card 三种 B。卡由 player 配置的模型生成，调用和成本计入源局 `memory` 角色，不读取私有 grader 信息；300 词是提示约束，不是截断器。

同组全部题按**有方向的两两组合**展开。28 组共 76 个 group-pairs，每次重复默认 228 局（76 个 A + 152 个 B）；repeat=3 是 684 局。both 模式每次重复 304 局，另有 76 次摘要调用。API 失败会提前终止，实际数量可能更少。

同一题对可属于多个组，保留为不同假设，不能视为独立证据：G02/G03/G04 的 15↔16、G09/G10 的 10↔42、G11/G26 的 33↔34 重叠。其中 G04 与 G02 的正负标签分别描述元策略帮助和具体答案固着，不能将标签当已知实验结果。当前汇总按 group+condition 分层，不计算把重叠对混在一起的总迁移结论。关系信息只供实验调度和研究者分析。

## 双 agent 合作

```sh
python3 scripts/experiment.py team \
  --dataset data/annotations/turtle50_v4/private.json \
  --config configs/loop.openai.json --puzzle TS002,TS031 --repeat 3

# 只比较单人和双人讨论；可用不同供应商作为第二位 solver。
python3 scripts/experiment.py team \
  --dataset data/annotations/turtle50_v4/private.json \
  --config configs/loop.openai.json --puzzle TS040 --repeat 3 \
  --strategies solo,discuss --partner-config configs/partner.deepseek.json
```

| condition | 每个外部回合的内部流程 | 玩家模型调用次数 |
| --- | --- | ---: |
| `solo` | player 独立提交 | 1 |
| `alternating` | player、partner 轮流提交，每人都看到本局完整公开历史；player 先手 | 1 |
| `discuss` | player 提草案 → partner 审查 → player 修订 → 提交 host/grader | 3 |
| `solo_reflect` | 同一 player 提草案 → 自己审查 → 自己修订 | 3 |
| `independent` | 两位 solver 根据相同公开历史独立提案 → leader 合并；partner 看不到第一份提案 | 3 |

默认仍运行原四种（不含 independent）；可通过 --strategies 选择。每题随机选一个初始条件顺序，再按重复编号循环轮换；block 的执行顺序随机化；各条件之间不共享答案或记忆。两 agent 共享同一个 100 次外部提交预算，错误/不完整交卷计 1。讨论草案与审查不送给 host，也不计外部问题数；其调用、token、耗时单独记录。第 100 次必须由最终提交者交卷。两个 solver 均不能接触参考答案、rubric 或私有评分。

`discuss` 中 partner 只看公开游戏状态和当轮草案，不具有独立历史秘密记忆；往轮讨论可供研究者查看，但不自动追加给后续模型。player 负责最终裁决，无投票和第三个 solver。额外 grader 是评估者，不是合作玩家。

`solo_reflect` 是调用数量匹配对照，不保证 token 或推理计算量完全相同。当 partner 与 player 配置完全一致时，两种讨论条件使用相同提示和无状态请求，`discuss` 与 `solo_reflect` 实际上是同一个采样流程，仅审查调用的日志角色名不同；两者样本差异不能解释为独立 agent 身份带来的收益。轮流合作在默认同一模型时，两位角色只是在轮次上分开，不能据此声称模型多样性收益。异构实验可通过 partner-config 改变第二位模型，且应另开单模型基线，避免把模型能力差异归因于合作。

## 使用当前 Codex 登录账号（无需 API key）

新增 `configs/loop.codex.json`，通过官方 `codex exec` 复用本机已有登录；不读取、复制或提交 auth.json。先确认 `codex login status` 显示已登录，然后将上面的配置路径换为此文件。

```sh
python3 scripts/experiment.py continual --dataset data/annotations/turtle50_v4/private.json \
  --config configs/loop.codex.json --group G07 --pair TS022:TS047 --repeat 2
```

该配置从下一批新实验起按用户指定使用 host/grader `gpt-6.1-sol`、player `gpt-6-luna`，所有角色均为 reasoning high。已运行批次的冻结配置保持不变。Codex backend 仅接受下列字段，和 HTTP API profile 不混用：

| 字段 | 默认/要求 | 含义 |
| --- | --- | --- |
| `provider` | 必填 `codex_cli` | 使用官方本机 CLI |
| `model` | 必填 | 精确模型名；当前 host/grader 为 gpt-6.1-sol，player 为 gpt-6-luna |
| `reasoning_effort` | `high` | low / medium / high / xhigh / max / ultra，实际支持由服务端决定 |
| `timeout` | `240` 秒，范围 (0,600] | 整个单次 CLI 调用的超时 |

不接受 `max_output_tokens / temperature / extra_body / base_url / api_key_env / max_retries`，避免把未支持的选项伪装成已生效。保留全局 max_questions=100。CLI 的网络重试由其自身处理；后端不做输出重新采样。当前重跑配置将 timeout 设为 600 秒（默认仍为 240）。日志中的 http_attempts 在此后端表示 CLI 调用次数，不是底层网络尝试次数。

v2 backend 使用官方 `--output-schema` 和 `--output-last-message`。player 返回原 JSON 协议，v3 数据的 grader 增加逐事实覆盖和矛盾证据；host 在传输层返回 `{ "label": "no" }` 等四标签对象，程序只将 label 展示给玩家。审查文本用 text 字段封装。最终消息文件与 JSONL 若同时有内容必须一致；文件可补足缺失的事件输出，但不会触发重新采样。日志保存原始封装、解码文本、schema 和实际传输 prompt，因此应与旧自由格式 backend 分开报告。

每次角色调用使用新的 ephemeral 会话，工作目录为临时隔离目录；关闭 shell、apps、plugins、browser、computer、multi-agent、memories 等工具功能，并禁止加载用户项目配置和 AGENTS.md。角色 prompt 通过 model_instructions_file 传入，不把仓库路径给玩家。日志若出现工具调用，则该次响应作废并停止该实验。所有角色依然只由 Python loop 提供各自允许的上下文。

CLI 事件不回传实际服务端模型名，日志固定记录请求的模型和这一验证限制，不谎称已独立验证返回模型。当前 CLI 可能对 gpt-6-luna 提示模型元数据缺失、采用 fallback metadata；这不等于切换模型，但可能影响默认上下文配置，警告保留在 diagnostics。用量读取 CLI 的 turn.completed usage，不按 API 价格推算费用。账号额度与 API 余额不是同一套口径。

依据：[OpenAI 非交互模式](https://learn.chatgpt.com/docs/non-interactive-mode)、[配置参考](https://learn.chatgpt.com/docs/config-file/config-reference)。本机 CLI 接入测试和 mock backend 测试已经通过，真实试跑另存于 runs/api/20261022_codex_pilot。

## 全部 CLI 参数

`-h / --help`：入口和子命令都可使用，不调用 API。

| 两个子命令共有 | 默认 / 约束 | 说明 |
| --- | --- | --- |
| `--dataset PATH` | 必填 | 原 XLSX 或 schema v1 私有 JSON；新增 50 题标注需使用本版 private.json |
| `--config PATH` | 必填 | 和 scripts/play.py 相同的 host/player/grader/max_questions 配置；支持全部现有 provider、base_url、api_key_env、reasoning 等字段 |
| `--repeat N` | `3`，正整数 | 每个题对或目标题独立重复次数 |
| `--seed N` | `0`，整数 | 调度随机种子，只控制 block 和条件顺序，不控制远端模型采样；重复不代表相同随机数配对 |
| `--out DIR` | 自动生成 `runs/api/experiment_<UUID8>/` | 必须是新目录，不覆盖、不自动续跑 |
| `--dry-run` | 关闭 | 不要求 key、不调用模型；验证配置/ID、保存计划与各局输入，得分 null。模型环境变量占位仍需设置 |
| `--quiet` | 关闭 | 不打印逐回合对话，仍打印目录及各局摘要；文件日志照常 |

| continual 专用 | 默认 / 约束 | 说明 |
| --- | --- | --- |
| `--groups PATH` | 仓库 `configs/transfer_groups.json` | 关系组 JSON，包含 groups 数组，每组 id/puzzles/relation；默认原用户 28 组 |
| `--group IDS` | `G07` | 单组、逗号分隔多组或 all，不要夹空格 |
| `--pair A:B` | 不限制 | 在选中组中只运行这个方向；如 TS012:TS017；两题必须不同，零匹配时报错 |
| `--memory MODE` | `transcript` | transcript / card / both；三种都包含 direct 基线 |
| `--source-feedback MODE` | `answer` | A 结束后揭示完整答案（不计数）；none 是显式历史消融。direct B 始终不接收 A 信息 |

| team 专用 | 默认 / 约束 | 说明 |
| --- | --- | --- |
| `--puzzle IDS` | `TS002` | 单 ID、逗号分隔列表或 all |
| `--strategies LIST` | `solo,alternating,discuss,solo_reflect` | 从 solo / alternating / discuss / solo_reflect / independent 中选择，不允许重复，必须含 solo 对照 |
| `--partner-config PATH` | 复制 config.player | **单个模型 profile 对象**的 JSON，不是 host/player/grader 顶层实验配置；支持和 player 相同的九个字段 |

此入口没有 `--host / --player / --grader` 覆盖选项，请直接编辑 `--config`。模型配置全部字段、默认值与 key 环境变量见 README 的参数表。`max_questions` 仍是 1..100，最后名额必须 final；每一局 A 和 B、每个 team condition 分别获得此预算。

partner 模板只需设置 `DEEPSEEK_API_KEY`、`DEEPSEEK_MODEL`。不传 partner-config 则与 player 使用相同模型及参数，创建独立请求。

## 输出与解读

- `plan.json`：完整调度、参数、关系组快照、模型设置和数据 SHA256；`experiment_prompts.json` 冻结合作、经验卡和迁移提示。
- 每局保留旧 loop 的 `trajectory.* / result.json / api_calls.jsonl / human_review.csv`，以及输入快照；B transfer 局额外保存 `prior_experience.json`，source 局保存 `transfer_input.json` 和可选 `memory_card.json`。
- 双 agent 与 self-reflection 局另有 `collaboration.jsonl / .md / .html`，记录草案、审查和修订；轮流模式记录提交者。失败调用的原始返回仍在 api_calls 中。
- `index.html` 导航到各局轨迹和合作记录；`experiment_runs.json / .csv` 是带 block/condition、分角色 usage 的运行明细。
- `contrasts.json / .csv`：配对的 B 差异或合作相对 solo 的差异。`score_gain = treatment − baseline`；`success_gain` 同理；`question_saving_both_solved = baseline问题数 − treatment问题数` **只在两边都成功时计算**。`consumption_difference = treatment − baseline` 包括失败消耗，不能解释成解题效率提升。
- `condition_summary.json`：各组/条件分别报告成功率、问题数均值与方差、成功局问题数、分数、HTTP 调用数和耗时；不含 A 的消耗，A 的额外成本在运行明细中单列。
- `contrast_summary.json`：上述指标逐组/逐条件的样本数、均值、总体方差和样本方差。无有效观察为 null；只有一个观察时样本方差为 null。source_success/source_status 在 contrasts 中，可区分 A 成功和未成功的迁移。
- 旧兼容文件 `summary.json / performance.csv` 包含**所有运行（包括 A）**，不要用其混合汇总代替实验效应；正式比较读取 contrasts。

相同 block 配对是实验设计匹配，不是模型随机性匹配。少量重复的均值/方差仅作描述，不输出未经校正的显著性结论。同 family、重叠 group 和多个对比都需要在后续统计分析中考虑依赖。host 的不同响应也可能影响 B 的表现，应人工审查异常轨迹后再解释迁移。

API/协议错误或 Ctrl+C 保存状态并停止批次；源局 needs_review 跳过整块，目标局 needs_review 不参与有效配对。源局正常耗尽预算仍可提供失败经验。所有计划中的对比均列出 valid_pair，不把未运行条件当作 0 分。暂无自动恢复功能。

退出码：0 正常（不保证解出），1 API/协议错误，2 参数或输入错误，130 对局中断。

## 验证

```sh
python3 -m unittest discover -s tests -v
```

已验证公开/私有数据隔离、两 agent 的共享历史、内部讨论不增加外部问题数、同模型反思对照、组内双向展开、冲突标签分组保留、失败局不计成功节省、dry-run 不调用 API，以及原有 100 次强制交卷测试。已通过现有 Codex 登录完成 GPT-6 Luna 试跑；不需要三家 API key。实际服务端模型名未由 CLI 事件独立返回；日志保留请求模型和 metadata fallback 警告，不将其解释为已证实的模型替换。试跑结果和协议校验均不能单独证明 host 语义正确或合作有统计提升。


## 多题重复实验：冻结快照、并发与完整轨迹

```sh
python3 scripts/team_sweep.py --dataset data/annotations/turtle50_v4/private.json \
  --config configs/loop.codex.json --puzzles TS023,TS032,TS033 \
  --repeat 3 --strategies solo,solo_reflect,discuss,independent \
  --workers 3 --out runs/api/my_team_sweep
```

这是 3 题 × 3 次 × 4 条件 = 36 局。host、grader、数据和运行代码在开跑前复制到 runtime_snapshot，并记录 SHA-256；运行中修改仓库不会改变已冻结的实验。每题一个 worker，每题内各条件顺序循环轮换，重复 block 随机执行。三次重复不能完全平衡四个条件在各位置的出现次数，也不能消除模型或题目选择偏差。

| 参数 | 默认值 | 含义 |
| --- | --- | --- |
| `--dataset PATH` | 新实验必填 | 私有 JSON 或 XLSX；开跑前检查所有选题和 host 绑定 |
| `--config PATH` | 新实验必填 | host/player/grader 的配置；凭据通过环境变量或已有 Codex 登录 |
| `--partner-config PATH` | 无，复用 player | 第二位 solver 的单个 profile，冻结保存；可与 player 使用不同模型 |
| `--puzzles IDS` | `TS023,TS032,TS033` | 不重复的逗号分隔题号 |
| `--repeat N` | `3` | 每道题每个条件独立运行次数，正整数 |
| `--strategies LIST` | `solo,solo_reflect,discuss,independent` | 条件列表，必须包含 solo；也支持 alternating |
| `--workers N` | `3` | 同时运行的题目批次数，1–4；不是 agent 数 |
| `--seed N` | `20261023` | 控制调度、条件初始顺序；不控制模型服务端采样 |
| `--out PATH` | 必填 | 新目录；防止覆盖已有真实实验 |
| `--poll-seconds N` | `20` | 每 1–60 秒更新状态、分题报告和 HTML |
| `--dry-run` | 关闭 | 冻结输入并遍历整个计划，但不调用模型、不给性能分数 |
| `--summarize-only` | 关闭 | 读取已有 --out 重建报告，不开模型调用，不恢复未完成局；无需 dataset/config |
| `-h / --help` | — | 显示全部参数 |

输出 `trajectories.html` 包含全部问答、交卷和两份独立提案／合作记录；`results_zh.md` 给出分题分条件完成数、成功数、均值与样本方差。`condition_summary_by_puzzle.json` 记录分题调用与 token 统计，`reflection_contrasts.json` 为相对三调用 solo_reflect 的配对差异。`progress.json`、`exit_codes.json`、`validation.json` 区分尚未运行、正在运行、失败和完成；未完成条件不填零分。历史八局试跑不混入新批次统计。

如果任一题目批次发生基础设施错误，停止启动新批次；已经启动的其他题目继续并保存结果。该题未执行的后续条件保留为未运行；不会重采样失败答案或假装完成。Ctrl-C 会向本 launcher 启动的 worker 发出中断并有界清理。修复后使用新的输出目录重跑并保留失败记录；目前没有自动续跑。

```sh
python3 scripts/team_sweep.py --out runs/api/my_team_sweep --summarize-only
```

错误／不完整交卷计一次，100 次内最后一次强制 final。统计同时保留完整成功率、最终 partial score、预算消耗、仅成功局问题数、模型调用、token 和时间。100 次失败是预算截尾，不能写成“解题用了 100 问”；同样三次调用也不意味着相同 token 成本。


当前 host 的独立核验、grader 的证据覆盖与格式修复、额外调用成本、回归命令见 [host v5.1 修复说明](host_repair_v5.md)。新实验使用 v3 数据；原 runtime_snapshot 不受仓库修改影响。

## 2026-10-24: shared buffer and audited boundaries

New trials use v4 data and `configs/loop.codex.json`: host/grader `gpt-6.1-sol`, player/partner `gpt-6-luna`, all reasoning high. The complete 100-submission limit remains unchanged. This is requested model configuration; CLI responses do not independently attest model identity.

```sh
python3 scripts/team_sweep.py --dataset data/annotations/turtle50_v4/private.json \
  --config configs/loop.codex.json --puzzles TS023,TS036 \
  --strategies solo,independent,shared_buffer --sync-interval 4 \
  --repeat 3 --workers 2 --seed 20261024 --out runs/api/team_v6
```

This is 18 games. Three conditions and three repeats fully balance condition positions per puzzle. Seeds affect ordering only. Three repeats do not eliminate bias. `shared_buffer` uses one solver call per submission, like solo; `independent` uses three and must not be called a compute-matched comparison.

`--sync-interval N` defaults to 4 and must be positive. It counts **completed submissions**, including rejected finals. A and B alternate submissions: A investigates identities, setting and causal sequence; B tests premises, alternatives and missing causal links. Before synchronization each sees the shared prefix plus its own subsequent answered turns, not the other agent's new observations. At synchronization both see all answered turns. The mandatory last submission forces a final synchronization. Buffers contain only submitted questions/answers and four-label feedback, never hidden truth, grades or reasoning. Exact visibility is covered by offline tests. `shared_buffer.jsonl` records each publication state. There is no merger in this condition.

`independent` now selects exactly one of the two candidate actions. If the selector rewrites it, the controller records `selection_override` and uses a candidate verbatim (prefer a question before the forced final; rotate eligible candidates by turn). This prevents new qualifiers from being inserted at the merge step. It does not guarantee the candidates themselves are good. Historical independent results used rewriting and must remain separately versioned.

Host reminders cover false crews/performances, plan versus execution, living persons versus remains, source consistency and incidental unknowns. Player reminders cover excluded branches and rejection loops. Grading reminders plus `half_credit_requires` enforce specified half-credit gates. Model semantic coverage judgments still require review; passing regression tests is not a population accuracy estimate.

A `superseded.json` sidecar marks replaced placeholder games in reports without altering raw trajectories. They are not running or completed observations.

完成后检查完整轨迹：

```sh
python3 scripts/audit_sweep.py --root runs/api/team_v6 \
  --out runs/api/team_v6_review --semantic-config configs/loop.codex.json
```

`--only-game` 可选，精确指定单局相对目录（如 `batches/TS023/TS023_r01_solo`），便于每局完成后立即审核。`--root` 是实验根目录；`--out` 必须是新目录。省略可选的 `--semantic-config` 只检查计数、预算、重复提交、host 分歧和选择器拦截。指定后，配置中的 host 对每个完成局额外调用一次，读取私有汤底、完整问答、双方合作记录和评分，输出带轮次依据的 AI 审核；这不是人工正确率评估。失败的审核调用保留错误，不重抽样。输出 `audit.json`、`audit.html`、`summary.json` 和私有审计调用记录。模型 ID、prompt 与每局请求都保留。只处理已完成且未被替代的局，不给未完成局补零分。

`check_grader.py` 的 expected 还支持 `checkpoint_credits` 对象，例如 `{"C1":0,"C2":0}`，用于检查具体半分门槛，而不混入其他评分项的波动。预期值不会传给模型。

指标解释：维持完整叙事的严格成功标准，不把“核心猜到”当作已通关。逐项 fact_coverage、requirement_coverage 和 checkpoint 分数均保留在 trajectory 的私有评分里，供分析核心解释与叙事细节的差别；没有额外引入一个未经人工定义的“核心机制成功率”。

CL 额度回归：使用真实控制循环与离线模型替身，分别让 A 首次成功、A 耗尽100次；验证 direct/transcript/card 三种 B 各执行完整100次（98个普通问题＋2个被拒交卷），第100次强制 final。这验证基础设施，不属于模型性能实验。每局预算取 `max_questions`，当前实验配置为100；A→B 的迁移和摘要调用不扣除 B 的额度。
