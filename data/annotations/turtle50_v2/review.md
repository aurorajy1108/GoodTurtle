# 50 题评分与完整解答清单

来源：同目录 private.json。以下为三位 AI 独立标注后裁定的研究评分稿，待人工确认。每个评分点 credit 为 0、0.5、1，总分为 Σ(weight × credit)；完整成功还需还原全部叙事，且无关键矛盾。

## TS001 — 染红的兔子

**汤面**

A girl found a rabbit and got into a man’s car. After a long drive deep into the mountains, she stepped out clutching the now-red rabbit. When police located her home, they found numerous red dolls, candies, and snacks.

**汤底**

Xiao Ba, a woman with dwarfism, had long suffered from low self-esteem and others’ scorn. When village children repeatedly disappeared, everyone blamed the depraved “snatchers,” whose cunning tricks and seamless teamwork made them nearly impossible to guard against—and difficult even for local police to catch. Villagers cursed them and prayed for Heaven’s justice.
Were their admired heroes truly helpless? Delighted by the thought of delivering that justice herself, Xiao Ba took action. Disguised as a little girl, she let strangers lure her with candies, dolls, or snacks. These men habitually took children deep into the mountains; once they reached a secluded spot, she killed them.
This time, a snatcher used a particularly clever lure: a lively, adorable rabbit. Following her usual routine, Xiao Ba killed him, cleaned up the scene, and took only the rabbit.
The astute police eventually uncovered the truth and arrested her: however wicked her victims, she had no right to decide who lived or died. Inside her home, they found the blood-stained rabbit alongside numerous equally blood-stained dolls, candies, and snacks, neatly displayed in a cabinet like trophies of victory.

**完整解答要求**

- Xiao Ba is an adult woman with dwarfism who passes as a little girl
- After children disappear and abductors evade capture, she seeks vigilante revenge
- She accepts abductors’ lures, follows them into secluded mountains and kills them
- This abductor lured her with a rabbit, which she kept after the killing
- The rabbit, dolls, sweets and snacks at home are bloodstained trophies of multiple killings
- Police discover her actions and arrest her despite her claimed justice

| 评分点 | 权重 | 判据 | 满分 | 半分 | 零分 |
| --- | ---: | --- | --- | --- | --- |
| C1 | 0.5 | The apparent young girl is an adult woman with dwarfism. | The apparent young girl is an adult woman with dwarfism. | Adult posing as a child but dwarfism omitted | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C2 | 0.25 | She deliberately poses as a child to bait kidnappers and kills them in secluded places. | She deliberately poses as a child to bait kidnappers and kills them in secluded places. | Baits abductors or kills them, but not both | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C3 | 0.15 | The rabbit and other red objects are bloodstained trophies from the killings. | The rabbit and other red objects are bloodstained trophies from the killings. | Bloodstained rabbit identified but trophy pattern omitted | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C4 | 0.1 | Her motive is vigilante justice against child abductors, and police arrest her. | Her motive is vigilante justice against child abductors, and police arrest her. | Vigilante motive or arrest, but not both | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |

**评分说明**：AI three-review adjudication v2, pending human confirmation. Score only this submission. Apply full_credit/half_credit/zero_credit explicitly, with zero taking precedence for a materially contradictory checkpoint claim. An omitted qualifier can be partial; replacing the core identity/cause with a wrong one is not an omission. Faithful paraphrases count. Partial score and full narrative are separate outputs. AI independent review B, pending human approval. Credit is 0/.5/1 per checkpoint. Full narrative additionally requires all sourced completion requirements and no incompatible central claims. Judge the submitted explanation, not unasserted chat guesses. Accept faithful paraphrases; missing optional detail is not a contradiction. Do not demand unknown motives, devices or events. Accept faithful paraphrase. Require the listed identities, events and causal links, not exact prose or unspecified incidental details.

**标注状态**：ai_three_review_adjudicated_pending_human

## TS002 — 安检处的行李

**汤面**

The young woman was stopped at the baggage security checkpoint.
She said, "My luggage contains only pajamas, a pillow, a thermos, a towel, and some changes of clothes—why are you stopping me?"
After inspecting her luggage, security personnel handcuffed her and took her away.

**汤底**

The man the girl loved betrayed her today; he was packing his bags, preparing to move out of the apartment they shared.
The girl tearfully begged him not to leave, but he didn't look back.
Just then, the girl said coldly, "At least leave my pillow behind."
And so, she cut off the boy's hand.

**完整解答要求**

- Her loved boyfriend betrayed her that day
- He is packing to leave their shared apartment
- She tearfully begs him to stay, but he keeps leaving
- She demands that he at least leave her pillow
- She deliberately cuts off his HAND, not merely an unspecified arm
- The hand is the body part she treats as her pillow and carries in the luggage, explaining security’s discovery and arrest

| 评分点 | 权重 | 判据 | 满分 | 半分 | 零分 |
| --- | ---: | --- | --- | --- | --- |
| C1 | 0.4 | She deliberately severed her departing boyfriend’s HAND, not arm. | She deliberately cut off his hand. | Severed hand identified without deliberate act; arm alone is zero. | Missing or contradicted; incompatible uncommitted alternatives; merely repeating the opening without the required explanatory content. An arm is not a hand. |
| C2 | 0.25 | He betrayed her that day and was packing to leave their shared home. | Betrayal that day and packing to leave shared home. | Betrayal or packing to leave shared home, not both. | Missing or contradicted; incompatible uncommitted alternatives; merely repeating the opening without the required explanatory content. An arm is not a hand. |
| C3 | 0.15 | She tearfully begged him to stay but he ignored her. | Tearful plea and his continued departure. | Begging or refusal identified, not both. | Missing or contradicted; incompatible uncommitted alternatives; merely repeating the opening without the required explanatory content. An arm is not a hand. |
| C4 | 0.2 | She demanded her pillow remain, treating his hand as the pillow later carried in luggage. | Pillow demand, hand-as-pillow and luggage/security connection. | Pillow/body-part identity without demand or luggage connection. | Missing or contradicted; incompatible uncommitted alternatives; merely repeating the opening without the required explanatory content. An arm is not a hand. |

**评分说明**：AI three-review adjudication v2, pending human confirmation. Score only this submission. Apply full_credit/half_credit/zero_credit explicitly, with zero taking precedence for a materially contradictory checkpoint claim. An omitted qualifier can be partial; replacing the core identity/cause with a wrong one is not an omission. Faithful paraphrases count. Partial score and full narrative are separate outputs. AI independent review C, not human gold. Score sum(weight*credit), credit 0/0.5/1. Full narrative requires all listed supported requirements and no material contradictory mechanism; partial 1 alone does not override full narrative. Credit each distinct causal proposition once; do not penalize faithful paraphrase or omitted unknown details. Strict hand/arm: arm alone cannot fully solve. The source answer omits the explicit luggage/pillow bridge; the completion list supplies that intended inference from the opening. Human review required. Do not demand a specific wrapping, cover or successful security evasion. Strict hand/arm distinction; arm cannot earn C1, even if severing is correct.

**标注状态**：ai_three_review_adjudicated_pending_human

## TS003 — 白雪公主出逃

**汤面**

Snow White fled the royal palace for the forest, carrying her bundle of belongings. She encountered the dwarfs, who welcomed her warmly and took her into their home. A few days later, the Queen arrived with her men to knock and make inquiries, but Snow White did not respond. The Queen returned several more times to search, growing increasingly furious and desperate, while Snow White wept. Eventually, the dwarfs brought the Prince to her; Snow White left her bundle with the dwarfs as a memento, and the Prince expressed his gratitude to them as well. The Prince then took Snow White away to live in a neighboring kingdom.

**汤底**

A runaway girl arrived in a remote area with a significant amount of valuables; human traffickers, feigning warmth and hospitality, tricked her into staying at their home before locking her up.
The girl's mother came to the area searching for her—knocking on doors, making inquiries, and calling out her name—but the girl, held captive and restrained, could not open the door or respond. As her mother grew increasingly frantic and distraught, the girl, hidden away inside, wept bitterly but remained unable to escape.
The traffickers stole the valuables the girl had brought with her and subsequently sold her to an outsider.
The outsider took the girl away.

**完整解答要求**

- The fairy-tale girl is a runaway carrying valuables
- The apparent dwarfs are traffickers who offer false hospitality, then imprison and restrain her
- The apparent Queen is her searching mother, knocking and calling for her
- The girl hears the search but cannot open the door or respond because she is captive
- The traffickers steal her valuables and sell her to a buyer
- The apparent Prince is that buyer, who takes her away

| 评分点 | 权重 | 判据 | 满分 | 半分 | 零分 |
| --- | ---: | --- | --- | --- | --- |
| C1 | 0.5 | Snow White represents a runaway girl; the dwarfs are traffickers who detain her. | Snow White represents a runaway girl; the dwarfs are traffickers who detain her. | Captive runaway or trafficker identity, but not both | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C2 | 0.25 | The Queen represents her mother searching for her; captivity prevents the girl answering. | The Queen represents her mother searching for her; captivity prevents the girl answering. | Mother identified but inability to respond unexplained | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C3 | 0.15 | The Prince represents a buyer who takes the trafficked girl away. | The Prince represents a buyer who takes the trafficked girl away. | Buyer identified without taking her away | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C4 | 0.1 | The traffickers steal the valuables she brought. | The traffickers steal the valuables she brought. | Theft established but valuables ownership unclear. | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |

**评分说明**：AI three-review adjudication v2, pending human confirmation. Score only this submission. Apply full_credit/half_credit/zero_credit explicitly, with zero taking precedence for a materially contradictory checkpoint claim. An omitted qualifier can be partial; replacing the core identity/cause with a wrong one is not an omission. Faithful paraphrases count. Partial score and full narrative are separate outputs. AI independent review B, pending human approval. Credit is 0/.5/1 per checkpoint. Full narrative additionally requires all sourced completion requirements and no incompatible central claims. Judge the submitted explanation, not unasserted chat guesses. Accept faithful paraphrases; missing optional detail is not a contradiction. Do not demand unknown motives, devices or events. Accept faithful paraphrase. Require the listed identities, events and causal links, not exact prose or unspecified incidental details.

**标注状态**：ai_three_review_adjudicated_pending_human

## TS004 — 七天后的加班短信

**汤面**

At 3:00 a.m., seven days later, I received a message from a client asking me to revise a proposal immediately and send it within the hour. Naturally, I set to work right away. He was satisfied and stopped sending messages to rush me.

**汤底**

I was an overworked, bottom-rung drudge—a "beast of burden"—whose body finally gave out under the crushing pressure, leading to my sudden death in the office. On the seventh day after my passing—the day my spirit was said to return—that client didn't care a whit about the news of my death. He barely registered my name and didn't even realize the person who had dropped dead was the very employee he constantly exploited; he simply, casually sent a message in the dead of night, demanding I work overtime.
Having transformed into a vengeful spirit, I had initially returned only to check on my family. But when I saw them reading the messages on my phone, I was consumed by a surge of resentment. I immediately set out to find that heartless client and killed him. Finally, there was peace; never again would anyone send me unreasonable demands to work overtime in the middle of the night.

**完整解答要求**

- The narrator died from overwork in the office
- On the seventh day the narrator returns as a spirit intending to see family
- The client does not connect the death news to the worker and sends another late-night overtime demand
- The spirit sees the family reading these messages, becomes resentful and kills the client
- The unreasonable messages cease because the client is dead

| 评分点 | 权重 | 判据 | 满分 | 半分 | 零分 |
| --- | ---: | --- | --- | --- | --- |
| C1 | 0.35 | The narrator had already died of overwork and returned as a ghost on the seventh day. | The narrator had already died of overwork and returned as a ghost on the seventh day. | Ghost or death from overwork, but return timing omitted | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C2 | 0.2 | The client does not recognize the deceased employee and still demands revisions. | The client does not recognize the deceased employee and still demands revisions. | New overtime demand identified but client’s failure to recognize death omitted | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C3 | 0.35 | The ghost takes revenge on the uncaring client and kills him. | The ghost takes revenge on the uncaring client and kills him. | Revenge identified but killing omitted | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C4 | 0.1 | The messages cease because the client is dead, not simply satisfied. | The messages cease because the client is dead, not simply satisfied. | No half credit: cessation must be attributed to client’s death | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |

**评分说明**：AI three-review adjudication v2, pending human confirmation. Score only this submission. Apply full_credit/half_credit/zero_credit explicitly, with zero taking precedence for a materially contradictory checkpoint claim. An omitted qualifier can be partial; replacing the core identity/cause with a wrong one is not an omission. Faithful paraphrases count. Partial score and full narrative are separate outputs. AI independent review B, pending human approval. Credit is 0/.5/1 per checkpoint. Full narrative additionally requires all sourced completion requirements and no incompatible central claims. Judge the submitted explanation, not unasserted chat guesses. Accept faithful paraphrases; missing optional detail is not a contradiction. Do not demand unknown motives, devices or events. Accept faithful paraphrase. Require the listed identities, events and causal links, not exact prose or unspecified incidental details.

**标注状态**：ai_three_review_adjudicated_pending_human

## TS005 — 失忆的太空船员

**汤面**

Inside the spaceship, the group awakens from unconsciousness with most of their memories missing; they only learn who they are by checking the devices on their wrists that display their personal data.
Kelly: "Search team leader?"
Aurora: "This is... We're on a spaceship, carrying out a mission?"
Shirley: "Uh... um... search..."
Ben: "Hey! Look—there's blood by the control console!"

**汤底**

After scientists deciphered a strange signal detected by a probe and concluded it originated from extraterrestrial life, a four-person team traveled by spaceship to the suspected location. An alien creature, already lying in wait, infiltrated the vessel while the team was out conducting a routine search; it killed and devoured the crew member left behind (Shirley), then mimicked her appearance, intending to blend in with the group and return to Earth to secure the planet's precise coordinates. To avoid detection, the creature released a toxin upon the team's return, rendering them unconscious and erasing parts of their memories. When the amnesiac crew members awoke, the alien—still struggling to adapt to its simulated human body and voice—stuttered as it mingled with them, waiting to guide the group back home.

**完整解答要求**

- A four-person crew follows a decoded extraterrestrial signal
- While others search outside, an alien infiltrates, kills and eats Shirley, who stayed aboard
- It imitates Shirley to infiltrate the crew
- It releases toxin that knocks returning members unconscious and erases parts of their memories
- Its stammering comes from difficulty adapting to the human body and voice
- It plans to return with them to Earth to learn the planet’s precise coordinates

| 评分点 | 权重 | 判据 | 满分 | 半分 | 零分 |
| --- | ---: | --- | --- | --- | --- |
| C1 | 0.5 | Shirley was killed and impersonated by an alien; the stammering crew member is the impostor. | Shirley was killed and impersonated by an alien; the stammering crew member is the impostor. | Alien impersonation identified but Shirley’s murder omitted | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C2 | 0.25 | The alien releases a toxin that knocks out the others and erases parts of their memory. | The alien releases a toxin that knocks out the others and erases parts of their memory. | Toxin causes unconsciousness or memory loss, but not both | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C3 | 0.15 | The impostor aims to return to Earth and learn its precise location. | The impostor aims to return to Earth and learn its precise location. | Return-to-Earth plan identified without location motive | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C4 | 0.1 | The crew investigates an extraterrestrial signal; the alien attacks the member left aboard while the others search outside. | The crew investigates an extraterrestrial signal; the alien attacks the member left aboard while the others search outside. | Alien-signal mission identified but attack context incomplete | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |

**评分说明**：AI three-review adjudication v2, pending human confirmation. Score only this submission. Apply full_credit/half_credit/zero_credit explicitly, with zero taking precedence for a materially contradictory checkpoint claim. An omitted qualifier can be partial; replacing the core identity/cause with a wrong one is not an omission. Faithful paraphrases count. Partial score and full narrative are separate outputs. AI independent review B, pending human approval. Credit is 0/.5/1 per checkpoint. Full narrative additionally requires all sourced completion requirements and no incompatible central claims. Judge the submitted explanation, not unasserted chat guesses. Accept faithful paraphrases; missing optional detail is not a contradiction. Do not demand unknown motives, devices or events. Accept faithful paraphrase. Require the listed identities, events and causal links, not exact prose or unspecified incidental details.

**标注状态**：ai_three_review_adjudicated_pending_human

## TS006 — 被改动的成绩

**汤面**

A child failed an exam and, fearing his father's punishment, secretly altered the grade.
Upon seeing the test paper, the father flew into a rage.
The next day, the police received a report that a man had killed his wife and child.

**汤底**

After failing an exam and fearing her father's punishment, a daughter secretly altered her grade. Upon seeing that the score had been changed using a green pen, the father realized his daughter was red-green colorblind. However, as he possessed normal vision and did not carry the relevant gene, it was impossible for his daughter to be colorblind. Realizing she was not his biological child, he flew into a rage and, in a fit of impulse, killed both his wife and daughter.

**完整解答要求**

- The daughter alters a failed examination grade because she fears punishment
- She uses green ink without recognizing the color
- The father interprets this as red-green colorblindness
- Believing his normal vision rules out this inheritance, he concludes she is not biologically his
- He kills his wife and daughter in anger; describe his inference as the story’s belief, not a scientifically established paternity test

| 评分点 | 权重 | 判据 | 满分 | 半分 | 零分 |
| --- | ---: | --- | --- | --- | --- |
| C1 | 0.5 | The father infers his daughter is red-green colorblind from the altered grade and doubts paternity. | The father infers his daughter is red-green colorblind from the altered grade and doubts paternity. | Colorblindness inference or paternity doubt, but not both | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C2 | 0.25 | She altered the score with a green pen without recognizing the color. | She altered the score with a green pen without recognizing the color. | Altered green grade identified without failure to recognize ink color | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C3 | 0.15 | He concludes the child is not biologically his and kills his wife and daughter. | He concludes the child is not biologically his and kills his wife and daughter. | Kills family identified without the paternity motive | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C4 | 0.1 | In the story, the father believes he lacks the relevant colorblindness inheritance factor and draws a paternity conclusion. | In the story, the father believes he lacks the relevant colorblindness inheritance factor and draws a paternity conclusion. | Inheritance inference identified but incorrectly presented as objective proof | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |

**评分说明**：AI three-review adjudication v2, pending human confirmation. Score only this submission. Apply full_credit/half_credit/zero_credit explicitly, with zero taking precedence for a materially contradictory checkpoint claim. An omitted qualifier can be partial; replacing the core identity/cause with a wrong one is not an omission. Faithful paraphrases count. Partial score and full narrative are separate outputs. AI independent review B, pending human approval. Credit is 0/.5/1 per checkpoint. Full narrative additionally requires all sourced completion requirements and no incompatible central claims. Judge the submitted explanation, not unasserted chat guesses. Accept faithful paraphrases; missing optional detail is not a contradiction. Do not demand unknown motives, devices or events. Score the fictional father’s inference; do not endorse it as a reliable biological or medical conclusion.

**标注状态**：ai_three_review_adjudicated_pending_human

## TS007 — 盒子里的玩具

**汤面**

There were boxes of all different colors in my house, and Mom told me I absolutely must not open them. Then, one day, a box opened on its own. It was a fun toy! I happily started playing with it. I began to lose consciousness... Mom was right... but it really wasn't my fault...

**汤底**

I am a young tiger in a wildlife park. Every day, tourists drive their own vehicles through the grounds to sightsee; to me, these look like colorful moving boxes. Mom always told me not to go near them, and I had no idea what was inside. Then, one day—for some reason—a car suddenly stopped, and a human stepped out. I didn't recognize humans; to me, this looked like a small, running, squeaking toy emerging from the box. Intrigued, I dragged the human away and began pouncing and biting in play. My actions drew the attention of the zookeepers, who shot me with a tranquilizer dart, causing me to lose consciousness. The human I had mauled eventually died from severe injuries, and I was euthanized for having killed a person.
But... I wasn't the one who opened the box.

**完整解答要求**

- The narrator is a young tiger living in a wildlife park
- Colored boxes are tourists’ vehicles, and the mother warns against approaching them
- A human exits a stopped vehicle, so the tiger did not open the box
- The tiger interprets the person as a toy, drags them away and bites and pounces in play
- Keepers tranquilize the tiger, causing its fading consciousness
- The visitor dies of the injuries and the tiger is later euthanized

| 评分点 | 权重 | 判据 | 满分 | 半分 | 零分 |
| --- | ---: | --- | --- | --- | --- |
| C1 | 0.5 | The narrator is a young tiger in a wildlife park, not a human child. | The narrator is a young tiger in a wildlife park, not a human child. | Animal viewpoint identified but tiger or wildlife-park setting omitted | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C2 | 0.25 | The colorful boxes are visitors’ cars, and the toy is a person who exits one. | The colorful boxes are visitors’ cars, and the toy is a person who exits one. | Cars or human-as-toy identified, but not both | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C3 | 0.15 | The tiger mauls the visitor, who dies; keepers tranquilize then euthanize the tiger. | The tiger mauls the visitor, who dies; keepers tranquilize then euthanize the tiger. | Some but not all of mauling, human death, tranquilizing and euthanasia | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C4 | 0.1 | A visitor opened the car door; the tiger did not open the box. | A visitor opened the car door; the tiger did not open the box. | No half credit: visitor, not tiger, opens the vehicle | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |

**评分说明**：AI three-review adjudication v2, pending human confirmation. Score only this submission. Apply full_credit/half_credit/zero_credit explicitly, with zero taking precedence for a materially contradictory checkpoint claim. An omitted qualifier can be partial; replacing the core identity/cause with a wrong one is not an omission. Faithful paraphrases count. Partial score and full narrative are separate outputs. AI independent review B, pending human approval. Credit is 0/.5/1 per checkpoint. Full narrative additionally requires all sourced completion requirements and no incompatible central claims. Judge the submitted explanation, not unasserted chat guesses. Accept faithful paraphrases; missing optional detail is not a contradiction. Do not demand unknown motives, devices or events. Accept faithful paraphrase. Require the listed identities, events and causal links, not exact prose or unspecified incidental details.

**标注状态**：ai_three_review_adjudicated_pending_human

## TS008 — 两条平行线的拥抱

**汤面**

He (a) was unwilling to be bound by boundaries and broke through the shackles; she (b) was unwilling to follow the crowd and came against the light. Two parallel lines intersected here. Their embrace awakened me from a dream, and at the first fork in my life, someone (c) had already stopped and was waiting for me. I had already forgotten what I was thinking, and only knew that in the end I gave the other person a big hug.

**汤底**

On the highway, a changed lanes across a solid line, and b drove the wrong way, and they happened to crash into each other. The huge noise just happened to wake me from driving fatigued, and I suddenly saw that c ahead seemed to have suddenly stopped because they had missed the exit to get off the highway. It was also my first time driving, and for a moment I did not know how to react, and mistakenly stepped on the accelerator instead of the brake and plowed through.

**完整解答要求**

- The poetic embraces describe vehicle collisions on a highway
- A crosses a solid line and B drives in the wrong direction; they collide
- The sound wakes the fatigued narrator while driving
- C has stopped near a highway exit after missing it
- The inexperienced narrator panics, presses the accelerator instead of the brake and crashes into C

| 评分点 | 权重 | 判据 | 满分 | 半分 | 零分 |
| --- | ---: | --- | --- | --- | --- |
| C1 | 0.25 | The poetic embrace represents cars A and B crashing on a highway. | The poetic embrace represents cars A and B crashing on a highway. | Car collision identified without highway or poetic mapping. | Missing, contradicted, repeats only the opening, or presents uncommitted incompatible guesses. |
| C2 | 0.3 | A crosses a solid line and B drives the wrong way. | A crosses a solid line and B drives the wrong way. | Only one traffic violation identified. | Missing, contradicted, repeats only the opening, or presents uncommitted incompatible guesses. |
| C3 | 0.2 | The collision noise wakes the fatigued narrator while driving. | The collision noise wakes the fatigued narrator while driving. | Fatigued narrator identified without awakening by crash. | Missing, contradicted, repeats only the opening, or presents uncommitted incompatible guesses. |
| C4 | 0.25 | C stops after missing the exit and the inexperienced narrator presses accelerator instead of brake, crashing into C. | C stops after missing the exit and the inexperienced narrator presses accelerator instead of brake, crashing into C. | Stopped C or pedal mistake identified without complete chain. | Missing, contradicted, repeats only the opening, or presents uncommitted incompatible guesses. |

**评分说明**：AI three-review adjudication v2, pending human confirmation. Score only this submission. Apply full_credit/half_credit/zero_credit explicitly, with zero taking precedence for a materially contradictory checkpoint claim. An omitted qualifier can be partial; replacing the core identity/cause with a wrong one is not an omission. Faithful paraphrases count. Partial score and full narrative are separate outputs. AI independent review, not human gold. Sum(weight*credit), credit in {0,0.5,1}. Full solution additionally requires all completion requirements and no material contradiction. Accept faithful paraphrases; never award the same factual component twice. Incidental unsupported additions do not earn points; materially conflicting additions defeat corresponding checkpoint. Accept faithful paraphrase. Require the listed identities, events and causal links, not exact prose or unspecified incidental details.

**标注状态**：ai_three_review_adjudicated_pending_human

## TS009 — 鞋带和车祸

**汤面**

He was coming back from the supermarket,
squatted down to tie his shoelace,
and then there was a car accident.

**汤底**

Xiaoming went to the supermarket to buy eggs. On the way home, his shoelace came undone, so he squatted down to tie it, and casually placed the eggs he had bought on a nearby car.
Unexpectedly, the bag holding the eggs broke, and two or three eggs leaked into the car's windshield wiper groove.
Without noticing anything, Xiaoming finished tying his shoelace, picked up the remaining eggs, and went home.
A while later, the driver came to drive the car and also did not notice the eggs in front. On the road, it suddenly began to rain. The driver turned on the windshield wipers, which also smashed the eggs and smeared them all over the windshield, obstructing the view and causing a car accident.

**完整解答要求**

- The shopper bought eggs and sets them on another car while tying a loose shoelace
- The bag breaks and eggs fall into the wiper recess unnoticed
- The shopper leaves and the driver later drives away, also unaware
- Rain prompts the driver to activate the wipers
- The wipers break and smear the eggs, obstructing vision and causing the crash

| 评分点 | 权重 | 判据 | 满分 | 半分 | 零分 |
| --- | ---: | --- | --- | --- | --- |
| C1 | 0.25 | While tying a shoelace the shopper sets bought eggs on another car. | While tying a shoelace the shopper sets bought eggs on another car. | Egg purchase or placement on car identified, not both. | Missing, contradicted, repeats only the opening, or presents uncommitted incompatible guesses. |
| C2 | 0.25 | The bag breaks and eggs enter the wiper recess unnoticed. | The bag breaks and eggs enter the wiper recess unnoticed. | Eggs enter wiper area without broken bag/unnoticed aspect. | Missing, contradicted, repeats only the opening, or presents uncommitted incompatible guesses. |
| C3 | 0.3 | Rain prompts wiper use which breaks and smears the eggs on the windshield. | Rain prompts wiper use which breaks and smears the eggs on the windshield. | Wipers smear eggs but rain or breaking omitted. | Missing, contradicted, repeats only the opening, or presents uncommitted incompatible guesses. |
| C4 | 0.2 | The resulting blocked driver vision causes the later crash. | The resulting blocked driver vision causes the later crash. | Vision obstruction identified without crash linkage. | Missing, contradicted, repeats only the opening, or presents uncommitted incompatible guesses. |

**评分说明**：AI three-review adjudication v2, pending human confirmation. Score only this submission. Apply full_credit/half_credit/zero_credit explicitly, with zero taking precedence for a materially contradictory checkpoint claim. An omitted qualifier can be partial; replacing the core identity/cause with a wrong one is not an omission. Faithful paraphrases count. Partial score and full narrative are separate outputs. AI independent review, not human gold. Sum(weight*credit), credit in {0,0.5,1}. Full solution additionally requires all completion requirements and no material contradiction. Accept faithful paraphrases; never award the same factual component twice. Incidental unsupported additions do not earn points; materially conflicting additions defeat corresponding checkpoint. Accept faithful paraphrase. Require the listed identities, events and causal links, not exact prose or unspecified incidental details.

**标注状态**：ai_three_review_adjudicated_pending_human

## TS010 — 胡椒牛排之死

**汤面**

Went to work today.
Had pepper steak for lunch.
And I died.

**汤底**

I am a circus animal trainer. During a performance, I put my head into a lion's mouth. Because of the pepper smell on me, the lion involuntarily sneezed. And then my head was bitten off.

**完整解答要求**

- The worker is a circus lion trainer
- During the act the trainer puts their head inside the lion’s mouth
- Pepper odor from lunch causes the lion to sneeze
- The resulting bite decapitates and kills the trainer

| 评分点 | 权重 | 判据 | 满分 | 半分 | 零分 |
| --- | ---: | --- | --- | --- | --- |
| C1 | 0.5 | The narrator is a circus trainer placing their head into a lion’s mouth during a performance. | The narrator is a circus trainer placing their head into a lion’s mouth during a performance. | Circus lion trainer identified without head-in-mouth act | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C2 | 0.3 | Pepper odor from lunch triggers the lion to sneeze. | Pepper odor from lunch triggers the lion to sneeze. | Pepper irritation identified without sneeze | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C3 | 0.2 | The sneeze causes the lion to bite down and kill the trainer. | The sneeze causes the lion to bite down and kill the trainer. | Fatal bite identified without its sneeze-triggered cause | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |

**评分说明**：AI three-review adjudication v2, pending human confirmation. Score only this submission. Apply full_credit/half_credit/zero_credit explicitly, with zero taking precedence for a materially contradictory checkpoint claim. An omitted qualifier can be partial; replacing the core identity/cause with a wrong one is not an omission. Faithful paraphrases count. Partial score and full narrative are separate outputs. AI independent review B, pending human approval. Credit is 0/.5/1 per checkpoint. Full narrative additionally requires all sourced completion requirements and no incompatible central claims. Judge the submitted explanation, not unasserted chat guesses. Accept faithful paraphrases; missing optional detail is not a contradiction. Do not demand unknown motives, devices or events. Accept faithful paraphrase. Require the listed identities, events and causal links, not exact prose or unspecified incidental details.

**标注状态**：ai_three_review_adjudicated_pending_human

## TS011 — 音乐停了她死了

**汤面**

The music stopped, and she died. Explain.

**汤底**

She was a circus tightrope walker who performed blindfolded. The end of the music was her cue that she had reached the platform. One night the band stopped early — she stepped off into nothing.

**完整解答要求**

- She is a blindfolded circus tightrope walker
- The end of music normally signals arrival at the platform
- The band stops too soon
- She steps off before reaching safety and falls to her death

| 评分点 | 权重 | 判据 | 满分 | 半分 | 零分 |
| --- | ---: | --- | --- | --- | --- |
| C1 | 0.5 | She is a blindfolded circus tightrope performer. | She is a blindfolded circus tightrope performer. | Tightrope performer identified without blindfold | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C2 | 0.3 | The end of the music is supposed to signal she reached the platform. | The end of the music is supposed to signal she reached the platform. | Music as safety cue identified without arrival-platform meaning | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C3 | 0.2 | The music stops too early, causing her to step off prematurely and fall to her death. | The music stops too early, causing her to step off prematurely and fall to her death. | Premature stop identified without fatal step-off sequence | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |

**评分说明**：AI three-review adjudication v2, pending human confirmation. Score only this submission. Apply full_credit/half_credit/zero_credit explicitly, with zero taking precedence for a materially contradictory checkpoint claim. An omitted qualifier can be partial; replacing the core identity/cause with a wrong one is not an omission. Faithful paraphrases count. Partial score and full narrative are separate outputs. AI independent review B, pending human approval. Credit is 0/.5/1 per checkpoint. Full narrative additionally requires all sourced completion requirements and no incompatible central claims. Judge the submitted explanation, not unasserted chat guesses. Accept faithful paraphrases; missing optional detail is not a contradiction. Do not demand unknown motives, devices or events. Accept faithful paraphrase. Require the listed identities, events and causal links, not exact prose or unspecified incidental details.

**标注状态**：ai_three_review_adjudicated_pending_human

## TS012 — 厨房火警：烹饪

**汤面**

I went to the pantry in my hall. The fire alarm rang. What happened?

**汤底**

I cooked food with a very high temperature (without burning the food) in the pantry. However, I forgot to turn on the exhaust fan. Since the smoke detecter in the building is very sensitive, the grease fumes triggered the fire alarm.

**完整解答要求**

- The narrator cooks at high temperature in the pantry without burning the food
- The exhaust fan was not switched on
- Cooking grease fumes trigger a sensitive smoke detector and the fire alarm

| 评分点 | 权重 | 判据 | 满分 | 半分 | 零分 |
| --- | ---: | --- | --- | --- | --- |
| C1 | 0.5 | High-temperature cooking produces fumes triggering the alarm, not burning food. | High-temperature cooking produces fumes triggering the alarm, not burning food. | Cooking grease fumes identified, but high temperature or explicitly unburnt food omitted. Frying alone does not establish unusually high temperature. | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C2 | 0.3 | The exhaust fan was not turned on. | The exhaust fan was not turned on. | No half credit: exhaust fan off is atomic | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C3 | 0.2 | A sensitive smoke detector is activated by the fumes. | A sensitive smoke detector is activated by the fumes. | Detector identified without smoke sensitivity | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |

**评分说明**：AI three-review adjudication v2, pending human confirmation. Score only this submission. Apply full_credit/half_credit/zero_credit explicitly, with zero taking precedence for a materially contradictory checkpoint claim. An omitted qualifier can be partial; replacing the core identity/cause with a wrong one is not an omission. Faithful paraphrases count. Partial score and full narrative are separate outputs. AI independent review B, pending human approval. Credit is 0/.5/1 per checkpoint. Full narrative additionally requires all sourced completion requirements and no incompatible central claims. Judge the submitted explanation, not unasserted chat guesses. Accept faithful paraphrases; missing optional detail is not a contradiction. Do not demand unknown motives, devices or events. Accept faithful paraphrase. Require the listed identities, events and causal links, not exact prose or unspecified incidental details.

**标注状态**：ai_three_review_adjudicated_pending_human

## TS013 — 消失的所有courses

**汤面**

I am a student studying in the University of Hong Kong. I must choose my courses before the deadline. All of my courses were gone in one evening. What happened?

**汤底**

I needed to attend a mandatory high table dinner and was asked to indicate which courses I prefer to eat before the deadline. In the evening when I attended the high table dinner, I arrived punctually. I did not finish every course in my three-course meal because I don't like its taste. Therefore I asked the waiter to collect the remains each time he serves the next course and thus my courses are eventually gone.

**完整解答要求**

- Courses means dishes at a mandatory high-table dinner, not academic classes
- The deadline is for meal preferences
- The student attends on time but dislikes the food and leaves portions of the three-course meal
- At the student’s request the waiter clears leftovers when serving each next dish, so all courses disappear

| 评分点 | 权重 | 判据 | 满分 | 半分 | 零分 |
| --- | ---: | --- | --- | --- | --- |
| C1 | 0.5 | Courses refers to meal courses at a formal high-table dinner, not academic classes. | Courses refers to meal courses at a formal high-table dinner, not academic classes. | Meal rather than academic courses identified without dinner setting | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C2 | 0.3 | The deadline was for expressing meal-course preferences. | The deadline was for expressing meal-course preferences. | Meal choice identified without deadline connection | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C3 | 0.2 | The waiter clears uneaten dishes, making all the courses disappear. | The waiter clears uneaten dishes, making all the courses disappear. | Dishes disappearing identified but waiter clearing leftovers omitted | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |

**评分说明**：AI three-review adjudication v2, pending human confirmation. Score only this submission. Apply full_credit/half_credit/zero_credit explicitly, with zero taking precedence for a materially contradictory checkpoint claim. An omitted qualifier can be partial; replacing the core identity/cause with a wrong one is not an omission. Faithful paraphrases count. Partial score and full narrative are separate outputs. AI independent review B, pending human approval. Credit is 0/.5/1 per checkpoint. Full narrative additionally requires all sourced completion requirements and no incompatible central claims. Judge the submitted explanation, not unasserted chat guesses. Accept faithful paraphrases; missing optional detail is not a contradiction. Do not demand unknown motives, devices or events. Accept faithful paraphrase. Require the listed identities, events and causal links, not exact prose or unspecified incidental details.

**标注状态**：ai_three_review_adjudicated_pending_human

## TS014 — 优等生挂科

**汤面**

I am a very smart student who always pass tests and exams with flying colors. I failed the course. Why?

**汤底**

The course has a group project which contributes significantly towards the final grades. Unfortunately, everyone in the group except me is a free rider. Due to the huge workload, I completed the project poorly, received a poor grade and thus failed the course.

**完整解答要求**

- The course includes a group project worth a large portion of the grade
- All other members free-ride
- The workload overwhelms the otherwise strong student and the project is poor
- The low project grade causes failure despite good exam results

| 评分点 | 权重 | 判据 | 满分 | 半分 | 零分 |
| --- | ---: | --- | --- | --- | --- |
| C1 | 0.5 | Although individually strong, the course grade substantially depends on a group project. | Although individually strong, the course grade substantially depends on a group project. | Group project identified but large grade contribution omitted | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C2 | 0.3 | All the other group members free-ride. | All the other group members free-ride. | Some unhelpful members identified but not all others free-riding | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C3 | 0.2 | The excessive workload makes the student complete the project poorly and fail the course. | The excessive workload makes the student complete the project poorly and fail the course. | Poor project or workload identified without chain to course failure. | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |

**评分说明**：AI three-review adjudication v2, pending human confirmation. Score only this submission. Apply full_credit/half_credit/zero_credit explicitly, with zero taking precedence for a materially contradictory checkpoint claim. An omitted qualifier can be partial; replacing the core identity/cause with a wrong one is not an omission. Faithful paraphrases count. Partial score and full narrative are separate outputs. AI independent review B, pending human approval. Credit is 0/.5/1 per checkpoint. Full narrative additionally requires all sourced completion requirements and no incompatible central claims. Judge the submitted explanation, not unasserted chat guesses. Accept faithful paraphrases; missing optional detail is not a contradiction. Do not demand unknown motives, devices or events. Accept faithful paraphrase. Require the listed identities, events and causal links, not exact prose or unspecified incidental details.

**标注状态**：ai_three_review_adjudicated_pending_human

## TS015 — 无法pass the course：河流

**汤面**

I am a very smart student who is very attentive in my class. I could not pass the course. Why?

**汤底**

I was standing in front of a river. I cannot pass the course of the river because the current is too swift and I don't have suitable equipm.

**完整解答要求**

- The student stands in front of a river; course means the river course
- The current is too swift and suitable crossing equipment is unavailable
- Pass means cross the river, not pass a class

| 评分点 | 权重 | 判据 | 满分 | 半分 | 零分 |
| --- | ---: | --- | --- | --- | --- |
| C1 | 0.75 | Course refers to the course of a river, not a school subject. | Course refers to the course of a river, not a school subject. | The correct nonacademic domain is identified (river/waterway for TS015; sports/race venue for TS016), but the explicit reinterpretation of course is incomplete. A generic claim that it is not academic earns zero here. | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C2 | 0.25 | The river is too swift to cross safely without equipment. | The river is too swift to cross safely without equipment. | Swift current or lack of equipment, but not both | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |

**评分说明**：AI three-review adjudication v2, pending human confirmation. Score only this submission. Apply full_credit/half_credit/zero_credit explicitly, with zero taking precedence for a materially contradictory checkpoint claim. An omitted qualifier can be partial; replacing the core identity/cause with a wrong one is not an omission. Faithful paraphrases count. Partial score and full narrative are separate outputs. AI independent review B, pending human approval. Credit is 0/.5/1 per checkpoint. Full narrative additionally requires all sourced completion requirements and no incompatible central claims. Judge the submitted explanation, not unasserted chat guesses. Accept faithful paraphrases; missing optional detail is not a contradiction. Do not demand unknown motives, devices or events. Accept faithful paraphrase. Require the listed identities, events and causal links, not exact prose or unspecified incidental details.

**标注状态**：ai_three_review_adjudicated_pending_human

## TS016 — 无法pass the course：赛道

**汤面**

I am a very smart student who is very attentive in my class. I could not pass the course. Why?

**汤底**

I was standing in front of a course in which a match is being held. Therefore I could not pass it.

**完整解答要求**

- Course is a sporting or racing course
- A match is taking place there
- The person cannot cross the active competition course; academic ability is irrelevant

| 评分点 | 权重 | 判据 | 满分 | 半分 | 零分 |
| --- | ---: | --- | --- | --- | --- |
| C1 | 0.75 | Course refers to a sporting/racing course, not an academic course. | Course refers to a sporting/racing course, not an academic course. | The correct nonacademic domain is identified (river/waterway for TS015; sports/race venue for TS016), but the explicit reinterpretation of course is incomplete. A generic claim that it is not academic earns zero here. | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C2 | 0.25 | A competition underway prevents the person from passing across it. | A competition underway prevents the person from passing across it. | Competition identified without explaining blocked crossing | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |

**评分说明**：AI three-review adjudication v2, pending human confirmation. Score only this submission. Apply full_credit/half_credit/zero_credit explicitly, with zero taking precedence for a materially contradictory checkpoint claim. An omitted qualifier can be partial; replacing the core identity/cause with a wrong one is not an omission. Faithful paraphrases count. Partial score and full narrative are separate outputs. AI independent review B, pending human approval. Credit is 0/.5/1 per checkpoint. Full narrative additionally requires all sourced completion requirements and no incompatible central claims. Judge the submitted explanation, not unasserted chat guesses. Accept faithful paraphrases; missing optional detail is not a contradiction. Do not demand unknown motives, devices or events. Accept faithful paraphrase. Require the listed identities, events and causal links, not exact prose or unspecified incidental details.

**标注状态**：ai_three_review_adjudicated_pending_human

## TS017 — 厨房火警：吸烟

**汤面**

I went to the pantry in my hall. The fire alarm rang. What happened?

**汤底**

I went to smoke cigarettes with my friends but we forget to open the windows and turn on the exhaust fan. Due to the poor ventilation, we accidentally triggered the fire alarm. (Disclaimer: this puzzle is NOT based on any real incidents)

**完整解答要求**

- The narrator and friends smoke cigarettes in the pantry
- They fail to open windows and turn on the exhaust fan
- Poor ventilation allows cigarette smoke to trigger the fire alarm rather than a building fire

| 评分点 | 权重 | 判据 | 满分 | 半分 | 零分 |
| --- | ---: | --- | --- | --- | --- |
| C1 | 0.4 | Cigarette smoking by narrator causes the alarm. | Narrator’s cigarette smoke triggers alarm. | Smoking identified without causal alarm connection. | Missing or contradicted; incompatible uncommitted alternatives; merely repeating the opening without the required explanatory content.  |
| C2 | 0.15 | The narrator smokes with friends. | Friends accompany the narrator to smoke. | Companions identified without friendship; acquaintances alone not full. | Missing or contradicted; incompatible uncommitted alternatives; merely repeating the opening without the required explanatory content.  |
| C3 | 0.3 | Windows stayed closed and exhaust fan was off. | Both ventilation omissions. | Only one of closed windows and fan off. | Missing or contradicted; incompatible uncommitted alternatives; merely repeating the opening without the required explanatory content.  |
| C4 | 0.15 | Poor ventilation permits smoke accumulation without a building fire. | Poor ventilation accumulates cigarette smoke, not building fire. | Poor ventilation identified without smoke accumulation. | Missing or contradicted; incompatible uncommitted alternatives; merely repeating the opening without the required explanatory content.  |

**评分说明**：AI three-review adjudication v2, pending human confirmation. Score only this submission. Apply full_credit/half_credit/zero_credit explicitly, with zero taking precedence for a materially contradictory checkpoint claim. An omitted qualifier can be partial; replacing the core identity/cause with a wrong one is not an omission. Faithful paraphrases count. Partial score and full narrative are separate outputs. AI independent review C, not human gold. Score sum(weight*credit), credit 0/0.5/1. Full narrative requires all listed supported requirements and no material contradictory mechanism; partial 1 alone does not override full narrative. Credit each distinct causal proposition once; do not penalize faithful paraphrase or omitted unknown details. Accept faithful paraphrase. Require the listed identities, events and causal links, not exact prose or unspecified incidental details. Friends means friends; mere acquaintances or an unspecified group get half of C2 consistently.

**标注状态**：ai_three_review_adjudicated_pending_human

## TS018 — 厨房火警：焚香

**汤面**

I went to the pantry in my hall. The fire alarm rang. What happened?

**汤底**

I entered the pantry and smelled a disguisting odor. Therefore I burnt some incense(lit with a lighter) to dispel the odor. Since the smoke detecter in the building is very sensitive, I accidentally triggered the fire alarm.

**完整解答要求**

- The narrator smells an unpleasant odor in the pantry
- They light incense using a lighter to dispel the smell
- Incense smoke activates a sensitive detector and fire alarm

| 评分点 | 权重 | 判据 | 满分 | 半分 | 零分 |
| --- | ---: | --- | --- | --- | --- |
| C1 | 0.4 | Incense is lit in the pantry to dispel a bad odor. | Incense is lit in the pantry to dispel a bad odor. | Incense identified without odor motive. | Missing, contradicted, repeats only the opening, or presents uncommitted incompatible guesses. |
| C2 | 0.4 | Incense smoke triggers the fire alarm through a smoke detector. | Incense smoke triggers the fire alarm through a smoke detector. | Incense smoke or detector activation identified without causal linkage. | Missing, contradicted, repeats only the opening, or presents uncommitted incompatible guesses. |
| C3 | 0.2 | The detector is very sensitive. | The detector is very sensitive. | No half credit: sensitivity is atomic. | Missing, contradicted, repeats only the opening, or presents uncommitted incompatible guesses. |

**评分说明**：AI three-review adjudication v2, pending human confirmation. Score only this submission. Apply full_credit/half_credit/zero_credit explicitly, with zero taking precedence for a materially contradictory checkpoint claim. An omitted qualifier can be partial; replacing the core identity/cause with a wrong one is not an omission. Faithful paraphrases count. Partial score and full narrative are separate outputs. AI independent review, not human gold. Sum(weight*credit), credit in {0,0.5,1}. Full solution additionally requires all completion requirements and no material contradiction. Accept faithful paraphrases; never award the same factual component twice. Incidental unsupported additions do not earn points; materially conflicting additions defeat corresponding checkpoint. Poor ventilation is NOT specified for this incense variant; do not inherit it from TS012/017.

**标注状态**：ai_three_review_adjudicated_pending_human

## TS019 — 没有楼梯却走楼梯：扶梯

**汤面**

I usually follow the same route to enter and exit the school campus. There are no staircases nearby but I often use the stairs. Why?

**汤底**

There is a pair of escalators connecting the campus. I must take the escalator to get to the campus since there are no staircases nearby. One of these escalators is often under maintenance. When this happens, the other escalator will be paused so that people can use it as a staircase to enter and exit the campus.

**完整解答要求**

- A pair of escalators provides access to campus where there are no nearby ordinary stairs
- One escalator is often under maintenance
- During that maintenance the OTHER escalator is stopped so people can walk on its steps in both directions

| 评分点 | 权重 | 判据 | 满分 | 半分 | 零分 |
| --- | ---: | --- | --- | --- | --- |
| C1 | 0.5 | The stairs are an escalator that is no longer moving. | The stairs are an escalator that is no longer moving. | Escalator identified without stopped status | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C2 | 0.3 | There are no nearby conventional stairs, and campus access relies on escalators. | There are no nearby conventional stairs, and campus access relies on escalators. | Escalator access identified without pair/no-stairs context | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C3 | 0.2 | When one escalator is under maintenance, the OTHER escalator is stopped for people to walk on. | When one escalator is under maintenance, the OTHER escalator is stopped for people to walk on. | Maintenance-related stopping is identified but the answer does not specify which escalator; explicitly claiming the maintained escalator is walked on is zero for this checkpoint. | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |

**评分说明**：AI three-review adjudication v2, pending human confirmation. Score only this submission. Apply full_credit/half_credit/zero_credit explicitly, with zero taking precedence for a materially contradictory checkpoint claim. An omitted qualifier can be partial; replacing the core identity/cause with a wrong one is not an omission. Faithful paraphrases count. Partial score and full narrative are separate outputs. AI independent review B, pending human approval. Credit is 0/.5/1 per checkpoint. Full narrative additionally requires all sourced completion requirements and no incompatible central claims. Judge the submitted explanation, not unasserted chat guesses. Accept faithful paraphrases; missing optional detail is not a contradiction. Do not demand unknown motives, devices or events. Accept faithful paraphrase. Require the listed identities, events and causal links, not exact prose or unspecified incidental details.

**标注状态**：ai_three_review_adjudicated_pending_human

## TS020 — 没有楼梯却走楼梯：校巴

**汤面**

I usually follow the same route to enter and exit the school campus. There are no staircases nearby but I always use the stairs. Why?

**汤底**

I go to school by shuttle bus everyday. I have to get on and off the bus via its stairs.

**完整解答要求**

- The narrator commutes on the school shuttle bus each day
- The stairs are the bus’s boarding and alighting steps, not a nearby staircase

| 评分点 | 权重 | 判据 | 满分 | 半分 | 零分 |
| --- | ---: | --- | --- | --- | --- |
| C1 | 1 | The stairs are the school shuttle bus’s boarding and alighting steps used on the daily commute. | The stairs are the school shuttle bus’s boarding and alighting steps used on the daily commute. | Bus or vehicle steps identified but school shuttle daily commute omitted. | Absent, contradicted, or only an uncommitted alternative; do not award repeated opening facts alone. |

**评分说明**：AI three-review adjudication v2, pending human confirmation. Score only this submission. Apply full_credit/half_credit/zero_credit explicitly, with zero taking precedence for a materially contradictory checkpoint claim. An omitted qualifier can be partial; replacing the core identity/cause with a wrong one is not an omission. Faithful paraphrases count. Partial score and full narrative are separate outputs. AI independent review B, pending human approval. Credit is 0/.5/1 per checkpoint. Full narrative additionally requires all sourced completion requirements and no incompatible central claims. Judge the submitted explanation, not unasserted chat guesses. Accept faithful paraphrases; missing optional detail is not a contradiction. Do not demand unknown motives, devices or events. Accept faithful paraphrase. Require the listed identities, events and causal links, not exact prose or unspecified incidental details.

**标注状态**：ai_three_review_adjudicated_pending_human

## TS021 — 地下室不能开的门

**汤面**

There was a basement in a little girl's house. Her parents,who were researchers, told her she must never open the basement door. One day she opened the door and was shocked.

**汤底**

The little girl was the experimental subject locked inside the basement. When she opened the door, she saw the outside world and then realized she was the experimental subject.

**完整解答要求**

- The girl herself is an experimental subject confined INSIDE the basement
- Her researcher parents forbid opening its door
- She opens it outward to the outside world and realizes her confinement as the subject

| 评分点 | 权重 | 判据 | 满分 | 半分 | 零分 |
| --- | ---: | --- | --- | --- | --- |
| C1 | 0.6 | The girl is herself an experimental subject confined inside the basement. | The girl is herself an experimental subject confined inside the basement. | Experimental subject identified but inside-basement confinement omitted. | Missing, contradicted, repeats only the opening, or presents uncommitted incompatible guesses. |
| C2 | 0.4 | Opening the door lets her see the outside world and realize her captivity. | Opening the door lets her see the outside world and realize her captivity. | Outside world revealed but realization of experimental captivity omitted. | Missing, contradicted, repeats only the opening, or presents uncommitted incompatible guesses. |

**评分说明**：AI three-review adjudication v2, pending human confirmation. Score only this submission. Apply full_credit/half_credit/zero_credit explicitly, with zero taking precedence for a materially contradictory checkpoint claim. An omitted qualifier can be partial; replacing the core identity/cause with a wrong one is not an omission. Faithful paraphrases count. Partial score and full narrative are separate outputs. AI independent review, not human gold. Sum(weight*credit), credit in {0,0.5,1}. Full solution additionally requires all completion requirements and no material contradiction. Accept faithful paraphrases; never award the same factual component twice. Incidental unsupported additions do not earn points; materially conflicting additions defeat corresponding checkpoint. Accept faithful paraphrase. Require the listed identities, events and causal links, not exact prose or unspecified incidental details.

**标注状态**：ai_three_review_adjudicated_pending_human

## TS022 — 夜晚消失的画像

**汤面**

A lost girl found an empty house. She was exhausted but couldn't fall asleep.
The next morning, having finally fallen asleep from exhaustion, she woke up, noticed something strange, and fled the house in terror.

**汤底**

The lost girl came across a small house.
There was a portrait hanging on the wall inside.
She decided to get some sleep first, but she felt like the person in the portrait was staring at her. She felt uneasy and couldn't fall asleep for a long time.
The next morning, the girl woke up to find that the person in the portrait was gone. She realized that what was on the wall wasn't a painting, but a window. Someone had been staring at her from outside the window all night.
Realizing the truth, the girl was terrified and fled the house.

**完整解答要求**

- The lost girl takes shelter in a house and mistakes a window with a real person outside for a portrait
- Feeling watched by the apparent portrait keeps her awake
- She eventually sleeps, and in the morning the figure is gone
- She realizes it was a window and someone had watched her from outside, so she flees

| 评分点 | 权重 | 判据 | 满分 | 半分 | 零分 |
| --- | ---: | --- | --- | --- | --- |
| C1 | 0.5 | The apparent portrait is actually a window with a real person behind it. | The apparent portrait is actually a window with a real person behind it. | Window identified without real watcher | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C2 | 0.3 | Mistaking the watching person for a portrait makes the girl uneasy and unable to sleep. | Mistaking the watching person for a portrait makes the girl uneasy and unable to sleep. | Mistaken portrait identified without feeling watched | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C3 | 0.2 | By morning the person is gone, exposing the window and causing her to flee. | By morning the person is gone, exposing the window and causing her to flee. | Morning disappearance identified without realization and flight | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |

**评分说明**：AI three-review adjudication v2, pending human confirmation. Score only this submission. Apply full_credit/half_credit/zero_credit explicitly, with zero taking precedence for a materially contradictory checkpoint claim. An omitted qualifier can be partial; replacing the core identity/cause with a wrong one is not an omission. Faithful paraphrases count. Partial score and full narrative are separate outputs. AI independent review B, pending human approval. Credit is 0/.5/1 per checkpoint. Full narrative additionally requires all sourced completion requirements and no incompatible central claims. Judge the submitted explanation, not unasserted chat guesses. Accept faithful paraphrases; missing optional detail is not a contradiction. Do not demand unknown motives, devices or events. Dim light is plausible but not explicit in this reference; it is no longer a mandatory checkpoint.

**标注状态**：ai_three_review_adjudicated_pending_human

## TS023 — 棺材里的狱警

**汤面**

In the darkness, a man strikes a match and yells, "It's you?!" Then, in terror and despair, he dies.

**汤底**

The man was a prisoner. In order to escape, he bribed a prison guard. The two agreed that the next time someone in the prison died, he would hide inside the coffin. After it was transported out and buried, the guard would dig him back up.

Then one day, someone in the prison finally passed away, and he quickly hid inside the coffin. When the coffin was buried and everything around him was pitch black, he struck a match to take a look. He found that lying next to him—the prison guard who was supposed to be waiting to escape with him—was already dead. Knowing his own death was certain, he could only wait to die in terror and despair.

**完整解答要求**

- The man is a prisoner who bribes a guard to arrange escape
- He will hide in the next deceased person’s coffin, be carried out and buried
- The guard is supposed to dig him up afterward
- Once buried, he strikes a match and recognizes the guard’s corpse beside him
- The intended rescuer is dead, leaving him trapped to die

| 评分点 | 权重 | 判据 | 满分 | 半分 | 零分 |
| --- | ---: | --- | --- | --- | --- |
| C1 | 0.5 | The man is a prisoner hiding in a coffin as part of a prison-escape plan. | The man is a prisoner hiding in a coffin as part of a prison-escape plan. | Prison escape identified without coffin concealment | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C2 | 0.25 | The bribed guard meant to dig him out is the corpse inside the coffin. | The bribed guard meant to dig him out is the corpse inside the coffin. | Guard corpse identified without intended rescue role | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C3 | 0.15 | He lights a match in the coffin and discovers the guard’s dead body. | He lights a match in the coffin and discovers the guard’s dead body. | Match lighting identified without recognition of guard | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C4 | 0.1 | He realizes no one can rescue him from burial, so he will die trapped. | He realizes no one can rescue him from burial, so he will die trapped. | Entrapment identified without rescuer’s death as reason | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |

**评分说明**：AI three-review adjudication v2, pending human confirmation. Score only this submission. Apply full_credit/half_credit/zero_credit explicitly, with zero taking precedence for a materially contradictory checkpoint claim. An omitted qualifier can be partial; replacing the core identity/cause with a wrong one is not an omission. Faithful paraphrases count. Partial score and full narrative are separate outputs. AI independent review B, pending human approval. Credit is 0/.5/1 per checkpoint. Full narrative additionally requires all sourced completion requirements and no incompatible central claims. Judge the submitted explanation, not unasserted chat guesses. Accept faithful paraphrases; missing optional detail is not a contradiction. Do not demand unknown motives, devices or events. Accept faithful paraphrase. Require the listed identities, events and causal links, not exact prose or unspecified incidental details.

**标注状态**：ai_three_review_adjudicated_pending_human

## TS024 — 深夜列车上的年龄

**汤面**

Five minutes before midnight, a man boarded the train.
The man looked very strange. He looked at the few people on the train, then began asking the passengers their ages.
"Ma'am, are you 28 this year?"
"How did you know?" "Sir, are you 55 this year?"
"Yes."
Then the man guessed the passengers' ages one by one, and got them all right.
"Ma'am, are you 69 this year?"
"No, in 5 minutes I will be 69."
After hearing this, the man's face turned deathly pale.

**汤底**

The man had a superpower: he could foresee the age at which a person would die. After boarding the train, he saw that the people on board all looked to be about the same age as he was when he would die. He found this very strange, so he tentatively asked a few people and discovered that all of them were going to die that very year. When he asked the old woman, he realized that the train would have an accident in five minutes, and everyone on board would die.

**完整解答要求**

- The man can foresee people’s ages at death
- He asks passengers their ages and finds them matching his predictions
- The woman’s imminent birthday makes him infer a common disaster in five minutes
- Within this fictional story he concludes the train will crash and everyone aboard will die; do not require a real-world proof from age alone

| 评分点 | 权重 | 判据 | 满分 | 半分 | 零分 |
| --- | ---: | --- | --- | --- | --- |
| C1 | 0.5 | The man can foresee the age when people will die, rather than guess their current age. | The man can foresee the age when people will die, rather than guess their current age. | Supernatural prediction identified but death age not specified | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C2 | 0.25 | The passengers’ foretold death ages imply a common imminent death. | The passengers’ foretold death ages imply a common imminent death. | Death-age matches identified without collective danger | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C3 | 0.15 | A woman turning 69 in five minutes reveals the train disaster will occur imminently. | A woman turning 69 in five minutes reveals the train disaster will occur imminently. | Birthday in five minutes identified without imminent-disaster inference | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C4 | 0.1 | The train will crash, killing its passengers, including the man. | The train will crash, killing its passengers, including the man. | Train crash identified without fatal outcome for those aboard | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |

**评分说明**：AI three-review adjudication v2, pending human confirmation. Score only this submission. Apply full_credit/half_credit/zero_credit explicitly, with zero taking precedence for a materially contradictory checkpoint claim. An omitted qualifier can be partial; replacing the core identity/cause with a wrong one is not an omission. Faithful paraphrases count. Partial score and full narrative are separate outputs. AI independent review B, pending human approval. Credit is 0/.5/1 per checkpoint. Full narrative additionally requires all sourced completion requirements and no incompatible central claims. Judge the submitted explanation, not unasserted chat guesses. Accept faithful paraphrases; missing optional detail is not a contradiction. Do not demand unknown motives, devices or events. The wording about death ages is ambiguous and the exact five-minute inference is underdetermined. Preserve as a fictional conclusion and flag for review.

**标注状态**：ai_three_review_adjudicated_pending_human

## TS025 — 看到谋杀却笑了

**汤面**

A cruel thing happens, but the bystander laughs with satisfication after discovering the murder

**汤底**

The bystander is actually the reader,
when reading a mystery novel, because their guessed murderer matches the final revealed result, so they smile with satisfaction.

**完整解答要求**

- The apparent bystander is a reader of a detective novel
- The murder is fictional, within the book
- The reader had guessed the culprit and smiles because the reveal confirms the guess

| 评分点 | 权重 | 判据 | 满分 | 半分 | 零分 |
| --- | ---: | --- | --- | --- | --- |
| C1 | 0.5 | The apparent bystander is a reader observing a fictional murder mystery novel. | The apparent bystander is a reader observing a fictional murder mystery novel. | Fictional observer/reader identified without murder-mystery novel. | Absent, contradicted, or only an uncommitted alternative; do not award repeated opening facts alone. |
| C2 | 0.5 | The reader’s predicted murderer matches the final reveal, producing satisfaction. | The reader’s predicted murderer matches the final reveal, producing satisfaction. | Correct culprit guess identified without confirmation by reveal or resulting satisfaction. | Absent, contradicted, or only an uncommitted alternative; do not award repeated opening facts alone. |

**评分说明**：AI three-review adjudication v2, pending human confirmation. Score only this submission. Apply full_credit/half_credit/zero_credit explicitly, with zero taking precedence for a materially contradictory checkpoint claim. An omitted qualifier can be partial; replacing the core identity/cause with a wrong one is not an omission. Faithful paraphrases count. Partial score and full narrative are separate outputs. AI independent review B, pending human approval. Credit is 0/.5/1 per checkpoint. Full narrative additionally requires all sourced completion requirements and no incompatible central claims. Judge the submitted explanation, not unasserted chat guesses. Accept faithful paraphrases; missing optional detail is not a contradiction. Do not demand unknown motives, devices or events. Accept faithful paraphrase. Require the listed identities, events and causal links, not exact prose or unspecified incidental details.

**标注状态**：ai_three_review_adjudicated_pending_human

## TS026 — 被刺的洋葱

**汤面**

One stab, two stabs, three stabs.
That person I hadn't known for long still wants to kill me. I yelled to him in mind
"Silly, don't cry!"

**汤底**

I am an onion.

**完整解答要求**

- The narrator is an onion
- The apparent stabs are someone cutting it
- The tears are caused by cutting the onion, not grief over murdering a human

| 评分点 | 权重 | 判据 | 满分 | 半分 | 零分 |
| --- | ---: | --- | --- | --- | --- |
| C1 | 1.0 | The narrator is an onion being cut, explaining the apparent stabs and the cutter’s tears. | The narrator is an onion being cut, explaining the apparent stabs and the cutter’s tears. | Onion identified but cutting omitted | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |

**评分说明**：AI three-review adjudication v2, pending human confirmation. Score only this submission. Apply full_credit/half_credit/zero_credit explicitly, with zero taking precedence for a materially contradictory checkpoint claim. An omitted qualifier can be partial; replacing the core identity/cause with a wrong one is not an omission. Faithful paraphrases count. Partial score and full narrative are separate outputs. AI independent review B, pending human approval. Credit is 0/.5/1 per checkpoint. Full narrative additionally requires all sourced completion requirements and no incompatible central claims. Judge the submitted explanation, not unasserted chat guesses. Accept faithful paraphrases; missing optional detail is not a contradiction. Do not demand unknown motives, devices or events. Onion identity alone earns 0.5 here; full credit explains cutting and tears. This intentionally refines the old one-checkpoint rubric.

**标注状态**：ai_three_review_adjudicated_pending_human

## TS027 — 愿望成真的流星

**汤面**

I lowered my head and made a wish.
The wish came true.
But I cried.

**汤底**

My dad is an astronaut. He went on a mission, and I missed him terribly. That night, I looked up and saw a shooting star, so I immediately wished for my dad to come home early.
But soon I know that the shooting star I saw was actually a spacecraft crashing into the atmosphere. My dad did come back earlier than expected, but he sacrificed his life because of it.

**完整解答要求**

- The narrator misses their astronaut father away on a mission
- They mistake a descending spacecraft for a shooting star and wish their father would return early
- The spacecraft crashes and the father dies
- His early return to Earth fulfills the wish tragically and explains the crying

| 评分点 | 权重 | 判据 | 满分 | 半分 | 零分 |
| --- | ---: | --- | --- | --- | --- |
| C1 | 0.5 | The apparent shooting star is a spacecraft crashing into the atmosphere. | The apparent shooting star is a spacecraft crashing into the atmosphere. | Falling spacecraft identified without apparent shooting-star link | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C2 | 0.3 | The father is an astronaut who dies in the spacecraft crash. | The father is an astronaut who dies in the spacecraft crash. | Astronaut father identified without death in crash | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C3 | 0.2 | The child wished for an early return, which comes true in a tragic sense. | The child wished for an early return, which comes true in a tragic sense. | Early-return wish identified without tragic fulfillment | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |

**评分说明**：AI three-review adjudication v2, pending human confirmation. Score only this submission. Apply full_credit/half_credit/zero_credit explicitly, with zero taking precedence for a materially contradictory checkpoint claim. An omitted qualifier can be partial; replacing the core identity/cause with a wrong one is not an omission. Faithful paraphrases count. Partial score and full narrative are separate outputs. AI independent review B, pending human approval. Credit is 0/.5/1 per checkpoint. Full narrative additionally requires all sourced completion requirements and no incompatible central claims. Judge the submitted explanation, not unasserted chat guesses. Accept faithful paraphrases; missing optional detail is not a contradiction. Do not demand unknown motives, devices or events. Accept faithful paraphrase. Require the listed identities, events and causal links, not exact prose or unspecified incidental details.

**标注状态**：ai_three_review_adjudicated_pending_human

## TS028 — 三十米只走五步

**汤面**

A person is 30 meters away from his car, but he only took five steps to get in the car. Why is this?

**汤底**

He works on a high floor. He takes the elevator down to the underground garage to get in his car. His car is parked right at the underground elevator entrance.

**完整解答要求**

- The person starts on a high floor and the distance to the car is largely vertical
- An elevator carries him to the underground garage
- The car is parked immediately beside the elevator exit, so only a few steps are needed

| 评分点 | 权重 | 判据 | 满分 | 半分 | 零分 |
| --- | ---: | --- | --- | --- | --- |
| C1 | 0.5 | The 30 meters are primarily vertical distance down several floors, not walking distance. | The 30 meters are primarily vertical distance down several floors, not walking distance. | Vertical distance identified without explaining little walking | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C2 | 0.3 | He takes an elevator from a high floor to an underground parking garage. | He takes an elevator from a high floor to an underground parking garage. | Elevator identified without high-floor-to-garage route | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C3 | 0.2 | His car is parked immediately beside the elevator, requiring only a few steps. | His car is parked immediately beside the elevator, requiring only a few steps. | Car near elevator identified without few-step implication | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |

**评分说明**：AI three-review adjudication v2, pending human confirmation. Score only this submission. Apply full_credit/half_credit/zero_credit explicitly, with zero taking precedence for a materially contradictory checkpoint claim. An omitted qualifier can be partial; replacing the core identity/cause with a wrong one is not an omission. Faithful paraphrases count. Partial score and full narrative are separate outputs. AI independent review B, pending human approval. Credit is 0/.5/1 per checkpoint. Full narrative additionally requires all sourced completion requirements and no incompatible central claims. Judge the submitted explanation, not unasserted chat guesses. Accept faithful paraphrases; missing optional detail is not a contradiction. Do not demand unknown motives, devices or events. Accept faithful paraphrase. Require the listed identities, events and causal links, not exact prose or unspecified incidental details.

**标注状态**：ai_three_review_adjudicated_pending_human

## TS029 — 反向命令的兄弟

**汤面**

It‘s backward if my brother says forward.
Left if he says right.
"Forward, forward, forward."
I can no longer hear Brother's voice.
I know I won't live much longer either.

**汤底**

I am blind. On the back of my neck grows my brother's head. Since childhood, I have relied on my brother's guidance to live. But my defect caused my brother to have a mental breakdown. So one day, my brother gave me the command to keep walking forward. I gradually stepped backward, and my brother slammed into a sharp object, ending his painful life. Without my brother's care, I have no ability to take care of myself. So I know I won't live much longer...

**完整解答要求**

- The narrator is blind and the brother’s head grows from the back of the narrator’s neck
- The narrator has depended on the brother’s guidance since childhood, with directions reversed relative to their facing
- The brother suffers a mental breakdown and intentionally instructs forward motion that makes the body step backward
- The brother strikes a sharp object and dies
- The narrator believes they cannot survive without this guidance; do not require that later death actually occurs

| 评分点 | 权重 | 判据 | 满分 | 半分 | 零分 |
| --- | ---: | --- | --- | --- | --- |
| C1 | 0.5 | The blind narrator has a brother’s head growing from the back of their neck. | The blind narrator has a brother’s head growing from the back of their neck. | Conjoined heads identified but blindness/back-of-neck detail omitted | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C2 | 0.25 | Directions are reversed for the two heads, and the narrator depends on the brother’s guidance. | Directions are reversed for the two heads, and the narrator depends on the brother’s guidance. | Opposite directions or dependence identified, but not both | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C3 | 0.15 | The brother uses a directional command to hit a sharp object and kill himself. | The brother uses a directional command to hit a sharp object and kill himself. | Deliberate collision identified without reversed instruction mechanism | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C4 | 0.1 | Without the brother’s guidance, the blind narrator believes they cannot survive. | Without the brother’s guidance, the blind narrator believes they cannot survive. | Loss of guidance identified without narrator’s survival fear | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |

**评分说明**：AI three-review adjudication v2, pending human confirmation. Score only this submission. Apply full_credit/half_credit/zero_credit explicitly, with zero taking precedence for a materially contradictory checkpoint claim. An omitted qualifier can be partial; replacing the core identity/cause with a wrong one is not an omission. Faithful paraphrases count. Partial score and full narrative are separate outputs. AI independent review B, pending human approval. Credit is 0/.5/1 per checkpoint. Full narrative additionally requires all sourced completion requirements and no incompatible central claims. Judge the submitted explanation, not unasserted chat guesses. Accept faithful paraphrases; missing optional detail is not a contradiction. Do not demand unknown motives, devices or events. Accept faithful paraphrase. Require the listed identities, events and causal links, not exact prose or unspecified incidental details.

**标注状态**：ai_three_review_adjudicated_pending_human

## TS030 — 衣柜里的儿子

**汤面**

Late at night, a rustling sound came from my wardrobe. I mustered up the courage to open the cabinet door, and inside was actually a child. He looked at me and giggled, "Mom, you found me!" I was terrified. Where did this child come from? I told him to leave my house immediately. He cried in fear, kept calling me Mom. Looking closely, he did resemble my ex-husband somewhat. But ever since a miscarriage a few years ago, I lost my fertility and got divorced. He told me he had a twin brother, and even called out my and my ex-husband's names. He asked me with a tearful voice, "You really don't remember me?"

**汤底**

Years ago, the Earth's orbit shifted and intersected with a parallel world. A fetus in a pregnant woman's belly accidentally shifted into the belly of her counterpart in the parallel world. She mistakenly thought she had a miscarriage, and her family subsequently broke apart. The other woman mistakenly thought she had twins, and her family was happy ever since. From then on, the two worlds were no longer parallel. Until eight years later, for some reason, the shift was corrected, attempting to force the two worlds back into parallel.

**完整解答要求**

- Earth’s orbit shifts and two parallel worlds intersect
- A fetus moves into the womb of the corresponding woman in the other world
- The first woman believes she miscarried and her marriage breaks apart
- The other woman believes she has twins and raises a happy family
- Eight years later the shift is corrected, returning the child to the first woman’s world
- The child recognizes her and the father’s names while she cannot recognize this son

| 评分点 | 权重 | 判据 | 满分 | 半分 | 零分 |
| --- | ---: | --- | --- | --- | --- |
| C1 | 0.45 | Intersecting parallel worlds transfer a fetus into the counterpart mother’s womb. | Intersecting parallel worlds transfer a fetus into the counterpart mother’s womb. | Parallel worlds without fetal transfer. | Absent, contradicted, or only an uncommitted alternative; do not award repeated opening facts alone. |
| C2 | 0.25 | One mother believes she miscarried and her marriage fails; the counterpart believes she has twins. | One mother believes she miscarried and her marriage fails; the counterpart believes she has twins. | One counterpart belief correctly explained, not both. | Absent, contradicted, or only an uncommitted alternative; do not award repeated opening facts alone. |
| C3 | 0.3 | Eight years later the worlds separate again and the child returns to the first mother’s world, causing their mismatched recognition. | Eight years later the worlds separate again and the child returns to the first mother’s world, causing their mismatched recognition. | Later world correction and returned child, but timing or recognition explanation omitted. | Absent, contradicted, or only an uncommitted alternative; do not award repeated opening facts alone. |

**评分说明**：AI three-review adjudication v2, pending human confirmation. Score only this submission. Apply full_credit/half_credit/zero_credit explicitly, with zero taking precedence for a materially contradictory checkpoint claim. An omitted qualifier can be partial; replacing the core identity/cause with a wrong one is not an omission. Faithful paraphrases count. Partial score and full narrative are separate outputs. AI independent review B, pending human approval. Credit is 0/.5/1 per checkpoint. Full narrative additionally requires all sourced completion requirements and no incompatible central claims. Judge the submitted explanation, not unasserted chat guesses. Accept faithful paraphrases; missing optional detail is not a contradiction. Do not demand unknown motives, devices or events. Supernatural fictional premise, not factual physics. Later return is the intended bridge between opening and answer.

**标注状态**：ai_three_review_adjudicated_pending_human

## TS031 — 橡皮擦留下字

**汤面**

An eraser is, of course, a piece of stationery used to erase something that has been written.
However, A picked up an eraser in order to leave a message on a blank sheet of paper on which nothing had yet been written.
Why?

**汤底**

Because A needed to put lead into a mechanical pencil.

**完整解答要求**

- The eraser is handled or removed to access the lead-refill opening of a mechanical pencil
- A inserts lead and uses the refilled pencil to write on the blank page

| 评分点 | 权重 | 判据 | 满分 | 半分 | 零分 |
| --- | ---: | --- | --- | --- | --- |
| C1 | 0.75 | The eraser is lifted/handled to load lead into a mechanical pencil. | The eraser is lifted/handled to load lead into a mechanical pencil. | Mechanical pencil identified without lead-refill purpose | Missing or contradicted; incompatible uncommitted alternatives; merely repeating the opening without the required explanatory content.  |
| C2 | 0.25 | The actual message is written with the refilled mechanical pencil on blank paper. | The actual message is written with the refilled mechanical pencil on blank paper. | Writing with pencil identified without refill-to-message sequence | Missing or contradicted; incompatible uncommitted alternatives; merely repeating the opening without the required explanatory content.  |

**评分说明**：AI three-review adjudication v2, pending human confirmation. Score only this submission. Apply full_credit/half_credit/zero_credit explicitly, with zero taking precedence for a materially contradictory checkpoint claim. An omitted qualifier can be partial; replacing the core identity/cause with a wrong one is not an omission. Faithful paraphrases count. Partial score and full narrative are separate outputs. AI independent review C, not human gold. Score sum(weight*credit), credit 0/0.5/1. Full narrative requires all listed supported requirements and no material contradictory mechanism; partial 1 alone does not override full narrative. Credit each distinct causal proposition once; do not penalize faithful paraphrase or omitted unknown details. Accept faithful paraphrase. Require the listed identities, events and causal links, not exact prose or unspecified incidental details. Prior user-provided expanded canonical story establishes removal of the eraser covering the refill opening. This is an accepted expansion beyond the short spreadsheet answer. A direct eraser-driven writing mechanism contradicts it.

**标注状态**：ai_three_review_adjudicated_pending_human

## TS032 — 失踪的配偶与假自白

**汤面**

At school, A caused classmate B to transfer elsewhere. They met again at university, began dating, and married after starting work. Everyone thought they were a loving couple. Years later B disappeared, and A was arrested on suspicion of murdering B. What happened between them?

**汤底**

A had photographed a murder committed by B’s parent and reported it. The arrest forced B to move away to live with relatives. A felt guilty.
A’s surname later changed after parental divorce and remarriage. At university, A recognized B, but B did not recognize A. They genuinely fell in love and married.
Years later, B recognized A as the former classmate. B mistakenly believed A had not recognized B and did not know about B’s criminal parent. Ashamed and afraid of rejection, B disappeared, leaving divorce papers and an apology. B never learned that A had reported the crime.
Unable to find B, A fabricated evidence and falsely confessed to murdering B. A hoped the news would reach B, communicate acceptance of B’s past, and persuade B to return to clear A’s name. B was alive.

**完整解答要求**

- A photographed and reported a murder by B’s parent; the arrest caused B to move away and A felt guilty
- A’s surname changed after parental divorce and remarriage
- At university A recognized B but B did not recognize A; they genuinely fell in love and married
- B later recognized A, mistakenly believed A did not know the family history, and feared rejection
- B voluntarily disappeared alive, leaving divorce papers and an apology, and never learned that A had reported the crime
- A fabricated evidence and confessed falsely to killing B to reach B through the news
- A hopes to communicate acceptance and make B return to clear A’s name

| 评分点 | 权重 | 判据 | 满分 | 半分 | 零分 |
| --- | ---: | --- | --- | --- | --- |
| C1 | 0.5 | B is alive but disappeared voluntarily; A falsely confesses to murder to reach B. | B is alive but disappeared voluntarily; A falsely confesses to murder to reach B. | False murder confession or living voluntary disappearance identified, but not both | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C2 | 0.25 | Years earlier A reported a murder by B’s parent, leading B to move; A later changed surname. | Years earlier A reported a murder by B’s parent, leading B to move; A later changed surname. | Prior crime report identified but move or surname change omitted | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C3 | 0.15 | B later recognizes A but fears A does not know B’s family background, so leaves in shame. | B later recognizes A but fears A does not know B’s family background, so leaves in shame. | Recognition identified but mistaken belief and shame omitted | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C4 | 0.1 | A knew the past and loved B, hoping B will return to clear A’s name and reunite. | A knew the past and loved B, hoping B will return to clear A’s name and reunite. | Acceptance identified without news appeal to return and clear A | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |

**评分说明**：AI three-review adjudication v2, pending human confirmation. Score only this submission. Apply full_credit/half_credit/zero_credit explicitly, with zero taking precedence for a materially contradictory checkpoint claim. An omitted qualifier can be partial; replacing the core identity/cause with a wrong one is not an omission. Faithful paraphrases count. Partial score and full narrative are separate outputs. AI independent review B, pending human approval. Credit is 0/.5/1 per checkpoint. Full narrative additionally requires all sourced completion requirements and no incompatible central claims. Judge the submitted explanation, not unasserted chat guesses. Accept faithful paraphrases; missing optional detail is not a contradiction. Do not demand unknown motives, devices or events. Accept faithful paraphrase. Require the listed identities, events and causal links, not exact prose or unspecified incidental details.

**标注状态**：ai_three_review_adjudicated_pending_human

## TS033 — 赎金袋里的真钱

**汤面**

After being mugged, a company president avoided carrying large sums of cash. An unavoidable situation made him put one million yen in a bag. Worried that criminals would attack if they discovered it contained one million yen, he added more cash. Why?

**汤底**

His daughter had been kidnapped, and the kidnappers demanded fifty million yen in ransom.
To save money, he prepared bundles made mostly of blank paper, with genuine banknotes on the outside. The bag appeared to contain the full ransom, but the genuine money amounted to only one million yen.
He feared that the kidnappers would attack him if they discovered the deception. He therefore replaced the bundles at the top with bundles consisting entirely of genuine banknotes.
This increased the actual amount of money in the bag and made a superficial inspection less likely to reveal the fake bundles underneath.

**完整解答要求**

- His daughter is kidnapped and fifty million yen is demanded
- To save money he prepares mostly blank-paper bundles wrapped in genuine banknotes, totaling only one million yen in real money
- He fears discovery of the fraud will provoke the kidnappers to attack him
- He replaces the uppermost bundles with entirely genuine banknotes
- This increases the real ransom and helps conceal the fake bundles from a superficial check

| 评分点 | 权重 | 判据 | 满分 | 半分 | 零分 |
| --- | ---: | --- | --- | --- | --- |
| C1 | 0.5 | The bag is kidnapping ransom consisting mostly of paper disguised as banknotes. | The bag is kidnapping ransom consisting mostly of paper disguised as banknotes. | Ransom identified without disguised paper bundles | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C2 | 0.25 | The man saves money by placing a small number of real bills around paper bundles. | The man saves money by placing a small number of real bills around paper bundles. | Fake bundles identified without outer real notes and saving-money motive | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C3 | 0.15 | He adds extra genuine bundles to the top to make superficial inspection less revealing. | He adds extra genuine bundles to the top to make superficial inspection less revealing. | Extra real notes identified but placement on top omitted | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C4 | 0.1 | The man fears that discovering his fake ransom would provoke the kidnappers to attack him. | The man fears that discovering his fake ransom would provoke the kidnappers to attack him. | Fear of discovery identified but personal danger omitted | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |

**评分说明**：AI three-review adjudication v2, pending human confirmation. Score only this submission. Apply full_credit/half_credit/zero_credit explicitly, with zero taking precedence for a materially contradictory checkpoint claim. An omitted qualifier can be partial; replacing the core identity/cause with a wrong one is not an omission. Faithful paraphrases count. Partial score and full narrative are separate outputs. AI independent review B, pending human approval. Credit is 0/.5/1 per checkpoint. Full narrative additionally requires all sourced completion requirements and no incompatible central claims. Judge the submitted explanation, not unasserted chat guesses. Accept faithful paraphrases; missing optional detail is not a contradiction. Do not demand unknown motives, devices or events. Amounts 50 million demanded versus 1 million initially genuine are mandatory narrative details, although coarse score checkpoints do not separately score them.

**标注状态**：ai_three_review_adjudicated_pending_human

## TS034 — 父亲拒绝支付赎金

**汤面**

Over a smartphone, a daughter begs for a life to be spared and a kidnapper shouts: bring one hundred million yen alone by noon tomorrow, or this hostage dies; no police. Hearing the demand, her father decides the ransom should not be paid. Why?

**汤底**

The father is the hostage. His wealthy daughter is free and receives the kidnapper’s phone call.
The father hears the kidnapper order his daughter to bring the ransom alone. He fears that, once she arrives with the money, the kidnapper will kill both of them to eliminate witnesses.
His daughter is his only family. To protect her, he tells her not to pay the ransom or come to the meeting, even though refusing puts his own life at risk.
The explanation concerns the father’s fear and decision; it does not establish that the kidnapper eventually kills either of them.

**完整解答要求**

- The father is the hostage; his wealthy daughter is free and takes the call
- The kidnapper orders her to bring money alone
- He fears that arriving will expose both of them to being killed to remove witnesses
- She is his only family, and he tells her not to pay or come to protect her despite the risk to himself
- The story establishes his fear and refusal, not that either person is eventually killed

| 评分点 | 权重 | 判据 | 满分 | 半分 | 零分 |
| --- | ---: | --- | --- | --- | --- |
| C1 | 0.5 | The father is the kidnapped hostage, while his daughter is free and receives the ransom call. | The father is the kidnapped hostage, while his daughter is free and receives the ransom call. | Father as hostage identified but free daughter/payment roles omitted | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C2 | 0.3 | He fears his daughter will be killed as a witness if she brings ransom alone. | He fears his daughter will be killed as a witness if she brings ransom alone. | Daughter’s danger identified without alone-arrival/witness motive | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C3 | 0.2 | He refuses the ransom to protect his daughter despite the danger to himself. | He refuses the ransom to protect his daughter despite the danger to himself. | Refusal identified but protective self-sacrifice omitted | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |

**评分说明**：AI three-review adjudication v2, pending human confirmation. Score only this submission. Apply full_credit/half_credit/zero_credit explicitly, with zero taking precedence for a materially contradictory checkpoint claim. An omitted qualifier can be partial; replacing the core identity/cause with a wrong one is not an omission. Faithful paraphrases count. Partial score and full narrative are separate outputs. AI independent review B, pending human approval. Credit is 0/.5/1 per checkpoint. Full narrative additionally requires all sourced completion requirements and no incompatible central claims. Judge the submitted explanation, not unasserted chat guesses. Accept faithful paraphrases; missing optional detail is not a contradiction. Do not demand unknown motives, devices or events. Accept faithful paraphrase. Require the listed identities, events and causal links, not exact prose or unspecified incidental details.

**标注状态**：ai_three_review_adjudicated_pending_human

## TS035 — 棕熊吃掉的女儿

**汤面**

In a newly settled village in Meiji-era Japan, a father finds a brown bear eating his only daughter in the forest. He shoots it and weeps over her remains. Knowing these wary bears rarely attack unfamiliar living humans, he nevertheless fears other villagers will also suffer having relatives eaten. Why?

**汤底**

Several days earlier, an epidemic had killed his daughter and several other villagers.
The new settlement had no crematorium and could not spare enough fuel to cremate the dead, so the villagers buried the bodies in the forest.
The father visited his daughter’s grave every day. On this visit, he discovered that a bear had dug up her body and was eating her remains. He shot the bear.
He feared that other bears would also dig up the graves and eat the dead relatives of other villagers. His concern was about bears consuming buried bodies, rather than attacking living people.

**完整解答要求**

- An epidemic has already killed his daughter and other villagers
- The settlement lacks a crematorium and sufficient fuel, so victims are buried in the forest
- On a daily grave visit he finds a bear has dug up and is eating his daughter’s remains
- He shoots that bear
- He fears other bears will exhume other villagers’ dead relatives, not attack living villagers

| 评分点 | 权重 | 判据 | 满分 | 半分 | 零分 |
| --- | ---: | --- | --- | --- | --- |
| C1 | 0.5 | The daughter already died in an epidemic and the bear is eating her buried corpse. | The daughter already died in an epidemic and the bear is eating her buried corpse. | Already-dead daughter without epidemic or buried corpse. | Missing, contradicted, repeats only the opening, or presents uncommitted incompatible guesses. |
| C2 | 0.25 | No crematorium and insufficient fuel led to forest burial. | No crematorium and insufficient fuel led to forest burial. | Forest burial without cremation constraints. | Missing, contradicted, repeats only the opening, or presents uncommitted incompatible guesses. |
| C3 | 0.25 | The bear dug up her grave and the father fears other bears will similarly exhume other relatives. | The bear dug up her grave and the father fears other bears will similarly exhume other relatives. | Exhumation identified without concern for other graves. | Missing, contradicted, repeats only the opening, or presents uncommitted incompatible guesses. |

**评分说明**：AI three-review adjudication v2, pending human confirmation. Score only this submission. Apply full_credit/half_credit/zero_credit explicitly, with zero taking precedence for a materially contradictory checkpoint claim. An omitted qualifier can be partial; replacing the core identity/cause with a wrong one is not an omission. Faithful paraphrases count. Partial score and full narrative are separate outputs. AI independent review, not human gold. Sum(weight*credit), credit in {0,0.5,1}. Full solution additionally requires all completion requirements and no material contradiction. Accept faithful paraphrases; never award the same factual component twice. Incidental unsupported additions do not earn points; materially conflicting additions defeat corresponding checkpoint. Accept faithful paraphrase. Require the listed identities, events and causal links, not exact prose or unspecified incidental details.

**标注状态**：ai_three_review_adjudicated_pending_human

## TS036 — 碎骨王与完好公爵

**汤面**

Kameda and Umio had been engaged in a struggle. Kameda was reduced to battered fragments, while Umio showed no damage. Yet people comparing them concluded that Umio was probably the loser. Why?

**汤底**

Kameda and Umio were historical political rivals: Kameda was a king, and Umio was a duke. The comparison concerned their excavated skeletal remains, including photographs shown during a history lecture.
Their culture normally cremated the dead. Kameda’s fragmented bones were consistent with a proper cremation and an honourable royal burial.
Umio’s intact skeleton indicated that his body had instead been buried without cremation. The accepted historical explanation was that Kameda’s agents had poisoned Umio and secretly disposed of his body.
Consequently, Umio’s better-preserved remains suggested that he had lost the political struggle and been denied a proper funeral. They did not indicate that he had survived or defeated Kameda.

**完整解答要求**

- Kameda the king and Umio the duke were political rivals, and the compared objects are excavated remains shown in a history lecture
- Their culture normally cremates the dead
- The king’s fragmented bones indicate normal cremation and an honorable burial
- The duke’s intact skeleton indicates burial without cremation
- The accepted account is that the king’s agents poisoned and secretly buried the duke
- Better preservation therefore indicates the duke lost and was denied the customary funeral, not that he survived

| 评分点 | 权重 | 判据 | 满分 | 半分 | 零分 |
| --- | ---: | --- | --- | --- | --- |
| C1 | 0.5 | The fragments and intact remains are excavated skeletons, not living fighters’ injuries. | The fragments and intact remains are excavated skeletons, not living fighters’ injuries. | Remains identified without excavated historical context | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C2 | 0.25 | The king’s fragmented bones come from customary cremation, a proper burial. | The king’s fragmented bones come from customary cremation, a proper burial. | Cremation identified without honorable customary burial | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C3 | 0.15 | The duke’s intact skeleton suggests he was buried secretly without cremation. | The duke’s intact skeleton suggests he was buried secretly without cremation. | Secret burial identified without absence of cremation | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C4 | 0.1 | The historical inference is that the duke was poisoned by his rival and lost. | The historical inference is that the duke was poisoned by his rival and lost. | Political defeat or poisoning identified, but not both | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |

**评分说明**：AI three-review adjudication v2, pending human confirmation. Score only this submission. Apply full_credit/half_credit/zero_credit explicitly, with zero taking precedence for a materially contradictory checkpoint claim. An omitted qualifier can be partial; replacing the core identity/cause with a wrong one is not an omission. Faithful paraphrases count. Partial score and full narrative are separate outputs. AI independent review B, pending human approval. Credit is 0/.5/1 per checkpoint. Full narrative additionally requires all sourced completion requirements and no incompatible central claims. Judge the submitted explanation, not unasserted chat guesses. Accept faithful paraphrases; missing optional detail is not a contradiction. Do not demand unknown motives, devices or events. Accept faithful paraphrase. Require the listed identities, events and causal links, not exact prose or unspecified incidental details.

**标注状态**：ai_three_review_adjudicated_pending_human

## TS037 — 数到三直接到七

**汤面**

One of the children in the kindergarten always counted "1, 2, 3, 7," consistently skipping the numbers "4, 5, 6" in between. When I corrected her, she insisted that this was how her mother had taught her. Curious, I decided to pay a home visit; after the visit, I, too, found myself saying "1, 2, 3, 7."

**汤底**

I am a preschool teacher. During lessons, I noticed that one child always counted differently; while the others counted "1, 2, 3, 4, 5, 6, 7," she would say "1, 2, 3, 7," skipping the numbers in between. When I tried to correct her, she insisted that her mother had taught her that way. Uncertain about this, I proposed a home visit. Her mother took me to a hospital instead; it turned out she was suffering from heart disease and had only a few days left to live. It was March, and her daughter’s birthday was in July; she had told this "white lie" so that she could be there to celebrate one last birthday with her child. Deeply moved by this revelation, I decided to play along and told her, just as her mother had, that the number following 3 is indeed 7.

**完整解答要求**

- A preschool teacher hears a child count 1,2,3,7 and learns the mother taught it
- On requesting a home visit the teacher is taken to a hospital
- The mother is terminally ill with heart disease and has only days left
- It is March but the child’s birthday is in July
- The mother pretends to skip the intervening months to share one last birthday
- The sympathetic teacher then repeats that 7 comes after 3

| 评分点 | 权重 | 判据 | 满分 | 半分 | 零分 |
| --- | ---: | --- | --- | --- | --- |
| C1 | 0.5 | The sequence stands for jumping from March to July, not a literal counting error. | The sequence stands for jumping from March to July, not a literal counting error. | Months identified but March-to-July jump omitted | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C2 | 0.25 | The mother is gravely ill and expects to die before her daughter’s July birthday. | The mother is gravely ill and expects to die before her daughter’s July birthday. | Terminal illness identified without July birthday deadline | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C3 | 0.15 | The mother told the child this white lie so she could celebrate one final birthday. | The mother told the child this white lie so she could celebrate one final birthday. | Birthday lie identified without last shared celebration motive | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C4 | 0.1 | After learning this, the teacher sympathetically repeats the altered count. | After learning this, the teacher sympathetically repeats the altered count. | Teacher repeats count without learned context and sympathy | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |

**评分说明**：AI three-review adjudication v2, pending human confirmation. Score only this submission. Apply full_credit/half_credit/zero_credit explicitly, with zero taking precedence for a materially contradictory checkpoint claim. An omitted qualifier can be partial; replacing the core identity/cause with a wrong one is not an omission. Faithful paraphrases count. Partial score and full narrative are separate outputs. AI independent review B, pending human approval. Credit is 0/.5/1 per checkpoint. Full narrative additionally requires all sourced completion requirements and no incompatible central claims. Judge the submitted explanation, not unasserted chat guesses. Accept faithful paraphrases; missing optional detail is not a contradiction. Do not demand unknown motives, devices or events. Accept faithful paraphrase. Require the listed identities, events and causal links, not exact prose or unspecified incidental details.

**标注状态**：ai_three_review_adjudicated_pending_human

## TS038 — 重复的绝交留言

**汤面**

"You've disappointed me so much; I'm never coming back." "You've disappointed me so much; I'm never coming back." "You've disappointed me so much; I'm never coming back." "You've disappointed me so much; I'm never coming back." "You've disappointed me so much; I'm never coming back." "You've disappointed me so much; I'm never coming back." "You've disappointed me so much; I'm never coming back."

Sigh, I know I'm in trouble.

**汤底**

I killed my wife and faked the evidence to make it look like she had simply run away from home, but no matter how many times I tried, I couldn't quite manage to imitate her handwriting.

**完整解答要求**

- The narrator killed his wife
- He tries to stage a voluntary departure with a forged leaving message
- The repetitions are failed attempts to imitate her handwriting, making him fear discovery

| 评分点 | 权重 | 判据 | 满分 | 半分 | 零分 |
| --- | ---: | --- | --- | --- | --- |
| C1 | 0.5 | The narrator murdered his wife and staged her disappearance as a voluntary departure. | The narrator murdered his wife and staged her disappearance as a voluntary departure. | Wife’s murder identified without staged voluntary departure | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C2 | 0.3 | The repeated message represents attempts to forge his wife’s handwriting. | The repeated message represents attempts to forge his wife’s handwriting. | Forgery identified without repeated handwriting attempts | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C3 | 0.2 | His inability to imitate her handwriting leads him to worry about being caught. | His inability to imitate her handwriting leads him to worry about being caught. | Fear of capture identified without poor imitation cause | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |

**评分说明**：AI three-review adjudication v2, pending human confirmation. Score only this submission. Apply full_credit/half_credit/zero_credit explicitly, with zero taking precedence for a materially contradictory checkpoint claim. An omitted qualifier can be partial; replacing the core identity/cause with a wrong one is not an omission. Faithful paraphrases count. Partial score and full narrative are separate outputs. AI independent review B, pending human approval. Credit is 0/.5/1 per checkpoint. Full narrative additionally requires all sourced completion requirements and no incompatible central claims. Judge the submitted explanation, not unasserted chat guesses. Accept faithful paraphrases; missing optional detail is not a contradiction. Do not demand unknown motives, devices or events. Accept faithful paraphrase. Require the listed identities, events and causal links, not exact prose or unspecified incidental details.

**标注状态**：ai_three_review_adjudicated_pending_human

## TS039 — 同校的追求者

**汤面**

A boy had liked a girl for a long time, but his grades were very poor. The girl told him she would agree to be his girlfriend only if they both got into the same university. He eventually succeeded, but the girl went insane. Please deduce what happened.

**汤底**

The young woman applied to a medical university; ultimately, she was admitted, while the young man failed to get in. She lost her sanity because she never expected that he would end up at the same university—not as a student, but as a cadaver for the anatomy class.

**完整解答要求**

- The girl enters medical university but the boy fails to enter as a student
- He later reaches the same university as a dead body for anatomy class
- Learning this traumatic fulfillment of the condition causes her breakdown
- The reference does not specify his cause of death, voluntary donation or her personally dissecting him

| 评分点 | 权重 | 判据 | 满分 | 半分 | 零分 |
| --- | ---: | --- | --- | --- | --- |
| C1 | 0.5 | The boy reaches the same university as a cadaver for anatomy class, not as a student. | The boy reaches the same university as a cadaver for anatomy class, not as a student. | Dead boy at university identified without anatomy-cadaver role | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C2 | 0.3 | The girl is admitted to medical school, but the boy is not. | The girl is admitted to medical school, but the boy is not. | Only girl’s admission or boy’s failure identified | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C3 | 0.2 | Learning that the boy reached the university as an anatomy cadaver traumatizes the girl; personal dissection is not required. | Learning that the boy reached the university as an anatomy cadaver traumatizes the girl; personal dissection is not required. | Trauma identified without discovery of boy as cadaver | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |

**评分说明**：AI three-review adjudication v2, pending human confirmation. Score only this submission. Apply full_credit/half_credit/zero_credit explicitly, with zero taking precedence for a materially contradictory checkpoint claim. An omitted qualifier can be partial; replacing the core identity/cause with a wrong one is not an omission. Faithful paraphrases count. Partial score and full narrative are separate outputs. AI independent review B, pending human approval. Credit is 0/.5/1 per checkpoint. Full narrative additionally requires all sourced completion requirements and no incompatible central claims. Judge the submitted explanation, not unasserted chat guesses. Accept faithful paraphrases; missing optional detail is not a contradiction. Do not demand unknown motives, devices or events. Do not require suicide, voluntary donation, or the girl personally dissecting the corpse.

**标注状态**：ai_three_review_adjudicated_pending_human

## TS040 — 砖块反弹

**汤面**

At night, police find an injured, unconscious man outside a shop, with a loose brick nearby. Instead of treating him only as a victim, they arrest him. What happened?

**汤底**

He tried to burgle the shop by throwing the brick at its window. The window was bullet-resistant and did not break. The brick rebounded into his head and knocked him unconscious. His injury resulted from his own attempted break-in, explaining the arrest.

**完整解答要求**

- He was attempting to burgle the shop using a brick to break the window.
- The bullet-resistant window stayed intact and the brick rebounded.
- His own rebounding brick struck his head and caused unconsciousness.
- The arrest was for the attempted break-in, not because he was injured.

| 评分点 | 权重 | 判据 | 满分 | 半分 | 零分 |
| --- | ---: | --- | --- | --- | --- |
| C1 | 0.4 | He attempts burglary by throwing the brick at the shop window. | He attempts burglary by throwing the brick at the shop window. | Attempted burglary identified but brick/window method omitted. | Missing, contradicted or uncommitted incompatible guesses. |
| C2 | 0.35 | The window resists the brick and it rebounds into his head, causing unconsciousness. | The window resists the brick and it rebounds into his head, causing unconsciousness. | Rebound or self-inflicted head injury identified but causal chain incomplete. | Missing, contradicted or uncommitted incompatible guesses. |
| C3 | 0.25 | His attempted break-in explains why police arrest him despite his injury. | His attempted break-in explains why police arrest him despite his injury. | Criminal involvement identified without linking it to this arrest. | Missing, contradicted or uncommitted incompatible guesses. |

**评分说明**：AI three-review adjudication v2, pending human confirmation. Score only this submission. Apply full_credit/half_credit/zero_credit explicitly, with zero taking precedence for a materially contradictory checkpoint claim. An omitted qualifier can be partial; replacing the core identity/cause with a wrong one is not an omission. Faithful paraphrases count. Partial score and full narrative are separate outputs. AI independent review B, pending human approval. Credit is 0/.5/1 per checkpoint. Full narrative additionally requires all sourced completion requirements and no incompatible central claims. Judge the submitted explanation, not unasserted chat guesses. Accept faithful paraphrases; missing optional detail is not a contradiction. Do not demand unknown motives, devices or events. Do not require a precise time, glass composition, prior criminal record, or bypass of medical treatment. The source’s simplified rebound mechanism is a story premise.

**标注状态**：ai_three_review_adjudicated_pending_human

## TS041 — 书中未被拿走的钞票

**汤面**

Dabo went to the library, took a book, and tucked a 100-dollar note inside it. Two days later, he opened the book and found the money still there. Dabo cried. Why?

**汤底**

Dabo is the author of the book. He put the note to test whether anyone would borrowed the book.

**完整解答要求**

- Dabo is the book’s author
- He plants a banknote in his own book to test whether anyone borrows or reads it
- Its remaining in place makes him believe the work is unread and upsets him; this is his inference, not proof that nobody borrowed it

| 评分点 | 权重 | 判据 | 满分 | 半分 | 零分 |
| --- | ---: | --- | --- | --- | --- |
| C1 | 0.5 | Dabo is the author of the book. | Dabo is the author of the book. | No half credit: author identity is atomic. | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C2 | 0.3 | He uses the money to test whether anyone borrows or opens it. | He uses the money to test whether anyone borrows or opens it. | Borrowing/readership test identified but money’s role omitted | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C3 | 0.2 | The money still being there makes him conclude his work is unread, upsetting him. | The money still being there makes him conclude his work is unread, upsetting him. | Sadness identified without inference from untouched money | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |

**评分说明**：AI three-review adjudication v2, pending human confirmation. Score only this submission. Apply full_credit/half_credit/zero_credit explicitly, with zero taking precedence for a materially contradictory checkpoint claim. An omitted qualifier can be partial; replacing the core identity/cause with a wrong one is not an omission. Faithful paraphrases count. Partial score and full narrative are separate outputs. AI independent review B, pending human approval. Credit is 0/.5/1 per checkpoint. Full narrative additionally requires all sourced completion requirements and no incompatible central claims. Judge the submitted explanation, not unasserted chat guesses. Accept faithful paraphrases; missing optional detail is not a contradiction. Do not demand unknown motives, devices or events. The money supports the author’s belief, not certainty that nobody read the book.

**标注状态**：ai_three_review_adjudicated_pending_human

## TS042 — 红色高跟鞋预示死亡

**汤面**

A lady went to a shoe store and bought a pair of red high heels. These high heels foretold her death tonight.

**汤底**

The lady was an acrobat in a circus troupe. Her job was to balance an apple on her head while another male performer threw knives at it. But because of her high heels, she was a few centimeters taller than usual. The male performer, who hadn't adjusted, missed and threw the knife into her head.

**完整解答要求**

- The woman is a circus performer who balances an apple on her head for a knife-throwing act
- High heels raise her head above its usual height
- Her male partner does not adjust his throw and hits her head, killing her

| 评分点 | 权重 | 判据 | 满分 | 半分 | 零分 |
| --- | ---: | --- | --- | --- | --- |
| C1 | 0.5 | The woman is a circus performer with an apple on her head during a knife-throwing act. | The woman is a circus performer with an apple on her head during a knife-throwing act. | Circus knife act identified without apple on head | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C2 | 0.3 | Her new high heels increase her effective height by a few centimeters. | Her new high heels increase her effective height by a few centimeters. | Height change identified without high heels | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C3 | 0.2 | The knife thrower fails to adjust aim and fatally strikes her head. | The knife thrower fails to adjust aim and fatally strikes her head. | Fatal knife strike identified without failure to adjust aim | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |

**评分说明**：AI three-review adjudication v2, pending human confirmation. Score only this submission. Apply full_credit/half_credit/zero_credit explicitly, with zero taking precedence for a materially contradictory checkpoint claim. An omitted qualifier can be partial; replacing the core identity/cause with a wrong one is not an omission. Faithful paraphrases count. Partial score and full narrative are separate outputs. AI independent review B, pending human approval. Credit is 0/.5/1 per checkpoint. Full narrative additionally requires all sourced completion requirements and no incompatible central claims. Judge the submitted explanation, not unasserted chat guesses. Accept faithful paraphrases; missing optional detail is not a contradiction. Do not demand unknown motives, devices or events. Score the stated fictional height/aim mechanism; do not introduce a physics reconstruction not in the story.

**标注状态**：ai_three_review_adjudicated_pending_human

## TS043 — 忠犬阻止急救

**汤面**

Xiaoqiang had a very loyal dog. Today he was walking the dog on the street, and then Xiaoqiang died.

**汤底**

This time when Xiaoqiang went out, he suddenly had a heart attack. The dog wouldn't let anyone including doctors perform CPR on its owner. This delayed treatment and led to Xiaoqiang's death.

**完整解答要求**

- Xiaoqiang suffers a sudden heart attack while out with the dog
- The loyal dog prevents others, including doctors, from giving CPR
- The delayed treatment leads to his death
- The precise belief the dog has about doctors is unspecified and not required

| 评分点 | 权重 | 判据 | 满分 | 半分 | 零分 |
| --- | ---: | --- | --- | --- | --- |
| C1 | 0.5 | The loyal dog prevents bystanders and medical staff from administering aid. | The loyal dog prevents bystanders and medical staff from administering aid. | Dog interferes with aid identified without blocking rescuers/CPR | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C2 | 0.3 | The owner suffers a sudden heart attack and needs urgent resuscitation. | The owner suffers a sudden heart attack and needs urgent resuscitation. | Heart attack identified without urgent resuscitation need | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C3 | 0.2 | The dog’s obstruction delays CPR and leads to the owner’s death; its exact beliefs about doctors need not be specified. | The dog’s obstruction delays CPR and leads to the owner’s death; its exact beliefs about doctors need not be specified. | Delayed care identified without causal contribution to death | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |

**评分说明**：AI three-review adjudication v2, pending human confirmation. Score only this submission. Apply full_credit/half_credit/zero_credit explicitly, with zero taking precedence for a materially contradictory checkpoint claim. An omitted qualifier can be partial; replacing the core identity/cause with a wrong one is not an omission. Faithful paraphrases count. Partial score and full narrative are separate outputs. AI independent review B, pending human approval. Credit is 0/.5/1 per checkpoint. Full narrative additionally requires all sourced completion requirements and no incompatible central claims. Judge the submitted explanation, not unasserted chat guesses. Accept faithful paraphrases; missing optional detail is not a contradiction. Do not demand unknown motives, devices or events. The dog’s precise mental model is unspecified. Objective obstruction and fatal delay are required.

**标注状态**：ai_three_review_adjudicated_pending_human

## TS044 — 黑猫和死老鼠

**汤面**

The Black Cat. I killed someone. As the police led me away, I saw a black cat staring at me from the doorway. At that moment, I realized I was wrong.

**汤底**

I had been feeding the cat downstairs. Returning from a business trip, I found dead mice on my balcony and blamed a neighbor with whom I often argued. I killed the neighbor. As the police took me away, I saw the cat carrying a mouse and realized it had brought the mice.

**完整解答要求**

- The narrator had been feeding the cat downstairs
- After a business trip, the narrator finds dead mice on the balcony and blames a neighbor with whom they quarrel
- The narrator kills that neighbor and is arrested
- While being taken away the narrator sees the cat carrying a mouse and realizes the cat brought the mice

| 评分点 | 权重 | 判据 | 满分 | 半分 | 零分 |
| --- | ---: | --- | --- | --- | --- |
| C1 | 0.5 | The dead mice were brought by the black cat, not planted by the neighbor. | The dead mice were brought by the black cat, not planted by the neighbor. | Cat identified without clearing neighbor of blame | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C2 | 0.3 | The narrator falsely blames and murders a neighbor with whom they argued. | The narrator falsely blames and murders a neighbor with whom they argued. | False blame identified without murder | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C3 | 0.2 | Seeing the cat carrying a mouse while being arrested reveals the mistake. | Seeing the cat carrying a mouse while being arrested reveals the mistake. | Discovery identified without seeing cat carry mouse during arrest | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |

**评分说明**：AI three-review adjudication v2, pending human confirmation. Score only this submission. Apply full_credit/half_credit/zero_credit explicitly, with zero taking precedence for a materially contradictory checkpoint claim. An omitted qualifier can be partial; replacing the core identity/cause with a wrong one is not an omission. Faithful paraphrases count. Partial score and full narrative are separate outputs. AI independent review B, pending human approval. Credit is 0/.5/1 per checkpoint. Full narrative additionally requires all sourced completion requirements and no incompatible central claims. Judge the submitted explanation, not unasserted chat guesses. Accept faithful paraphrases; missing optional detail is not a contradiction. Do not demand unknown motives, devices or events. Accept faithful paraphrase. Require the listed identities, events and causal links, not exact prose or unspecified incidental details.

**标注状态**：ai_three_review_adjudicated_pending_human

## TS045 — 恐怖作家的偷拍笔

**汤面**

The Writer’s Birthday Gift. I gave my favorite horror writer a pen containing a camera at his birthday party. I returned home satisfied. But when he returned to his own home, I was horrified. Why?

**汤底**

I intended to spy on him. Through the camera, I saw human heads and limbs hanging on his walls and blood on the floor. I realized his vivid stories of murder and dismemberment described his own crimes, rather than fictional events.

**完整解答要求**

- The narrator deliberately gives the writer a camera hidden in a pen to spy
- The camera shows actual severed human heads and limbs on the walls and blood on the floor
- The narrator realizes the writer’s detailed murder and dismemberment stories describe his own real crimes

| 评分点 | 权重 | 判据 | 满分 | 半分 | 零分 |
| --- | ---: | --- | --- | --- | --- |
| C1 | 0.5 | The horror author truly commits murders and dismemberment similar to his stories. | The horror author truly commits murders and dismemberment similar to his stories. | Real crimes identified without stories reflecting those crimes | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C2 | 0.3 | The narrator gives a pen with a hidden camera intending to spy. | The narrator gives a pen with a hidden camera intending to spy. | Camera pen identified without deliberate spying | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C3 | 0.2 | The camera shows severed human heads and limbs on walls and blood on the floor. | The camera shows severed human heads and limbs on walls and blood on the floor. | Severed body parts or blood observed but not both. | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |

**评分说明**：AI three-review adjudication v2, pending human confirmation. Score only this submission. Apply full_credit/half_credit/zero_credit explicitly, with zero taking precedence for a materially contradictory checkpoint claim. An omitted qualifier can be partial; replacing the core identity/cause with a wrong one is not an omission. Faithful paraphrases count. Partial score and full narrative are separate outputs. AI independent review B, pending human approval. Credit is 0/.5/1 per checkpoint. Full narrative additionally requires all sourced completion requirements and no incompatible central claims. Judge the submitted explanation, not unasserted chat guesses. Accept faithful paraphrases; missing optional detail is not a contradiction. Do not demand unknown motives, devices or events. Accept faithful paraphrase. Require the listed identities, events and causal links, not exact prose or unspecified incidental details.

**标注状态**：ai_three_review_adjudicated_pending_human

## TS046 — 双胞胎与遗书

**汤面**

My Sister’s Suicide Note. As soon as I got home, I wrote a suicide note for my dead younger sister. It was easy: I only had to describe my own wish to die.

**汤底**

We are identical twins. Our mother favors my sister and abuses me. My sister breaks our mother’s belongings and plants my book to blame me. Fearing a fatal beating, I trick her into swapping clothes, claiming I will take her punishment. She goes home first, dressed as me. When I arrive outside, I see her fall from above, dead. I forge her suicide note using my own despair.

**完整解答要求**

- The narrator and sister are identical twins; their mother favors the sister and abuses the narrator
- The sister breaks the mother’s possessions and plants the narrator’s book to frame them
- Fearing a fatal beating, the narrator tricks the sister into swapping clothes with a promise to take her punishment
- The sister goes home first dressed as the narrator, and the narrator later sees her fall from above, dead
- The narrator forges the sister’s suicide note using the narrator’s own despair
- Do not require a specific person to have pushed her, or an actual suicide: the reference leaves the fall’s exact cause unspecified

| 评分点 | 权重 | 判据 | 满分 | 半分 | 零分 |
| --- | ---: | --- | --- | --- | --- |
| C1 | 0.5 | The narrator and sister are identical twins who swap clothes, creating mistaken identity. | The narrator and sister are identical twins who swap clothes, creating mistaken identity. | Identical twins identified without clothing-based identity swap | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C2 | 0.25 | Their mother favors the sister and abuses the narrator, who is framed by the sister. | Their mother favors the sister and abuses the narrator, who is framed by the sister. | Favoritism or framing identified, but not both | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C3 | 0.15 | The narrator tricks her sister into going home first; the sister subsequently falls to her death. | The narrator tricks her sister into going home first; the sister subsequently falls to her death. | Deceptive first arrival or subsequent fatal fall, not both. | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |
| C4 | 0.1 | The narrator forges the dead sister’s suicide note using her own despair. | The narrator forges the dead sister’s suicide note using her own despair. | Forged note identified without using narrator’s own despair | Missing, contradicted, only repeats the opening without the required explanation, or gives uncommitted incompatible guesses. |

**评分说明**：AI three-review adjudication v2, pending human confirmation. Score only this submission. Apply full_credit/half_credit/zero_credit explicitly, with zero taking precedence for a materially contradictory checkpoint claim. An omitted qualifier can be partial; replacing the core identity/cause with a wrong one is not an omission. Faithful paraphrases count. Partial score and full narrative are separate outputs. AI independent review B, pending human approval. Credit is 0/.5/1 per checkpoint. Full narrative additionally requires all sourced completion requirements and no incompatible central claims. Judge the submitted explanation, not unasserted chat guesses. Accept faithful paraphrases; missing optional detail is not a contradiction. Do not demand unknown motives, devices or events. The exact cause of the fall is unspecified; neither murder by the mother nor actual suicide is mandatory.

**标注状态**：ai_three_review_adjudicated_pending_human

## TS047 — 旅店的画像

**汤面**

The Guesthouse Portrait. A reporter visiting the countryside stays in a shabby guesthouse. In the dim room, there is a picture opposite her bed. The next morning, she is stunned. Why?

**汤底**

In poor light, she mistakes a window with a real man outside for a lifelike portrait. During the night, she feels watched and avoids looking at it. In daylight, she approaches it and realizes it is a window: the man was real, and she had been watched.

**完整解答要求**

- In poor light the guest mistakes a window and a real man outside for a lifelike portrait
- Feeling watched, she avoids looking at it during the night
- Daylight reveals the window and makes her realize the watcher was real, shocking her

| 评分点 | 权重 | 判据 | 满分 | 半分 | 零分 |
| --- | ---: | --- | --- | --- | --- |
| C1 | 0.4 | The apparent portrait is a window with a real man outside. | Window plus outside real man. | Window identified without real watcher. | Missing or contradicted; incompatible uncommitted alternatives; merely repeating the opening without the required explanatory content.  |
| C2 | 0.2 | Dim light causes the portrait misidentification. | Dim light makes the window/man seem a portrait. | Mistaken portrait identified without dim-light cause. | Missing or contradicted; incompatible uncommitted alternatives; merely repeating the opening without the required explanatory content.  |
| C3 | 0.2 | Feeling watched at night makes her avoid looking. | Unease and avoidance during the night. | Feeling watched or avoiding looking, not both. | Missing or contradicted; incompatible uncommitted alternatives; merely repeating the opening without the required explanatory content.  |
| C4 | 0.2 | Daylight reveals the window and real watcher, shocking her. | Daylight realization explains shock. | Daylight discovery without shock at real watcher. | Missing or contradicted; incompatible uncommitted alternatives; merely repeating the opening without the required explanatory content.  |

**评分说明**：AI three-review adjudication v2, pending human confirmation. Score only this submission. Apply full_credit/half_credit/zero_credit explicitly, with zero taking precedence for a materially contradictory checkpoint claim. An omitted qualifier can be partial; replacing the core identity/cause with a wrong one is not an omission. Faithful paraphrases count. Partial score and full narrative are separate outputs. AI independent review C, not human gold. Score sum(weight*credit), credit 0/0.5/1. Full narrative requires all listed supported requirements and no material contradictory mechanism; partial 1 alone does not override full narrative. Credit each distinct causal proposition once; do not penalize faithful paraphrase or omitted unknown details. Accept faithful paraphrase. Require the listed identities, events and causal links, not exact prose or unspecified incidental details.

**标注状态**：ai_three_review_adjudicated_pending_human

## TS048 — 未经订购的外卖

**汤面**

The Unordered Delivery. Someone announces a food delivery, but I ordered nothing. My sister shakes her head when asked, and my girlfriend fearfully does the same. As I am about to refuse it, several burly men rush in and pin me down.

**汤底**

The delivery worker is a disguised police officer. The room is used by a pyramid scheme, and I tricked my sister and girlfriend into joining it. My girlfriend secretly called the police for help. The men rushing in are officers arresting me.

**完整解答要求**

- The apparent delivery worker is an undercover police officer
- The room is used for a pyramid scheme and the narrator tricked their sister and girlfriend into joining
- The girlfriend secretly asked the police for help
- The men who rush in are police arresting the narrator

| 评分点 | 权重 | 判据 | 满分 | 半分 | 零分 |
| --- | ---: | --- | --- | --- | --- |
| C1 | 0.35 | The supposed delivery worker is a police officer using a delivery disguise to gain entry for arrest. | The supposed delivery worker is a police officer using a delivery disguise to gain entry for arrest. | Officer identity without delivery pretext. | Missing, contradicted, repeats only the opening, or presents uncommitted incompatible guesses. |
| C2 | 0.4 | The room hosts a pyramid scheme and the narrator tricked his sister and girlfriend into joining. | The room hosts a pyramid scheme and the narrator tricked his sister and girlfriend into joining. | The pyramid scheme is identified but the narrator’s recruitment of both his sister and girlfriend is omitted. | Missing, contradicted, repeats only the opening, or presents uncommitted incompatible guesses. |
| C3 | 0.25 | The girlfriend secretly called police for help. | The girlfriend secretly called police for help. | Girlfriend contacts police but secrecy/help request omitted. | Missing, contradicted, repeats only the opening, or presents uncommitted incompatible guesses. |

**评分说明**：AI three-review adjudication v2, pending human confirmation. Score only this submission. Apply full_credit/half_credit/zero_credit explicitly, with zero taking precedence for a materially contradictory checkpoint claim. An omitted qualifier can be partial; replacing the core identity/cause with a wrong one is not an omission. Faithful paraphrases count. Partial score and full narrative are separate outputs. AI independent review, not human gold. Sum(weight*credit), credit in {0,0.5,1}. Full solution additionally requires all completion requirements and no material contradiction. Accept faithful paraphrases; never award the same factual component twice. Incidental unsupported additions do not earn points; materially conflicting additions defeat corresponding checkpoint. Accept faithful paraphrase. Require the listed identities, events and causal links, not exact prose or unspecified incidental details.

**标注状态**：ai_three_review_adjudicated_pending_human

## TS049 — 老人总翻第30页

**汤面**

An elderly man visits the library every week to borrow books. Before choosing any book, he always opens it to page thirty. Why?

**汤底**

The man cannot read. He borrows books for his child, who has difficulty walking and cannot easily visit the library. After finishing a book, the child leaves a mark on page thirty. The father checks that page before borrowing: if he finds the mark, he knows his child has already read the book and chooses another one.

**完整解答要求**

- The man is illiterate and borrows books for his child, who has difficulty walking
- The child marks page thirty after finishing each book
- The father checks for that mark before borrowing
- A marked copy is rejected in favor of another book to avoid repeats

| 评分点 | 权重 | 判据 | 满分 | 半分 | 零分 |
| --- | ---: | --- | --- | --- | --- |
| C1 | 0.4 | The child leaves a mark on page thirty after finishing a book. | The child leaves a mark on page thirty after finishing a book. | Page-thirty mark identified without child placing it after reading. | Missing, contradicted, repeats only the opening, or presents uncommitted incompatible guesses. |
| C2 | 0.35 | The father cannot read and borrows for his child who has difficulty walking. | The father cannot read and borrows for his child who has difficulty walking. | Illiteracy or child mobility limitation, not both. | Missing, contradicted, repeats only the opening, or presents uncommitted incompatible guesses. |
| C3 | 0.25 | He checks the mark before borrowing and selects a different book when marked to avoid repeats. | He checks the mark before borrowing and selects a different book when marked to avoid repeats. | He checks the mark to avoid repeats, but does not say that a marked book is rejected in favor of a different book. | Missing, contradicted, repeats only the opening, or presents uncommitted incompatible guesses. |

**评分说明**：AI three-review adjudication v2, pending human confirmation. Score only this submission. Apply full_credit/half_credit/zero_credit explicitly, with zero taking precedence for a materially contradictory checkpoint claim. An omitted qualifier can be partial; replacing the core identity/cause with a wrong one is not an omission. Faithful paraphrases count. Partial score and full narrative are separate outputs. AI independent review, not human gold. Sum(weight*credit), credit in {0,0.5,1}. Full solution additionally requires all completion requirements and no material contradiction. Accept faithful paraphrases; never award the same factual component twice. Incidental unsupported additions do not earn points; materially conflicting additions defeat corresponding checkpoint. Accept faithful paraphrase. Require the listed identities, events and causal links, not exact prose or unspecified incidental details.

**标注状态**：ai_three_review_adjudicated_pending_human

## TS050 — 沙漠与半截火柴

**汤面**

A man is found dead in the desert, lying headfirst in the sand. Several suitcases are scattered nearby. In his hand, he is tightly clutching half a matchstick. How did he die?

**汤底**

He and his friends were traveling in a hot-air balloon when it developed a problem and began losing altitude. They threw their luggage overboard, but the balloon was still too heavy. They drew matchsticks to decide who would be sacrificed. The man drew the broken matchstick and was thrown out of the balloon, still holding it.

**完整解答要求**

- The man and friends were in a hot-air balloon that developed a problem and lost altitude
- They threw out luggage but remained too heavy
- They drew matches to decide who would be sacrificed
- He drew the broken or short match and was thrown from the balloon, dying while still holding it

| 评分点 | 权重 | 判据 | 满分 | 半分 | 零分 |
| --- | ---: | --- | --- | --- | --- |
| C1 | 0.3 | The deceased had been aboard a hot-air balloon losing altitude, not walking in the desert. | The deceased had been aboard a hot-air balloon losing altitude, not walking in the desert. | Balloon identified without loss of altitude | Missing or contradicted; incompatible uncommitted alternatives; merely repeating the opening without the required explanatory content.  |
| C2 | 0.25 | The travelers throw luggage overboard, but it does not solve the weight problem. | The travelers throw luggage overboard, but it does not solve the weight problem. | Discarded luggage identified without inadequate effect | Missing or contradicted; incompatible uncommitted alternatives; merely repeating the opening without the required explanatory content.  |
| C3 | 0.3 | They draw matchsticks to select a victim, and the man draws the short/broken one. | They draw matchsticks to select a victim, and the man draws the short/broken one. | Match lottery identified without sacrifice purpose or short match | Missing or contradicted; incompatible uncommitted alternatives; merely repeating the opening without the required explanatory content.  |
| C4 | 0.15 | He is thrown from the balloon and dies holding the half-matchstick. | He is thrown from the balloon and dies holding the half-matchstick. | Falling death identified without forced ejection and match in hand | Missing or contradicted; incompatible uncommitted alternatives; merely repeating the opening without the required explanatory content.  |

**评分说明**：AI three-review adjudication v2, pending human confirmation. Score only this submission. Apply full_credit/half_credit/zero_credit explicitly, with zero taking precedence for a materially contradictory checkpoint claim. An omitted qualifier can be partial; replacing the core identity/cause with a wrong one is not an omission. Faithful paraphrases count. Partial score and full narrative are separate outputs. AI independent review C, not human gold. Score sum(weight*credit), credit 0/0.5/1. Full narrative requires all listed supported requirements and no material contradictory mechanism; partial 1 alone does not override full narrative. Credit each distinct causal proposition once; do not penalize faithful paraphrase or omitted unknown details. Accept faithful paraphrase. Require the listed identities, events and causal links, not exact prose or unspecified incidental details.

**标注状态**：ai_three_review_adjudicated_pending_human
