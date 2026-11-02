# Aurora 人工问答提交核对（2026-10-29）

核对本地与 fetch 后的 `origin/main`：均为 `1aa06db`。范围为本次列出的 15 道不同题目；Set 1 另有一个未指定题号的 unrelated 对照。

**结论：3 题已有可见聊天原文归档；1 题只有人工来源片段；11 题未找到人工原文。新链接未读取成功，因此以下是“仓库缺哪些”，不代表这些题目还没做过。**

| 组 | 题号 | 人工原始资料 | 已进入 active 的人工来源示例 | 下一步 |
| --- | --- | --- | --- | --- |
| set1 | TS013 | 未找到人工原文 | 0 | 补完整对话 |
| set1 | TS014 | 未找到人工原文 | 0 | 补完整对话 |
| set1 | TS015 | 未找到人工原文 | 0 | 补完整对话 |
| set1 | TS016 | 未找到人工原文 | 0 | 补完整对话 |
| set2 | TS034 | 已归档；行动记录 9 + 37 | 5 | 不用重复上传已有版本；有新一轮可另存来源 |
| set2 | TS033 | 已归档；行动记录 101 | 4 | 不用重复上传已有版本；有新一轮可另存来源 |
| set2 | TS035 | 未找到人工原文 | 0 | 补完整对话 |
| set3 | TS022 | 未找到人工原文 | 0 | 补完整对话 |
| set3 | TS047 | 未找到人工原文 | 0 | 补完整对话 |
| set4 | TS007 | 只有 11 条候选片段，缺完整原文 | 11 | 补完整对话 |
| set4 | TS026 | 未找到人工原文 | 0 | 补完整对话 |
| set4 | TS021 | 未找到人工原文 | 0 | 补完整对话 |
| set5 | TS038 | 未找到人工原文 | 0 | 补完整对话 |
| set5 | TS046 | 未找到人工原文 | 0 | 补完整对话 |
| set5 | TS032 | 已归档；行动记录 100 | 5 | 不用重复上传已有版本；有新一轮可另存来源 |

## 完整性与审核边界

- TS032：100 条行动记录中有 `mo`、`yes and ni` 两个未确定标签；原文已经保留，不能擅自补成标准答案。
- TS033：101 条行动记录，包括一次未编号的失败交卷。历史人工对话长度超出当前 100 问规则，不删去原文。
- TS034：两次尝试分别 9、37 条行动记录；第二次 Q6 的后续更正已保留，不能把该更正误认成 Q7 的答复。
- TS007：原始来源名为 `turtle_soup_tiger_guessing_record.json`，仓库只有精选片段，没有该完整文件。11 条均保留在 active，但仍待人工确认。
- TS022 的 94 条、TS047 的 125 条 active 示例来自 AI 实验/审核等资料；数量多不代表已有人工原始问答。
- 本次列出的题目 active 示例中没有 `human_confirmed: true`。人工来源、AI 审核、人工最终确认是不同状态。

## 新链接读取状态

- [新 ChatGPT 分享](https://chatgpt.com/share/6ae2bbf3-51a8-83ee-89a6-8df90cff3e4b)：HTTP 403；尚未提取任何消息或确认题号。
- [set1](https://app.notion.com/p/Set-1-result-4079ebc0e9b0801d85adc2c2137ee811?pvs=21)：未读到问答正文，不能确认是否含完整人工 trajectory。
- [set2](https://app.notion.com/p/Set-2-Result-4079ebc0e9b08064b40ee14db0e64469?pvs=21)：未读到问答正文，不能确认是否含完整人工 trajectory。
- [set3](https://app.notion.com/p/Set-3-Result-4079ebc0e9b080c8ac0df21a3b2b8d05?pvs=21)：未读到问答正文，不能确认是否含完整人工 trajectory。
- [set4](https://app.notion.com/p/Set-4-Result-4079ebc0e9b080c5afe8ea0f7b44c422?pvs=21)：未读到问答正文，不能确认是否含完整人工 trajectory。

## 应提交的位置

将对应对话导出为 Markdown/文本/JSON，保留完整顺序、Host 回答、纠正和最终提交，再使用：

```sh
python3 scripts/host_reference.py init --puzzle TS038 \
  --source-id 20261029_aurora_ts038 --file /path/to/TS038.md

# 同一对话含多题：题号按实际内容填写，只保存一份原文。
python3 scripts/host_reference.py init --puzzle TS013,TS014,TS015,TS016 \
  --source-id 20261029_aurora_set1 --file /path/to/set1.md
python3 scripts/host_reference.py validate
```

入口为 `data/host_reference/inbox/TSxxx/<source-id>/`，多题为 `inbox/multi/<source-id>/`。检查 `source.json` 的角色映射是否符合实际。上传后再审核、分段并绑定；不会自动进入 Host prompt。

本次仅新增核对清单及其 JSON；没有导入未能读取的聊天，没有修改 active Host，也没有启动实验。

机器可读清单：[aurora_submission_inventory_20261029.json](../data/host_reference/reviews/aurora_submission_inventory_20261029.json)。
