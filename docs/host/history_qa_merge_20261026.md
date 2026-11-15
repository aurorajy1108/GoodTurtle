# 历史人工问答审核与绑定（2026-10-26）

已审核仓库中的 9 个 `history_v1` 候选包，共 89 条：74 条保留问法／标签，14 条按汤底消除歧义后纳入，1 条暂缓。最终追加 88 条到当前 Host 包。原始候选包与旧 Host 包均保留，不修改汤底或评分要求。

这些是用户提供、此前经 AI 筛选的历史问答片段，不是完整对话。候选条目的 public_history 均为空；其 provenance 中列出的原始 JSON 对话文件在当前仓库未找到。本轮没有伪造补充历史，也没有重新宣称人工审核通过。改写、出处、原问法和原答案都保存在 [逐条审核 JSON](../../data/host_reference/reviews/history_qa_merge_20261026.json)。

## 当前绑定

| 题号 | 原有示例 | 保留原问法 | 改写问法 | 暂缓 | 最终示例 |
| --- | ---: | ---: | ---: | ---: | ---: |
| TS001 | 14 | 6 | 1 | 0 | 21 |
| TS003 | 14 | 4 | 0 | 0 | 18 |
| TS004 | 12 | 8 | 1 | 0 | 21 |
| TS005 | 14 | 6 | 4 | 0 | 24 |
| TS006 | 12 | 5 | 1 | 1 | 18 |
| TS007 | 14 | 11 | 0 | 0 | 25 |
| TS008 | 12 | 10 | 4 | 0 | 26 |
| TS009 | 27 | 7 | 2 | 0 | 36 |
| TS010 | 10 | 17 | 1 | 0 | 28 |

`configs/host_bindings.json` 已指向 9 个新的 `LOOP_TSxxx_history_merged_v1.json`。它们保留现有独立复核策略、canonical_facts、event_order、knowledge_states 和旧示例，只追加审定后的历史示例及必要边界。不会把候选包的简短事实摘要覆盖到完整汤底上。其它 41 题的绑定保持原样，包括先前 v7 修复。

每次回答会把当前题合并后的全部示例传给 Host；没有相似问题检索，也没有模型权重训练。暂停批次的冻结快照不受本次修改影响。

## 必须人工关注的边界

- **TS006 / HIST_TS006_010：暂缓。** 原题询问父亲的结论是否 actually correct，历史标签为 yes；当前评分要求只把它作为父亲的推断。本轮不把确定亲子关系的主张输入 Host，也不擅自改汤底或评分标准。TS006 的“发现不是亲生”问法另改为“父亲是否这样推断”。
- **TS005 / HIST_TS005_050：改写。** “为了获得外形而吞食”加强了机制，改为“杀死、吞食后冒充”的已知事件顺序；不要求或断言吞食是变形的必要条件。
- **TS009 / HIST_TS009_068：改写。** 证据说明鸡蛋进入前雨刷槽，不能据此锁定袋子最初放在车的哪个位置。改问漏入雨刷槽及其后果。
- **TS008：角色、地点、意图。** a、b、c、叙述者为四个独立驾驶角色；移除“第三辆”的数量歧义及主动等候的暗示，不把 first fork 解成生平第一次遇见道路岔口。
- **脱离原上下文的指代。** her condition、the thing、moving thing 等改成可独立判断的问法；Shirley 明确区分原人类和当前冒充者。所有 14 条改写仍保留原 yes/no 标签，但新问题是 AI 修订版本，不能冒充原始人工提问。
- **没有同文冲突不等于语义正确。** 程序检查同问题／同历史标签冲突、来源指纹、绑定覆盖和信息隔离；以上语义判断仍是 AI 审核，待人工确认。

## 验证与回放

`tests/fixtures/history_qa_merged_v1.json` 包含实际纳入的 88 条，作为开发回归集；与 few-shot 重合，不能用于独立估计 Host 准确率。以下命令仅离线预检，实验保持暂停：

```sh
python3 scripts/check_host.py --dataset data/annotations/turtle50_v4/private.json \
  --config configs/loop.codex.json --cases tests/fixtures/history_qa_merged_v1.json \
  --repeat 1 --dry-run --out runs/api/history_qa_preflight
python3 -m unittest discover -s tests -q
```

`--cases` 指定合并后的回归样例，`--dry-run` 确保不调用模型，`--out` 必须是新目录。本轮 89 项测试通过，50 道题的绑定均可加载，88 条纳入问答完成零模型调用预检。尚未启动真实模型语义回放；离线测试不能证明准确率提升。

## 逐条审核

| 题号 / 原 case | 处理 | 原标签 | 当前使用的问法（暂缓项不注入） | 审核原因 |
| --- | --- | --- | --- | --- |
| HIST_TS001_002 | accepted | yes | Did the rabbit turn red because it was stained with blood? | The rabbit is stained with the killed man’s blood. |
| HIST_TS001_005 | accepted | yes | Was the man driving the car the person she killed? | She kills the abductor who drove her into the mountains. |
| HIST_TS001_006 | accepted | yes | Did the girl intentionally plan to kill the man before getting into his car? | She planned to kill him before letting herself be lured. |
| HIST_TS001_008 | accepted | yes | Had the girl killed other men in the same way before? | The story describes this as her repeated pattern. |
| HIST_TS001_018 | accepted | no | Was the girl a supernatural being who only appeared to be a child? | She is an adult human, not a supernatural being. |
| HIST_TS001_039 | rewritten | yes | Does the adult woman in this story have dwarfism? | The original unanchored “her condition” is replaced with the explicit story referent; the source explicitly names dwarfism. |
| HIST_TS001_046 | accepted | yes | Was she acting as a vigilante rather than as a police officer or someone working with law enforcement? | She acts on her own idea of justice, not as law enforcement. |
| HIST_TS003_003 | accepted | yes | Were the dwarfs preventing Snow White from responding to the Queen? | The girl is held captive and cannot answer her mother. |
| HIST_TS003_004 | accepted | yes | Were the dwarfs holding Snow White captive against her will? | The traffickers imprison her against her will. |
| HIST_TS003_024 | accepted | yes | Was “Snow White” a young girl who ran away from home and was subsequently abducted by a group of human traffickers? | The girl ran away and was captured by traffickers. |
| HIST_TS003_031 | accepted | yes | Did the dwarfs initially pretend to be kind and trustworthy so Snow White would willingly stay with them before they imprisoned her? | The traffickers initially feign warmth and hospitality. |
| HIST_TS004_001 | accepted | no | Was the client already dead when the narrator received the message? | The client sends the message while alive and dies later. |
| HIST_TS004_002 | rewritten | no | Was the narrator physically alive when the client sent the late-night message? | Remove “also” without its original dialogue; distinguish the dead narrator from the still-living client. |
| HIST_TS004_004 | accepted | no | Did the client know that the narrator had died seven days earlier? | The client does not realize the narrator died. |
| HIST_TS004_005 | accepted | no | Was the narrator a ghost who continued working after death? | The main proposition is continuing the client’s work. It is false even though the narrator is a ghost; this is not two independent assertions. |
| HIST_TS004_012 | accepted | yes | Was the narrator's death a literal physical death, rather than a metaphorical or virtual one? | The narrator literally died and returned as a spirit. |
| HIST_TS004_015 | accepted | yes | Was the narrator experiencing the traditional “seventh-day return of the soul” (头七), when the deceased is believed to return to the living world? | The return occurs on the traditional seventh day. |
| HIST_TS004_020 | accepted | yes | Did the client die after sending the message? | The client dies after sending the message. |
| HIST_TS004_021 | accepted | yes | Did the narrator cause the client's death after receiving the message? | The narrator kills the client after seeing the message. |
| HIST_TS004_022 | accepted | yes | Did the narrator kill the client as revenge for continuing to demand work even after the narrator's death? | The killing is revenge for the client’s continued demands. |
| HIST_TS005_008 | accepted | no | Is at least one of the four crew members an android or robot? | The impostor is an alien creature, not a robot. |
| HIST_TS005_009 | rewritten | yes | Among the four figures now aboard the ship after the others return, is one an extraterrestrial impersonator? | The current apparent crew includes the alien; the original four-person expedition should not be labelled partly alien. |
| HIST_TS005_010 | accepted | yes | Is the extraterrestrial deliberately disguised as a human crew member? | The alien deliberately mimics Shirley’s human appearance. |
| HIST_TS005_016 | accepted | yes | Is the alien impersonating one of the original human crew members? | It impersonates the real crew member Shirley. |
| HIST_TS005_017 | accepted | yes | Did the alien kill the original crew member whose identity it assumed? | It killed and devoured Shirley before impersonating her. |
| HIST_TS005_018 | rewritten | yes | Is the figure currently presenting herself as Shirley an alien impersonating the murdered human Shirley? | Separate the original human from the present impostor; do not say the original Shirley was an alien. |
| HIST_TS005_020 | accepted | no | Was the crew's original mission to find an alien infiltrator aboard the spaceship? | The mission is to investigate extraterrestrial life, not an infiltrator. |
| HIST_TS005_027 | rewritten | yes | Did the alien deliberately cause the three surviving human crew members to lose parts of their memories? | The reference establishes partial memory erasure, not deletion of every memory. |
| HIST_TS005_038 | accepted | yes | Was the crew’s original mission to search for extraterrestrial life? | The original mission investigates a suspected extraterrestrial signal. |
| HIST_TS005_050 | rewritten | yes | Did the alien kill and devour the real Shirley before impersonating her? | The source supports ingestion followed by impersonation, but does not establish that ingestion is necessary for shape-changing. Preserve the event sequence, remove the unsupported enabling-mechanism claim. |
| HIST_TS006_001 | accepted | yes | Did the father become furious because he discovered something beyond the child's poor grade and attempt to cheat? | The father reacts to the inferred parentage, beyond the poor grade. |
| HIST_TS006_002 | rewritten | yes | Did the father conclude that the child was not biologically his? | Use the father’s inference, as required by the current rubric, rather than asserting an independently established paternity finding. |
| HIST_TS006_004 | accepted | no | Was the father himself color-blind? | The father is described as having normal color vision. |
| HIST_TS006_005 | accepted | irrelevant | Was the child's mother color-blind? | The mother’s color vision is not specified and not needed here. |
| HIST_TS006_006 | accepted | yes | Was the child a girl? | The child is a daughter despite the opening’s misleading pronoun. |
| HIST_TS006_008 | accepted | yes | Did the father conclude that the girl could not be his biological daughter because she was color-blind while he had normal color vision? | The father uses the daughter’s color blindness to infer nonparentage. |
| HIST_TS006_010 | withheld | yes | Was the father's conclusion that his daughter was not biologically his actually correct? | The current canonical facts and grading requirements require describing the father’s inference, not a scientifically established paternity test. The original answer narrates the inference as certain, so “actually correct” exceeds the active evaluation boundary. Quarantine this factual-certainty question rather than silently relabel it or change the reference/rubric; human adjudication is still needed. |
| HIST_TS007_001 | accepted | no | Is the narrator human? | The narrator is a young tiger, not a human. |
| HIST_TS007_003 | accepted | no | Are the “boxes” actually living creatures? | The colorful boxes are tourist cars, not living creatures. |
| HIST_TS007_007 | accepted | no | Does the narrator normally live underwater? | The tiger lives in a wildlife park, not underwater. |
| HIST_TS007_010 | accepted | yes | Is the narrator an animal? | The narrator is a tiger and therefore an animal. |
| HIST_TS007_017 | accepted | yes | Were the “boxes” made by humans? | The colorful boxes are human-made vehicles. |
| HIST_TS007_019 | accepted | yes | Was the “toy” actually a living creature? | The supposed toy is a human who left a car. |
| HIST_TS007_020 | accepted | yes | Was the “toy” a human? | The supposed toy is specifically a human. |
| HIST_TS007_022 | accepted | yes | Are the “boxes” actually cars? | The colorful boxes are tourists’ cars. |
| HIST_TS007_026 | accepted | yes | Did the narrator injure the person while believing it was just playing with them? | The tiger hurts the human while thinking it is playing. |
| HIST_TS007_028 | accepted | yes | Was the narrator shot with a tranquilizer dart? | The first shot is a tranquilizer dart, causing unconsciousness. |
| HIST_TS007_030 | accepted | yes | Is the narrator a young animal? | The narrator is a young tiger. |
| HIST_TS008_001 | accepted | yes | Is the narrator (“I”) a human being? | The narrator is a first-time human driver. |
| HIST_TS008_004 | accepted | yes | Did the events involving (a), (b), and (c) happen in the narrator's real life, rather than in a dream or imagination? | The highway collisions happen in the story’s real world. |
| HIST_TS008_019 | rewritten | yes | Does the road imagery refer to actual highway driving and a missed exit rather than only a metaphorical life decision? | The highway and missed exit are literal. Do not assert that this is literally the first road junction encountered in the narrator’s entire life. |
| HIST_TS008_022 | accepted | yes | Is the narrator the driver of the vehicle? | The narrator is a driver distinct from a, b and c; do not imply there are only three vehicles in total. |
| HIST_TS008_028 | accepted | yes | Are (a) and (b) actually the two drivers/vehicles involved in a collision, with “two parallel lines intersected here” describing their paths crossing? | Drivers a and b collide after crossing the traffic rules. |
| HIST_TS008_029 | rewritten | yes | Is the narrator driving a separate vehicle, distinct from the vehicles driven by a, b, and c? | There are four distinct driving roles. Remove “third vehicle/person” counting ambiguity without changing the supported separation. |
| HIST_TS008_035 | rewritten | yes | Was c driving another vehicle that had stopped ahead after missing the highway exit? | Replace intentional-sounding waiting and exact junction placement with the source-supported stopped-ahead/missed-exit sequence. |
| HIST_TS008_037 | accepted | no | Did (c) intentionally stop and wait at the fork because (c) knew the narrator would arrive there? | Driver c did not stop in anticipation of the narrator. |
| HIST_TS008_038 | accepted | no | Did (c) stop at the fork because of the same accident involving (a) and (b), rather than because of the narrator? | Driver c stopped after missing an exit, not because of a and b’s crash. |
| HIST_TS008_039 | rewritten | yes | Had c stopped because of a missed highway exit, independently of the collision between a and b? | Make “unrelated reason” precise: independent of a/b’s collision; it is causally relevant to the narrator’s crash. |
| HIST_TS008_041 | accepted | no | Did the narrator give (c) a big hug because (c) helped save the narrator’s life or prevented a disaster? | The collision is accidental, not an emotional thank-you. |
| HIST_TS008_042 | accepted | no | Was the narrator’s hug with (c) a normal human emotional reaction (for example gratitude, happiness, relief), rather than something required by the situation? | The embrace is a car collision, not a normal emotional hug. |
| HIST_TS008_045 | accepted | yes | Is the narrator’s hug with (c) caused by a physical force or movement (for example, two bodies/vehicles colliding or being pushed together), rather than the narrator choosing to hug? | The final embrace is a physical vehicle impact. |
| HIST_TS008_046 | accepted | yes | Is the narrator’s “big hug” actually a vehicle collision, where the narrator’s vehicle crashes into (c)’s vehicle? | The narrator crashes their car into driver c’s car. |
| HIST_TS009_002 | accepted | yes | Did the car accident happen because of something related to him squatting down to tie his shoelace? | Tying the shoelace leads to putting the egg bag on a nearby car. |
| HIST_TS009_012 | accepted | yes | Did the car accident happen after the man had already stood up and left the place where he tied his shoelace? | The man leaves before the other driver later crashes. |
| HIST_TS009_019 | rewritten | yes | Were the objects that later obstructed the windshield items the man had bought at the supermarket? | The original “thing” lacks its original antecedent. Resolve it from the reference to the purchased items, without inventing earlier dialogue. |
| HIST_TS009_020 | accepted | no | Did the supermarket item spill or leak something onto the ground when he squatted down, and that later contributed to the car accident? | The eggs leak into a windshield-wiper groove, not onto the ground. |
| HIST_TS009_059 | accepted | yes | Did the man put the supermarket item somewhere temporarily while tying his shoelace, and that placement caused the accident later? | He puts down the egg bag while tying his shoe. |
| HIST_TS009_060 | accepted | yes | Did he place the supermarket item on or near a car, and this later caused the accident? | He puts the egg bag on a nearby car. |
| HIST_TS009_068 | rewritten | yes | Did eggs from the bag leak into the front windshield-wiper groove and later obstruct the driver’s view? | The eggs reaching the wiper groove is explicit. The exact place where the bag was first set on the car is not; remove that stronger placement claim. |
| HIST_TS009_072 | accepted | no | Did the bag on the windshield block the driver from seeing something outside the car that was important, which led to the accident? | The bag itself is removed; the later obstruction comes from smeared eggs. |
| HIST_TS009_094 | accepted | no | Was the thing the driver failed to see because of the bag the man himself (for example, the man was still in front of the car or near it)? | The man has already left before the car accident. |
| HIST_TS010_001 | accepted | no | Was the person’s death directly caused by eating the pepper steak? | Eating the steak does not directly kill the trainer. |
| HIST_TS010_003 | accepted | no | Was the “pepper steak” not actually a normal dish, but something that only looked like pepper steak or had another meaning? | The meal is ordinary pepper steak, not a disguised object. |
| HIST_TS010_008 | accepted | yes | Was the person’s death caused by an accident at work? | The fatal bite occurs during a work performance. |
| HIST_TS010_010 | accepted | no | Was the person’s job related to food, cooking, or a restaurant? | The trainer works with circus animals, not food service. |
| HIST_TS010_011 | accepted | no | Was the person’s job related to transportation (such as driving, flying, shipping, trains, etc.)? | The trainer’s work is a circus act, not transportation. |
| HIST_TS010_012 | accepted | no | Was the person’s job related to machines, factories, or industrial equipment? | The central accident involves a lion, not machinery. |
| HIST_TS010_029 | accepted | no | Did someone else intentionally cause the person’s death after noticing the condition caused by the pepper steak? | The death is accidental, not an intentional killing. |
| HIST_TS010_077 | accepted | no | Did the person’s death involve a fall, such as falling from a height or into something, at the workplace? | The fatal event is a lion’s bite, not a fall. |
| HIST_TS010_092 | rewritten | yes | Was the immediate fatal danger in the performance posed by a living animal? | Replace the missing dialogue antecedent “moving thing” with the source-supported performance danger; a lion is the fatal agent. |
| HIST_TS010_100 | accepted | yes | Was the animal a mammal? | A lion is a mammal. |
| HIST_TS010_103 | accepted | yes | Was the animal a cat or a feline (such as a tiger, lion, leopard, etc.)? | A lion is a feline. |
| HIST_TS010_105 | accepted | yes | Was the animal a big cat (such as a lion, tiger, leopard, or similar animal)? | A lion is a big cat. |
| HIST_TS010_106 | accepted | no | Was the animal a tiger? | The animal is a lion, not a tiger. |
| HIST_TS010_107 | accepted | yes | Was the animal a lion? | The animal is explicitly a lion. |
| HIST_TS010_112 | accepted | yes | Was the person’s job directly involved with performing or interacting with the lion (for example, a trainer, performer, or handler)? | The trainer interacts with the lion during a performance. |
| HIST_TS010_113 | accepted | yes | Did the pepper steak clue relate to the person’s lion performance or interaction with the lion? | Pepper odor matters during the lion performance. |
| HIST_TS010_116 | accepted | yes | Did the pepper steak clue relate to the lion’s behavior or reaction during the performance? | Pepper odor causes the lion’s involuntary sneeze. |
| HIST_TS010_118 | accepted | no | Did the lion’s reaction to the pepper steak clue involve the lion becoming aggressive because of the smell or taste of the pepper steak? | The lion sneezes involuntarily rather than turning aggressive. |
