# 六道日语来源题：单次难度筛选

以完整因果叙事为成功条件；必须首次完整解出前提问 **31 次或更多**，并且没有影响结果的重大 host 错答/泄漏，才列为暂定保留。一次试跑不足以证明稳定难度。人工审核尚未完成。

Solver GPT-6 Sol (high)；host GPT-6.1 Sol；v0.5.1；每题独立上下文；无次数上限；错误交卷继续。问题与交卷分别计数。

| ID | 日语来源 | 状态 | 提问数 | 交卷数 | 完整解出 | 暂定保留 |
| --- | --- | --- | ---: | ---: | --- | --- |
| [JP001](JP001_r2/trajectory.md) | [難問と、答え合わせ](https://late-late.jp/mondai/show/13003) | running | 30 | 0 | None | False |
| [JP002](JP002/trajectory.md) | [犯人と暮らした一週間](https://late-late.jp/mondai/show/18149) | parked_for_fair_scheduling | 110 | 4 | None | False |
| [JP003](JP003/trajectory.md) | [田中の着膨れしない暴漢対策](https://late-late.jp/mondai/show/17998) | completed | 73 | 4 | True | True |
| [JP004](JP004_r2/trajectory.md) | [Youか一億円か](https://late-late.jp/mondai/show/10912) | running | 25 | 0 | None | False |
| [JP005](JP005/trajectory.md) | [ʕ•ᴥ•ʔ](https://late-late.jp/mondai/show/9571) | running | 75 | 4 | None | False |
| [JP006](JP006/trajectory.md) | [不敗者](https://late-late.jp/mondai/show/21352) | running | 39 | 0 | None | False |

无效局单独保留，不作为失败或难度成绩：
- [JP001](JP001/trajectory.md)：25 问，invalidated。修复 host 资料后换全新 solver 重跑；评分条件与 solver 提示不变。
- [JP004](JP004/trajectory.md)：25 问，invalidated。修复 host 资料后换全新 solver 重跑；评分条件与 solver 提示不变。

[全部可见问答（持续更新）](all_trajectories.md) · [来源提取审核](source_audit.md)

[候选英文汤面、汤底与来源说明](../../docs/nonenglish_candidates.md) · [Host 通用规则与验证](../../docs/host_v05.md)

所有候选保留 provenance、冻结输入、问答和交卷记录；未入选题不删除。只有已完成局的结果可以用于筛选。正在运行的局不计失败，未解出不等于难题。
