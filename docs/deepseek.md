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
| response_format | 不强制JSON，直接四标签 | 依具体动作prompt；兼容旧策略文本审查 | json_object |

player/默认partner、显式partner模板、同模型对照中的player及混合模板中的DeepSeek player均已关闭thinking，并删除reasoning_effort；玩家的内部审查和经验总结继承此设置。Host/grader仍开启high推理。

这些参数在 `configs/loop.deepseek.json` 中修改。输出预算是每次调用的上限，包含模型推理及可见输出，不是每次都会用满；到上限而截断会记为错误，不重新采样答案。推理模式不设置 temperature；如果要关闭推理，把相应角色的 `extra_body.thinking.type` 改为 `disabled` 并删除该角色的 `reasoning_effort`。本模板不把原 GPT 的 medium 直接等同为 DeepSeek medium：官方当前将 medium 映射为 high，因此明确写 high。记录并单独比较模型/推理配置不同的批次。[官方推理参数说明](https://api-docs.deepseek.com/guides/thinking_mode/)

普通问题仍只调用一次 Host，最多6条检索参考/6000字符；grader最多3条相关判例/3000字符。不为降低成本省略完整汤底及评分要求。player不强制全局JSON模式，是因为旧 `solo_reflect`/`discuss` 的内部审查、CL摘要需要纯文本；提问/交卷/free_dialogue仍由各自prompt与controller严格校验JSON，不合规即记录错误。

默认 `session_mode=persistent`。每局每角色（MAS A/B也各自独立）持续维护同一消息历史；下一局新建。DeepSeek Chat Completions 接口本身无状态，客户端每次需发送同一会话累积的messages；新增上下文仍按无损增量追加，先前的消息不会重复展开成多份汤底。不能据此声称只计新消息tokens或历史免费。[官方多轮聊天说明](https://api-docs.deepseek.com/guides/multi_round_chat/)

MAS默认partner自动复制player配置，**无需另设 partner-config**。底层 `experiment.py team` 或 `team_sweep.py` 如显式传 `--partner-config`，会覆盖默认partner；全DeepSeek实验应使用 `configs/partner.deepseek.json`，避免误传其他供应商。这个模板默认使用Flash/thinking关闭，与新默认player相同；如修改player模型，显式partner模板也需一起调整，否则省略partner-config即可自动复制player。

## 5. 查看轨迹、tokens与费用

study目录包含 `study_plan.json`、`status.json`、`continual/index.html`、`team/index.html`。MAS逐局 `shared_dialogue.html` 展示A/B及Host的全部公开对话，`trajectory.html`展示外部问答与私有评分供研究者审阅。

每局 `api_calls.jsonl` 保存请求模型及响应模型、usage、缓存命中、推理token数量（供应商返回时）；不保存 `reasoning_content`。`token_costs.csv` 和 `cost_summary.json` 保留所有角色及失败调用的可用计量，不把推理token重复加到输出总数。

**当前内置价格表尚未收录这次选用的 DeepSeek 模型价格**：tokens照常记录；没有精确模型费率的费用明确为 unknown，不记作0。若需金额，按你账号适用的官方价，在JSON顶层 `pricing` 填入完整费率表（见[费用参数](study_20261102.md#token-与费用记录自动启用)）；provider应为deepseek、model为响应中的精确ID、endpoint_prefix为 `https://api.deepseek.com/`，提供 input/cached_input/output 的每百万token美元单价及来源。未知的响应模型版本仍保持unknown，账单以DeepSeek控制台为准。

已用模拟HTTP覆盖全部角色、持续会话、共享聊天、Key隔离、usage记录，以及原18局和精简后14局dry-run。旧thinking开启批次曾真实启动，在A=14完成8轮问答后遇到HTTP IncompleteRead并停止，无交卷结果。连接异常现会计入transport_error并停止持续会话；不会自动重试或续跑旧局。当前关闭玩家thinking的配置尚未真实试跑。
