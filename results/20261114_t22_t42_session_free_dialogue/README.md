# T22 / T42：2026-11-14 实验轨迹

[结果浏览页](index.html) · [完整分析](report.md) · [逐局CSV](games.csv) · [汇总CSV](summary.csv)

主分析31局全部完成：T22五轮baseline/after-A session（20局）与五局双agent free_dialogue；T42一局baseline与五局双agent free_dialogue。另收录三个原A及最早三个session，共37份trajectory。

- `trajectories/TS022/`：baseline、after_TS047_session（positive）、after_TS045_session（negative）、after_TS019_session（irrelevant）、free_dialogue。
- `trajectories/TS042/`：baseline、free_dialogue。
- `appendix/sources/`：只保留一份原A。15局主session始终复用这三个固定前缀，没有重跑A。
- `appendix/early_session/`：最早三个session，缺少同轮baseline，未并入主比较。

每局有trajectory的Markdown/HTML/JSONL、原始result、汤面汤底和评分点、配置与提示词、费用及核验记录；MAS另有共享讨论JSONL/HTML。`experiment_metadata.json`明确记录前题A和源trajectory位置，整理轮号不改写原始result轮号。原始result、问答及评分保持不变。

13局充值后续跑的失败调用和恢复事件保留在审计与trajectory中，最终归档替代原中断快照，计数一次。compact `api_audit.jsonl.gz`保留各次返回、用量、错误、完整请求哈希；不含重复HTTP请求body及内嵌A前缀，不能单独重建完整HTTP请求。源文件哈希见逐局verification及manifest。

Player/伙伴是DeepSeek Flash（thinking disabled）；Host/Grader是DeepSeek v4 Pro（thinking enabled/high）。B共用100次外部提交上限，MAS另有内部讨论调用，计算量不匹配。所有语义评分待人工审核。T22 MAS最终均分36%，完整解出1/5；T42 MAS均分63%，完整解出0/5，baseline仅一局50%。

`protocol/frozen_runtime/`保存审计使用的冻结Python模块、配置、提示词及题库；包含原恢复适配器，仅作历史审阅。此目录不是完整可续跑的API原归档；未包含密钥或环境文件。31局的费用单独计，附录原A和早期session未并入主费用。

在保存原本地归档的机器上可离线重建（不调用模型）：

```sh
python3 scripts/publish_t22_t42_results.py \
  --report reports/t22_t42_20261114 \
  --frozen-runtime runs/api/t22_t42_20261114_paid_resume13/runtime_snapshot \
  --out results/NEW_T22_T42_RELEASE
```
