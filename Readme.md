# GoodTurtle — COMP1110

**同事运行入口：[从 clone 到实验的完整指南](docs/coworker_quickstart.md)**。Git 已包含完整 50 题、partial score 标注和所需 host packs；无需另取数据包，配置自己的模型账号即可运行。指南覆盖模型配置、所有 sweep 参数、CL、报告和后台运行。


2026-10-23 追加：已加入多题重复双 agent 实验入口，冻结 host／rubric／代码快照，按题统计均值与方差，并提供三调用的单 agent 对照及独立提案合并策略。

```sh
python3 scripts/team_sweep.py --dataset data/annotations/turtle50_v4/private.json \
  --config configs/loop.codex.json --puzzles TS023,TS032,TS033 \
  --repeat 3 --strategies solo,solo_reflect,discuss,independent \
  --workers 3 --out runs/api/my_team_sweep
```

共 36 局；加 `--dry-run` 零模型调用预检。打开输出目录的 `trajectories.html` 看全部轨迹，`results_zh.md` 看分题结果；每 20 秒更新一次，刷新文件即可看到新记录。[全部参数、策略差异及异常处理](docs/experiment_pipelines.md#多题重复实验冻结快照并发与完整轨迹)。完整题库与最终标注已入库；标注仍为 AI 审核待人工确认。

研究海龟汤中的经验迁移与双 agent 合作。当前提供 **50 道英文题目**、评分标注和可配置的 host／player 实验框架。

## 三方审核后的当前版本（2026-10-23）

当前运行数据为 `data/annotations/turtle50_v4/private.json`：50 题、161 个评分点，权重沿用已与原 XLSX 对比并经过三方 AI 复核的 v2。v3 增加逐事实证据覆盖、TS023 评分边界和 host 修复；**仍是 AI 标注，尚未人工确认**。运行新实验请用 v3；复现旧实验使用原始 runtime_snapshot，不混合新旧分数。

当前全部 50 题都绑定专属资料。其中新增 35 题的示例是来源事实、否定问法和无关细节的基础覆盖，不能当作真实模型准确率验证。新 host 用同一配置模型独立回答两次，分歧时再裁决一次，只向 player 返回一个四标签答案；内部调用不增加问题数。grader 逐项列证据，控制器限制遗漏/矛盾下的分数和通关。参见 [修复说明与运行成本](docs/host_repair_v5.md)。

[评分／host 审核总入口](runs/api/20261023_three_review/index.html) · [50 题评分对照](runs/api/20261023_three_review/partial_score_review.html) · [最新单文件 trajectory](runs/api/20261023_three_review_rerun/trajectories.html)。这些原始审核过程和运行记录仍在本地；已发布的最终标注可直接查看 [逐题评分文档](data/annotations/turtle50_v3/review.md)。

运行后可重新生成单文件轨迹：

```sh
python3 scripts/render_trajectories.py runs/api/20261023_three_review_rerun
```

全部参数：`directory` 为必填实验根目录（含 `positive` / `negative` / `team` 子目录）；`--out` 为可选 HTML 输出路径，默认 `directory/trajectories.html`；`-h / --help` 查看帮助。HTML 内嵌完整提交、反馈、私有评分、A 的转移经验及合作讨论，无外部资源依赖；运行中可重复生成并刷新查看。它是人工审核文件，包含汤底，不应发送给 player。

## 新增：跨题经验迁移与双 agent（2026-10-22）

入口 `python3 scripts/experiment.py`；完整实验设计、全部 CLI 参数与结果解读见 [实验 pipeline 指南](docs/experiment_pipelines.md)。

若使用当前已登录的 Codex 账号，将 `--config` 改为 `configs/loop.codex.json`，无需 API key；从下一批新实验起，host 与复用其配置的 grader 使用 `gpt-6.1-sol`，player 使用 `gpt-6-luna`，均为 reasoning `high`。已启动批次保留各自冻结配置。该 backend 的独立参数与隔离方式见实验指南。

```sh
# 先配置 OPENAI_API_KEY / OPENAI_MODEL，或更换现有 API 配置。
# A→B 对比直接 B；默认只传 A 的公开轨迹，不揭示标准答案。
python3 scripts/experiment.py continual --dataset data/annotations/turtle50_v4/private.json \
  --config configs/loop.openai.json --group G07 --repeat 3

# 单人、轮流合作、双人讨论、自我审查四条件对比。
python3 scripts/experiment.py team --dataset data/annotations/turtle50_v4/private.json \
  --config configs/loop.openai.json --puzzle TS002,TS031 --repeat 3
```

加 `--dry-run` 可不调用 API。每局继续执行四标签、失败交卷计数和最多 100 次提交规则；内部讨论另记调用/token 消耗。每次运行生成配对差异、均值/方差、轨迹和合作过程。本版 continual learning 指上下文经验迁移，没有模型权重更新。

[50 题评分阅读版](data/annotations/turtle50_v3/review.md) 为每题列出完整解答清单及满分／半分／零分条件，共 161 个评分点；[运行数据](data/annotations/turtle50_v4/private.json) 已随仓库发布。新增 TS040 有来源记录，原 XLSX 未改写，标注均待人工审核。[关系组配置](configs/transfer_groups.json) 保存 28 个组的题号与关系假设。

2026-10-23 已修正 host 接入：通过 `configs/host_bindings.json` 按题目 ID 与汤面／汤底 SHA-256 绑定专属资料，橡皮和 pillow 复用旧资料并应用四标签修订；窗户题、火警题补充专属案例。host 与 grader 读取同一个 `host_context.json` 私有快照，player 不可见。绑定的原文变化或资料文件缺失会报错，不会静默串题或退回空示例。目前共 15 题有专属案例（含新增 TS009、TS037、TS048），其余题使用原文与已有完成清单；所有新增标签仍待人工审核。详见 [host 修正与回归方法](docs/host_repair_v2.md)。

已完成本地 GPT-6 Luna 小规模试跑：[中文结果](runs/api/20261022_codex_rerun/results_zh.md)、[完整轨迹入口](runs/api/20261022_codex_rerun/index.html)、[审核疑点](runs/api/20261022_codex_rerun/audit_notes.md)。原 20 局计划因 host／评分一致性问题缩减为 8 局；每条件仅一次，不能估计样本方差。这些本地运行资料位于 Git 忽略的 `runs/api/`。

可从已有记录重建试跑汇总（不调用模型）：

```sh
python3 scripts/summarize_pilot.py runs/api/20261022_codex_rerun
```

`scripts/summarize_pilot.py` 的全部参数：`directory` 为必填位置参数，指向包含 `positive`、`negative`、`team` 中一个或多个实验子目录的根目录，读取其中的计划、运行明细、结果及轨迹；`-h / --help` 显示帮助。它重写该目录的 `summary.md`、`pilot_summary.json`、`submission_scores.csv` 和 `index.html`，保留原始轨迹与评分；存在 `scope_amendment.json` 时同时展示调整后的试跑范围。

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
| [loop.openai.json](configs/loop.openai.json) | OpenAI / OpenAI / 复用 host 配置 | `OPENAI_MODEL` | `OPENAI_API_KEY` |
| [loop.deepseek.json](configs/loop.deepseek.json) | DeepSeek / DeepSeek / 复用 host 配置 | `DEEPSEEK_MODEL` | `DEEPSEEK_API_KEY` |
| [loop.claude.json](configs/loop.claude.json) | Claude / Claude / 复用 host 配置 | `ANTHROPIC_MODEL` | `ANTHROPIC_API_KEY` |
| [loop.mixed.json](configs/loop.mixed.json) | OpenAI / DeepSeek / Claude | `HOST_MODEL`、`PLAYER_MODEL`、`GRADER_MODEL` | `OPENAI_API_KEY`、`DEEPSEEK_API_KEY`、`ANTHROPIC_API_KEY` |

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

顶层仅允许以下四个字段，拼错或添加其他字段会报错：

| 字段 | 类型 / 默认值 | 含义 |
| --- | --- | --- |
| `max_questions` | 整数，默认 `100`，范围 `1..100` | 普通问题与失败交卷的计数预算；最后一个名额必须交卷。设置为 1 时第一条就必须最终提交。 |
| `host` | 模型配置对象，必填（或 CLI 提供） | 普通问题的四标签主持模型。 |
| `player` | 模型配置对象，必填（或 CLI 提供） | 提问并提交完整故事的模型。 |
| `grader` | 模型配置对象或字符串 `"host"`；默认 `"host"` | 私有答案评估模型；默认复用 host 参数。 |

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

三个角色分别使用 [host prompt](prompts/loop_host_v1.txt)、[player prompt](prompts/loop_player_v1.txt)、[grader prompt](prompts/loop_grader_v1.txt)。host 根据当前题的统一私有事实、专属示例（如已配置）和公开历史回答；grader 使用同一事实快照与评分规则；player 只看汤面、自己的提交和四标签反馈。每次调用重传完整可见历史，不继续供应商私有 reasoning 状态，不使用工具。表格没有逐题经过审核的大量问答示例，新 loop 不能据此声称已经达到高准确性。

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

目前完成离线模拟、模拟 HTTP 接口及计数/评分/日志测试；**尚未使用真实账号完成三家 API 的付费端到端验证**。模型和配置不会因出错自动替换。进一步的数据说明与历史实现区别见 [API loop 指南](docs/api_loop.md)。

## 历史原型交付与状态

旧版只发布 eraser／pillow；2026-10-23 用户已授权完整 50 题及最终标注入库。`data/release_scope.json` 的 loop_puzzle_ids 记录当前范围，puzzle_ids 则保留旧 prepare.py 的两题 ID，以兼容历史流程。其他未纳入这 50 题的研究候选仍留本地。历史 `runs/` 和文档仍按批准范围完整归档，可能包含其他题目。当前新建 host 仅加载该题专属示例；复现旧实验使用各 run 冻结上下文中的原始共享示例，不用新配置替换。

- [Host system prompt](prompts/host_system.txt)：v0.5.1 三标签协议，仅输出 `yes` / `no` / `yes and no`，按汤底中的实际用途判定。
- 历史共享示例库：6 个独立小故事、52 条标注示例，冻结副本保存在历史 run；本次不发布独立 `data/host_examples.json`。
- [20 道英文候选题](docs/candidate_review.md)：方便组员审题的版本，**包含答案**。
- 结构化发布资料：[eraser](data/host_packs/USER_ERASER_001.json)、[pillow](data/host_packs/USER_PILLOW_001.json)；原 20 题候选 JSON 不在本次发布范围。
- [执行与验收细则](docs/protocol.md)：host 校准、难度筛选、数据隔离与日志要求。
- `python3 scripts/prepare.py host USER_ERASER_001`：加载橡皮题的 20 条专属示例。
- `python3 scripts/prepare.py validate`：检查数据结构。
- `python3 scripts/prepare.py export`：导出仅含 ID 和英文汤面的 `data/public/puzzles.jsonl`。
- `python3 scripts/prepare.py host USER_PILLOW_001`：加载枕头题的 80 条专属示例，输出 host 消息模板（含秘密答案，不可交给 solver）。

**这些是 prompt / 数据原型，不是已经上线的模型服务。已通过指定模型子 agent 完成橡皮题试跑与复测，并完成枕头题三次严格叙事测试（见下方链接）；20 道候选仍未经过模型难度测试、人工双审或原创性查重，不能声称已满足“当前模型不容易解出”。** 英文故事为本次 AI 辅助新写草稿，未搬运公开题目；这不保证其机制从未出现过。

## Host 配置更新（2026-10-08）

[当前三标签与通用语义规则](docs/host_v05.md)。输出严格限定为 `yes`、`no`、`yes and no`，小写且不带解释；核心用途错误判 `no`，完整正确猜测可判 `yes`。部分正确、信息未定或无法明确二分的情况使用 `yes and no`，不能据此推断猜测一定有正确部分。

[橡皮题专属资料包](data/host_packs/USER_ERASER_001.json)已接入当前 host，包含 20 条待人工确认问答。每题可以有不同的大量专属示例；统一规则保持相同。新标签尚待人工确认，**模型复测记录已保存在 runs/，host 语义准确性仍待人工审核**。旧局输入、旧版协议、轨迹和审核表保留原样；v0.2 文档和开发数据仅作历史记录。

## 枕头题三次试跑（2026-10-08）

[本题 host 资料](data/host_packs/USER_PILLOW_001.json)包含 80 条专属示例。历史实验另配 52 条共享示例，完整输入保存在各局快照；当前发布配置只加载专属示例。使用用户确认的安检汤面，完整叙事评分，严格区分 hand/arm。

[三次结果与审核入口](runs/2026-10-08_pillow_repeats_summary/summary.md)：提问数 48、48、49；均值 48.3333，总体方差 0.2222，样本方差 0.3333。三次均用完 50 次总提交，完整解出 0/3，不能把实际消耗解释为成功解题所需问题数。资料包与 host 存在待审边界，见 [审核疑点](runs/2026-10-08_pillow_repeats_summary/audit_notes.md)，当前不能声称 host 已达到高准确性。每局保留冻结输入、原始轨迹、交卷评分和空白人工审核表。

## 不限次数的新三局（2026-10-09，已按用户要求暂停）

按最新要求取消提问与总提交上限，错误交卷继续，仍须还原全部叙事并严格区分 hand/arm。[新实验与合并轨迹](runs/2026-10-09_pillow_unlimited_summary/summary.md)。旧有预算试跑保留，不能混作相同停止条件的样本。详情见 [协议第九节](docs/protocol.md)。

暂停时按“普通问题＋错误交卷”计数为 **169、166、173**，三局均恢复手作枕头的核心机制，但未完整还原叙事。第三局最后一个问题已保存、尚未发送给 host；需要用户明确恢复后才继续。当前数值是暂停时消耗，不是成功所需问题数。

## 非英语来源筛选（2026-10-09）

新增 [6 道日语来源候选及英文转述](docs/nonenglish_candidates.md)，与原有 20 道 AI 草稿分开保存。[本批计数及筛选结果](runs/2026-10-09_nonenglish_screening/summary.md)持续更新。每题实跑一次，只有完整解出前超过 30 问、且 host 无重大错误的题才暂定保留；未完成和 host 污染的局不冒充难题。

另录入用户提供的中文来源题 [CN001：条件](docs/nonenglish_candidates.md#cn001--条件用户新增未试跑)，包含 [60 条专属 host 示例](data/host_packs/CN001.json)。原 sample 中的自杀、主动遗体捐献及女生亲自解剖均未获汤底支持，已按未知事实标注。此题仅在本地研究题库中，尚未试跑，也未加入发布 allowlist。可用 `python3 scripts/prepare.py host CN001 --local` 生成该题 host 消息。

[Host v0.5.1](docs/host_v05.md)统一增加身份/容器、因果关系、时点、信念/事实、上位概念、保证/可能、否定一致性等规则；本批每题配 41–57 条专属示例。先做实际模型校准，再冻结资料运行；这些标签与轨迹仍需人工审核。

## TODO 1 — 搭建并验证 host

目标：host 根据固定汤底稳定回答，不泄漏提示、不补写故事；host 质量不能成为 solver 表现的混杂变量。

- [x] 定义 `yes / no / yes and no` 和异常问题处理。
- [x] 写 system prompt 与独立的 few-shot 示例库，覆盖改写、否定、未知、前提错误、指代、复合问题和指令注入。
- [ ] 选定 host 模型的精确 ID、参数、API 适配器；记录 prompt / examples 版本和哈希。
- [ ] 为最终每题建立约 40–80 条专属问答并人工审核，优先覆盖关键路径、常见错误及措辞边界。共享示例配置作为辅助，不追求跨题泛化。
- [ ] 两人独立审核每题示例，第三人裁决；分别检查示例遵循度与该题新问法的准确性，不以示例回放成绩代替新问法验收。
- [ ] 每题另做 10–20 条新问法及 2 段多轮检查；失败用例可用于修复该题资料，修复后再用新问法复验。见 [准确性验证方案](docs/host_validation.md)。
- [ ] 验收建议（开发期确定后冻结）：准确率 ≥95%、macro-F1 ≥0.90、格式合规率 100%；专门的泄漏/编造用例观察到 0 次失败。报告分母和混淆矩阵，小样本通过不等于总体无误。
- [ ] 接入三标签严格校验、查询计数和日志；非法输出不能偷偷转换成 `yes and no`。服务重试独立计数，不能多次采样择优。
- [ ] 冻结后再做 untouched TurtleBench 外部评价，保留其原始任务及计分约定；本地三标签协议不能直接替换官方标签。

Host 看见：汤面、汤底、事实表、当前题全部专属示例、公开问答、当前问题。Host 不看见：M0–M3 条件、solver 私有讨论、经验卡、评分 rubric。最终解答由独立 grader 评判。

## TODO 2 — 筛出首批 20 道英文题

目标：筛出 **在固定模型和预算下不易快速解出、但能够通过提问合理还原** 的故事。冷门只是降低记忆风险的线索，不能代替难度测量。

- [x] 准备 20 道新写英文候选，每题附答案、事实边界、评分要点与问答路径。
- [ ] 人工审题：英语自然、因果完整、没有自相矛盾、不依赖专业冷知识；替代解答和隐藏规则足够明确；可通过中间问题逐步接近答案。
- [ ] 为每题登记 provenance、复用权限、家族 ID、机制标签、表面标签、语言依赖；当前来源为 AI 辅助草稿，发布权限和重复故事检查待组员确认。
- [ ] 扩充到约 40–60 道候选，以便淘汰后仍有 20 道。若这 20 道只通过 9 道，就报告 9 道，不为凑数放宽标准。
- [ ] 用固定 baseline 模型无记忆、无协作筛选：每题 3 次只看汤面的直接解答；另做 3 次最多 50 次 host 查询的完整游戏，记录首次完整正确解答出现在第几问。
- [ ] 建议初筛规则：直接解答至多 1/3 成功；完整游戏中前 10 问至多 1/3 成功；50 问内至少 1/3 成功。三次只是低成本初筛，边界题追加预先约定的重复，不能据此声称精确成功率。
- [ ] 50 问内 0/3 的题进入人工可解性复核；只有两位独立人类 solver 通过固定 host 在预算内解出，才作为“超难候选”保留，且数量限制在最终题库的少数，避免地板效应。
- [ ] 排除由 host 错答、汤面歧义或不可查询的任意细节造成的“难题”；所有失败、替换、排除原因留档。
- [ ] 冻结首批 20 题与 rubric；再建立独立 source-memory / development 集，solver 的 few-shot 不使用目标题答案；host 可使用该题专属问答。不同翻译、改写、换皮按 story family 整体隔离。

主实验模型筛选会产生 **针对该模型的挑战集**。报告这一选择偏差；冻结后用新会话/新重复评估，不把筛选结果当正式实验结果，也不根据 M1/M2/M3 或协作增益挑题。若最终要概括一般海龟汤能力，需要额外保留未按失败筛选的随机对照题。

## 建议这一周完成的工作

1. 确定模型、host 协议；两人审阅示例标签和首批故事。
2. 并行开展人工 host 标注与补充候选题（人员分工，不要求额外 agent）。
3. 先让 host 通过小规模验证，再运行难度筛选；不可靠 host 的失败不能计为 solver 失败。
4. 冻结候选、筛选规则和预算，导出 solver 版本，形成真实的入选名单。

Proposal 中摄影例子的 `Did she photograph her husband? → No` 应修正为 **Yes**，与 `Did she shoot a photograph of him?` 保持语义一致。否则实验会把自然同义表达误判为探索失败。

## 已核对的外部资源（2026-10-05）

- [LatEval 官方仓库](https://github.com/THUKElab/LatEval)：提供英文数据和 host/player 原型，可作为候选来源与实现参考。
- [SPLAT 官方仓库](https://github.com/chenqi008/LateralThinking)：提供分级 situation puzzles，数据位于 `puzzles.xlsx`；等级需要在本项目模型上重新验证。
- [TurtleBench 官方仓库](https://github.com/mazzzystar/TurtleBench)：本项目用于独立 host 评价，避免与本地题目/示例家族重叠。

本次没有复制这些仓库的题目。若后续导入，逐一核对数据本身的授权、来源与适用范围，不以仓库可访问代替复用许可。

实验输入、历史版本与暂停续接方法见 [复现说明](docs/reproducing_experiments.md)。

2026-10-24：新增共享记录双 agent、严格候选选择和结构化半分门槛；新实验固定 Sol host / Luna player，详见 [v6 修复与验证范围](docs/host_repair_v6.md)。

CL 当前默认在 A 结束后揭示完整标准答案（`--source-feedback answer`），B 独立重置为配置中的100次额度；direct B 不接收 A 信息。摘要卡模式也单独保留完整 A 答案。
