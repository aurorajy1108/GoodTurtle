# Turtle Soup trajectory

A lady went to a shoe store and bought a pair of red high heels. These high heels foretold her death tonight.

Status: completed | counted questions: 100 | submissions: 100 | final partial score: 0.5

[Token usage and estimated costs](token_costs.csv)

## 1 · question

Did the lady die because she was murdered?

Host: no

## 2 · question

Was the lady's death caused by an accident?

Host: yes

## 3 · question

Did the red high heels play a physical role in causing the accident?

Host: yes

## 4 · question

Did the heels cause her to trip or fall?

Host: no

## 5 · question

Did the heels cause a vehicle accident (for example, by interfering with driving)?

Host: no

## 6 · question

Did the heels lead her into a dangerous place or situation (for example, drawing attention because of their appearance)?

Host: no

## 7 · question

Was the lady killed by being struck by a moving vehicle?

Host: no

## 8 · question

Did the heels cause a fire or come into contact with something that led to a fatal accident?

Host: no

## 9 · question

Were the heels made of a dangerous or unusual material?

Host: irrelevant

## 10 · question

Did the lady die from a fall that was not caused by the heels themselves?

Host: no

## 11 · question

Was the fatal accident caused by an object falling on her?

Host: no

## 12 · question

Did the heels' red color contribute to her death?

Host: no

## 13 · question

Was she wearing the high heels when the fatal accident occurred?

Host: yes

## 14 · question

Was the fatal accident caused by the heel of the shoe breaking or getting caught?

Host: no

## 15 · question

Did she fall onto a sharp object or dangerous surface because she was unsteady in the heels?

Host: no

## 16 · question

Did she die from a fall down stairs?

Host: no

## 17 · question

Did the heel physically touch something that caused the fatal accident (for example, stepping on a switch or lever)?

Host: no

## 18 · question

Did the heels get caught in or interfere with machinery or equipment?

Host: no

## 19 · question

Did the heels cause her to be unable to escape a dangerous situation (for example, slowing her down)?

Host: no

## 20 · question

Did she die from drowning?

Host: no

## 21 · question

Did the heels cause her to be electrocuted?

Host: no

## 22 · question

Were the shoes themselves rigged or booby-trapped to kill her?

Host: no

## 23 · question

Is the "lady" a performer, such as a dancer or acrobat, wearing the heels as part of an act?

Host: yes

## 24 · question

Was the fatal accident during a performance involving a stunt or dangerous act?

Host: yes

## 25 · question

Was the stunt a tightrope or high-wire walk?

Host: no

## 26 · question

Was the stunt performed high above the ground?

Host: irrelevant

## 27 · question

Was the stunt a knife-throwing act in which she was the target?

Host: yes

## 28 · question

Did one of the thrown knives strike her in a fatal spot because her position was different from what the thrower expected?

Host: yes

## 29 · question

Did the red high heels change her height or stance so that the knife-thrower's aim was off?

Host: yes

## 30 · question

Had the knife-throwing act been rehearsed or performed before with her wearing different shoes?

Host: yes

## 31 · question

Did the knife-thrower aim based on her usual height or stance from rehearsals, so the added height from the new heels made the knife hit her fatally?

Host: yes

## 32 · final

The lady was a performer in a knife-throwing act. She and the knife-thrower had rehearsed and performed the routine with her wearing her usual shoes, so the thrower's aim was calibrated to her familiar height and stance. Tonight she bought and wore a new pair of red high heels, which raised her body and altered her posture. When the act was performed, the knife-thrower threw as rehearsed, but the added height from the heels made the knife strike her fatally instead of passing safely as intended. Thus the high heels "foretold" her death by inadvertently causing the fatal accident during the performance.

Host: yes and no

<details><summary>Private evaluator result (not sent to player)</summary>

```json
{
  "checkpoints": [
    {
      "id": "C1",
      "credit": 0.5,
      "evidence": "The lady was a performer in a knife-throwing act.",
      "reason": "Identifies her as a performer in a knife-throwing act, but omits the circus and apple-on-head qualifiers required for full credit."
    },
    {
      "id": "C2",
      "credit": 0.5,
      "evidence": "Tonight she bought and wore a new pair of red high heels, which raised her body and altered her posture ... the added height from the heels",
      "reason": "Covers wearing new high heels raising her height, but omits the few-centimeters measurement and explicit head-above-usual-height relation."
    },
    {
      "id": "C3",
      "credit": 0.5,
      "evidence": "the knife-thrower threw as rehearsed, but the added height from the heels made the knife strike her fatally",
      "reason": "Covers failure to adjust aim and a fatal strike, but omits the required head location and male partner qualifier."
    }
  ],
  "material_contradiction": false,
  "irrelevant": false,
  "rubric_conflict": false,
  "full_solution": false,
  "completion_note": "Scored facts remain missing, partial or contradicted; see fact_coverage.",
  "fact_coverage": [
    {
      "id": "C1.F1",
      "status": "partial",
      "evidence": "The lady was a performer in a knife-throwing act."
    },
    {
      "id": "C1.F2",
      "status": "partial",
      "evidence": "The lady was a performer in a knife-throwing act."
    },
    {
      "id": "C2.F1",
      "status": "partial",
      "evidence": "Tonight she bought and wore a new pair of red high heels, which raised her body and altered her posture ... the added height from the heels"
    },
    {
      "id": "C2.F2",
      "status": "partial",
      "evidence": "which raised her body and altered her posture ... the added height from the heels"
    },
    {
      "id": "C3.F1",
      "status": "partial",
      "evidence": "the knife-thrower threw as rehearsed, but the added height from the heels made the knife strike her fatally"
    },
    {
      "id": "C3.F2",
      "status": "partial",
      "evidence": "the knife-thrower threw as rehearsed, but the added height from the heels made the knife strike her fatally"
    }
  ],
  "requirement_coverage": [],
  "contradictions": [],
  "partial_score": 0.5,
  "complete": false,
  "label": "yes and no",
  "grading_protocol": "coverage-v3-unified",
  "controller_corrections": []
}
```
</details>

## 33 · question

Was the fatal knife aimed at a body part that would have been safe if she had been wearing her usual shoes?

Host: no

## 34 · question

Did the knife-thrower intend to hit her (was the death deliberate)?

Host: no

## 35 · question

Did the heels cause her to move or flinch unexpectedly during the act?

Host: no

## 36 · question

Was the fatal outcome caused by the thrower misjudging the distance or timing because of the heels' added height?

Host: yes

## 37 · question

Was there a specific target or mark (such as a board or outline) that the knives were supposed to land around, and the heels shifted her relative to it?

Host: no

## 38 · question

Was she standing against a target board while the thrower outlined her body with knives?

Host: no

## 39 · question

Did she die immediately from the knife wound during the act, rather than later?

Host: yes

## 40 · question

Was the knife-thrower a person close to her, such as a partner or assistant in the act?

Host: yes

## 41 · question

Was the fatal knife thrown at her head or neck area?

Host: yes

## 42 · question

Had the thrower practiced throwing knives near her head or neck in previous rehearsals without injuring her?

Host: yes

## 43 · question

Did the red high heels make her taller only slightly, but enough that a knife meant to pass just above or beside her head struck her instead?

Host: no

## 44 · question

Did the knife-thrower throw while blindfolded?

Host: irrelevant

## 45 · question

Was her neck the intended safe target area—the knife was supposed to pass close to her neck in the rehearsed routine?

Host: no

## 46 · question

Was the knife meant to land in a gap or space related to her head, and the heels moved her head into its path?

Host: no

## 47 · question

Was the knife-thrower positioned in front of her, aiming at a point above her head that the knife was supposed to clear?

Host: no

## 48 · question

Was her hair or headpiece part of the act, such that the knife was meant to pin or cut something above her head?

Host: no

## 49 · question

Was the fatal knife supposed to strike something she was holding or wearing near her head, rather than her head itself?

Host: no

## 50 · question

Did the high heels make her taller by a significant amount compared to her usual performance footwear?

Host: yes

## 51 · question

Were the fatal knives being thrown at her head as part of the act's climax or a specific trick?

Host: no

## 52 · question

Was the knife supposed to be thrown between her and an object or person near her head?

Host: no

## 53 · question

Was the knife thrown at an apple or similar object placed on her head?

Host: yes

## 54 · question

Did the added height from the heels cause the knife-thrower to misjudge where the apple on her head was, so the knife struck her head instead of the apple?

Host: yes

## 55 · final

The lady was a performer in a knife-throwing act in which an apple (or similar object) was placed on her head and the thrower aimed at it. In rehearsal and prior performances she wore her usual shoes, and the thrower had calibrated his aim to that familiar height. That night she bought and wore a new pair of red high heels, which raised her by a significant amount. When the trick was performed, the thrower threw as practiced, but her head—and the apple on it—was now higher than expected. Misjudging the position, he hit her head instead of the apple, and she died immediately from the knife wound. Thus the red high heels inadvertently caused the accident that killed her.

Host: yes and no

<details><summary>Private evaluator result (not sent to player)</summary>

```json
{
  "checkpoints": [
    {
      "id": "C1",
      "credit": 0.5,
      "evidence": "The lady was a performer in a knife-throwing act in which an apple (or similar object) was placed on her head and the thrower aimed at it.",
      "reason": "Covers performer, knife-throwing act, and apple on head, but omits the circus-performer qualifier required for full credit."
    },
    {
      "id": "C2",
      "credit": 0.5,
      "evidence": "That night she bought and wore a new pair of red high heels, which raised her by a significant amount. ... her head—and the apple on it—was now higher than expected.",
      "reason": "Covers high heels raising her height and head higher than expected, but omits the explicit few-centimeters increase required for full coverage."
    },
    {
      "id": "C3",
      "credit": 0.5,
      "evidence": "the thrower threw as practiced, but her head—and the apple on it—was now higher than expected. Misjudging the position, he hit her head instead of the apple, and she died immediately from the knife wound.",
      "reason": "Covers failure to adjust aim and a fatal head strike, but omits the male-partner qualifier required for full credit."
    }
  ],
  "material_contradiction": false,
  "irrelevant": false,
  "rubric_conflict": false,
  "full_solution": false,
  "completion_note": "Scored facts remain missing, partial or contradicted; see fact_coverage.",
  "fact_coverage": [
    {
      "id": "C1.F1",
      "status": "partial",
      "evidence": "The lady was a performer in a knife-throwing act in which an apple (or similar object) was placed on her head and the thrower aimed at it."
    },
    {
      "id": "C1.F2",
      "status": "partial",
      "evidence": "The lady was a performer in a knife-throwing act in which an apple (or similar object) was placed on her head and the thrower aimed at it."
    },
    {
      "id": "C2.F1",
      "status": "partial",
      "evidence": "That night she bought and wore a new pair of red high heels, which raised her by a significant amount. ... her head—and the apple on it—was now higher than expected."
    },
    {
      "id": "C2.F2",
      "status": "partial",
      "evidence": "That night she bought and wore a new pair of red high heels, which raised her by a significant amount. ... her head—and the apple on it—was now higher than expected."
    },
    {
      "id": "C3.F1",
      "status": "partial",
      "evidence": "the thrower threw as practiced, but her head—and the apple on it—was now higher than expected. Misjudging the position, he hit her head instead of the apple, and she died immediately from the knife wound."
    },
    {
      "id": "C3.F2",
      "status": "partial",
      "evidence": "the thrower threw as practiced, but her head—and the apple on it—was now higher than expected. Misjudging the position, he hit her head instead of the apple, and she died immediately from the knife wound."
    }
  ],
  "requirement_coverage": [],
  "contradictions": [],
  "partial_score": 0.5,
  "complete": false,
  "label": "yes and no",
  "grading_protocol": "coverage-v3-unified",
  "controller_corrections": []
}
```
</details>

## 56 · question

Was the apple placed on her head directly, with no stand or holder?

Host: yes

## 57 · question

Was the knife supposed to pin or cut the apple itself, rather than pass near it?

Host: yes

## 58 · question

Did the knife hit her head because she tilted or moved her head to balance the apple in the unfamiliar heels?

Host: no

## 59 · question

Did the thrower aim at where the apple would have been had she worn her usual shoes?

Host: yes

## 60 · question

Was the thrower unaware that she was wearing the new high heels?

Host: irrelevant

## 61 · question

Did the knife strike her head below the apple—at the position where the apple used to be in rehearsal?

Host: yes

## 62 · question

Was the rehearsal throw aimed at a point that, with her usual height, was at the level of the apple on her head?

Host: yes

## 63 · question

Did the thrower rely on a fixed mark on the wall or background to aim, rather than on her actual head position?

Host: irrelevant

## 64 · question

Did the knife hit her head because her head—raised by the heels—was now exactly at the height the thrower was aiming for?

Host: yes

## 65 · question

Was the apple supposed to be above the point the thrower aimed at, so the knife would pass under the apple in the rehearsed trick?

Host: no

## 66 · question

Was the knife supposed to hit the apple, and the added height simply put her head where the thrower's fixed aim already was?

Host: yes

## 67 · question

Was the thrower aiming at the height where the apple normally was, calibrated from her usual shoe height?

Host: yes

## 68 · question

Did the added height from the red high heels raise her head to the exact height where the apple would have been with her usual shoes?

Host: yes

## 69 · question

With her usual shoes, was the apple held high enough that the knife would pass through the apple, while the extra heel height put her skull at that same point?

Host: yes

## 70 · question

Did she place the apple on her head after putting on the high heels, so that the apple and her head were both that much higher than in rehearsal?

Host: yes

## 71 · question

Was the apple not actually on her head at the moment of the throw, so the thrower aimed at her head believing it was the apple's usual position?

Host: no

## 72 · question

Was the fatal throw aimed at a fruit other than an apple?

Host: no

## 73 · question

Was the fatal throw intended to hit the apple but hit her head because the apple sat higher above her head than the thrower realized?

Host: yes

## 74 · question

Was the apple placed on top of a tall hairstyle or headpiece rather than directly against her scalp?

Host: irrelevant

## 75 · question

Did the thrower deliberately aim lower than the apple because in rehearsal the knife was supposed to graze or strike just beneath the apple?

Host: no

## 76 · question

Was there a second person or object involved—such that the thrower was aiming past the apple at another target, and the heels brought her head into that line?

Host: no

## 77 · question

Was the apple resting on top of her head in such a way that when she was taller, the apple was pushed upward but her head also blocked the direct line to it?

Host: no

## 78 · question

Did the thrower aim by looking at the apple and throwing along that line, but because the apple was higher, the knife traveled upward and struck her forehead instead?

Host: no

## 79 · question

Was the apple on her head supported by something that failed or shifted because of the heels?

Host: no

## 80 · question

Did the fatal knife first pass through the apple and then into her head because the apple was resting directly against her skull?

Host: no

## 81 · question

Did the thrower aim at the apple using a predetermined trajectory from rehearsal, such that with her raised height the knife entered her head at the apple's former level without the apple intercepting it?

Host: yes

## 82 · question

Did the apple slide or fall off her head just before or during the throw?

Host: no

## 83 · question

Was the knife's path such that it would have struck the apple slightly off-center had she worn her usual shoes?

Host: irrelevant

## 84 · question

Did the thrower aim at a point on the background or wall at the apple's usual height, so that with her raised head the knife hit her skull before reaching that point?

Host: no

## 85 · question

Was the apple still on her head and untouched when the knife struck her?

Host: yes

## 86 · question

Did the knife strike the apple and then continue into her head, with the apple failing to stop it?

Host: no

## 87 · question

Did the knife strike her head at a point below the apple, even though the apple was still resting on her head?

Host: yes

## 88 · final

The lady was a performer in a knife-throwing act in which an apple rested directly on her head and the thrower's practiced aim was calibrated to her usual height: the knife's predetermined trajectory passed at the level of the apple, striking it just above her head. That night she wore new red high heels, which raised her significantly. She placed the apple on her head after putting on the heels, so both her head and the apple were higher than in rehearsal—but the thrower still threw along the rehearsal trajectory. The knife therefore passed at the apple's former height, which was now the level of her skull, and struck her head below the still-resting apple. She died immediately from the wound. The red high heels inadvertently caused her death by changing her height while the thrower's fixed aim remained calibrated to her usual shoes.

Host: yes and no

<details><summary>Private evaluator result (not sent to player)</summary>

```json
{
  "checkpoints": [
    {
      "id": "C1",
      "credit": 0.5,
      "evidence": "The lady was a performer in a knife-throwing act in which an apple rested directly on her head",
      "reason": "Covers performer, knife-throwing act, and apple on head, but omits the required circus-performer identity."
    },
    {
      "id": "C2",
      "credit": 0.5,
      "evidence": "she wore new red high heels, which raised her significantly ... both her head and the apple were higher than in rehearsal",
      "reason": "Covers high heels raising her and head above usual height, but omits the explicit few-centimeters increase required for full coverage."
    },
    {
      "id": "C3",
      "credit": 0.5,
      "evidence": "the thrower still threw along the rehearsal trajectory ... struck her head below the still-resting apple ... died immediately",
      "reason": "Covers failure to adjust aim and fatal head strike, but omits the required male-partner qualifier."
    }
  ],
  "material_contradiction": false,
  "irrelevant": false,
  "rubric_conflict": false,
  "full_solution": false,
  "completion_note": "Scored facts remain missing, partial or contradicted; see fact_coverage.",
  "fact_coverage": [
    {
      "id": "C1.F1",
      "status": "partial",
      "evidence": "The lady was a performer in a knife-throwing act in which an apple rested directly on her head"
    },
    {
      "id": "C1.F2",
      "status": "partial",
      "evidence": "The lady was a performer in a knife-throwing act in which an apple rested directly on her head"
    },
    {
      "id": "C2.F1",
      "status": "partial",
      "evidence": "she wore new red high heels, which raised her significantly"
    },
    {
      "id": "C2.F2",
      "status": "covered",
      "evidence": "both her head and the apple were higher than in rehearsal"
    },
    {
      "id": "C3.F1",
      "status": "covered",
      "evidence": "the thrower still threw along the rehearsal trajectory ... struck her head below the still-resting apple"
    },
    {
      "id": "C3.F2",
      "status": "partial",
      "evidence": "the thrower still threw along the rehearsal trajectory ... struck her head ... died immediately"
    }
  ],
  "requirement_coverage": [],
  "contradictions": [],
  "partial_score": 0.5,
  "complete": false,
  "label": "yes and no",
  "grading_protocol": "coverage-v3-unified",
  "controller_corrections": []
}
```
</details>

## 89 · question

Did the thrower intend to strike the apple, but the knife missed the apple?

Host: yes

## 90 · question

Was the knife aimed at the apple itself—following the apple's actual position—rather than at the apple's old rehearsal height?

Host: no

## 91 · question

Did the thrower aim at the apple's position as it would have been had she been wearing her usual shoes?

Host: yes

## 92 · question

With her usual shoes, would the knife have struck the apple at that aimed position?

Host: yes

## 93 · final

The lady performed a knife-throwing act in which an apple was placed directly on her head. The thrower's throw was calibrated from rehearsal to the apple's position when she wore her usual shoes, so the knife would have struck the apple safely. That night, however, she wore new red high heels, which significantly raised her. Because she placed the apple on her head while wearing the heels, both the apple and her head were higher than in rehearsal, but the thrower still aimed at the apple's old, familiar position. The knife therefore missed the apple—which remained untouched on her head—and instead struck her skull below it, killing her. The red high heels thus inadvertently brought about the fatal accident.

Host: yes and no

<details><summary>Private evaluator result (not sent to player)</summary>

```json
{
  "checkpoints": [
    {
      "id": "C1",
      "credit": 0.5,
      "evidence": "The lady performed a knife-throwing act in which an apple was placed directly on her head.",
      "reason": "Covers performer, knife-throwing act, and apple on head, but omits the required circus-performer identity."
    },
    {
      "id": "C2",
      "credit": 0.5,
      "evidence": "she wore new red high heels, which significantly raised her ... both the apple and her head were higher than in rehearsal",
      "reason": "Covers high heels raising her and head above usual height, but omits the explicit few-centimeters increase required for full coverage."
    },
    {
      "id": "C3",
      "credit": 0.5,
      "evidence": "the thrower still aimed at the apple's old, familiar position ... instead struck her skull below it, killing her",
      "reason": "Covers failure to adjust aim and fatal head strike, but omits the required male-partner qualifier."
    }
  ],
  "material_contradiction": false,
  "irrelevant": false,
  "rubric_conflict": false,
  "full_solution": false,
  "completion_note": "Scored facts remain missing, partial or contradicted; see fact_coverage.",
  "fact_coverage": [
    {
      "id": "C1.F1",
      "status": "partial",
      "evidence": "The lady performed a knife-throwing act in which an apple was placed directly on her head."
    },
    {
      "id": "C1.F2",
      "status": "partial",
      "evidence": "The lady performed a knife-throwing act in which an apple was placed directly on her head."
    },
    {
      "id": "C2.F1",
      "status": "partial",
      "evidence": "she wore new red high heels, which significantly raised her"
    },
    {
      "id": "C2.F2",
      "status": "covered",
      "evidence": "both the apple and her head were higher than in rehearsal"
    },
    {
      "id": "C3.F1",
      "status": "covered",
      "evidence": "the thrower still aimed at the apple's old, familiar position ... instead struck her skull below it, killing her"
    },
    {
      "id": "C3.F2",
      "status": "partial",
      "evidence": "the thrower still aimed at the apple's old, familiar position ... struck her skull below it, killing her"
    }
  ],
  "requirement_coverage": [],
  "contradictions": [],
  "partial_score": 0.5,
  "complete": false,
  "label": "yes and no",
  "grading_protocol": "coverage-v3-unified",
  "controller_corrections": []
}
```
</details>

## 94 · question

Was the thrower aiming at the apple's position from rehearsal, but her raised head blocked the knife's path to that point, so it hit her before reaching the apple's old location?

Host: no

## 95 · question

Did the knife hit her head at the exact height the thrower aimed for—the apple's old rehearsal position—so her head was struck because it now occupied that position?

Host: yes

## 96 · question

Was the apple's old rehearsal position (the aimed point) at the level of her head when she wore the high heels?

Host: yes

## 97 · final

The lady was a performer in a knife-throwing act that used an apple placed directly on her head. In rehearsal, with her usual shoes, the thrower's aim was calibrated so the knife would pass at the height of the apple—the apple's old position. That night she wore new red high heels, which raised her significantly, and she then placed the apple on her head, so both her head and the apple sat higher than before. The thrower still threw at the apple's old, rehearsal height. But with the heels, her head had risen to exactly that old apple height. The knife therefore missed the higher apple and struck her head at the aimed point, killing her. The red high heels, by raising her head into the knife's fixed path, inadvertently caused her death.

Host: yes and no

<details><summary>Private evaluator result (not sent to player)</summary>

```json
{
  "checkpoints": [
    {
      "id": "C1",
      "credit": 0.5,
      "evidence": "The lady was a performer in a knife-throwing act that used an apple placed directly on her head.",
      "reason": "Covers performer, knife-throwing act, and apple on head, but omits the required circus-performer identity."
    },
    {
      "id": "C2",
      "credit": 0.5,
      "evidence": "wore new red high heels, which raised her significantly ... her head had risen to exactly that old apple height",
      "reason": "Covers high heels raising her and head above its usual height, but omits the explicit few-centimeters increase required for full coverage."
    },
    {
      "id": "C3",
      "credit": 0.5,
      "evidence": "The thrower still threw at the apple's old, rehearsal height ... struck her head at the aimed point, killing her",
      "reason": "Covers failure to adjust aim and fatal head strike, but omits the required male-partner qualifier."
    }
  ],
  "material_contradiction": false,
  "irrelevant": false,
  "rubric_conflict": false,
  "full_solution": false,
  "completion_note": "Scored facts remain missing, partial or contradicted; see fact_coverage.",
  "fact_coverage": [
    {
      "id": "C1.F1",
      "status": "partial",
      "evidence": "The lady was a performer in a knife-throwing act that used an apple placed directly on her head."
    },
    {
      "id": "C1.F2",
      "status": "partial",
      "evidence": "The lady was a performer in a knife-throwing act that used an apple placed directly on her head."
    },
    {
      "id": "C2.F1",
      "status": "partial",
      "evidence": "wore new red high heels, which raised her significantly"
    },
    {
      "id": "C2.F2",
      "status": "covered",
      "evidence": "both her head and the apple sat higher than before ... her head had risen to exactly that old apple height"
    },
    {
      "id": "C3.F1",
      "status": "covered",
      "evidence": "The thrower still threw at the apple's old, rehearsal height ... struck her head at the aimed point, killing her"
    },
    {
      "id": "C3.F2",
      "status": "partial",
      "evidence": "The thrower still threw at the apple's old, rehearsal height ... struck her head at the aimed point, killing her"
    }
  ],
  "requirement_coverage": [],
  "contradictions": [],
  "partial_score": 0.5,
  "complete": false,
  "label": "yes and no",
  "grading_protocol": "coverage-v3-unified",
  "controller_corrections": []
}
```
</details>

## 98 · question

Did the thrower aim the knife so it would pass just above the apple, expecting the apple to be at its usual, lower height?

Host: no

## 99 · question

With her usual shoes, would the knife have struck and hit the apple if thrown along that rehearsal line?

Host: yes

## 100 · final · mandatory final

The lady was a performer in a knife-throwing act in which an apple was placed directly on her head. With her usual shoes, the thrower's rehearsed line of throw was calibrated to strike the apple safely. That night she bought and wore new red high heels, which raised her significantly, and she placed the apple on her head while wearing them, so both her head and the apple were higher than in rehearsal. The thrower nevertheless threw at the old, familiar height—the apple's position from practice. Her raised head now occupied that aimed point: the knife missed the elevated apple, which remained untouched on her head, and struck her skull below it. She died immediately from the wound. Thus the red high heels inadvertently caused her death by changing her height while the thrower's fixed aim remained calibrated to her usual shoes.

Host: yes and no

<details><summary>Private evaluator result (not sent to player)</summary>

```json
{
  "checkpoints": [
    {
      "id": "C1",
      "credit": 0.5,
      "evidence": "The lady was a performer in a knife-throwing act in which an apple was placed directly on her head.",
      "reason": "Covers performer, knife-throwing act, and apple on head, but omits the required circus-performer identity."
    },
    {
      "id": "C2",
      "credit": 0.5,
      "evidence": "she bought and wore new red high heels, which raised her significantly ... both her head and the apple were higher than in rehearsal",
      "reason": "Covers high heels raising her and head above usual height, but omits the explicit few-centimeters increase required for full coverage."
    },
    {
      "id": "C3",
      "credit": 0.5,
      "evidence": "The thrower nevertheless threw at the old, familiar height ... struck her skull below it. She died immediately",
      "reason": "Covers failure to adjust aim and fatal head strike, but omits the required male-partner qualifier."
    }
  ],
  "material_contradiction": false,
  "irrelevant": false,
  "rubric_conflict": false,
  "full_solution": false,
  "completion_note": "Scored facts remain missing, partial or contradicted; see fact_coverage.",
  "fact_coverage": [
    {
      "id": "C1.F1",
      "status": "partial",
      "evidence": "The lady was a performer in a knife-throwing act in which an apple was placed directly on her head."
    },
    {
      "id": "C1.F2",
      "status": "partial",
      "evidence": "The lady was a performer in a knife-throwing act in which an apple was placed directly on her head."
    },
    {
      "id": "C2.F1",
      "status": "partial",
      "evidence": "she bought and wore new red high heels, which raised her significantly"
    },
    {
      "id": "C2.F2",
      "status": "covered",
      "evidence": "both her head and the apple were higher than in rehearsal ... Her raised head now occupied that aimed point"
    },
    {
      "id": "C3.F1",
      "status": "covered",
      "evidence": "The thrower nevertheless threw at the old, familiar height ... struck her skull below it. She died immediately"
    },
    {
      "id": "C3.F2",
      "status": "partial",
      "evidence": "The thrower nevertheless threw at the old, familiar height ... struck her skull below it. She died immediately"
    }
  ],
  "requirement_coverage": [],
  "contradictions": [],
  "partial_score": 0.5,
  "complete": false,
  "label": "yes and no",
  "grading_protocol": "coverage-v3-unified",
  "controller_corrections": []
}
```
</details>
