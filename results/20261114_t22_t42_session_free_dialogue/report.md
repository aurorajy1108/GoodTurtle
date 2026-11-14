# T22 / T42 实验结果（2026-11-14）

主分析共31局，全部完成，无未恢复中断。T22：五轮baseline＋三个after-A session，共20局，另5局双agent free_dialogue；T42：1局baseline＋5局双agent free_dialogue。

## 汇总

分数为最终提交的partial score；完整解出要求100%。过程最高分单独列出。

| 题目 | 条件 | n | 最终平均分 ± 样本SD | 过程最高分均值 | 比baseline | 完整解出 | 平均提交数 |
|---|---|---:|---:|---:|---:|---:|---:|
| TS022 | baseline | 5 | 26.0% ± 13.9% | 28.0% | +0.0个百分点 | 0/5 | 100.0 |
| TS022 | after TS047 (positive) | 5 | 27.0% ± 27.5% | 29.0% | +1.0个百分点 | 0/5 | 100.0 |
| TS022 | after TS045 (negative) | 5 | 21.0% ± 20.1% | 26.0% | -5.0个百分点 | 0/5 | 100.0 |
| TS022 | after TS019 (irrelevant) | 5 | 28.0% ± 25.9% | 28.0% | +2.0个百分点 | 0/5 | 100.0 |
| TS022 | multi-agent free_dialogue | 5 | 36.0% ± 39.7% | 36.0% | +10.0个百分点 | 1/5 | 98.6 |
| TS042 | baseline | 1 | 50.0% ± — | 50.0% | +0.0个百分点 | 0/1 | 100.0 |
| TS042 | multi-agent free_dialogue | 5 | 63.0% ± 18.9% | 64.0% | +13.0个百分点 | 0/5 | 100.0 |

## 每轮最终分

T22五轮baseline/after-A的轮号为整理编号；第一轮来自先前四局批次，后四轮来自追加批次。MAS的轮号为其独立重复编号，未与CL作随机数配对。

| 轮次 | T22 baseline | after TS047 positive | after TS045 negative | after TS019 irrelevant | T22 MAS（独立重复） |
|---:|---:|---:|---:|---:|---:|
| 1 | 10.0% | 25.0% | 25.0% | 40.0% | 10.0% |
| 2 | 15.0% | 10.0% | 0.0% | 0.0% | 10.0% |
| 3 | 40.0% | 10.0% | 0.0% | 50.0% | 100.0% |
| 4 | 25.0% | 75.0% | 40.0% | 50.0% | 50.0% |
| 5 | 40.0% | 15.0% | 40.0% | 0.0% | 10.0% |

| T42条件 | 最终分 | 提交次数 | 完整解出 |
|---|---:|---:|---|
| baseline #1 | 50.0% | 100 | 否 |
| multi-agent free_dialogue #1 | 35.0% | 100 | 否 |
| multi-agent free_dialogue #2 | 60.0% | 100 | 否 |
| multi-agent free_dialogue #3 | 75.0% | 100 | 否 |
| multi-agent free_dialogue #4 | 60.0% | 100 | 否 |
| multi-agent free_dialogue #5 | 85.0% | 100 | 否 |

## 结果解读

T22 baseline最终平均分26%，after TS047为27%（+1个百分点），after TS045为21%（−5个百分点），after TS019为28%（+2个百分点）。当前五次重复的分数波动较大，不能据此确认预设的positive/negative/irrelevant关系。

T22双agent最终平均分36%，高于baseline 10个百分点；其中第3次在93次外部提交时完整解出，其余4次耗尽100次额度。T42双agent平均63%，单次baseline为50%；T42所有6局均未完整解出。T42 baseline只有1次，比较仅是描述性结果。

MAS增加内部讨论和模型调用，不能将这里的差值解释为同计算量下的优势。自动Host/Grader评分仍待人工语义复核。

## 原A及最早session（附录，不并入主比较）

| A | 类型 | 最终分 | 提交数 |
|---|---|---:|---:|
| TS019 | session | 15.0% | 100 |
| TS019 | source | 75.0% | 100 |
| TS045 | session | 40.0% | 100 |
| TS045 | source | 55.0% | 100 |
| TS047 | session | 60.0% | 100 |
| TS047 | source | 80.0% | 100 |

三个A各只有一份原始100次提交轨迹；主分析的15局session，各条件5次独立分支，已校验同一A的源调用前缀哈希一致。最早session三局无同轮baseline，所以仅列附录。

## 实验配置与恢复记录

- Player及MAS伙伴：DeepSeek Flash，thinking disabled；Host/Grader：DeepSeek v4 Pro，thinking enabled/high。
- 每局目标题共100次外部提交额度；不成功的final也计入额度。
- session继承原A的Player会话，边界揭示A答案；Host/Grader使用目标题独立会话。
- free_dialogue使用两名独立agent、共享公开讨论、互补角色、adaptive调度，每次外部提交前至多4条内部消息。
- 13局在充值后续接：11局HTTP 402、2局Host网络中断。原调用记录、会话位置和剩余额度保留。原中断快照不重复计入结果。
- 已取消的新source、早期direct/answer_only探索和离线dry-run不并入这次主比较。

## 费用与原始记录

31局目标题可计算的峰时参考API估算合计 $14.7457；13条失败尝试没有usage，实际账单未知。该金额不包括原A费用，不是充值扣款金额。

[逐局CSV](games.csv) · [汇总CSV](summary.csv) · [完整逐局JSON（含最终答案和评分）](games.json) · [汇总JSON](summary.json)

| 题目 | 条件 | 轮次 | 原始记录 |
|---|---|---:|---|
| TS022 | baseline | 1 | [TS022_r01](trajectories/TS022/baseline/r01/trajectory.md) |
| TS022 | baseline | 2 | [TS022_r01](trajectories/TS022/baseline/r02/trajectory.md) |
| TS022 | baseline | 3 | [TS022_r01](trajectories/TS022/baseline/r03/trajectory.md) |
| TS022 | baseline | 4 | [TS022_r01](trajectories/TS022/baseline/r04/trajectory.md) |
| TS022 | baseline | 5 | [TS022_r01](trajectories/TS022/baseline/r05/trajectory.md) |
| TS022 | after TS047 (positive) | 1 | [S3_TS047_TS022_TS047_TS022_r02_session](trajectories/TS022/after_TS047_session/r01/trajectory.md) |
| TS022 | after TS047 (positive) | 2 | [S3_TS047_TS022_TS047_TS022_r03_session](trajectories/TS022/after_TS047_session/r02/trajectory.md) |
| TS022 | after TS047 (positive) | 3 | [S3_TS047_TS022_TS047_TS022_r04_session](trajectories/TS022/after_TS047_session/r03/trajectory.md) |
| TS022 | after TS047 (positive) | 4 | [S3_TS047_TS022_TS047_TS022_r05_session](trajectories/TS022/after_TS047_session/r04/trajectory.md) |
| TS022 | after TS047 (positive) | 5 | [S3_TS047_TS022_TS047_TS022_r06_session](trajectories/TS022/after_TS047_session/r05/trajectory.md) |
| TS022 | after TS045 (negative) | 1 | [S3_TS045_TS022_TS045_TS022_r02_session](trajectories/TS022/after_TS045_session/r01/trajectory.md) |
| TS022 | after TS045 (negative) | 2 | [S3_TS045_TS022_TS045_TS022_r03_session](trajectories/TS022/after_TS045_session/r02/trajectory.md) |
| TS022 | after TS045 (negative) | 3 | [S3_TS045_TS022_TS045_TS022_r04_session](trajectories/TS022/after_TS045_session/r03/trajectory.md) |
| TS022 | after TS045 (negative) | 4 | [S3_TS045_TS022_TS045_TS022_r05_session](trajectories/TS022/after_TS045_session/r04/trajectory.md) |
| TS022 | after TS045 (negative) | 5 | [S3_TS045_TS022_TS045_TS022_r06_session](trajectories/TS022/after_TS045_session/r05/trajectory.md) |
| TS022 | after TS019 (irrelevant) | 1 | [S3_TS019_TS022_TS019_TS022_r02_session](trajectories/TS022/after_TS019_session/r01/trajectory.md) |
| TS022 | after TS019 (irrelevant) | 2 | [S3_TS019_TS022_TS019_TS022_r03_session](trajectories/TS022/after_TS019_session/r02/trajectory.md) |
| TS022 | after TS019 (irrelevant) | 3 | [S3_TS019_TS022_TS019_TS022_r04_session](trajectories/TS022/after_TS019_session/r03/trajectory.md) |
| TS022 | after TS019 (irrelevant) | 4 | [S3_TS019_TS022_TS019_TS022_r05_session](trajectories/TS022/after_TS019_session/r04/trajectory.md) |
| TS022 | after TS019 (irrelevant) | 5 | [S3_TS019_TS022_TS019_TS022_r06_session](trajectories/TS022/after_TS019_session/r05/trajectory.md) |
| TS022 | multi-agent free_dialogue | 1 | [TS022_r01_free_dialogue](trajectories/TS022/free_dialogue/r01/trajectory.md) |
| TS022 | multi-agent free_dialogue | 2 | [TS022_r02_free_dialogue](trajectories/TS022/free_dialogue/r02/trajectory.md) |
| TS022 | multi-agent free_dialogue | 3 | [TS022_r03_free_dialogue](trajectories/TS022/free_dialogue/r03/trajectory.md) |
| TS022 | multi-agent free_dialogue | 4 | [TS022_r04_free_dialogue](trajectories/TS022/free_dialogue/r04/trajectory.md) |
| TS022 | multi-agent free_dialogue | 5 | [TS022_r05_free_dialogue](trajectories/TS022/free_dialogue/r05/trajectory.md) |
| TS042 | baseline | 1 | [TS042_r01](trajectories/TS042/baseline/r01/trajectory.md) |
| TS042 | multi-agent free_dialogue | 1 | [TS042_r01_free_dialogue](trajectories/TS042/free_dialogue/r01/trajectory.md) |
| TS042 | multi-agent free_dialogue | 2 | [TS042_r02_free_dialogue](trajectories/TS042/free_dialogue/r02/trajectory.md) |
| TS042 | multi-agent free_dialogue | 3 | [TS042_r03_free_dialogue](trajectories/TS042/free_dialogue/r03/trajectory.md) |
| TS042 | multi-agent free_dialogue | 4 | [TS042_r04_free_dialogue](trajectories/TS042/free_dialogue/r04/trajectory.md) |
| TS042 | multi-agent free_dialogue | 5 | [TS042_r05_free_dialogue](trajectories/TS042/free_dialogue/r05/trajectory.md) |
