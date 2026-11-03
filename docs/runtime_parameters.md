# 运行方式与完整参数

当前数据入口为 `data/annotations/turtle50_v4/private.json`；当前Host包由 `configs/host_bindings.json` 指向 `data/host_packs/active/`。本页保留原README的完整运行参数表。CL/双agent参数见 [实验指南](experiment_pipelines.md)，v7新增参数优先见 [v7设计](host_repair_v7.md)。

## 四标签 API 对局：运行方式与全部参数

入口是 `python3 scripts/play.py`。一个命令串起 **player 提问 → host 回答 → player 交卷 → grader 评分 → 保存轨迹和统计**。host、player、grader 可以独立选择供应商、模型和 API 地址。需要 **Python 3.10+**，仅使用标准库，无需安装 SDK；以下命令均在仓库根目录执行。

新 loop 使用四标签 `yes / no / yes and no / irrelevant`；下方“历史原型”中的三标签 prompt、旧预算和暂停实验仅用于历史复现。新入口不会自动恢复旧实验。

### 1. 下载后先看离线演示

```sh
git clone https://github.com/aurorajy1108/GoodTurtle.git
cd GoodTurtle
python3 --version
python3 scripts/play.py demo
```

打开终端显示目录中的 `index.html`，点击进入各局 `trajectory.html`。演示包含错误交卷、继续提问和强制最终交卷，全程不调用 API，明确标记为 **simulation，不是模型成绩**。

### 2. 准备数据

**Git 已提供完整 50 题和评分标注**，默认使用 `data/annotations/turtle50_v4/private.json`，无需原 XLSX。下面的导入命令仅用于你自己的额外表格；历史 host pack JSON 不是新 loop 的 dataset 格式。

```sh
# 直接使用仓库内题库；若导入自己的 XLSX，再修改此路径。
export TURTLE_DATASET="data/annotations/turtle50_v4/private.json"
python3 scripts/play.py inspect --dataset "$TURTLE_DATASET"

# 可选：导入目录必须尚不存在。
python3 scripts/play.py import --dataset "$TURTLE_DATASET" --out data/imported/my_dataset
```

导入生成 `private.json`（完整题目、答案和 rubric）、`public.jsonl`（仅 ID 和汤面）、`audit.json`（数据质量概览）。之后可用 `--dataset data/imported/my_dataset/private.json` 替代 XLSX。`public.jsonl` 不包含主持和评分所需信息，不能用于 `run`。

XLSX 读取 `逐题标注` 的 `puzzle_id / problem / answer` 和 `Partial Rubric` 的 `Puzzle ID / Checkpoint / 权重 (0–1) / English scoring criterion`，保留 family、质量标记等元数据，不执行表格公式或指令。当前表格是 49 题、161 个 checkpoints，ID 为 TS001–TS050（没有 TS040）；每题权重合计 1。部分题存在多解、同汤面或待复核标记，导入成功不等于通过质量验收。

### 3. 配置模型并启动

以 OpenAI 为例，将占位值换成自己的 key 和账号支持的**准确 API 模型 ID**：

```sh
export OPENAI_API_KEY='替换为你的 API key'
export OPENAI_MODEL='替换为你的 API 模型 ID'

# 先预检：不调用模型、不产生分数。
python3 scripts/play.py run --dataset "$TURTLE_DATASET" \
  --config configs/loop.openai.json --puzzle TS002 --dry-run

# 同一题独立运行三次。
python3 scripts/play.py run --dataset "$TURTLE_DATASET" \
  --config configs/loop.openai.json --puzzle TS002 --repeat 3

# 全部题各跑三次，串行运行；这会产生实际 API 费用。
python3 scripts/play.py run --dataset "$TURTLE_DATASET" \
  --config configs/loop.openai.json --puzzle all --repeat 3
```

无需设置输出路径，程序自动创建独立 batch 目录。真实运行前验证三个角色的配置和 key 是否存在；模型是否有权限、参数是否被供应商支持，要到实际请求时才能确认。程序不自动读取 `.env` 文件，请在启动它的终端中 `export` 环境变量。

| 配置模板 | host / player / grader | 必须设置的模型环境变量 | 默认 key 环境变量 |
| --- | --- | --- | --- |
| [loop.openai.json](../configs/loop.openai.json) | OpenAI / OpenAI / 复用 host 配置 | `OPENAI_MODEL` | `OPENAI_API_KEY` |
| [loop.deepseek.json](../configs/loop.deepseek.json) | DeepSeek / DeepSeek / 复用 host 配置 | `DEEPSEEK_MODEL` | `DEEPSEEK_API_KEY` |
| [loop.claude.json](../configs/loop.claude.json) | Claude / Claude / 复用 host 配置 | `ANTHROPIC_MODEL` | `ANTHROPIC_API_KEY` |
| [loop.mixed.json](../configs/loop.mixed.json) | OpenAI / DeepSeek / Claude | `HOST_MODEL`、`PLAYER_MODEL`、`GRADER_MODEL` | `OPENAI_API_KEY`、`DEEPSEEK_API_KEY`、`ANTHROPIC_API_KEY` |

DeepSeek、Claude 的运行命令只需换 `--config`，并设置表中对应环境变量。混合模板示例：

```sh
export OPENAI_API_KEY='替换为 OpenAI key'
export DEEPSEEK_API_KEY='替换为 DeepSeek key'
export ANTHROPIC_API_KEY='替换为 Anthropic key'
export HOST_MODEL='替换为 OpenAI API 模型 ID'
export PLAYER_MODEL='替换为 DeepSeek API 模型 ID'
export GRADER_MODEL='替换为 Claude API 模型 ID'
python3 scripts/play.py run --dataset "$TURTLE_DATASET" \
  --config configs/loop.mixed.json --puzzle TS001,TS002 --repeat 3
```

也可不使用配置文件，直接指定角色；此时预算默认 100，其余参数使用默认值：

```sh
python3 scripts/play.py run --dataset "$TURTLE_DATASET" \
  --host "openai:$HOST_MODEL" --player "deepseek:$PLAYER_MODEL" \
  --grader "anthropic:$GRADER_MODEL" --puzzle TS002
```

### 4. 全部命令行参数

所有命令都支持 `-h / --help`，显示帮助并退出，不执行实验。例如 `python3 scripts/play.py run --help`。下表覆盖 `scripts/play.py` 的全部子命令与选项；配置文件字段另见下一节。

| 子命令 | 用途 | 参数 |
| --- | --- | --- |
| `inspect` | 读取并输出数据概览，不调用 API | `--dataset PATH` 必填，XLSX 或已导入的私有 JSON |
| `import` | 生成 private/public/audit 三份数据 | `--dataset PATH` 必填，同上；`--out DIR` 必填，新的导入目录 |
| `demo` | 离线脚本演示，不使用真实模型 | `--out DIR` 可选；默认 `runs/api/demo_<UUID8>/`，目录必须尚不存在 |
| `run` | API 对局，或冻结输入预检 | 完整参数如下表 |

| `run` 参数 | 必填 / 默认值 | 含义、取值和示例 |
| --- | --- | --- |
| `--dataset PATH` | 必填 | `.xlsx` 或 importer 生成的 schema v1 私有 `.json`；路径相对当前工作目录解析。不是 public JSONL 或旧 host pack。 |
| `--puzzle IDS` | 默认 `TS002` | 单个 ID、逗号分隔的多个 ID，或 `all`。如 `TS001,TS002`，逗号两侧不要加空格；重复或不存在的 ID 报错。 |
| `--config PATH` | 可选，无默认文件 | JSON 实验配置路径。省略时必须提供 `--host` 和 `--player`；不会自动加载 configs 目录。 |
| `--host PROVIDER:MODEL` | 可选，使用配置中的 host | 覆盖 host 整份配置，如 `openai:YOUR_MODEL_ID`。未通过任何方式配置 host 则报错。 |
| `--player PROVIDER:MODEL` | 可选，使用配置中的 player | 覆盖 player 整份配置，如 `deepseek:YOUR_MODEL_ID`。未配置则报错。 |
| `--grader PROVIDER:MODEL` | 可选，使用配置中的 grader，否则复用 host 配置 | 覆盖 grader 整份配置，如 `anthropic:YOUR_MODEL_ID`。复用模型配置仍是独立评分请求，不共享评分上下文给 player。 |
| `--repeat N` | 默认 `1` | 正整数，每个所选题运行 N 次。按题目、重复序号串行运行，每局重新开始，不继承上一局对话。 |
| `--out DIR` | 可选 | 新 batch 目录；默认仓库内 `runs/api/<UTC时间>_<UUID8>/`。已有目录会报错，不覆盖也不续跑。 |
| `--dry-run` | 默认关闭 | 不调用模型、不要求 API key；冻结配置、prompt 和题目，生成空轨迹/统计，分数为 null。配置中的 `${MODEL_ENV}` 仍须能解析；不验证远程模型权限。 |
| `--quiet` | 默认关闭 | 关闭终端逐轮对话和逐局 trajectory 路径提示；仍显示输出目录与逐局摘要，所有日志照常保存。 |

**CLI 角色覆盖是整份替换，不是合并**：`--host openai:MODEL` 会将该角色设为 provider/model/max_output_tokens=4096，原来的自定义 `base_url`、`api_key_env`、`extra_body`、`temperature`、`timeout`、`max_retries` 均不保留。需要自定义参数时，编辑 JSON 中的该角色。grader 省略或为 `"host"` 时，在 CLI 覆盖之后复制 host 配置。

不存在 `--max-questions`、`--temperature`、`--api-key` 或 `--resume` 参数；预算和模型选项通过 JSON 设置。

### 5. JSON 实验配置：全部字段

顶层允许以下字段，拼错或添加其他字段会报错：

| 字段 | 类型 / 默认值 | 含义 |
| --- | --- | --- |
| `max_questions` | 整数，默认 `100`，范围 `1..100` | 普通问题与失败交卷的计数预算；最后一个名额必须交卷。设置为 1 时第一条就必须最终提交。 |
| `host` | 模型配置对象，必填（或 CLI 提供） | 普通问题的四标签主持模型。 |
| `player` | 模型配置对象，必填（或 CLI 提供） | 提问并提交完整故事的模型。 |
| `grader` | 模型配置对象或字符串 `"host"`；默认 `"host"` | 私有答案评估模型；默认复用 host 参数。 |
| `pricing` | 可选对象 | 自定义估算费率；见[费用字段](study_20261102.md#token-与费用记录自动启用)。 |
| `context_policy` | 可选对象 | 本地参考检索预算，字段见下表；所有供应商通用。 |
| `session_mode` | 字符串，默认 `"persistent"` | 每局角色隔离持续会话；`"replay"` 每次独立重放，用于对照。Codex显式thread续聊，Responses用previous_response_id，其余供应商本地多轮messages。persistent中断不自动恢复或降级。 |

`codex_cli`角色配置支持 `provider`、`model`、`reasoning_effort`（默认high）、`timeout`（默认240秒，范围1–600）、
`max_retries`（默认2，整数0–5）和 `usage_scope`（默认 `thread_total`；可设 `turn`）。
本机CLI 0.154.0续聊返回thread累计usage，所以每次按同一lane的前后差值记账；原累计量、baseline和
有效每轮usage同时归档。若所用CLI明确改为逐轮usage，须显式设置 `usage_scope: turn`，不能凭单轮大小猜测。
计数倒退或baseline字段缺失时费用标未知，不套零值。该参数不适用于HTTP供应商。

| `context_policy` 字段 | 默认值 / 范围 | 含义 |
| --- | --- | --- |
| `host_examples_limit` | 6 / 整数 0–20 | 每问最多6条相关参考，0禁用示例 |
| `grader_examples_limit` | 3 / 整数 0–20 | 每次交卷最多3条相关判例 |
| `host_examples_max_chars` | 6000 / 整数 0–50000 | Host参考列表JSON字符预算，不是token数；0禁用示例 |
| `grader_examples_max_chars` | 3000 / 整数 0–50000 | Grader参考列表JSON字符预算；0禁用示例 |

仅在本题已绑定的参考中本地检索，数量与字符双限制；过长案例整条跳过并记录。
普通问题固定一次Host判断，不能通过旧题包的 `verification_policy` 恢复多次复核。
完整汤底及当前对话历史不受以上参考预算裁剪。参见[具体设计](study_20261102.md#11月3日参考检索与精简评分上下文)。

host / player / grader 对象均仅允许下列九个字段：

| 字段 | 类型 / 默认值 | 含义与限制 |
| --- | --- | --- |
| `provider` | 字符串，必填 | `openai`、`openai_chat`、`deepseek`、`anthropic`、`openai_compatible` 之一，决定请求和响应格式。 |
| `model` | 非空字符串，必填 | 供应商认可的精确模型 ID；可写 `${HOST_MODEL}` 等环境变量占位符。Codex 子 agent 名称不一定是 API 模型 ID。 |
| `base_url` | 字符串，按 provider 默认 | API 基础路径，见下表；不要添加 `/responses`、`/messages` 或 `/chat/completions`。远程必须 HTTPS；HTTP 只接受 localhost、127.0.0.1、::1。不允许 URL 内包含用户名、密码、query 或 fragment。 |
| `api_key_env` | 字符串，按 provider 默认 | 保存 key 的**环境变量名**，例如 `MY_GATEWAY_KEY`，不是 key 本身。变量名必须符合 `[A-Za-z_][A-Za-z0-9_]*`；真实运行时读取其值。 |
| `max_output_tokens` | 正整数，默认 `4096` | 单次响应 token 上限，和问题数量无关。按接口映射到对应字段；实际可用范围由模型限制，推理 token 也可能占预算。截断不会自动增大或重新采样。 |
| `temperature` | 可选，默认不发送 | 原样传递采样温度；支持情况和数值范围由模型/API 决定，程序不做范围转换。若 extra_body 中也有同名值，以此字段为准。 |
| `extra_body` | JSON 对象，默认 `{}` | 供应商特定请求参数，例如兼容模型的 reasoning/thinking 选项。没有跨供应商自动转换，不支持的参数会报 API 错误；保留字段不能覆盖，见下文。 |
| `timeout` | 数字，默认 `120` 秒，`0 < 值 <= 600` | 每次 HTTP 尝试的超时，不是整局时间上限。 |
| `max_retries` | 整数，默认 `2`，范围 `0..5` | 网络错误、HTTP 429/5xx 的额外重试次数，总尝试最多 1+此值。退避等待依次 1、2、4、8、8 秒。格式错误、拒答、截断不重新采样；重试不增加玩家问题数。 |

| provider | 默认 base_url | 自动追加的 endpoint | 默认 api_key_env | 输出 token 字段 |
| --- | --- | --- | --- | --- |
| `openai` | `https://api.openai.com/v1` | `/responses` | `OPENAI_API_KEY` | `max_output_tokens` |
| `openai_chat` | `https://api.openai.com/v1` | `/chat/completions` | `OPENAI_API_KEY` | `max_completion_tokens` |
| `deepseek` | `https://api.deepseek.com` | `/chat/completions` | `DEEPSEEK_API_KEY` | `max_tokens` |
| `anthropic` | `https://api.anthropic.com/v1` | `/messages` | `ANTHROPIC_API_KEY` | `max_tokens` |
| `openai_compatible` | `https://api.openai.com/v1`，第三方网关需自行修改 | `/chat/completions` | `OPENAI_API_KEY`，可自定义 | `max_tokens` |

选择 provider 看**实际接口格式**：通过 OpenAI-compatible 网关调用 Claude 时使用 `openai_compatible`；原生 Anthropic API 才使用 `anthropic`。未实现 Bedrock、Vertex、OAuth 或其他云厂商专有认证。所有请求关闭 stream；OpenAI Responses 设置 `store=false`。

包含全部配置字段的示例（自行保存为 JSON；temperature/reasoning 是否支持须与所选模型核对，不支持时删除）：

```json
{
  "max_questions": 100,
  "host": {
    "provider": "openai",
    "model": "${HOST_MODEL}",
    "base_url": "https://api.openai.com/v1",
    "api_key_env": "OPENAI_API_KEY",
    "max_output_tokens": 8192,
    "temperature": 1,
    "extra_body": {"reasoning": {"effort": "high"}},
    "timeout": 120,
    "max_retries": 2
  },
  "player": {
    "provider": "deepseek",
    "model": "${PLAYER_MODEL}",
    "max_output_tokens": 4096
  },
  "grader": "host"
}
```

配置字符串中的 `${VARIABLE}` 会递归替换，变量不存在或为空时报错（包括 dry-run）。模型可以直接写 ID，就不必设置对应模型环境变量。密钥只通过 `api_key_env` 指定变量名；不要将 `${API_KEY}` 嵌进配置或额外请求体，配置会随实验保存。

`extra_body` 禁止覆盖的全部字段：`model`、`messages`、`input`、`instructions`、`system`、`tools`、`tool_choice`、`stream`、`store`、`previous_response_id`、`conversation`、`api_key`、`authorization`、`headers`、`max_tokens`、`max_completion_tokens`、`max_output_tokens`。这些值由 loop 管理；未列出的参数也必须符合目标供应商规范。

### 6. Host、提交和计分规则

三个角色分别使用 [host prompt](../prompts/loop_host_v1.txt)、[player prompt](../prompts/loop_player_v1.txt)、[grader prompt](../prompts/loop_grader_v1.txt)。host 根据当前题的统一私有事实、检索示例和公开历史回答；grader 使用精简事实视图与完整评分规则；player 只看授权的公开材料。默认每局持续独立角色会话，以增量更新上下文；`replay`可作对照，不使用工具。持续会话并不免除历史计费，也不能保证评分不受先前答案锚定；[设计与限制](study_20261102.md#持续会话隔离和对照)说明具体边界。

普通问题由 host 输出一个标签；交卷由 grader 私下评分，再由程序生成相同四标签之一。player **看不到得分、缺失项或解释**。player 的响应协议为 `{"type":"question","text":"..."}` 或 `{"type":"final","text":"..."}`，最终答案应在一次 final 中写完整；非法格式保留日志并报错。

| 反馈 | 普通问题 | 交卷 |
| --- | --- | --- |
| `yes` | 故事支持该判断 | 完整解出 |
| `no` | 事实、身份、机制或因果错误 | 未取得 checkpoint 得分且不属于无关提交/评分冲突 |
| `yes and no` | 混合判断、相关事实未指定或必要歧义 | 有部分得分但尚未完整解出，或存在 rubric 冲突 |
| `irrelevant` | 与解题无关 | 无关交卷 |

计数口径固定为 `counted_questions = host_questions + rejected_finals`。普通提问加 1，错误/不完整交卷也加 1，并继续游戏；正确交卷单独记入总提交数 `submissions`。**达到 99 次计数后，第 100 次总提交必须是 final**：答错计数 100 并结束，答对计数 99、总提交 100；第一条直接答对则计数 0、总提交 1。模型不遵守强制交卷要求时记 protocol error，不伪造答案。调低 `max_questions` 时同样保留最后一个名额。

每次 final 按表格 checkpoints 单独评估：`partial_score = Σ(weight × credit)`，credit 只允许 `0 / 0.5 / 1`，总分由程序计算。`final_partial_score` 是最近一次交卷得分，`best_partial_score` 是单次最高分，不累加不同交卷的内容。没有交卷或最后交卷尚未完成评分时为 null。**满分不必然是完整成功**：还需要完整参考叙事已还原、所有 checkpoints 满分、无关键矛盾、无 rubric 冲突。评分仍是模型判断，供人工审核；rubric 冲突标记 `needs_review` 并停止该局。

### 7. 轨迹、performance 和审核输出

终端会显示 batch 路径，直接用浏览器打开其中的 `index.html`。逐局 HTML 在运行中每 5 秒刷新，无需启动网页服务。

| 位置 / 文件 | 内容 |
| --- | --- |
| batch / `index.html` | 所有局的导航和状态 |
| batch / `performance.csv` | 每局题号、family、质量标记、计数、提交数、分数、完成情况 |
| batch / `summary.json` | 成功率、问题数均值、总体方差、样本方差和 partial score 汇总；成功局与全部正常完成局分开统计 |
| batch / `batch_config.json` | 实际模型和预算、选题、重复次数、输入及 prompt 哈希 |
| batch / `dataset_audit.json` | 数据集概览和质量标记 |
| 每局 / `trajectory.html`、`trajectory.md`、`trajectory.jsonl` | 可视化、可读文本、逐事件记录；HTML 的私有评价默认折叠 |
| 每局 / `result.json` | host_questions、final_attempts、rejected_finals、counted_questions、submissions、pending_feedback、forced_final、得分、状态、耗时和分角色 usage |
| 每局 / `api_calls.jsonl` | 请求体、模型可见输出、响应 ID、重试、usage；不记录认证 headers 和供应商隐藏 reasoning |
| 每局 / `config.json`、`prompts.json`、`puzzle_private.json` | 冻结该局配置、提示和私有题目 |
| 每局 / `review_template.csv`、`human_review.csv` | 前者运行中更新；后者结束时生成，供人工填写，不覆盖已有人工审核文件 |

成功率分母为正常完成的局（成功或预算耗尽）；`error / interrupted / needs_review` 单列，不伪装成模型失败。问题数同时报告成功局的解题消耗与所有正常完成局的消耗，不能把失败耗尽 100 次说成“100 次解出”。供应商 usage 保留原始口径，不自动换算费用。模拟演示和 dry-run 不作为真实模型性能。

**运行目录包含汤底、rubric 和私有评分，只供研究者审核，不能交给 player。** `/runs/api/` 和新导入数据默认被 Git 忽略；历史归档实验已单独发布，不受新 loop 改写。

### 8. 错误、退出码与验证

Ctrl+C 会保存当前局为 `interrupted`。API 或协议错误会保存为 `error` 并停止剩余 batch；已经发出但尚未完成反馈的提交标记 pending。当前没有半局自动恢复，修复配置后须使用新目录开新实验。`needs_review` 停止当前局，batch 可继续下一局。

| 退出码 | 含义 |
| --- | --- |
| `0` | 命令正常结束；不代表全部解出，预算耗尽或待复核也可能正常返回 |
| `1` | 对局遇到 API / 协议错误 |
| `2` | CLI、输入文件或配置检查错误 |
| `130` | 对局运行中被 Ctrl+C 中断 |

```sh
python3 scripts/play.py --help
python3 scripts/play.py run --help
python3 -m unittest discover -s tests -v
```

目前完成离线模拟、模拟 HTTP 接口及计数/评分/日志测试；**尚未使用真实账号完成三家 API 的付费端到端验证**。模型和配置不会因出错自动替换。进一步的数据说明与历史实现区别见 [API loop 指南](api_loop.md)。
