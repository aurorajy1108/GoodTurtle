# 2026-11-13 已完成结果与审核入口

本批 CL 已完成39/39局：3个固定A前题、36个B实验（3类前题×3个条件×4次重复）。MAS计算预算对照已完成7/8局。只取每批最后一个权威归档，续跑副本不算额外重复。

**核验范围：** 提交顺序、反馈唯一性、100次额度和强制交卷、分数加权与complete一致性、持久会话链、MAS公开聊天、计算上限和API费用逐项通过离线检查。所有模型Host判断和Grader语义评分仍为**待人工审核**；这份发布不声称人工已经逐条认定正确。

直接打开[index.html](index.html)浏览全部46局HTML轨迹；[runs.csv](runs.csv)和[runs.json](runs.json)提供逐局结果。每局的`verification.json`列出核验范围、原文件及发布文件哈希、已知元数据问题；`review_template.csv`供后续人工复核。`self_review.html`可查看私有自查，MAS另有`shared_dialogue.html`。

## CL Set1：固定B=TS013，重复4次

| 前题A | 直接做B | 仅给A完整答案 | 保留A会话再做B |
| --- | ---: | ---: | ---: |
| TS014 | 40.00% | 33.75% | 6.25% |
| TS015 | 36.25% | 56.25% | 45.00% |
| TS028 | 36.25% | 48.75% | 31.25% |

36局B均未达到完整解答标准，均使用100次提交额度。因此当前不能用“平均问题数相同”判断效率相同；这是到达预算上限的观测，不是成功所需问题数。上述百分比是最终partial score均值，不是成功率。三种relation是预设假说，n=4且每个A只有一份固定前缀，不作普遍迁移结论。

A即使未被Player完全解出，也在B前揭晓完整答案；所有session条件均核验这一揭晓与B的新100次额度。详见[完整CL分析](cl_analysis/analysis.md)及逐次分数向量。

## MAS TS038：共同计算预算上限

| 条件 | 完成局数 | 成功局数 | 已完成局partial score均值 |
| --- | ---: | ---: | ---: |
| solo | 2/2 | 0 | 12.50% |
| solo_review | 2/2 | 2 | 100.00% |
| mas | 2/2 | 1 | 75.00% |
| mas_review | 1/2 | 0 | 50.00% |

各局上限均为225次solver生成、77,696输出token及100次外部提交；这表示可用预算上限一致，实际输入、输出、缓存及费用并不相等。普通solo、solo自查、MAS均有2次结果；MAS自查仅1次完成，不能把它与其他完整条件当成平衡2×2结果作结论。样本很小，不足以证明哪种架构普遍更好。

未完成的`TS038_r01_mas_review`停在第79次外部提交后，下一轮A的review输出`finish_reason=length`，用完该次2048输出token；未生成第80次公开动作。它仍是基础设施/生成中断，不是失败样本或0分，排除记录见[excluded.json](excluded.json)。原断点保存在本地，可另行修复续跑；本次没有重采样这段已观察到的截断文本。

## 文件和费用边界

- 每局保留原始问答轨迹、评分、配置、提示词、汤面汤底及评分点；原始结果JSON不修改。旧solo/MAS的`stop_reason`可能把100次外部上限称为solver预算耗尽，`verification.json`已标注，解释时结合实际预算余量。
- `api_audit.jsonl.gz`保留每次调用的完整返回正文、用量、错误和请求哈希；重复的完整HTTP请求历史留在本地原归档，未上传约693MB的原始API日志。精简audit不能还原完整请求body；源日志哈希见每局核验文件。
- `included_games_cost_summary.json`只汇总这46个完成局，包括其中失败尝试；不包括未完成MAS局和单独Host门禁。未知usage/费用继续保留unknown，已知部分是标准API等价估计，不是实际账单。不要重复叠加旧恢复目录。
- `protocol/`含原计划及冻结代码指纹，逐局文件含实际冻结输入；本发布未复制整个运行时快照。运行新实验请使用仓库运行指南，不能将结果目录直接当成续跑目录。
- `.env.local`、API key、其他个人工作文件及未完成局的部分成绩未发布。

## 如何重建这份发布

在有完整本地原归档的机器上执行（无API调用）：

```bash
python3.11 scripts/publish_verified_results.py \
  --cl-study LATEST_CL_STUDY \
  --mas-run LATEST_MAS_2X2_RUN \
  --out results/NEW_RELEASE_DIRECTORY
```

`--cl-study`为含`continual/`的最后一个单批次study；`--mas-run`为含`plan.json`的最后一个四组对照根目录；`--out`必须为尚不存在的新目录。脚本先完整核验再导出，不调用模型、不改源归档、不会覆盖已有发布。
