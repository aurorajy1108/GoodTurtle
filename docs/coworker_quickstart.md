# 同事从 clone 到运行实验

本指南对应当前四标签 loop，Python 3.10+，只使用标准库。macOS、Linux 或 Windows 的 WSL 可运行并发 sweep；直接 Windows 环境的进程组停止行为尚未验证。运行真实模型需要你自己的 API key，或本机已安装且登录的官方 Codex CLI；仓库不包含账号凭据。以下命令都在仓库根目录执行。

## 1. 获取代码并做零调用检查

```sh
git clone https://github.com/aurorajy1108/GoodTurtle.git
cd GoodTurtle
python3 --version
python3 -m unittest discover -s tests -v
python3 scripts/play.py demo --out runs/api/my_demo
```

`demo` 是脚本模拟，不调用模型，不代表性能结果。所有输出目录必须尚不存在；第二次运行请改名字。

## 2. 选择数据：clone 自带两题；完整题库单独交接

Git 自带 `data/public/loop_eraser_pillow.json`，含 TS002（pillow）和 TS031（eraser）的汤底、评分和完成条件，以及对应 host pack。`public` 目录名是历史路径，**这个文件含秘密答案，只供控制器使用，不可直接给 player**。

```sh
python3 scripts/play.py inspect --dataset data/public/loop_eraser_pillow.json
```

完整 50 题及其他专属 host pack 遵循原发布范围，不随 Git 上传。要跑 TS023 等题，向项目负责人取得与当前代码匹配的 `goodturtle_experiment_inputs.zip`，在仓库根目录验证并解压：

```sh
python3 scripts/experiment_bundle.py verify --archive /path/to/goodturtle_experiment_inputs.zip
python3 -m zipfile -e /path/to/goodturtle_experiment_inputs.zip .
python3 scripts/play.py inspect --dataset data/annotations/turtle50_v2/private.json
```

ZIP 只含题库、所需 host packs 和 SHA-256 清单，无 key、登录文件、模型配置或运行记录。验证同时检查当前 `configs/host_bindings.json` 是否与数据包匹配。若不匹配，请取得对应版本，不要删除绑定校验。对已有工作副本解压会写入相同路径，推荐使用干净 clone。

项目负责人生成本地交接包的方法：

```sh
python3 scripts/experiment_bundle.py export \
  --dataset data/annotations/turtle50_v2/private.json \
  --out /tmp/goodturtle_experiment_inputs.zip
```

`export --dataset` 是源 JSON/XLSX，`--out` 是尚不存在的 ZIP，父目录需存在；`verify --archive` 只校验不解压、不调用模型。两子命令均支持 `-h / --help`。生成的数据集固定放在包内 `data/annotations/turtle50_v2/private.json`；如果传入的是其他标注版本，内容以输入为准，不会自动升级评分。不要把 ZIP 加入 Git。

原始 49 题 XLSX 可以被读取，但它不等于已经审核的 50 题 v2 数据。相同题号的汤面／汤底若改变，当前绑定会拒绝运行；不能靠重命名文件假装复现了相同数据。

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
export DEEPSEEK_MODEL='你账号可用的准确模型 ID'
# 配置：configs/loop.deepseek.json

export ANTHROPIC_API_KEY='你的 key'
export ANTHROPIC_MODEL='你账号可用的准确模型 ID'
# 配置：configs/loop.claude.json
```

这些配置的模型 ID 由你自己的服务账号决定，不自动映射 Codex 模型别名。允许分别配置 host、player、grader；参见 `configs/loop.mixed.json` 与 README 的完整模型参数表。

### 使用本机现有 Codex 登录

确认本机的 `codex` 命令可用且已登录，使用 `--config configs/loop.codex.json`。当前配置请求 `gpt-6-luna`、reasoning `high`、单次超时 600 秒；需要账号支持这个模型。不要复制其他人的登录文件。如果账号不支持该 ID，请编辑自己的配置文件，实验报告会记录实际请求配置。

该后端通过官方 `codex exec` 调用，工具禁用，每次为新会话。部分 CLI 版本可能不支持本项目使用的参数；若启动报 unsupported option，请查看本机 `codex exec --help` 与 `api_calls.jsonl`，不要把失败当作模型成绩。CLI 的模型 metadata fallback 警告不证明实际换了模型；实际模型名若没有由事件返回，报告保持未独立核验。

## 4. 跑一局（先 dry-run，再真实调用）

以下用 OpenAI API 配置举例；也可把配置路径替换成上面其他配置。即使 dry-run，配置中的模型环境变量也要设置，但不需要真实 key；Codex backend 还会检查 CLI 是否安装。

```sh
python3 scripts/play.py run --dataset data/public/loop_eraser_pillow.json \
  --puzzle TS031 --config configs/loop.openai.json --dry-run \
  --out runs/api/eraser_check

python3 scripts/play.py run --dataset data/public/loop_eraser_pillow.json \
  --puzzle TS031 --config configs/loop.openai.json \
  --out runs/api/eraser_real
```

打开输出目录的 `index.html` 或各局 `trajectory.html`。普通提问交给 host；final 交给私有 grader；player 只看到 `yes / no / yes and no / irrelevant`，看不到评分或缺失点。错误／不完整交卷计一次；第 100 个名额必须 final，正确交卷单独记录。

## 5. 多题、多次双 agent 对比

```sh
# 完整数据包解压后：先不花模型调用检查 36 局计划。
python3 scripts/team_sweep.py --dataset data/annotations/turtle50_v2/private.json \
  --config configs/loop.openai.json --puzzles TS023,TS032,TS033 \
  --repeat 3 --strategies solo,solo_reflect,discuss,independent \
  --workers 3 --dry-run --out runs/api/team_check

# 真正开始；每题每条件 3 局，总计 36 局。
python3 scripts/team_sweep.py --dataset data/annotations/turtle50_v2/private.json \
  --config configs/loop.openai.json --puzzles TS023,TS032,TS033 \
  --repeat 3 --strategies solo,solo_reflect,discuss,independent \
  --workers 3 --out runs/api/team_real
```

新增另一批可将 `--puzzles` 改成 `TS035,TS036,TS049` 并换输出目录。只用 Git 自带数据可改为 `--dataset data/public/loop_eraser_pillow.json --puzzles TS002,TS031`，此时总计 24 局。

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
python3 scripts/experiment.py continual --dataset data/annotations/turtle50_v2/private.json \
  --config configs/loop.openai.json --group G07 --pair TS022:TS047 \
  --memory transcript --source-feedback none --repeat 3 \
  --out runs/api/cl_real
```

每次做 A，再比较直接 B 和携带 A 公开轨迹的 B。此例 3 次共 9 局。A 失败仍会传递失败经历；参考答案默认不传入。这里只是上下文经验迁移，不更新模型权重。`--memory card/both`、`--source-feedback answer` 会改变实验条件，具体全部参数见 [实验指南](experiment_pipelines.md#全部-cli-参数)。

## 7. 查看结果、后台运行和故障

- `trajectories.html`：sweep 全部问答、最终答案、私有评分和协作记录，刷新可见最新内容。
- `results_zh.md`：分题分条件成功数、最终得分和消耗次数的均值／样本方差。
- `condition_summary_by_puzzle.json`：调用数、token、耗时、均值／方差。
- `contrasts.json`、`reflection_contrasts.json`：按题和重复编号配对的差异。
- `progress.json`、`exit_codes.json`、`validation.json`：运行状态、退出码及覆盖／计数校验；passed 不代表 host 的语义准确率。
- `runtime_snapshot/`：冻结输入。`api_calls.jsonl` 在各局目录，含原始输入输出，可能包含答案，不给 player。

```sh
# 可选：在已有运行环境中让终端退出后仍运行。
nohup python3 scripts/team_sweep.py --dataset data/annotations/turtle50_v2/private.json \
  --config configs/loop.openai.json --puzzles TS035,TS036,TS049 --repeat 3 \
  --workers 1 --out runs/api/team_background > team_background.log 2>&1 &

# 不调用模型，仅重建已有 sweep 报告。
python3 scripts/team_sweep.py --out runs/api/team_background --summarize-only
```

需要停止时优先对前台 launcher 按 Ctrl-C；后台请记录启动时的 launcher PID 并给它 SIGINT。不要按名称批量 kill 其他实验。每局遇到 API、超时或协议错误会保留原记录并停止该题后续条件；launcher 不再启动新题，已经启动的其他题仍继续。没有自动续跑，也不会自动重采样“较差答案”。修复后请用新目录并保留失败批次。

缺文件通常是尚未解压匹配数据包；fingerprint mismatch 是原文／绑定版本不同；缺环境变量先检查对应模型配置；401/403 检查本人的账号权限；429 时降低并行数并核对已有任务。100 次未解出是预算截尾，不是解题耗时为 100。三次重复只降低部分随机波动，不证明统计显著。
