# 用 DeepSeek 运行全部角色与实验

在仓库根目录执行。选择 `--config configs/loop.deepseek.json` 后，Host、player、grader、默认 MAS partner，以及需要时的反思/选择/经验总结/评分证据修复全部走 DeepSeek HTTP API。无需 Codex 登录或 OpenAI/Anthropic Key，也不会自动回退到 GPT。基础适配器原已支持 DeepSeek；11月7日补齐配置并移除了 study 启动器对 GPT Host 的硬性限制。

## 1. 设置 Key 和模型

在本机终端设置，不把真实 Key 写入 JSON、聊天或 Git。程序不自动读取 `.env`。

```sh
export DEEPSEEK_API_KEY='在本机替换成你的DeepSeek Key'
```

默认按角色分配模型：**Host/grader 使用 `deepseek-v4-pro / high`，player/partner 使用 `deepseek-flash / thinking disabled`**。模型ID在 `configs/loop.deepseek.json` 的各角色 `model` 中独立指定，可分别修改。官方当前列有这两个模型；本配置按研究设计选择Pro承担主持与评分、Flash承担玩家，尚未通过本项目实验证明准确率改善。换模型时核对其是否支持配置中的 thinking/JSON 参数。[官方接口与模型说明](https://api-docs.deepseek.com/quick_start/)

只要求 `DEEPSEEK_API_KEY`；新默认配置无需设置 `DEEPSEEK_MODEL`，已有同名变量不会覆盖各角色模型。Key 通过 `Authorization` 请求头使用，配置和 API 日志不保存认证请求头。真实运行缺少 Key 会在模型调用前报错。

如需恢复三角色共用同一模型，选择 `--config configs/loop.deepseek.same-model.json`，并额外设置 `export DEEPSEEK_MODEL=deepseek-flash`（或其他明确模型ID）。这是独立的同模型对照模板。

## 单人 Player JSON 模式配置

`configs/loop.deepseek.solo-json.json` 保留上述 Host、grader 和 Player 模型与推理设置，同时为 Player 增加 `response_format: {"type": "json_object"}`。适用于单人对局，以及只使用 transcript / answer-only 的 CL；运行方式是将下方命令的 `--config` 换成此文件。API key 仍只从 `DEEPSEEK_API_KEY` 环境变量读取。

此配置会影响所有使用 Player profile 的调用，因此不要直接用于要求纯文本的 CL memory card、`solo_reflect` 或 `discuss` 内部审查。JSON 模式仍可能返回空白、截断或字段不合规，控制器继续验证动作并记录失败。2026-11-08 的 TS035 单人试跑使用了这份角色配置，完整运行至100次提交但未解出；这是一次试跑，不构成可靠性或性能结论。该次运行还使用了当时本地未合并的网络诊断改动；复现需核对运行快照与版本，不要仅凭配置文件推断整个环境相同。

## 2. 先验证配置

本次小规模实验仅保留15作为positive A，不跑16；A=15/14/28，B=13。下面dry-run会冻结代码、题包、模型与计划，生成12局CL和2局TS038空轨迹，不调用API、不收费：

```sh
python3 scripts/study_20261102.py \
  --config configs/loop.deepseek.json \
  --suite all --sets 1 --team-puzzles TS038 \
  --source-puzzles TS015,TS014,TS028 \
  --strategies solo,free_dialogue --repeat 1 \
  --mode dry-run --out runs/api/deepseek_set1_ts038_check
```

可选的6次小请求连通测试（合成记忆任务，不是题目表现；此命令会调用 API）：

```sh
python3 scripts/smoke_sessions.py --config configs/loop.deepseek.json \
  --run --out runs/api/deepseek_session_smoke
```

检查 Host/player/grader 各两轮能否正确续聊。输出模型、usage、缓存与会话日志；不加 `--run` 则只写计划。

## 3. 正式运行

当前按用户要求暂停实验。下列真实运行命令仅供之后明确恢复时使用，更新代码不会自动启动实验。需要恢复小批次时，可在已export Key的终端执行 `bash scripts/start_deepseek_pilot.sh`，后台启动A=15/14/28、B=13及TS038两局，共14局，输出新目录 `runs/api/deepseek_set1_ts038_nothinking_once`。脚本可选第一个参数指定其他新输出目录，拒绝覆盖现有目录。

先跑 CL Set 1 与小规模 MAS：

```sh
python3 scripts/study_20261102.py \
  --config configs/loop.deepseek.json \
  --suite all --sets 1 --team-puzzles TS038 \
  --source-puzzles TS015,TS014,TS028 \
  --strategies solo,free_dialogue --repeat 1 \
  --mode run --out runs/api/deepseek_set1_ts038_once
```

CL固定目标B=13，A=15/14/28各解一次、揭晓完整答案并冻结，比较direct/transcript/answer_only；每局新100次额度。共3局A+9局B=12局CL。MAS只跑solo与free_dialogue各一次，共14局。详细规则见[研究方案](study_20261102.md)。

全部5个 Set + 全部5道 MAS 目标题，每策略重复3次（共198局：CL168 + MAS30）：

```sh
python3 scripts/study_20261102.py \
  --config configs/loop.deepseek.json \
  --suite all --sets all --team-puzzles TS038,TS002,TS014,TS022,TS042 \
  --strategies solo,free_dialogue --repeat 3 \
  --mode run --out runs/api/deepseek_full_study_r3
```

`--suite continual` 只跑CL，`--suite team` 只跑MAS；`--sets` 选CL集合，`--team-puzzles` 选MAS题号。`--repeat` 控制B或团队条件重复数，固定模式不重新解A。`--mode plan` 只生成计划、`dry-run`生成空实验输出、`run`真实调用。`--out`必须是新目录，不能复用已存在的目录。完整入口、方向、额度及共享聊天参数见[研究方案](study_20261102.md)和[MAS参数表](mas_free_dialogue.md)。

单独跑题或50题基线同样可用此配置，例如：

```sh
python3 scripts/play.py run --dataset data/annotations/turtle50_v4/private.json \
  --config configs/loop.deepseek.json --puzzle all --repeat 1 \
  --out runs/api/deepseek_50_solo
```

## 4. 默认参数和持续会话

| 设置 | Host | player / 默认partner | grader |
| --- | --- | --- | --- |
| provider | deepseek | deepseek | deepseek |
| model | deepseek-v4-pro | deepseek-flash | deepseek-v4-pro |
| api_key_env | DEEPSEEK_API_KEY | DEEPSEEK_API_KEY | DEEPSEEK_API_KEY |
| thinking.type | enabled | disabled | enabled |
| reasoning_effort | high | 不发送 | high |
| max_output_tokens | 32768 | 8192 | 32768 |
| timeout（秒） | 600 | 600 | 600 |
| max_retries | 2 | 2 | 2 |
| response_format | 不强制JSON，直接四标签 | 动作自动JSON模式；文本审查/摘要不强制 | json_object |

player/默认partner、显式partner模板、同模型对照中的player及混合模板中的DeepSeek player均已关闭thinking，并删除reasoning_effort；玩家的内部审查和经验总结继承此设置。Host/grader仍开启high推理。

这些参数在 `configs/loop.deepseek.json` 中修改。输出预算是每次调用的上限，包含模型推理及可见输出，不是每次都会用满；到上限而截断会记为错误，不重新采样答案。推理模式不设置 temperature；如果要关闭推理，把相应角色的 `extra_body.thinking.type` 改为 `disabled` 并删除该角色的 `reasoning_effort`。本模板不把原 GPT 的 medium 直接等同为 DeepSeek medium：官方当前将 medium 映射为 high，因此明确写 high。记录并单独比较模型/推理配置不同的批次。[官方推理参数说明](https://api-docs.deepseek.com/guides/thinking_mode/)

普通问题仍只调用一次 Host，最多6条检索参考/6000字符；grader最多3条相关判例/3000字符。不为降低成本省略完整汤底及评分要求。DeepSeek player/partner的提问、交卷、free_dialogue动作会自动加response_format=json_object（显式配置response_format时以配置为准），使用更新前的原始逻辑payload识别动作，后续会话delta也不会漏加。纯文本审查使用public_context包装、CL摘要使用memory角色，因此不会误加强制JSON。结构和语义仍由controller校验，不自动重采样。

默认 `session_mode=persistent`。每局每角色（MAS A/B也各自独立）持续维护同一消息历史；下一局新建。DeepSeek Chat Completions 接口本身无状态，客户端每次需发送同一会话累积的messages；新增上下文仍按无损增量追加，先前的消息不会重复展开成多份汤底。不能据此声称只计新消息tokens或历史免费。[官方多轮聊天说明](https://api-docs.deepseek.com/guides/multi_round_chat/)

HTTP 网络错误在 `api_calls.jsonl` 中记录 `transport_phase`、`transport_category`、`reason_type`、`reason_errno` 和 `safe_pre_send_retry`，不保存异常原文或响应正文。DNS 解析失败，以及受跟踪的 HTTPS 连接阶段出现 TLS 握手 EOF 或网络不可达时，应用请求尚未发送，可按 `max_retries` 有限重试；每次尝试单独记录。HTTP 429 仍按已有规则重试。超时、连接重置、响应读取错误和 HTTP 5xx 的请求是否已处理无法确认，不自动重试，持续会话停止并保留原始轨迹。旧日志只有 `URLError` 的情况下无法事后确定具体原因。

MAS默认partner自动复制player配置，**无需另设 partner-config**。底层 `experiment.py team` 或 `team_sweep.py` 如显式传 `--partner-config`，会覆盖默认partner；全DeepSeek实验应使用 `configs/partner.deepseek.json`，避免误传其他供应商。这个模板默认使用Flash/thinking关闭，与新默认player相同；如修改player模型，显式partner模板也需一起调整，否则省略partner-config即可自动复制player。

## 5. 查看轨迹、tokens与费用

### Grader覆盖评分中的reason说明

`fact_coverage`、`requirement_coverage` 的每条记录仍按id/status/evidence校验，但额外的字符串 `reason` 视为说明元数据：控制器复制后移除它，并在 `controller_corrections` 中记录 `ignored_metadata`。原始响应仍保留在API日志；不因此增加grader调用、重新采样分数或改变事实判断。checkpoint本身要求的reason字段不受影响。

未知额外字段、非字符串reason、重复/缺失/错误ID、非法status及无法在当前交卷中验证的evidence仍会拒绝。说明文字不能替代证据或提高分数。若确实需要原有的证据引用格式修复，最多一次调用，不能改变评分判断。

11月9日已用旧批次保存的完整grader响应离线验证该兼容修复；原批次、交卷和原始输出保留，没有重新调用模型。旧冻结代码不会因pull自动改变，也不会自动续跑。

若旧局正好因此中断，`resume_study.py --repair-grader-reason` 可复用完整评分：验证该响应与待评交卷、冻结rubric和消息链一致，离线移除字符串reason后按相同规则计算分数，把已有交卷的公开反馈写入副本，不再次调用grader。错误交卷正常计一次，额度不会重置。该模式与repair-player-note二选一，额外记录coverage/grader控制器模块的覆盖哈希；模型、Host包、prompt及评分标准保持原冻结内容。缺失响应、无效ID/证据或不确定请求不支持恢复。

```sh
python3 scripts/resume_study.py \
  --from-study runs/api/20261108_deepseek_set1_cl_note_resume01 \
  --out runs/api/20261109_deepseek_set1_cl_grade_resume02 \
  --repair-grader-reason --mode run
```

此命令需要在有Key的终端执行，out必须为新目录；改成mode plan只准备恢复副本。当前实例保存了91问及第92次交卷，复用评分后已用92次，下一次为第93次提交。

### 缺失问题结束引号的恢复

仅对完整返回（finish_reason=stop）的双字段question对象，若type/text字段次序明确、问题以问号结束、已有末尾对象右括号，并且只缺text的一个结束双引号，可在右括号前插入该引号。字段、问题文字逐字保留，原始输出及插入位置归档为player_format_recovery。截断响应、缺少问号、多个对象、额外字段、正文中歧义括号、代码块或final答案不使用该修复。

旧批次可显式使用 `resume_study.py --repair-player-json`：在副本中验证消息链并提交已保存问题，不重新生成；已完成的A局及公开问答、标准答案、配额和费用沿用原记录。恢复清单列出preserved_completed_runs及格式控制变化，不当成新的独立重复。新的动作调用自动使用JSON模式，不增加API调用；模型、Host参考和评分标准仍沿用原冻结版本。

```sh
python3 scripts/resume_study.py \
  --from-study runs/api/20261109_deepseek_set1_cl_grade_resume02 \
  --out runs/api/20261109_deepseek_set1_cl_json_resume03 \
  --repair-player-json --mode run
```

本次复用已结束的A=14，直接把answer_only B=13已保存的第1问交给Host，不重跑A、不重新生成B的第1问。out必须是新目录；mode plan仅准备副本且无付费调用。

同一恢复入口也支持另一种独立的窄修复：完整双字段question对象的正文中，仅有一对短语引号未转义时，只为这两个引号添加反斜线。问题文字及引号本身保留，原始输出和转义位置归档。多个引号短语、疑似字段/对象分隔符、正文中歧义括号、截断输出和final答案仍不修复；玩家JSON中的重复键也拒绝。

当前断点为 `20261109_deepseek_set1_cl_json_resume03` 的第74问，前73轮已有反馈。可使用相同 `--repair-player-json` 从该目录复制到新out并续跑，不重新调用player生成第74问；A=14的100次提交及结果同样复用。

### 字符串text_note的恢复

玩家的question/final动作允许额外的字符串 `text_note`。控制器只取原有type/text，不改写问题或答案；原始输出保留在API及submission日志，移除动作另记 `player_action_normalized`。未知额外字段、非字符串note、空正文及错误动作类型仍报错，不靠重新采样修复。

仅在旧局因这个note被拒绝，且最后一次DeepSeek玩家响应完整、尚未提交Host、前面没有不确定的失败请求时，可以在新目录续跑。工具会验证原快照哈希和完整消息链，保留原Host包、模型、prompt、评分、实验顺序、问数及费用；复制原目录后，只覆盖manifest列明的engine/sessions/providers三个控制器模块。DeepSeek no-tools chat的本地消息按原样恢复，直接提交保存的动作，不重新生成它。恢复批次需单独标注控制器修复，不算一次新独立重复。

```sh
# 默认plan仅创建恢复副本及manifest，零模型调用；out必须为新目录。
python3 scripts/resume_study.py \
  --from-study runs/api/20261108_deepseek_set1_cl_once \
  --out runs/api/20261108_deepseek_set1_cl_note_resume01 \
  --repair-player-note --mode plan
```

在已export Key的终端将mode改为run并选择另一个新out，才会真实续跑。该功能当前限单玩家DeepSeek三角色；不用于MAS中途恢复、修改Host答案/评分之后续跑、缺失响应或网络错误的重试。完整原批次保留；此次从A=14的48轮后保存的第49问继续，A和B额度均不重置。

study目录包含 `study_plan.json`、`status.json`、`continual/index.html`、`team/index.html`。MAS逐局 `shared_dialogue.html` 展示A/B及Host的全部公开对话，`trajectory.html`展示外部问答与私有评分供研究者审阅。

每局 `api_calls.jsonl` 保存请求模型及响应模型、usage、缓存命中、推理token数量（供应商返回时）；不保存 `reasoning_content`。`token_costs.csv` 和 `cost_summary.json` 保留所有角色及失败调用的可用计量，不把推理token重复加到输出总数。

**当前内置价格表尚未收录这次选用的 DeepSeek 模型价格**：tokens照常记录；没有精确模型费率的费用明确为 unknown，不记作0。若需金额，按你账号适用的官方价，在JSON顶层 `pricing` 填入完整费率表（见[费用参数](study_20261102.md#token-与费用记录自动启用)）；provider应为deepseek、model为响应中的精确ID、endpoint_prefix为 `https://api.deepseek.com/`，提供 input/cached_input/output 的每百万token美元单价及来源。未知的响应模型版本仍保持unknown，账单以DeepSeek控制台为准。

已用模拟HTTP覆盖全部角色、持续会话、共享聊天、Key隔离、usage记录，以及原18局和精简后14局dry-run。旧thinking开启批次曾真实启动，在A=14完成8轮问答后遇到HTTP IncompleteRead并停止，无交卷结果。连接异常现会计入transport_error并停止持续会话；不会自动重试或续跑旧局。当前关闭玩家thinking的配置尚未真实试跑。
