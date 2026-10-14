# 一键运行 host / player / evaluator 对局

新增入口：`python3 scripts/play.py`，Python 3.10+，仅标准库，无需安装第三方 SDK。旧 `prepare.py` 只生成历史三标签 host 资料；新 loop 独立使用四标签协议，不覆盖旧实验、prompt 或暂停状态。

## 先看一个无需 API key 的演示

```sh
python3 scripts/play.py demo
```

终端显示新目录。打开目录中的 `index.html`，进入 `trajectory.html` 查看全过程。演示是明确标记的脚本模拟，包含一次错误交卷和强制最终提交，**不是模型性能测试**。

## 使用这次的 49 题表格

可直接传 XLSX，不必导入：

```sh
python3 scripts/play.py inspect --dataset "/Users/aurorasun/Downloads/turtle_soup_labeled_49_with_partial_score.xlsx"
```

已在本地生成 `data/imported/turtle49_20261014/private.json`、`public.jsonl`、`audit.json`。也可以对新表格执行：

```sh
python3 scripts/play.py import --dataset "/path/to/workbook.xlsx" --out data/imported/my_dataset
```

读取 `逐题标注` 中的 ID、problem、answer，以及 `Partial Rubric` 中的 checkpoint、权重和英文评分标准；保留原 ID（49 题中没有 TS040）、story_family、质量标记与复核说明。不会执行 Excel 公式或其中的指令，也不会把 Score Inputs 的空白当成零分。

当前表格共有 49 题、161 checkpoints，每题权重合计 1。正常 36 题；其余包含复核、多解和同故事变体。TS012/017/018、TS015/016 存在完全相同汤面；还有同家族题。默认可运行全部 49 题，但这不表示它们都已通过 benchmark 质量验收，不要跨 family 随机拆分训练与测试。TS002 的新 partial rubric 比旧六要素评分更粗，旧成绩不直接混算。

本次只是构建和本地导入，没有发布新数据。此前 Git 的 data 白名单继续生效，新导入数据仍被忽略；不要把私有 dataset、rubric 或运行目录交给 player。

## 一条命令开始实际 API 对局

先在终端配置 API key 和**账号实际支持的 API 模型 ID**；这不是 Codex 子 agent 名称。密钥只从环境变量读取，不写进 JSON、trajectory 或请求日志。

```sh
export OPENAI_API_KEY='填入你的 key'
export OPENAI_MODEL='填入实际 API model ID'
python3 scripts/play.py run \
  --dataset data/imported/turtle49_20261014/private.json \
  --config configs/loop.openai.json --puzzle TS002 --repeat 3
```

无需指定输出目录，自动在 `runs/api/时间_UUID/` 下创建独立 batch。`--out` 可指定新目录，但已有目录不会被覆盖。`--puzzle TS001,TS002` 选择多题，`--puzzle all --repeat 3` 运行全部 49 题三次。每局上下文独立，不共享其他局的内容。

DeepSeek：导出 `DEEPSEEK_API_KEY`、`DEEPSEEK_MODEL`，改用 `configs/loop.deepseek.json`。

Claude：导出 `ANTHROPIC_API_KEY`、`ANTHROPIC_MODEL`，改用 `configs/loop.claude.json`。

混合供应商使用 `configs/loop.mixed.json`，host、player、grader 可分别选择模型。需要对应的三个 API key，以及 `HOST_MODEL`、`PLAYER_MODEL`、`GRADER_MODEL`。也可直接覆盖配置中的某个角色：

```sh
python3 scripts/play.py run --dataset data/imported/turtle49_20261014/private.json \
  --host openai:YOUR_HOST_API_MODEL --player deepseek:YOUR_PLAYER_API_MODEL \
  --grader anthropic:YOUR_GRADER_API_MODEL --puzzle TS002
```

没有单独指定 grader 时，默认复用 host 的模型配置，但使用**独立评估请求**，不把评分上下文混入 host/player。

## 接口和参数

| provider 配置 | 请求格式 | 默认 base_url | API key 环境变量 |
| --- | --- | --- | --- |
| `openai` | Responses | `https://api.openai.com/v1` | `OPENAI_API_KEY` |
| `openai_chat` | Chat Completions，max_completion_tokens | 同上 | `OPENAI_API_KEY` |
| `deepseek` | Chat Completions，max_tokens | `https://api.deepseek.com` | `DEEPSEEK_API_KEY` |
| `anthropic` | Messages，独立 system 字段 | `https://api.anthropic.com/v1` | `ANTHROPIC_API_KEY` |
| `openai_compatible` | Chat Completions，max_tokens | 自行配置 | `OPENAI_API_KEY` 或自定义 |

实现依据：[OpenAI 文本生成](https://developers.openai.com/api/docs/guides/text)、[Claude Messages](https://platform.claude.com/docs/en/api/messages/create)、[DeepSeek 首次调用](https://api-docs.deepseek.com/)。这里只声明接口适配，不保证每个账号均有某模型权限。每次请求保存供应商返回的 model、response ID、usage 与耗时。不同平台的 token 口径保留原样，不推算价格。

每个角色支持如下配置；API key 直接值不允许写入文件：

```json
{
  "provider": "openai",
  "model": "${HOST_MODEL}",
  "base_url": "https://your-gateway.example/v1",
  "api_key_env": "MY_GATEWAY_KEY",
  "max_output_tokens": 8192,
  "timeout": 120,
  "max_retries": 2,
  "extra_body": {"reasoning": {"effort": "high"}}
}
```

base_url 是 API 基础路径，不含 `/responses`、`/messages` 或 `/chat/completions` 后缀。第三方转发若提供 OpenAI-compatible 格式，即使调用 Claude 模型也应选 `openai_compatible`，不是原生 `anthropic`。未实现 AWS Bedrock、Vertex、OAuth 和各云厂商专有认证；不要将它们当成通用 HTTP key 接口。

`temperature` 可选，默认不发送，避免强行传给不支持的模型。`extra_body` 可传模型支持的 reasoning/thinking 等选项，但不能覆盖模型、上下文、工具、凭据、输出长度或服务端存储设置。不支持的参数会明确报 API 错误，不会静默删除或更换模型。输出 token 限制与 100 次提问预算不同；reasoning 模型若输出被截断，需手动调高 `max_output_tokens` 后开新实验。

所有角色采用 stateless 请求：每轮重传完整可见历史。不跨请求缓存/继续私有思维链，不提供工具。OpenAI Responses 使用 `store=false`；原生 Claude 的 system 字段与 messages 分开。提供商的隐藏 reasoning 内容不写入 trajectory。

## 四种反馈与错误交卷

- `yes`：支持；对最终交卷表示已完整解出。
- `no`：错误事实、错误原因、机制或身份。
- `yes and no`：混合判断、相关事实未指定或必要歧义；对交卷表示有得分但仍不完整/存在关键冲突。
- `irrelevant`：与解题无关的细节/请求，或完全不相关的交卷。错误的核心机制不是 irrelevant。

普通问题由 host 回答。交卷由独立 evaluator 评分，程序计算分数并产生四标签反馈；不再额外调用 host 重复裁决。玩家只获得这个标签，**看不到分数、缺失项、解释或 rubric**。host 的后续可见历史包含此前交卷和标签，修复旧框架里“last final explanation”没有上下文的问题。

新 host 使用汤面、汤底、完整公开历史及四标签示范。表格没有提供每题经人工审核的问答示例，故不能声称已达到高鲁棒性；日志和人工审核表用于继续校准。

## 100 次严格上限与统计口径

用户已确认：**第 100 次提交预留为强制最终提交**。

- 普通问题计 1；错误或不完整交卷计 1，继续游戏。
- 到计数 99 时，下次只允许 type=final，不再允许问题。
- 这次最终答案错误/不完整：计数达到 100，结束为 budget_exhausted。
- 这次答对：结束为 solved。正确交卷不属于“错误交卷”，计数问题为 99，总提交为 100。
- 第一条就是正确答案时，计数问题为 0、总提交为 1。两个数都报告。
- 可在 config 中将 `max_questions` 调小作调试，但不能超过 100。
- 若模型无视最后交卷要求，记录 protocol error，不伪造或把它的问题强行当作答案。

## Partial score 与完整成功分开

对每次 final **单独**评分，覆盖率只能是 0、0.5、1：

`partial_score = Σ(weight × credit)`

程序验证 checkpoint IDs、取值、证据字段、权重和类型，自行计算总分，不信任模型输出总分。完全猜对还需 evaluator 判断完整参考叙事已经还原、全部 checkpoint 得满分、没有关键矛盾或 rubric 冲突。**partial_score=1 仍可能 incomplete**，保留之前要求的完整叙事标准；接受忠实改写，不要求逐字复述，也不要求汤底未指定的细节。

`final_partial_score` 是最后一次交卷得分；`best_partial_score` 是本局单次交卷最高分，两个都保存。不会累加几次交卷，也不会从整个对话拼出玩家从未提交过的满分答案。尚无交卷或最后交卷尚未成功评分时，final_partial_score 为 null。所有模型评分均待人工审核，不当成人类 ground truth。发现 rubric 与答案冲突时标记 needs_review，停止该局并排除出正常完成率统计。

## 直接看 trajectory 和 performance

Batch 目录：

- `index.html`：进入各局的页面。
- `performance.csv`：逐局 ID、family、质量、提问数、交卷数、得分、完成状态。
- `summary.json`：成功率、问题均值/总体方差/样本方差、partial score 统计。
- `batch_config.json`、`dataset_audit.json`：模型、预算、输入/提示哈希和质量标记。

每局目录：

- `trajectory.html`：可直接打开；运行中每 5 秒刷新，private evaluation 默认折叠。
- `trajectory.md`、`trajectory.jsonl`：可读记录与逐事件原始记录。
- `result.json`：计数、最新/最高得分、成功状态、usage、时长及错误。
- `api_calls.jsonl`：每次真实请求体、可见输出、调用 ID、重试和 usage；不保存认证 headers/API key 或隐藏 reasoning。**包含答案与私有 rubric，只供研究者审查。**
- `config.json`、`prompts.json`、`puzzle_private.json`：冻结输入。
- `human_review.csv`：局结束后生成，供人工填写；运行中使用模型拥有的 `review_template.csv`。

成功率分母是正常结束的局；error/interrupted/needs_review 单列。成功局的问题数与所有已完成局的消耗统计分开，失败达到上限不能伪装成成功所需次数。按当前临时 rubric 产生的分数不代表模型通用能力。

## 运行前检查、错误与恢复

不调用 API 的全题预检：

```sh
python3 scripts/play.py run --dataset data/imported/turtle49_20261014/private.json \
  --host openai:YOUR_HOST_API_MODEL --player deepseek:YOUR_PLAYER_API_MODEL \
  --puzzle all --dry-run
python3 -m unittest discover -s tests -v
```

dry-run 不要求 API key，不产生假分数。API key/model 配置会在真实运行开始前统一检查。网络/429/5xx 可限次数退避重试，并记录每次调用；重试不算新的玩家问题。格式错误、截断和 API 拒绝不偷偷转换标签、不多次采样择优。

Ctrl+C 保存当前局为 interrupted，API/格式错误保存为 error，并停止剩余 batch，避免持续付费失败。已产生但尚未收到反馈的提交标记 pending。当前没有自动恢复半局命令；排查后可对未完成 ID 开新的独立实验，不能把新会话假装原局无缝延续。旧 pillow unlimited 实验仍保持暂停，不会由此入口自动恢复。

验证情况：本地测试使用模拟 HTTP/脚本客户端；当前环境未配置 OpenAI、Anthropic、DeepSeek API key，尚未执行三家真实付费端到端对局。需要实际账号完成少量 smoke test 后，再启动 49 题批量实验。
