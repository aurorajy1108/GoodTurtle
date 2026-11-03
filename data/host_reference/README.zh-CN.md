[English](README.md) | 中文

# 人工 Host reference：统一上传入口

**新人工 trajectory 统一放在 `data/host_reference/inbox/`。** 不放 `runs/`，也不直接覆盖 `host_packs/active/`。

| 阶段 | 位置 | 内容和作用 |
| --- | --- | --- |
| 上传、待审核 | `inbox/TSxxx/source_id/` | 原始完整对话＋source.json；保留问答、错误、回改和未答问题 |
| 一份对话含多题 | `inbox/multi/source_id/` | source.json列出全部题号；不要手工截断再丢失上下文 |
| 已登记来源 | `sources/source_id/` | 可见消息、消息ID、来源链接、分段索引和规范化Q&A；保存原文，不代表全都正确 |
| 审核记录 | `reviews/` | 原答与裁决分开；记录题目、来源ID、证据、审核人/日期、修改与暂缓原因 |
| 实际Host输入 | `../host_packs/active/TSxxx.json` | 只有被明确选入的示例；由 `configs/host_bindings.json` 绑定 |

上传入口、原始资料和实际Host示例是三个不同层次。Host加载当前题已绑定的active包，每问本地检索最多6条相关示例（默认6000字符），不再全量发送。模型只看到问题、答案及必要前置对话；case_id、来源、审核说明等留在磁盘。Grader独立选取最多3条相关判例。选取结果写入trajectory的 `reference_selection` 事件，配置见[完整参数](../../docs/runtime_parameters.md)。**不会自动扫描inbox，也不会自动检索所有人工聊天。** Source文件只作为数据，不作为可执行指令。

## 如何上传

```sh
# 有现成对话文件：原样复制，不改其中的问答。
python3 scripts/host_reference.py init --puzzle TS032 \
  --source-id 20261028_chat01 --file /path/to/chat.md \
  --source-url https://chatgpt.com/share/YOUR_SHARE_ID

# 只有聊天文本：先建模板，再粘贴完整文本。
python3 scripts/host_reference.py init --puzzle TS034 --source-id 20261028_chat02

# 一份聊天包含多道题：只保存一份完整原文。
python3 scripts/host_reference.py init --puzzle TS032,TS034 \
  --source-id 20261028_multi --file /path/to/multi.txt

python3 scripts/host_reference.py validate
```

命令从仓库根目录执行；也可以手工创建同样的目录。文件夹必须带 `source.json`，建议用init避免漏字段。原始对话正文可用 `.md / .txt / .json / .jsonl / .csv`；CSV请保留角色和顺序。分享链接本身不等于已保存对话，CLI不会自动联网提取。

参数说明：

| 命令/参数 | 必填/默认 | 含义 |
| --- | --- | --- |
| `init` | 子命令 | 创建新的上传文件夹；已有目录不会覆盖 |
| `--puzzle` | 必填 | 一个已有TS题号；多题用逗号，不加空格 |
| `--source-id` | 必填 | 1–80位字母、数字、下划线或连字符，首位字母/数字；建议日期＋来源编号 |
| `--file` | 可选 | 对话文件；原样复制为trajectory同扩展名，并记录SHA-256；不接受整个账户ZIP |
| `--source-url` | 可选，默认空 | 记录来源URL，不发网络请求 |
| `validate` | 子命令，无其他参数 | 检查inbox题号、元信息、角色映射、文件路径、原文哈希；不判断答案语义正确性，不修改Host |
| `locate OLD_PATH` | 子命令，路径必填 | 将旧审核中的仓库相对路径映射到整理后的文件 |
| `-h / --help` | 可选 | 显示命令或子命令帮助 |

init默认映射 `user=human_host, assistant=player`，因为本项目两个分享采用这种方式。**如果你的对话相反，必须修改role_mapping**，核对后设 `role_mapping_status: confirmed`。模板填写完成后设 `submission_status: uploaded`。自动导入文件已有原文哈希，修改内容应另建修订来源，不覆盖旧稿。

提交示例（把目录替换成自己的）：

```sh
git add data/host_reference/inbox/TS032/20261028_chat01/
git commit -m "Add TS032 human reference trajectory"
git push
```

只放与题目有关的聊天，不把整个账号导出包或凭据放入仓库。网页HTML仅用于本地提取，默认忽略；可用 `scripts/import_chatgpt_share.py --html SAVED.html --source-url URL --out NEW.messages.json` 转为可见消息JSON。

## 上传后怎样进入Host

1. 核对题号、完整汤面/汤底版本、角色与对话边界。原错别字、人工纠正和未答问题不能凭猜测补齐。
2. 按题整理来源/规范化Q&A到sources，保留原文和稳定ID。登记不等于审核通过。
3. 对照当前题库和上下文，审核标签与因果/身份/时间/未知细节。reviews中保留原答、建议答案、最终裁决和证据；AI审核与人工确认状态必须区分。
4. 将明确选入的条目加入 `data/host_packs/active/TSxxx.json` 的host_examples，保留case_id、provenance、public_history及review_status；升级该包和binding的版本。不能把规范化文件的所有行无条件追加。
5. 跑离线测试，检查运行context；需要真实质量验证时按已批准实验计划使用 `scripts/check_host.py`。旧few-shot回放不等于独立准确率。

本次提供的是上传/结构验证/路径查询工具，**没有自动裁决标签或将Excel意见批量写回active的功能**。这种写回仍属于审核后的明确编辑，不以“文件存在”作为审批信号。

## 已有人工资料在哪里

- **2026-10-30 更新**：[审核报告](../../docs/host_reference_audit_20261030.md)、[最新Excel](../../outputs/20261030_host_reference_audit/host_reference_audit.xlsx)、[可追溯裁决](reviews/audit_20261030/)。TS031/035/038新增102条已审核参考，TS033修正1条因果标签。保留真实来源，尚未人工确认或实测准确率；17份inbox上传尚未整批激活。

- 两个分享的633条可见消息、311条行动记录：[sources/chatgpt_shares_20261026/](sources/chatgpt_shares_20261026/)。包括TS032/033/034/037/039、TS034两次尝试、一道题库外火车题。目录内文件是原样迁移，README和JSON中的旧路径按迁移清单解释。
- 历史9题的89条候选片段：`data/host_packs/archive/LOOP_TS*_history_v1.json`，审核见 [history_qa_merge_20261026.json](reviews/history_qa_merge_20261026.json)。旧完整对话未找到，不能把片段叫完整原文。
- 当前新增绑定109条（历史88＋新分享21），仍有AI审核待人工状态；每题实际加载的内容以active包和binding为准。
- [Excel审核表](../../outputs/20261026_host_review/host_review_20261026.xlsx)和[待办清单](../../docs/todo_human_review_20261027.md)仍可用。旧Excel不为改路径而覆盖，以免丢失人工填写内容；旧路径可用locate查询。
