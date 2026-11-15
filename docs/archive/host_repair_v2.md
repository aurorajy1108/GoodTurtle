# 当前 loop 的 host 修正（2026-10-23）

此前新 loop 没有读取旧题目资料包，host 只拿到原始短汤底，而 grader 读取额外完成清单。本次将两者接到同一份私有事实快照，并纠正错误因果、错误前提与无关细节的标签边界。四种公开标签、失败交卷计数、100 次提交上限、最终强制交卷规则不变。修正适用于 `scripts/play.py` 和 `scripts/experiment.py`；历史运行快照不改写。

## 接入方式

`turtle_loop/host_context.py` 使用 `configs/host_bindings.json` 中的题目 ID、原始汤面与汤底指纹寻找资料。不能只按汤面匹配：火警题有同题面异解。改动原文后需要审核绑定，而非自动套旧答案。

每局创建 `host_context.json`，保存原始答案、规范故事、事实、明确否定、未知／无关边界、完成清单、专属问答和上下文指纹。host 与 grader 使用同一个快照。rubric 权重和判分条件仍只给 grader；专属问答不是交卷评分规则。player 与合作伙伴不接收私有快照。

绑定文件中的 `legacy_pack` 指向旧资料，`overlay_pack` 指向四标签修订；修订覆盖指定 case ID 的标签，附加事实／示例，保留旧文件和旧实验可复现性。路径限定在 `data/host_packs`。不存在绑定的题目使用原始汤底和数据中的完成清单，不声称拥有专属例子。

| 题目 | 专属示例数 | 资料 |
| --- | ---: | --- |
| TS002 pillow | 84 | 80 条旧例＋4 条补充，并修订无关细节标签 |
| TS031 eraser | 29 | 20 条旧例＋9 条补充，并修订错误机制／无关细节 |
| TS022 window | 17 | 区分窗户身份、画中内容、人物消失版本 |
| TS047 window | 17 | 区分窗户身份、画中内容、震惊原因和无关人物身份 |
| TS012 cooking | 5 | 高温烹饪油烟版本 |
| TS017 smoking | 5 | 朋友吸烟版本 |

其余 44 题没有在本次补齐大量专属示例，不能据此声称 50 题已达到高准确性。新增事实／标签为待人工审核稿。LOOP_TS*_v2.json、回归 cases 与完整数据目前保留本地、受 Git 忽略规则保护；复制运行环境时必须一起提供，缺失的绑定资料会报错。

## 规则变化

- 单一错误因果或机制回答 `no`，不因句中存在一个真词就答 `yes and no`。
- “橡皮本身留下痕迹”与“取下橡皮让铅笔可以补芯”分开判断。
- “所谓画像本身是窗户”不等于“有一幅画描绘窗户／人造物”。
- 无关且未说明的品牌、衣服颜色、人物职业等用 `irrelevant`；重要事实确实不确定时仍可用 `yes and no`。
- 独立命题有真有假用 `yes and no`；包含任一已知真项的逻辑 OR 用 `yes`。
- 先前错误反馈、玩家假说和 A 题经验不会成为当前 B 题的事实。

## 一键回归检查

```sh
python3 scripts/check_host.py \
  --dataset data/annotations/turtle50_v1/private.json \
  --config configs/loop.codex.json \
  --cases data/host_dev/loop_host_regression_v2.json \
  --out runs/api/host_check_new
```

| 参数 | 必填／默认 | 含义 |
| --- | --- | --- |
| `--dataset` | 必填 | 私有 JSON 或 XLSX 数据集 |
| `--config` | 必填 | 现有模型配置，仅调用其中的 host；兼容现有各 API backend |
| `--cases` | 必填 | JSON 数组，每项含 id、puzzle_id、question、expected，可选 history（公开历史） |
| `--out` | 必填 | 新输出目录；已存在则拒绝覆盖 |
| `--repeat` | 默认 1 | 每条案例的独立调用次数，必须大于 0；答错也记录，不自动重抽 |
| `--dry-run` | 默认关闭 | 验证资料并保存输入，不调用模型 |
| `-h / --help` | 可选 | 显示参数帮助 |

输出包括 `cases.json`、`inputs.json`、`config.json`、`host_prompt.txt`、逐次 `api_calls.jsonl`、`results.jsonl` 和 `summary.json`。expected 标签不会发给模型。语义失败继续检查后续案例；传输错误则停止并保存已完成结果。全通过或 dry-run 返回 0，标签失败／传输失败返回 1。

这些案例来自已知错误及邻近问法，用于确认修复是否生效；训练示例已针对相同问题设计，不能把通过率当成独立测试集准确率。正式实验前仍需人工审核标签及更多不同问法、长历史和跨题干扰案例。

本次实际验证：46 项离线测试通过；Luna 基本回归 12/12，补充检查按初始预期为 3/4，另 1 条存在预期标签与既定规则冲突，修正及原始记录均保留。详见 [验证与人工审核记录](../runs/api/20261023_host_repair/review.md)。
