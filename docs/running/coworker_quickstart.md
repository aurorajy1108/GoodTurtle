# 同事从 clone 到运行实验

11月11日新分支 `fix/cl-session-prefix-compat-20261111`：CL原始会话续接、新Player返回格式及兼容性请优先按 [新版本运行指南](run_session_prefix_v1.md) 操作。

> 2026-10-24 v7：新增 CL 四条件对照、共享 buffer 问题预约、容量错误有限重试及 `--on-error`。旧实验已暂停，新增参数与设计边界见 [v7 修复说明](../host/host_repair_v7.md)。

本指南对应当前四标签 loop，Python 3.10+，只使用标准库。macOS、Linux 或 Windows 的 WSL 可运行并发 sweep；直接 Windows 环境的进程组停止行为尚未验证。运行真实模型需要你自己的 API key，或本机已安装且登录的官方 Codex CLI；仓库不包含账号凭据。以下命令都在仓库根目录执行。

人工参考问答统一上传到 [Host reference入口](../../data/host_reference/README.md)，不要直接混进运行输出或active包。

## 11月2日当前实验入口

11月7日新增全DeepSeek配置：Host/player/grader/默认partner及辅助调用均可使用同一个DeepSeek Key，study入口已解除GPT Host限制。参见[DeepSeek设置及CL/MAS运行命令](deepseek.md)。下面Codex配置仍可显式选择。

study 最新默认配置为 `configs/loop.deepseek.json`：Host/Grader Pro/high，Player/Partner Flash/thinking disabled。显式选择 `configs/loop.codex.json` 时使用其中的GPT模型配置，CL须指定 `--memory transcript`。
CL 固定每组首题为 B；同一批次每道 A 解一次后冻结复用，揭示 A 完整答案。
B 每次有独立100次额度；session 从固定A原始Player消息分支，其余条件新建会话。Token/费用自动记录，Codex账号费用仅作API等价估算。
完整参数、实验方向、四种协作策略及费用说明见 [当前实验文档](../archive/guides/study_20261102.md)。

已安装 Codex CLI 的同事先自行完成 `codex login`；不会共享任何人的登录凭据。

```sh
git pull --ff-only
# 只写计划，零模型调用；每次选择新输出目录。
python3 scripts/study_20261102.py --suite all --sets 1 --team-puzzles TS038 \
  --repeat 1 --out runs/api/my_set1_ts038_plan

# CL Set 1：固定 B=13，A=15/16/14/28；4局A + 12局B =16局。
python3 scripts/study_20261102.py --suite continual --sets 1 --repeat 1 \
  --mode run --out runs/api/my_set1_once

# TS038：solo/solo_reflect/independent/shared_buffer，各1局，共4局。
python3 scripts/study_20261102.py --suite team --team-puzzles TS038 --repeat 1 \
  --mode run --out runs/api/my_ts038_once
```

后两条可在独立终端运行。每批 `status.json` 记录状态，子目录 `index.html` 链接各局轨迹；
`experiment_runs.csv` 是性能结果，`costs_by_game.csv` / `cost_summary.json` 是用量和估算费用。
一次重复只用于检查行为，不足以估计稳定的方差或研究效果。
普通实验运行不需要 openpyxl；仅重新导入/制作人工审核 Excel 的维护脚本可能需要安装它。

## 1. 获取代码并做零调用检查

```sh
git clone https://github.com/aurorajy1108/GoodTurtle.git
cd GoodTurtle
python3 --version
python3 -m unittest discover -s tests -v
python3 scripts/play.py demo --out runs/api/my_demo
```

`demo` 是脚本模拟，不调用模型，不代表性能结果。所有输出目录必须尚不存在；第二次运行请改名字。

## 2. 题库与评分已随代码发布

```sh
# 已有工作副本使用 git pull；新同事直接 clone 即可。
git pull --ff-only
python3 scripts/play.py inspect --dataset data/annotations/turtle50_v4/private.json
```

当前仓库包含完整 **50 题、161 个评分点**，无需下载 XLSX 或单独的数据 ZIP：

- `data/annotations/turtle50_v4/private.json`：每题英文汤面、汤底、完整解答要求、partial score 权重和满分／半分／零分规则。
- `data/annotations/turtle50_v3/review.md`：逐题可读标注。
- `configs/host_bindings.json` 和它引用的所有 `data/host_packs/active/` 文件：当前 50 题均有基础示例；新补示例仍需真实历史和人工验证。
- 历史 `data/public/loop_eraser_pillow.json` 保留供旧数据查阅；新实验用 v4 数据配合题号筛选。

`private.json` 中的 private 指“对 player 保密”，不是未上传。控制器会隔离答案和评分，玩家只看到汤面及四标签反馈。标注经过 AI 审核，仍待人工确认，不能当作已验证的人工 gold。

模型账号必须由运行者自己配置。原始 49 题 XLSX 不是运行依赖；直接使用仓库中的 v4 JSON，避免旧表格和新 host 绑定版本不一致。

如果此前解压过旧数据包，`git pull` 提示未跟踪文件将被覆盖时，先备份提示中的文件或使用新的 clone，不要强制清理。旧 ZIP 不再是运行前置条件。

可选的离线传输工具仍可用：`python3 scripts/experiment_bundle.py export --dataset data/annotations/turtle50_v4/private.json --out /tmp/new_bundle.zip`；`--dataset` 指源 JSON/XLSX，`--out` 指新 ZIP（父目录需存在）。`python3 scripts/experiment_bundle.py verify --archive /tmp/new_bundle.zip` 检查哈希及绑定版本，不解压、不调用模型；两子命令支持 `-h / --help`。不需要为正常 clone/pull 运行这些命令。

## 3. 模型配置：任选一种

### OpenAI API

```sh
export OPENAI_API_KEY='你的 key，勿提交到 Git'
export OPENAI_MODEL='你账号可用的准确模型 ID'
```

使用 `--config configs/loop.openai.json`。host、player 默认同模型，grader 复用 host profile。

### DeepSeek 或 Anthropic API

```sh
export DEEPSEEK_API_KEY='你的 key'
# configs/loop.deepseek.json 已按角色指定：Host/grader Pro/high，player/partner Flash/thinking关闭
# 无需设置 DEEPSEEK_MODEL；同模型对照另用 configs/loop.deepseek.same-model.json

export ANTHROPIC_API_KEY='你的 key'
export ANTHROPIC_MODEL='你账号可用的准确模型 ID'
# 配置：configs/loop.claude.json
```

这些配置的模型 ID 由你自己的服务账号决定，不自动映射 Codex 模型别名。允许分别配置 host、player、grader；参见 `configs/loop.mixed.json` 与 [完整模型参数表](runtime_parameters.md)。

### 使用本机现有 Codex 登录

确认本机的 `codex` 命令可用且已登录，使用 `--config configs/loop.codex.json`。当前配置请求 host 为 `gpt-6.1-sol / medium`、grader 为 `gpt-6.1-sol / high`、player/默认partner 为 `gpt-5.6-luna / low`，单次超时 600 秒；需要账号支持相应模型。新配置只影响之后启动的批次。不要复制其他人的登录文件。如果账号不支持该 ID，请编辑自己的配置文件，实验报告会记录实际请求配置。

该后端通过官方 `codex exec` 调用，工具禁用；默认每局每角色独立持续会话，同局续接对应 thread ID，下一局新建。部分 CLI 版本可能不支持本项目使用的参数；若启动报 unsupported option，请查看本机 `codex exec --help` 与 `api_calls.jsonl`，不要把失败当作模型成绩。CLI 的模型 metadata fallback 警告不证明实际换了模型；实际模型名若没有由事件返回，报告保持未独立核验。

当前 host 每次普通提问只调用一次；只有最终四标签进入公开历史。证据格式修复最多增加一次 grader 调用。新增的自由协作 MAS 及角色 ablation 参数见 [free_dialogue](mas_free_dialogue.md)。

## 4. 跑一局（先 dry-run，再真实调用）

以下用 OpenAI API 配置举例；也可把配置路径替换成上面其他配置。即使 dry-run，配置中的模型环境变量也要设置，但不需要真实 key；Codex backend 还会检查 CLI 是否安装。

```sh
python3 scripts/play.py run --dataset data/annotations/turtle50_v4/private.json \
  --puzzle TS031 --config configs/loop.openai.json --dry-run \
  --out runs/api/eraser_check

python3 scripts/play.py run --dataset data/annotations/turtle50_v4/private.json \
  --puzzle TS031 --config configs/loop.openai.json \
  --out runs/api/eraser_real
```

打开输出目录的 `index.html` 或各局 `trajectory.html`。普通提问交给 host；final 交给私有 grader；player 只看到 `yes / no / yes and no / irrelevant`，看不到评分或缺失点。错误／不完整交卷计一次；第 100 个名额必须 final，正确交卷单独记录。

## 5. 多题、多次双 agent 对比

```sh
# clone/pull 后：先不花模型调用检查 36 局计划。
python3 scripts/team_sweep.py --dataset data/annotations/turtle50_v4/private.json \
  --config configs/loop.openai.json --puzzles TS023,TS032,TS033 \
  --repeat 3 --strategies solo,solo_reflect,discuss,independent \
  --workers 3 --dry-run --out runs/api/team_check

# 真正开始；每题每条件 3 局，总计 36 局。
python3 scripts/team_sweep.py --dataset data/annotations/turtle50_v4/private.json \
  --config configs/loop.openai.json --puzzles TS023,TS032,TS033 \
  --repeat 3 --strategies solo,solo_reflect,discuss,independent \
  --workers 3 --out runs/api/team_real
```

新增另一批可将 `--puzzles` 改成 `TS035,TS036,TS049` 并换输出目录。想用两题小子集可改为 `--dataset data/annotations/turtle50_v4/private.json --puzzles TS002,TS031`，此时总计 24 局。

| 条件 | 每轮 solver 调用 | 行为 |
| --- | ---: | --- |
| solo | 1 | 一位 player 直接决定问题／交卷 |
| solo_reflect | 3 | 草案、同模型审查、修订 |
| discuss | 3 | leader 草案、partner 审查、leader 修订 |
| independent | 3 | 双方独立提案，再由 leader 综合；partner 看不到首份提案 |
| alternating | 1 | 两位 player 轮流提交；不是默认 sweep 条件 |

同模型无状态请求下，discuss 与 solo_reflect 的区别主要是日志角色名，不能将其样本差异解释为 agent 身份效应。independent 改变了提案信息流。调用数匹配也不保证 token 成本相同。

要让第二位 solver 使用不同模型，可额外传 `--partner-config configs/partner.deepseek.json`，并设置对应环境变量；它是单个 provider profile，不能放整个 loop 配置。异构模型实验应保留模型能力对照。

全部 sweep 参数：

| 参数 | 默认值／要求 | 说明 |
| --- | --- | --- |
| --dataset PATH | 新实验必填 | 私有 JSON/XLSX |
| --config PATH | 新实验必填 | host/player/grader 配置 |
| --partner-config PATH | 无，复用 player | 第二位 solver 的单个 profile |
| --puzzles IDS | TS023,TS032,TS033 | 不重复的逗号分隔题号 |
| --repeat N | 3 | 每题每条件重复次数，正整数 |
| --strategies LIST | solo,solo_reflect,discuss,independent | 不重复、必须含 solo |
| --workers N | 3 | 同时进行的题目批次数，范围 1–4 |
| --seed N | 20261023 | 只控制调度，不能控制模型服务端采样 |
| --out PATH | 必填 | 新输出目录 |
| --poll-seconds N | 20 | 状态／HTML 更新间隔，范围 1–60 秒 |
| --dry-run | 关闭 | 冻结并遍历计划，不调用模型、不产生性能分数 |
| --summarize-only | 关闭 | 读取已有 out 重建报告，无需 dataset/config；不会恢复对局 |
| -h / --help | — | 帮助 |

每题内部循环轮换条件顺序，再随机化重复 block；三次重复无法完全平衡四个位置。开跑前冻结代码、题库、host、prompt、配置和哈希，运行中修改仓库不改变本批实验。

## 6. Continual learning 对照

```sh
python3 scripts/experiment.py continual --dataset data/annotations/turtle50_v4/private.json \
  --config configs/loop.openai.json --group G07 --pair TS022:TS047 \
  --memory transcript --source-feedback answer --repeat 3 \
  --out runs/api/cl_real
```

每次做 A，结束后揭示完整 A 答案，再比较直接 B 和携带 A 公开轨迹＋完整答案的 B。此例 3 次共 9 局。A 失败也照常揭示答案；直接 B 不接收任何 A 信息。A 和每局 B 分别有新的100次额度，揭示答案不扣额度。这里只是上下文经验迁移，不更新模型权重。`--memory card/both` 改变记忆形式，但仍保留完整 A 答案；`--source-feedback none` 是显式消融。具体全部参数见 [实验指南](experiment_pipelines.md#全部-cli-参数)。

## 7. 查看结果、后台运行和故障

- `trajectories.html`：sweep 全部问答、最终答案、私有评分和协作记录，刷新可见最新内容。
- `results_zh.md`：分题分条件成功数、最终得分和消耗次数的均值／样本方差。
- `condition_summary_by_puzzle.json`：调用数、token、耗时、均值／方差。
- `contrasts.json`、`reflection_contrasts.json`：按题和重复编号配对的差异。
- `progress.json`、`exit_codes.json`、`validation.json`：运行状态、退出码及覆盖／计数校验；passed 不代表 host 的语义准确率。
- `runtime_snapshot/`：冻结输入。`api_calls.jsonl` 在各局目录，含原始输入输出，可能包含答案，不给 player。

```sh
# 可选：在已有运行环境中让终端退出后仍运行。
nohup python3 scripts/team_sweep.py --dataset data/annotations/turtle50_v4/private.json \
  --config configs/loop.openai.json --puzzles TS035,TS036,TS049 --repeat 3 \
  --workers 1 --out runs/api/team_background > team_background.log 2>&1 &

# 不调用模型，仅重建已有 sweep 报告。
python3 scripts/team_sweep.py --out runs/api/team_background --summarize-only
```

需要停止时优先对前台 launcher 按 Ctrl-C；后台请记录启动时的 launcher PID 并给它 SIGINT。不要按名称批量 kill 其他实验。每局遇到 API、超时或协议错误会保留原记录并停止该题后续条件；launcher 不再启动新题，已经启动的其他题仍继续。没有自动续跑，也不会自动重采样“较差答案”。修复后请用新目录并保留失败批次。

缺文件先确认已拉取最新代码且文件没有被本地删除；fingerprint mismatch 是原文／绑定版本不同；缺环境变量先检查对应模型配置；401/403 检查本人的账号权限；429 时降低并行数并核对已有任务。100 次未解出是预算截尾，不是解题耗时为 100。三次重复只降低部分随机波动，不证明统计显著。
