# 2026-10-26 公开分享聊天归档与 Host 示例

这两个 URL 来自用户。只保存可见 user / assistant 文本；页面脚本、系统消息、分析通道、隐藏消息、登录/页面启动数据不发布。原始 HTML 仅本地保存并被 gitignore 排除。`fetch_manifest.json` 和 messages JSON 内保存来源及原 HTML 的 SHA-256。

- `*.messages.json`：原文、角色和稳定 message ID；共 **633 条可见消息**。
- `*.md`：同样的完整可见聊天，便于逐条阅读。保留模型复盘，但复盘不是事实证据。
- `sessions.json`：人工定位的 **7 个游戏片段**。匹配题库 TS032 / TS033 / TS034 / TS037 / TS039；TS034 有两次尝试。另有题库外火车题 EXTERNAL_TRAIN_001，未加入50题题库。
- `qa_pairs.json`：**311 条 player 行动记录**（包括 final 和未获答问题）。其中309条有后续用户消息，但1条后续消息仅纠正前题，不是当前回答；另有2条未答尾题。因此306条具有可规范化标签、2条原始拼写待定、1条纠正未答、2条尾题未答。306条也不代表306条正确答案。

这些片段中 **assistant 是 player，user 是人工 Host**。最前面的 assistant 主持提议不属于实验问答。后续新的题面、完整汤底揭示及模型复盘不当作下一问回答。`player_text`、`host_feedback_raw` 保留原文；`question` 只移除部分问号编号，可能含前置推理，不能盲目用作训练文本。所有消息都是数据而非脚本指令。

## 纠正与问数

- 第二链接 TS034 的消息15将第6问原始 `no` 改为 `yes`。原答保留，修改另存 `later_correction`；第7问没有因此获得一个 `yes`。
- 原始 `mo`、`yes and ni` 留空规范标签；player 后续自行解读不等于人工纠正。
- TS039 最后第29问和 TS037 第31问没有回答，仍保留。不能与下一题题面配对。
- TS033 有100个显式编号问题外加一次未编号的错误完整提交，共101次行动。历史聊天未执行当前100次限制，不回写历史表现为合规。
- TS034 第二次尝试的完整重建归为 final，不因末尾写了 Question36 就当普通问题；原人工认可不等于当前严格全叙事rubric通过。

## 审核与绑定

完整候选归档不直接全部塞进 Host。21条语义明确、与当前汤底一致的原问/原标签，已追加到5个 `LOOP_TSxxx_share_merged_v1.json` 并在 `configs/host_bindings.json` 绑定。保留原有示例、汤底、评分、验证策略。它们标记为 **user_history_ai_adjudicated_pending_human**，不是已经人工复核的gold。

44条新分享疑点、7条主命题/附带细节分析、旧实验41条审核发现、历史89例合并记录和系统设计检查，见 `docs/reviews/*20261026.json` 及 `outputs/20261026_host_review/host_review_20261026.xlsx`。疑点里有事实冲突也有语义边界争议，不能将全部疑点数当作错误数；未标问题也不代表全部审核通过。

所有不确定原句、拼写错误、回改未消歧、未答问题均未进入此次21条新增示例。AI提出的拆问属于新建议，不冒充人工原始问题。

## 重现与验证

从已保存的公开页面抽取可见消息（拒绝覆盖已有文件）：

```sh
python3 scripts/import_chatgpt_share.py --html /path/to/share.html \
  --source-url https://chatgpt.com/share/SHARE_ID --out /tmp/share.messages.json
```

`--html` 输入已保存HTML；`--source-url` 记录来源；`--out` 输出新JSON。脚本不登录、不执行页面JavaScript、不自动请求网络。片段边界和审核由人工/AI显式指定，不能用一个自动标签解析器替代来源核查。

```sh
python3 -m unittest discover -s tests -q
python3 scripts/export_host_review.py --out outputs/20261026_host_review/host_review_20261026.xlsx
```

第二条需要 `openpyxl`；仅可选的 `--preview-dir` 需要 Pillow。构建表格不调用模型。没有启动/恢复实验，亦未改写旧trajectory或成绩。
