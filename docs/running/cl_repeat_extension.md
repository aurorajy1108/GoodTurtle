# Set1：复用原A，将B累计补到四次重复

本次固定 B=TS013；A=TS015（positive）、TS014（negative）、TS028（neutral）。每个A只使用原来那一条已完成 trajectory，并在B开始时揭示A的完整答案。

| 内容 | 保留的历史 | 新增 | 累计 |
| --- | ---: | ---: | ---: |
| 前题A | 3局 | 0局 | 3局 |
| B：直接做题 | 6局 | 6局 | 12局 |
| B：只提供A答案 | 6局 | 6局 | 12局 |
| B：延续A原始角色消息 | 6局 | 6局 | 12局 |
| 合计 | 21局 | 18局 | 39局 |

每个“前题×条件”累计四次B重复。第3、4次是新的模型采样；前两次不重跑、不重新评分，所有A不重新生成。每个B从原A独立分叉，清空B的公开历史，重新获得100次外部提交额度，第100次强制最终交卷。失败或不完整交卷计一次额度。

本次不修改Host：Host/Grader代码、prompt、参考包、数据、评分点、模型、thinking参数、检索策略和pricing全部保留原冻结字节。Player为原配置DeepSeek Flash关闭thinking；Host和Grader为原配置DeepSeek v4 Pro。只修复action解析与扩展时的固定A查找。原历史与新增采样使用不同解析版本，报告时注明这个cohort差异；这仍是固定一个A前缀下的四次B采样，不是四条独立A学习经历。

action恢复只提取唯一明确的`QUESTION`/`FINAL`（MAS也支持原`NEXT=A/B`），接受前置说明、单行、换行或冒号格式，正文原文保留。恢复不重新生成提问、不访问汤底、评分或Host反馈，不消耗额外API调用。多个action不按分数挑选。没有明确action时沿用受限的同会话纠正规则。这个实验关闭旧版可选Codex格式化后备接口，所有模型接口继续使用DeepSeek。

在仓库根目录运行：

```bash
python3.11 scripts/extend_cl_repeats.py prepare \
  --reference runs/api/20261112_jiayang_supervised_v4/continuations/cl-set1-a/attempt_01 \
  --out runs/api/20261112_set1_fixed_prefix_r1r4_v2 \
  --total-repeats 4
bash scripts/run_extended_set1.sh runs/api/20261112_set1_fixed_prefix_r1r4_v2
```

- `prepare`：仅复制归档、验证冻结哈希、规划新增局数，不调用API。
- `--reference`：原来已完成的单个CL study目录，包含`study_plan.json`、`runtime_snapshot/`、`continual/`；不要填campaign或单局目录。
- `--out`：prepare时必须不存在的新campaign目录；run时指向已准备目录。原始归档不修改。
- `--total-repeats`：包含已有重复的累计次数；默认4，必须大于历史次数，上限20。
- `run`：内部由shell启动，也可用`python3.11 scripts/extend_cl_repeats.py run --out 输出目录`；并非再次prepare。
- shell唯一参数：已准备好的输出目录。它从忽略的`.env.local`读取`export DEEPSEEK_API_KEY=...`（或沿用已export的key），不会打印key；macOS下阻止空闲休眠。

输出根目录`index.html`、`progress.json`和`status.json`提供实时进度，`study/continual/index.html`查看逐局trajectory与条件比较，`cost_summary.json`包含历史复用和新增调用各一次。不能再把原study的相同历史费用叠加一遍。

新增18局沿用原批次的顺序调度，单独一名worker，避免对相同日志并发写入。一次受控启动受`launcher.lock`保护，不能重复启动同一目录。出现可校验的发送前网络错误、已返回评分漏字段等，会转入既有监督器，保留轨迹和额度续跑；监督输出在`输出目录_supervised/`。未知错误或无法安全恢复的输出暂停并请求macOS通知，原记录不删除、不静默抽取新局。

单agent自我复查是另一种MAS对照：同一个Player在同一个持续会话内先提出候选、再检查自己的假设、最后提问或交卷；draft/review笔记不是Host证据，也不是第二个agent。它用于区分额外复查计算预算与两名独立agent协作的影响。本次新增18局是CL，不引入该复查策略。
