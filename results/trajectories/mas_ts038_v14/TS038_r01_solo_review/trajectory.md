# Turtle Soup trajectory

"You've disappointed me so much; I'm never coming back." "You've disappointed me so much; I'm never coming back." "You've disappointed me so much; I'm never coming back." "You've disappointed me so much; I'm never coming back." "You've disappointed me so much; I'm never coming back." "You've disappointed me so much; I'm never coming back." "You've disappointed me so much; I'm never coming back."

Sigh, I know I'm in trouble.

Status: completed | counted questions: 99 | submissions: 100 | final partial score: 1.0

[Token usage and estimated costs](token_costs.csv)

## 1 · question

Is the repeated sentence spoken by a person to the same listener each time?

Host: no

## 2 · question

Are the seven repetitions seven different people each expressing disappointment?

Host: no

## 3 · question

Is the repeated sentence written text rather than spoken aloud?

Host: yes

## 4 · question

Are the seven written copies addressed to seven different recipients?

Host: no

## 5 · question

Are all seven written copies part of a single document or surface?

Host: irrelevant

## 6 · question

Is there a single author of all seven written copies?

Host: yes

## 7 · question

Is the person who says "I know I'm in trouble" the intended recipient of the seven copies?

Host: no

## 8 · question

Is the person who says "I know I'm in trouble" the author of the seven copies?

Host: yes

## 9 · question

Was the author required to write the sentence repeatedly by someone else, as a punishment or assignment?

Host: no

## 10 · question

Had someone actually said this sentence to the author before the author wrote it?

Host: no

## 11 · question

Were the seven copies written on something the author was not allowed to write on?

Host: irrelevant

## 12 · question

Did the author write the sentence as a statement that the author himself will leave?

Host: no

## 13 · question

Does the "you" in the sentence refer to the author?

Host: yes

## 14 · question

Did the author commit some misdeed that would disappoint the person referred to in the sentence?

Host: no

## 15 · question

Is the "I" who says "I'm never coming back" a specific real person in the author's life?

Host: yes

## 16 · question

Is the author in trouble with that real person?

Host: no

## 17 · question

Does the author intend the seven copies to be taken as the real person's own words or writing?

Host: yes

## 18 · question

Is the author trying to mislead a third person (someone other than the real person) with the forged copies?

Host: yes

## 19 · question

Is the author's goal to make the third person feel sorry for the author?

Host: no

## 20 · question

Is the third person an authority figure over the author, such as a parent, teacher, or employer?

Host: irrelevant

## 21 · question

Is the author trying to make the third person believe the author is now available or unattached?

Host: no

## 22 · question

Is the author trying to hide that the real person is still present in the author's life?

Host: no

## 23 · question

Does the real person know about the seven forged copies?

Host: no

## 24 · question

Is the deception intended as a prank or joke on the third person?

Host: no

## 25 · question

Are the forged copies meant to explain to the third person why the real person will not be present or return?

Host: yes

## 26 · question

Is the real person actually absent for some reason the author wants to conceal from the third person?

Host: yes

## 27 · question

Is the real person unable, rather than merely unwilling, to return?

Host: yes

## 28 · question

Has the real person died?

Host: yes

## 29 · question

Were the forged notes made to spare the third person from learning of the death?

Host: yes

## 30 · question

Is the third person a child?

Host: irrelevant

## 31 · question

Will the third person fault the author for the real person's not returning?

Host: irrelevant

## 32 · question

Does the third person actually see or receive the forged notes?

Host: irrelevant

## 33 · final

A real person close to the author has died and can never return, but a third party expects that person to come back and would be shattered by the truth. So the author forges the dead person's own words—"You've disappointed me so much; I'm never coming back"—written as though addressed to the author, and presents them as that person's farewell. The third party is then spared the news of the death, instead believing the absent person simply chose to cut ties after being let down. The author writes the same farewell again and again, seven copies in all, maintaining the fiction that shelters the other person from grief; seeing the repeated lines, the author sighs that the lie is a burden that will land them in trouble: "I know I'm in trouble."

Host: yes and no

<details><summary>Private evaluator result (not sent to player)</summary>

```json
{
  "checkpoints": [
    {
      "id": "C1",
      "credit": 0.5,
      "evidence": "the author forges the dead person's own words—\"You've disappointed me so much; I'm never coming back\"—written as though addressed to the author, and presents them as that person's farewell. The third party is then spared the news of the death, instead believing the absent person simply chose to cut ties after being let down.",
      "reason": "The staged voluntary departure via a forged farewell is present, but the wife and murder are missing, so the checkpoint is only partly correct."
    },
    {
      "id": "C2",
      "credit": 0.5,
      "evidence": "the author forges the dead person's own words—\"You've disappointed me so much; I'm never coming back\" ... The author writes the same farewell again and again, seven copies in all.",
      "reason": "The repeated forged message is present, but the crucial element that the repetitions are attempts to imitate the wife's handwriting is absent."
    },
    {
      "id": "C3",
      "credit": 0.5,
      "evidence": "seeing the repeated lines, the author sighs that the lie is a burden that will land them in trouble: \"I know I'm in trouble.\"",
      "reason": "The submission conveys worry about trouble, but it does not identify the required cause: inability to imitate her handwriting."
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
      "evidence": "the author forges the dead person's own words—\"You've disappointed me so much; I'm never coming back\"—written as though addressed to the author, and presents them as that person's farewell. The third party is then spared the news of the death, instead believing the absent person simply chose to cut ties after being let down."
    },
    {
      "id": "C1.F2",
      "status": "missing",
      "evidence": ""
    },
    {
      "id": "C1.F3",
      "status": "covered",
      "evidence": "the author forges the dead person's own words—\"You've disappointed me so much; I'm never coming back\"—written as though addressed to the author, and presents them as that person's farewell. The third party is then spared the news of the death, instead believing the absent person simply chose to cut ties after being let down."
    },
    {
      "id": "C2.F1",
      "status": "partial",
      "evidence": "the author forges the dead person's own words—\"You've disappointed me so much; I'm never coming back\" ... The author writes the same farewell again and again, seven copies in all."
    },
    {
      "id": "C2.F2",
      "status": "partial",
      "evidence": "seeing the repeated lines, the author sighs that the lie is a burden that will land them in trouble: \"I know I'm in trouble.\""
    },
    {
      "id": "C3.F1",
      "status": "partial",
      "evidence": "seeing the repeated lines, the author sighs that the lie is a burden that will land them in trouble: \"I know I'm in trouble.\""
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

## 34 · question

Must the author repeatedly produce letters in the dead person's name to keep the third person from learning of the death?

Host: no

## 35 · question

Does the author fear being exposed as the forger?

Host: yes

## 36 · final

Someone in the author's life—call him X—has died and can never return. Rather than let a third person learn of the death, the author fabricates X's own bitter farewell: "You've disappointed me so much; I'm never coming back." Written in X's voice and addressed to the author himself, the forged note explains X's permanent absence as X choosing to cut ties, sparing the third person the news of the death. The same line exists as seven identical copies. Seeing them, the author sighs, "I know I'm in trouble"—not because of the dead man, but out of guilt and the dread that the forgery will be exposed.

Host: no

<details><summary>Private evaluator result (not sent to player)</summary>

```json
{
  "checkpoints": [
    {
      "id": "C1",
      "credit": 0,
      "evidence": "Someone in the author's life—call him X—has died and can never return.",
      "reason": "The required fact that the narrator murdered his wife is contradicted by the male dead man X and omitted entirely; only the staged voluntary departure is present."
    },
    {
      "id": "C2",
      "credit": 0,
      "evidence": "The same line exists as seven identical copies.",
      "reason": "The repeated message is present, but the required fact that the repetitions are attempts to forge his wife's handwriting is contradicted by the male X and missing, so credit is capped at zero."
    },
    {
      "id": "C3",
      "credit": 0,
      "evidence": "out of guilt and the dread that the forgery will be exposed",
      "reason": "The worry is present, but the required causal fact that inability to imitate her handwriting causes it is contradicted by the dead man framing and absent."
    }
  ],
  "material_contradiction": true,
  "irrelevant": false,
  "rubric_conflict": false,
  "full_solution": false,
  "completion_note": "Scored facts remain missing, partial or contradicted; see fact_coverage.",
  "fact_coverage": [
    {
      "id": "C1.F1",
      "status": "contradicted",
      "evidence": "Someone in the author's life—call him X—has died and can never return."
    },
    {
      "id": "C1.F2",
      "status": "contradicted",
      "evidence": "Someone in the author's life—call him X—has died and can never return."
    },
    {
      "id": "C1.F3",
      "status": "covered",
      "evidence": "Rather than let a third person learn of the death, the author fabricates X's own bitter farewell ... explains X's permanent absence as X choosing to cut ties."
    },
    {
      "id": "C2.F1",
      "status": "contradicted",
      "evidence": "Someone in the author's life—call him X—has died and can never return."
    },
    {
      "id": "C2.F2",
      "status": "contradicted",
      "evidence": "not because of the dead man, but out of guilt and the dread that the forgery will be exposed"
    },
    {
      "id": "C3.F1",
      "status": "contradicted",
      "evidence": "not because of the dead man, but out of guilt and the dread that the forgery will be exposed"
    }
  ],
  "requirement_coverage": [],
  "contradictions": [
    {
      "quote": "Someone in the author's life—call him X—has died and can never return",
      "reference": "The narrator killed his wife",
      "checkpoint_ids": [
        "C1"
      ]
    },
    {
      "quote": "not because of the dead man, but out of guilt and the dread that the forgery will be exposed",
      "reference": "His inability to imitate her handwriting leads him to worry about being caught",
      "checkpoint_ids": [
        "C2",
        "C3"
      ]
    }
  ],
  "partial_score": 0.0,
  "complete": false,
  "label": "no",
  "grading_protocol": "coverage-v3-unified",
  "controller_corrections": []
}
```
</details>

## 37 · question

Do the seven copies serve a formal or official purpose, such as a legal or bureaucratic claim?

Host: no

## 38 · question

Is the author the dead person's spouse or partner?

Host: yes

## 39 · question

Does the author feel personally responsible for the partner's death?

Host: yes

## 40 · question

Did the death occur during a conflict or argument between the author and the partner?

Host: irrelevant

## 41 · question

Does the author read the forged farewell aloud to the third party?

Host: irrelevant

## 42 · final

The author was the dead partner's spouse. The partner has died, and the author feels personally responsible for that death—believing they disappointed the partner and drove them away. Unable to voice the loss plainly, the author writes the dead partner's reproach in the partner's own voice, addressed to the author: "You've disappointed me so much; I'm never coming back." With this forged farewell, the author accounts for the partner's permanent absence to another person as a deliberate break-up rather than a death, sparing that person from learning of it. Writing the same line over and over is the author's way of keeping the story—and the guilt—in place; seeing it, the author sighs, "I know I'm in trouble," dreading that the forgery will be found out.

Host: no

<details><summary>Private evaluator result (not sent to player)</summary>

```json
{
  "checkpoints": [
    {
      "id": "C1",
      "credit": 0,
      "evidence": "The partner has died, and the author feels personally responsible for that death—believing they disappointed the partner and drove them away.",
      "reason": "The required murder of the wife is contradicted by the alternative death-by-disappointment/driving-away narrative; only the staged voluntary departure is present."
    },
    {
      "id": "C2",
      "credit": 0,
      "evidence": "Writing the same line over and over is the author's way of keeping the story—and the guilt—in place.",
      "reason": "The repeated message is present, but the required fact that the repetitions are attempts to forge the wife's handwriting is contradicted by this alternative purpose and the wife is omitted."
    },
    {
      "id": "C3",
      "credit": 0,
      "evidence": "dreading that the forgery will be found out",
      "reason": "The worry is present, but the required causal fact—inability to imitate her handwriting—is absent and replaced by guilt and keeping the story, so this is contradicted."
    }
  ],
  "material_contradiction": true,
  "irrelevant": false,
  "rubric_conflict": false,
  "full_solution": false,
  "completion_note": "Scored facts remain missing, partial or contradicted; see fact_coverage.",
  "fact_coverage": [
    {
      "id": "C1.F1",
      "status": "contradicted",
      "evidence": "The partner has died, and the author feels personally responsible for that death—believing they disappointed the partner and drove them away."
    },
    {
      "id": "C1.F2",
      "status": "contradicted",
      "evidence": "The partner has died, and the author feels personally responsible for that death—believing they disappointed the partner and drove them away."
    },
    {
      "id": "C1.F3",
      "status": "covered",
      "evidence": "With this forged farewell, the author accounts for the partner's permanent absence to another person as a deliberate break-up rather than a death, sparing that person from learning of it."
    },
    {
      "id": "C2.F1",
      "status": "contradicted",
      "evidence": "Writing the same line over and over is the author's way of keeping the story—and the guilt—in place."
    },
    {
      "id": "C2.F2",
      "status": "contradicted",
      "evidence": "Writing the same line over and over is the author's way of keeping the story—and the guilt—in place; seeing it, the author sighs, \"I know I'm in trouble,\" dreading that the forgery will be found out."
    },
    {
      "id": "C3.F1",
      "status": "contradicted",
      "evidence": "Writing the same line over and over is the author's way of keeping the story—and the guilt—in place; seeing it, the author sighs, \"I know I'm in trouble,\" dreading that the forgery will be found out."
    }
  ],
  "requirement_coverage": [],
  "contradictions": [
    {
      "quote": "The partner has died, and the author feels personally responsible for that death—believing they disappointed the partner and drove them away.",
      "reference": "The narrator killed his wife",
      "checkpoint_ids": [
        "C1"
      ]
    },
    {
      "quote": "Writing the same line over and over is the author's way of keeping the story—and the guilt—in place",
      "reference": "The repetitions are failed attempts to imitate her handwriting, making him fear discovery",
      "checkpoint_ids": [
        "C2"
      ]
    },
    {
      "quote": "Writing the same line over and over is the author's way of keeping the story—and the guilt—in place; seeing it, the author sighs, \"I know I'm in trouble,\" dreading that the forgery will be found out.",
      "reference": "His inability to imitate her handwriting leads him to worry about being caught",
      "checkpoint_ids": [
        "C3"
      ]
    }
  ],
  "partial_score": 0.0,
  "complete": false,
  "label": "no",
  "grading_protocol": "coverage-v3-unified",
  "controller_corrections": []
}
```
</details>

## 43 · question

Did the author's own actions cause the partner's death?

Host: yes

## 44 · question

Was the partner's death accidental?

Host: no

## 45 · final

The author was married to the dead person. By the author's own deliberate actions, that partner died—something the author knows and feels personally responsible for. To keep anyone from learning of the death, the author fabricates the dead partner's own words: "You've disappointed me so much; I'm never coming back," written in the partner's voice and addressed to the author, as though the partner had walked out for good. The seven identical copies are the author's forged evidence of that supposed break-up. Someone who would otherwise ask where the partner went is instead led to believe the partner simply chose to leave and will never return—so the death stays hidden. Seeing the repeated forgeries, the author sighs, "I know I'm in trouble": the lie is what stands between them and exposure for the killing.

Host: yes and no

<details><summary>Private evaluator result (not sent to player)</summary>

```json
{
  "checkpoints": [
    {
      "id": "C1",
      "credit": 0.5,
      "evidence": "By the author's own deliberate actions, that partner died ... To keep anyone from learning of the death, the author fabricates the dead partner's own words ... as though the partner had walked out for good ... exposure for the killing.",
      "reason": "The submission covers a deliberate killing and the staging of a voluntary departure through a forged farewell, but it does not explicitly identify the victim as the narrator's wife, so the checkpoint is only partly correct."
    },
    {
      "id": "C2",
      "credit": 0.5,
      "evidence": "The seven identical copies are the author's forged evidence of that supposed break-up ... Seeing the repeated forgeries, the author sighs, \"I know I'm in trouble\".",
      "reason": "The repeated forged message is present, but the required fact that the repetitions are attempts to imitate his wife's handwriting is missing, so the checkpoint is only partly correct."
    },
    {
      "id": "C3",
      "credit": 0.5,
      "evidence": "the lie is what stands between them and exposure for the killing",
      "reason": "The worry about exposure is present, but the required causal fact that inability to imitate her handwriting leads to this worry is absent and replaced by a vaguer explanation about the lie itself."
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
      "evidence": "By the author's own deliberate actions, that partner died ... To keep anyone from learning of the death, the author fabricates the dead partner's own words ... as though the partner had walked out for good."
    },
    {
      "id": "C1.F2",
      "status": "partial",
      "evidence": "By the author's own deliberate actions, that partner died ... exposure for the killing."
    },
    {
      "id": "C1.F3",
      "status": "covered",
      "evidence": "To keep anyone from learning of the death, the author fabricates the dead partner's own words ... as though the partner had walked out for good ... Someone who would otherwise ask where the partner went is instead led to believe the partner simply chose to leave and will never return."
    },
    {
      "id": "C2.F1",
      "status": "partial",
      "evidence": "The seven identical copies are the author's forged evidence of that supposed break-up."
    },
    {
      "id": "C2.F2",
      "status": "partial",
      "evidence": "The seven identical copies are the author's forged evidence of that supposed break-up ... Seeing the repeated forgeries, the author sighs, \"I know I'm in trouble\": the lie is what stands between them and exposure for the killing."
    },
    {
      "id": "C3.F1",
      "status": "partial",
      "evidence": "Seeing the repeated forgeries, the author sighs, \"I know I'm in trouble\": the lie is what stands between them and exposure for the killing."
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

## 46 · question

Does the author fear the third person will learn that the author caused the partner's death?

Host: yes

## 47 · final

The author killed their spouse. The spouse is dead and cannot return, and a third person would otherwise find out—both that the spouse is dead and that the author caused it. So the author forged the dead spouse's own voice, writing "You've disappointed me so much; I'm never coming back" as though the spouse had addressed the author and simply chosen to leave for good. That way the spouse's permanent absence is explained as a deliberate departure, and the death stays concealed. The author set down the same forged lines seven times. Looking at them, the author sighs, "I know I'm in trouble"—the fabrication is all that keeps the death and the killing hidden, and exposure would reveal everything.

Host: yes and no

<details><summary>Private evaluator result (not sent to player)</summary>

```json
{
  "checkpoints": [
    {
      "id": "C1",
      "credit": 0.5,
      "evidence": "The author killed their spouse. ... So the author forged the dead spouse's own voice ... explained as a deliberate departure, and the death stays concealed.",
      "reason": "The killing and staged voluntary departure are covered, but the required identity—the narrator's wife—is replaced by the generic 'spouse,' so full credit is not possible."
    },
    {
      "id": "C2",
      "credit": 0.5,
      "evidence": "The author set down the same forged lines seven times.",
      "reason": "The repeated forged message is present, but the required fact that the repetitions are attempts to forge the wife's handwriting is missing."
    },
    {
      "id": "C3",
      "credit": 0.5,
      "evidence": "Looking at them, the author sighs, \"I know I'm in trouble\"—the fabrication is all that keeps the death and the killing hidden, and exposure would reveal everything.",
      "reason": "Fear of exposure is present, but the required causal fact—inability to imitate her handwriting—is absent."
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
      "evidence": "The author killed their spouse. ... as though the spouse had addressed the author and simply chosen to leave for good. ... the death and the killing hidden."
    },
    {
      "id": "C1.F2",
      "status": "partial",
      "evidence": "The author killed their spouse."
    },
    {
      "id": "C1.F3",
      "status": "covered",
      "evidence": "the author forged the dead spouse's own voice ... as though the spouse had addressed the author and simply chosen to leave for good. That way the spouse's permanent absence is explained as a deliberate departure, and the death stays concealed."
    },
    {
      "id": "C2.F1",
      "status": "partial",
      "evidence": "The author set down the same forged lines seven times."
    },
    {
      "id": "C2.F2",
      "status": "partial",
      "evidence": "The author set down the same forged lines seven times. Looking at them, the author sighs, \"I know I'm in trouble\"—the fabrication is all that keeps the death and the killing hidden, and exposure would reveal everything."
    },
    {
      "id": "C3.F1",
      "status": "partial",
      "evidence": "Looking at them, the author sighs, \"I know I'm in trouble\"—the fabrication is all that keeps the death and the killing hidden, and exposure would reveal everything."
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

## 48 · question

Does the third person believe the spouse is dead?

Host: no

## 49 · question

Is the forged note meant to stop the third person from searching for or making inquiries about the spouse?

Host: yes

## 50 · final

The author killed their spouse. Because someone else would otherwise search for or keep asking about the spouse, the author forged the dead spouse's own voice—writing out "You've disappointed me so much; I'm never coming back" as though the spouse had addressed the author and deliberately ended things. The forged farewell is meant to pass as the spouse's own writing, so that the third person explains the spouse's absence as a chosen break-up, stops searching, and never learns of the death. The author produced the same sentence seven times; looking at those fabricated lines, the author sighs, "I know I'm in trouble"—the lie is what keeps the death hidden, and if it unravels, the third person will learn both that the spouse is dead and that the author caused it.

Host: yes and no

<details><summary>Private evaluator result (not sent to player)</summary>

```json
{
  "checkpoints": [
    {
      "id": "C1",
      "credit": 0.5,
      "evidence": "The author killed their spouse. ... the author forged the dead spouse's own voice—writing out \"You've disappointed me so much; I'm never coming back\" as though the spouse had addressed the author and deliberately ended things. The forged farewell is meant to pass as the spouse's own writing, so that the third person explains the spouse's absence as a chosen break-up, stops searching, and never learns of the death.",
      "reason": "The deliberate killing and staged voluntary departure are covered, but the submission uses 'spouse' rather than the required 'wife,' omitting that specific identity qualifier."
    },
    {
      "id": "C2",
      "credit": 0.5,
      "evidence": "The forged farewell is meant to pass as the spouse's own writing ... The author produced the same sentence seven times",
      "reason": "The repeated forged message is present, but the required fact that the repetitions are attempts to imitate the wife's handwriting is missing; the submission only says the text is meant to pass as the spouse's writing."
    },
    {
      "id": "C3",
      "credit": 0.5,
      "evidence": "looking at those fabricated lines, the author sighs, \"I know I'm in trouble\"—the lie is what keeps the death hidden, and if it unravels, the third person will learn both that the spouse is dead and that the author caused it.",
      "reason": "The worry about being caught is present, but the required causal link—his inability to imitate her handwriting—is missing; the explanation instead attributes the fear to the lie unraveling."
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
      "evidence": "The author killed their spouse. ... the author forged the dead spouse's own voice—writing out \"You've disappointed me so much; I'm never coming back\" as though the spouse had addressed the author and deliberately ended things. The forged farewell is meant to pass as the spouse's own writing, so that the third person explains the spouse's absence as a chosen break-up, stops searching, and never learns of the death."
    },
    {
      "id": "C1.F2",
      "status": "partial",
      "evidence": "The author killed their spouse."
    },
    {
      "id": "C1.F3",
      "status": "covered",
      "evidence": "the author forged the dead spouse's own voice—writing out \"You've disappointed me so much; I'm never coming back\" as though the spouse had addressed the author and deliberately ended things. The forged farewell is meant to pass as the spouse's own writing, so that the third person explains the spouse's absence as a chosen break-up, stops searching, and never learns of the death."
    },
    {
      "id": "C2.F1",
      "status": "partial",
      "evidence": "The forged farewell is meant to pass as the spouse's own writing ... The author produced the same sentence seven times"
    },
    {
      "id": "C2.F2",
      "status": "partial",
      "evidence": "The author produced the same sentence seven times; looking at those fabricated lines, the author sighs, \"I know I'm in trouble\"—the lie is what keeps the death hidden, and if it unravels, the third person will learn both that the spouse is dead and that the author caused it."
    },
    {
      "id": "C3.F1",
      "status": "partial",
      "evidence": "looking at those fabricated lines, the author sighs, \"I know I'm in trouble\"—the lie is what keeps the death hidden, and if it unravels, the third person will learn both that the spouse is dead and that the author caused it."
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

## 51 · question

Had the spouse wanted or consented to die?

Host: no

## 52 · question

Has the author concealed the spouse's body?

Host: irrelevant

## 53 · question

Is the deception aimed at people generally rather than one identifiable individual?

Host: yes

## 54 · final

The author deliberately caused their spouse's death and feels personally responsible for it. The spouse is dead and cannot return. To keep the death from being discovered, the author forged the dead spouse's own voice—writing "You've disappointed me so much; I'm never coming back" as though the spouse were addressing the author and had chosen to break off contact for good. The forged farewell is meant to be read as the spouse's own writing and to explain, to people generally, why the spouse has gone and will not return, so that no one keeps searching and no one realizes the spouse is dead. The author set down the same sentence seven times, repeating the fabrication; looking at those lines, the author sighs, "I know I'm in trouble," because the deception is all that hides the death and the author's responsibility for it, and its exposure would uncover both.

Host: yes and no

<details><summary>Private evaluator result (not sent to player)</summary>

```json
{
  "checkpoints": [
    {
      "id": "C1",
      "credit": 0.5,
      "evidence": "The author deliberately caused their spouse's death ... To keep the death from being discovered, the author forged the dead spouse's own voice ... as though the spouse were addressing the author and had chosen to break off contact for good.",
      "reason": "The deliberate killing and staged voluntary departure are covered, but the required identity 'wife' is omitted, so the checkpoint is only partly correct."
    },
    {
      "id": "C2",
      "credit": 0.5,
      "evidence": "The author set down the same sentence seven times, repeating the fabrication ... The forged farewell is meant to be read as the spouse's own writing.",
      "reason": "The repeated forged message is present, but the required fact that the repetitions are attempts to forge the wife's handwriting is missing."
    },
    {
      "id": "C3",
      "credit": 0.5,
      "evidence": "looking at those lines, the author sighs, \"I know I'm in trouble,\" because the deception is all that hides the death and the author's responsibility for it, and its exposure would uncover both.",
      "reason": "The fear of exposure is present, but the required causal fact—inability to imitate her handwriting—is absent."
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
      "evidence": "The author deliberately caused their spouse's death ... To keep the death from being discovered, the author forged the dead spouse's own voice ... as though the spouse were addressing the author and had chosen to break off contact for good ... The forged farewell is meant to be read as the spouse's own writing and to explain ... why the spouse has gone and will not return."
    },
    {
      "id": "C1.F2",
      "status": "partial",
      "evidence": "The author deliberately caused their spouse's death."
    },
    {
      "id": "C1.F3",
      "status": "covered",
      "evidence": "the author forged the dead spouse's own voice ... as though the spouse were addressing the author and had chosen to break off contact for good. The forged farewell is meant to be read as the spouse's own writing and to explain ... why the spouse has gone and will not return, so that no one keeps searching and no one realizes the spouse is dead."
    },
    {
      "id": "C2.F1",
      "status": "partial",
      "evidence": "The forged farewell is meant to be read as the spouse's own writing and to explain, to people generally, why the spouse has gone and will not return, so that no one keeps searching and no one realizes the spouse is dead. … The author set down the same sentence seven times, repeating the fabrication; looking at those lines, the author sighs, \"I know I'm in trouble,\" because the deception is all that hides the death and the author's responsibility for it, and its exposure would uncover both."
    },
    {
      "id": "C2.F2",
      "status": "partial",
      "evidence": "The author set down the same sentence seven times, repeating the fabrication; looking at those lines, the author sighs, \"I know I'm in trouble,\" because the deception is all that hides the death and the author's responsibility for it, and its exposure would uncover both."
    },
    {
      "id": "C3.F1",
      "status": "partial",
      "evidence": "looking at those lines, the author sighs, \"I know I'm in trouble,\" because the deception is all that hides the death and the author's responsibility for it, and its exposure would uncover both."
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

## 55 · question

Does the author gain something materially by the spouse being thought merely absent rather than dead?

Host: no

## 56 · final

The author's spouse is dead, and the author's own deliberate actions caused that death; the author knows this and feels personally responsible. Because the spouse cannot return, the author fabricated the dead spouse's own words, "You've disappointed me so much; I'm never coming back," in the spouse's voice and addressed to the author, so that it would be read as the spouse's own writing. Presented to people generally, it lets the spouse's absence be taken as a voluntary departure rather than a death: inquiries stop, and no one learns what really happened. The same sentence appears seven times, the author's repeated fabrication. Confronted with those forged lines, the author sighs, "I know I'm in trouble"—dreading that the forgery will be exposed and the death, and the author's part in it, revealed.

Host: yes and no

<details><summary>Private evaluator result (not sent to player)</summary>

```json
{
  "checkpoints": [
    {
      "id": "C1",
      "credit": 0.5,
      "evidence": "The author's spouse is dead, and the author's own deliberate actions caused that death ... the author fabricated the dead spouse's own words ... so that it would be read as the spouse's own writing. Presented to people generally, it lets the spouse's absence be taken as a voluntary departure rather than a death",
      "reason": "The deliberate killing and staged voluntary departure are covered, but the required identity 'wife' is omitted, so the checkpoint is only partly correct."
    },
    {
      "id": "C2",
      "credit": 0.5,
      "evidence": "The same sentence appears seven times, the author's repeated fabrication ... so that it would be read as the spouse's own writing",
      "reason": "The repeated forged message is present, but the required fact that the repetitions are attempts to imitate his wife's handwriting is missing."
    },
    {
      "id": "C3",
      "credit": 0.5,
      "evidence": "Confronted with those forged lines, the author sighs, \"I know I'm in trouble\"—dreading that the forgery will be exposed and the death, and the author's part in it, revealed.",
      "reason": "The worry about exposure is present, but the required causal fact—inability to imitate her handwriting—is absent."
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
      "evidence": "The author's spouse is dead, and the author's own deliberate actions caused that death ... the author fabricated the dead spouse's own words ... so that it would be read as the spouse's own writing. Presented to people generally, it lets the spouse's absence be taken as a voluntary departure rather than a death"
    },
    {
      "id": "C1.F2",
      "status": "partial",
      "evidence": "The author's spouse is dead, and the author's own deliberate actions caused that death"
    },
    {
      "id": "C1.F3",
      "status": "covered",
      "evidence": "the author fabricated the dead spouse's own words ... so that it would be read as the spouse's own writing. Presented to people generally, it lets the spouse's absence be taken as a voluntary departure rather than a death: inquiries stop, and no one learns what really happened."
    },
    {
      "id": "C2.F1",
      "status": "partial",
      "evidence": "Because the spouse cannot return, the author fabricated the dead spouse's own words, \"You've disappointed me so much; I'm never coming back,\" in the spouse's voice and addressed to the author, so that it would be read as the spouse's own writing. … The same sentence appears seven times, the author's repeated fabrication."
    },
    {
      "id": "C2.F2",
      "status": "partial",
      "evidence": "The same sentence appears seven times, the author's repeated fabrication. Confronted with those forged lines, the author sighs, \"I know I'm in trouble\"—dreading that the forgery will be exposed and the death, and the author's part in it, revealed."
    },
    {
      "id": "C3.F1",
      "status": "partial",
      "evidence": "Confronted with those forged lines, the author sighs, \"I know I'm in trouble\"—dreading that the forgery will be exposed and the death, and the author's part in it, revealed."
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

## 57 · question

Was the author acting in self-defence or to protect someone when the spouse died?

Host: irrelevant

## 58 · final

The author and the dead person were spouses. The author's own deliberate actions caused the spouse's death—not an accident—and the author feels personally responsible. The spouse is dead and cannot return. The author fabricated the dead spouse's own words, "You've disappointed me so much; I'm never coming back," written in the spouse's voice and addressed to the author, and intended to be read as the spouse's own writing; the same sentence exists seven times over. It is meant to mislead people generally: it gives a reason the spouse will never return, so that those who might otherwise wonder or search stop inquiring, and no one learns that the spouse is dead. Nothing material is gained by it. Seeing those forged lines, the author sighs, "I know I'm in trouble," knowing that exposure of the forgery would reveal the death and that the author caused it.

Host: yes and no

<details><summary>Private evaluator result (not sent to player)</summary>

```json
{
  "checkpoints": [
    {
      "id": "C1",
      "credit": 0.5,
      "evidence": "The author's own deliberate actions caused the spouse's death—not an accident ... The author fabricated the dead spouse's own words ... It is meant to mislead people generally: it gives a reason the spouse will never return, so that those who might otherwise wonder or search stop inquiring, and no one learns that the spouse is dead.",
      "reason": "The deliberate killing and staged voluntary departure via forged farewell are covered, but the required identity 'wife' is omitted, so the checkpoint is only partly correct."
    },
    {
      "id": "C2",
      "credit": 0.5,
      "evidence": "The author fabricated the dead spouse's own words ... intended to be read as the spouse's own writing; the same sentence exists seven times over.",
      "reason": "The repeated forged message is present, but the required fact that the repetitions are attempts to forge his wife's handwriting is missing."
    },
    {
      "id": "C3",
      "credit": 0.5,
      "evidence": "Seeing those forged lines, the author sighs, \"I know I'm in trouble,\" knowing that exposure of the forgery would reveal the death and that the author caused it.",
      "reason": "The worry about being caught is present, but the required causal fact—inability to imitate her handwriting—is absent."
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
      "evidence": "The author's own deliberate actions caused the spouse's death—not an accident ... The author fabricated the dead spouse's own words ... It is meant to mislead people generally: it gives a reason the spouse will never return, so that those who might otherwise wonder or search stop inquiring, and no one learns that the spouse is dead."
    },
    {
      "id": "C1.F2",
      "status": "partial",
      "evidence": "The author's own deliberate actions caused the spouse's death—not an accident"
    },
    {
      "id": "C1.F3",
      "status": "covered",
      "evidence": "The author fabricated the dead spouse's own words ... intended to be read as the spouse's own writing ... It is meant to mislead people generally: it gives a reason the spouse will never return, so that those who might otherwise wonder or search stop inquiring, and no one learns that the spouse is dead."
    },
    {
      "id": "C2.F1",
      "status": "partial",
      "evidence": "The author fabricated the dead spouse's own words ... intended to be read as the spouse's own writing; the same sentence exists seven times over."
    },
    {
      "id": "C2.F2",
      "status": "partial",
      "evidence": "the same sentence exists seven times over ... Seeing those forged lines, the author sighs, \"I know I'm in trouble,\" knowing that exposure of the forgery would reveal the death and that the author caused it."
    },
    {
      "id": "C3.F1",
      "status": "partial",
      "evidence": "Seeing those forged lines, the author sighs, \"I know I'm in trouble,\" knowing that exposure of the forgery would reveal the death and that the author caused it."
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

## 59 · question

Were the forged copies made after the spouse's death?

Host: yes

## 60 · final

The author killed their spouse—by their own deliberate act, not by accident. The spouse is dead and cannot return. Outwardly, the author gives people a different explanation for the spouse's continuing absence: that the spouse was disappointed and left for good, never to come back. So those who might wonder or search stop asking, and no one learns the spouse is dead. The same bitter farewell—"You've disappointed me so much; I'm never coming back"—appears seven times over, written by the author in the dead spouse's voice as though the spouse had addressed the author. Because the author fabricated those words, seeing them is a reminder that the whole account is a lie; the author sighs, "I know I'm in trouble," knowing that exposure of the fabrication would uncover both the death and the author's responsibility for it.

Host: yes and no

<details><summary>Private evaluator result (not sent to player)</summary>

```json
{
  "checkpoints": [
    {
      "id": "C1",
      "credit": 0.5,
      "evidence": "The author killed their spouse—by their own deliberate act, not by accident. ... Outwardly, the author gives people a different explanation for the spouse's continuing absence: that the spouse was disappointed and left for good, never to come back.",
      "reason": "The deliberate killing and staged voluntary departure are covered, but the required identity 'wife' is omitted, so the checkpoint is only partly correct."
    },
    {
      "id": "C2",
      "credit": 0.5,
      "evidence": "The same bitter farewell—\"You've disappointed me so much; I'm never coming back\"—appears seven times over, written by the author in the dead spouse's voice as though the spouse had addressed the author.",
      "reason": "The repeated forged message is present, but the required fact that the repetitions are attempts to imitate his wife's handwriting is missing."
    },
    {
      "id": "C3",
      "credit": 0.5,
      "evidence": "the author sighs, \"I know I'm in trouble,\" knowing that exposure of the fabrication would uncover both the death and the author's responsibility for it.",
      "reason": "The worry about being caught is present, but the required causal fact—inability to imitate her handwriting—is absent."
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
      "evidence": "The author killed their spouse—by their own deliberate act, not by accident. ... Outwardly, the author gives people a different explanation for the spouse's continuing absence: that the spouse was disappointed and left for good, never to come back."
    },
    {
      "id": "C1.F2",
      "status": "partial",
      "evidence": "The author killed their spouse—by their own deliberate act, not by accident."
    },
    {
      "id": "C1.F3",
      "status": "covered",
      "evidence": "Outwardly, the author gives people a different explanation for the spouse's continuing absence: that the spouse was disappointed and left for good, never to come back. ... The same bitter farewell—\"You've disappointed me so much; I'm never coming back\"—appears seven times over, written by the author in the dead spouse's voice as though the spouse had addressed the author."
    },
    {
      "id": "C2.F1",
      "status": "partial",
      "evidence": "The same bitter farewell—\"You've disappointed me so much; I'm never coming back\"—appears seven times over, written by the author in the dead spouse's voice as though the spouse had addressed the author."
    },
    {
      "id": "C2.F2",
      "status": "partial",
      "evidence": "The same bitter farewell—\"You've disappointed me so much; I'm never coming back\"—appears seven times over, written by the author in the dead spouse's voice as though the spouse had addressed the author. Because the author fabricated those words, seeing them is a reminder that the whole account is a lie; the author sighs, \"I know I'm in trouble,\" knowing that exposure of the fabrication would uncover both the death and the author's responsibility for it."
    },
    {
      "id": "C3.F1",
      "status": "partial",
      "evidence": "the author sighs, \"I know I'm in trouble,\" knowing that exposure of the fabrication would uncover both the death and the author's responsibility for it."
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

## 61 · question

Does the author's fabricated account make people believe the spouse left because of the author—that the author is the one the spouse rejected?

Host: yes

## 62 · final

The author and the dead person were spouses. By the author's own deliberate act—not an accident—the spouse died, and the author feels personally responsible. The spouse is dead and cannot return. After the death, the author fabricated the dead spouse's own words, "You've disappointed me so much; I'm never coming back," written in the spouse's voice, addressed to the author, and set down seven times so as to pass as the spouse's real writing. The author lets people generally read it, and it makes them believe the spouse rejected the author and walked out for good because of the author. So they stop searching or inquiring, never learn the spouse is dead, and suspect nothing; the author gains nothing material by this. Seeing the forged lines, the author sighs, "I know I'm in trouble": the author has arranged to be seen as the spouse's rejected partner, but that humiliation is only the surface—exposure of the fabrication would reveal the death and the author's responsibility for it.

Host: yes and no

<details><summary>Private evaluator result (not sent to player)</summary>

```json
{
  "checkpoints": [
    {
      "id": "C1",
      "credit": 0.5,
      "evidence": "The author and the dead person were spouses. By the author's own deliberate act—not an accident—the spouse died ... the author fabricated the dead spouse's own words ... it makes them believe the spouse rejected the author and walked out for good",
      "reason": "The deliberate killing and staged voluntary departure are covered, but the required identity 'wife' is omitted."
    },
    {
      "id": "C2",
      "credit": 0.5,
      "evidence": "fabricated the dead spouse's own words ... written in the spouse's voice, addressed to the author, and set down seven times so as to pass as the spouse's real writing.",
      "reason": "The repeated forged message is present, but the required fact that the repetitions are attempts to imitate his wife's handwriting is missing."
    },
    {
      "id": "C3",
      "credit": 0.5,
      "evidence": "Seeing the forged lines, the author sighs, \"I know I'm in trouble\" ... exposure of the fabrication would reveal the death and the author's responsibility for it.",
      "reason": "Fear of exposure is present, but the required causal fact—inability to imitate her handwriting—is absent."
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
      "evidence": "The author and the dead person were spouses. By the author's own deliberate act—not an accident—the spouse died ... the author fabricated the dead spouse's own words ... it makes them believe the spouse rejected the author and walked out for good"
    },
    {
      "id": "C1.F2",
      "status": "partial",
      "evidence": "By the author's own deliberate act—not an accident—the spouse died"
    },
    {
      "id": "C1.F3",
      "status": "covered",
      "evidence": "the author fabricated the dead spouse's own words ... written in the spouse's voice, addressed to the author ... it makes them believe the spouse rejected the author and walked out for good because of the author. So they stop searching or inquiring, never learn the spouse is dead"
    },
    {
      "id": "C2.F1",
      "status": "partial",
      "evidence": "the author fabricated the dead spouse's own words ... written in the spouse's voice, addressed to the author, and set down seven times so as to pass as the spouse's real writing"
    },
    {
      "id": "C2.F2",
      "status": "partial",
      "evidence": "set down seven times so as to pass as the spouse's real writing ... Seeing the forged lines, the author sighs, \"I know I'm in trouble\" ... exposure of the fabrication would reveal the death and the author's responsibility for it"
    },
    {
      "id": "C3.F1",
      "status": "partial",
      "evidence": "Seeing the forged lines, the author sighs, \"I know I'm in trouble\" ... exposure of the fabrication would reveal the death and the author's responsibility for it"
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

## 63 · question

Does the author fabricate the spouse's rejection partly to punish themselves?

Host: no

## 64 · question

Had the spouse been planning to leave the author?

Host: no

## 65 · question

Has someone already discovered the forgery?

Host: no

## 66 · question

Did the author intend to cause the spouse's death?

Host: yes

## 67 · question

Were the seven copies practice attempts at imitating the spouse's handwriting?

Host: yes

## 68 · final

The author and the dead person were spouses. The author deliberately, intentionally caused the spouse's death—not by accident, and not with the spouse's consent—and the author feels personally responsible. The spouse is dead and can never return. After the death, the author set about forging the spouse's own farewell, and what we see are practice attempts at imitating the dead spouse's handwriting: the same sentence, "You've disappointed me so much; I'm never coming back," written in the spouse's voice and addressed to the author, seven times over. The goal is to pass it off as the spouse's real writing, so that people generally will believe the spouse rejected the author and walked out for good, never to return—thus no one keeps searching, and no one learns that the spouse is dead. Nothing material is gained. Looking at the seven practiced forgeries, the author sighs, "I know I'm in trouble": the imitation is what shields the death and the killing, and if it is spotted as a fake, everything comes out.

Host: yes and no

<details><summary>Private evaluator result (not sent to player)</summary>

```json
{
  "checkpoints": [
    {
      "id": "C1",
      "credit": 0.5,
      "evidence": "The author and the dead person were spouses. The author deliberately, intentionally caused the spouse's death—not by accident ... forged the spouse's own farewell ... people generally will believe the spouse rejected the author and walked out for good",
      "reason": "The deliberate killing and staged voluntary departure are covered, but the required identity 'wife' is omitted."
    },
    {
      "id": "C2",
      "credit": 0.5,
      "evidence": "what we see are practice attempts at imitating the dead spouse's handwriting: the same sentence ... seven times over",
      "reason": "The repeated message as practice attempts to imitate handwriting is present, but the required fact is partial because it does not identify the handwriting as his wife's and lacks the explicit failure qualifier."
    },
    {
      "id": "C3",
      "credit": 0.5,
      "evidence": "the imitation is what shields the death and the killing, and if it is spotted as a fake, everything comes out.",
      "reason": "The fear of being caught is present, but the required causal fact—inability to imitate her handwriting—is absent."
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
      "evidence": "The author and the dead person were spouses. … The author deliberately, intentionally caused the spouse's death—not by accident, and not with the spouse's consent—and the author feels personally responsible. … After the death, the author set about forging the spouse's own farewell, and what we see are practice attempts at imitating the dead spouse's handwriting: the same sentence, \"You've disappointed me so much; I'm never coming back,\" written in the spouse's voice and addressed to the author, seven times over. … The goal is to pass it off as the spouse's real writing, so that people generally will believe the spouse rejected the author and walked out for good, never to return—thus no one keeps searching, and no one learns that the spouse is dead."
    },
    {
      "id": "C1.F2",
      "status": "partial",
      "evidence": "The author deliberately, intentionally caused the spouse's death—not by accident"
    },
    {
      "id": "C1.F3",
      "status": "covered",
      "evidence": "After the death, the author set about forging the spouse's own farewell ... The goal is to pass it off as the spouse's real writing, so that people generally will believe the spouse rejected the author and walked out for good, never to return"
    },
    {
      "id": "C2.F1",
      "status": "partial",
      "evidence": "what we see are practice attempts at imitating the dead spouse's handwriting: the same sentence ... seven times over"
    },
    {
      "id": "C2.F2",
      "status": "partial",
      "evidence": "practice attempts at imitating the dead spouse's handwriting ... if it is spotted as a fake, everything comes out"
    },
    {
      "id": "C3.F1",
      "status": "partial",
      "evidence": "the imitation is what shields the death and the killing, and if it is spotted as a fake, everything comes out"
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

## 69 · question

Has the author already used a completed forgery to deceive anyone?

Host: no

## 70 · final

The author and the dead person were spouses. The author deliberately and intentionally caused the spouse's death—not by accident, and not with the spouse's consent—and feels personally responsible. The spouse is dead and can never return. What we are looking at is not a deception already carried out but one being prepared: the author is practising how to imitate the dead spouse's handwriting, writing the same sentence over and over, seven attempts in all—"You've disappointed me so much; I'm never coming back"—in the spouse's voice and addressed to the author. The plan is for this to be taken as the spouse's own writing, so that people generally will believe the spouse rejected the author and walked out for good, never to return; then inquiries will stop and no one will learn that the spouse is dead or that the author caused it. Nothing material is gained, no one has yet been fooled, and the forgery has not been discovered. Looking at the seven practised copies, the author sighs, "I know I'm in trouble": the imitation is the whole shield for the death and the killing, and if it is detected as a fake, everything will come out.

Host: yes and no

<details><summary>Private evaluator result (not sent to player)</summary>

```json
{
  "checkpoints": [
    {
      "id": "C1",
      "credit": 0.5,
      "evidence": "The author deliberately and intentionally caused the spouse's death ... The plan is for this to be taken as the spouse's own writing, so that people generally will believe the spouse rejected the author and walked out for good.",
      "reason": "The deliberate killing and staged voluntary departure are covered, but the required identity 'wife' is omitted."
    },
    {
      "id": "C2",
      "credit": 0.5,
      "evidence": "the author is practising how to imitate the dead spouse's handwriting, writing the same sentence over and over, seven attempts in all",
      "reason": "The repeated message as practice attempts to imitate handwriting is present, but the wife identity and the explicit failure qualifier are missing."
    },
    {
      "id": "C3",
      "credit": 0.5,
      "evidence": "the imitation is the whole shield for the death and the killing, and if it is detected as a fake, everything will come out.",
      "reason": "Fear of being caught is present, but the required causal fact—inability to imitate her handwriting—is absent."
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
      "evidence": "The author and the dead person were spouses. The author deliberately and intentionally caused the spouse's death—not by accident, and not with the spouse's consent—and feels personally responsible. ... The plan is for this to be taken as the spouse's own writing, so that people generally will believe the spouse rejected the author and walked out for good, never to return; then inquiries will stop and no one will learn that the spouse is dead or that the author caused it."
    },
    {
      "id": "C1.F2",
      "status": "partial",
      "evidence": "The author deliberately and intentionally caused the spouse's death—not by accident, and not with the spouse's consent—"
    },
    {
      "id": "C1.F3",
      "status": "covered",
      "evidence": "the author is practising how to imitate the dead spouse's handwriting, writing the same sentence over and over, seven attempts in all—\"You've disappointed me so much; I'm never coming back\"—in the spouse's voice and addressed to the author. The plan is for this to be taken as the spouse's own writing, so that people generally will believe the spouse rejected the author and walked out for good, never to return"
    },
    {
      "id": "C2.F1",
      "status": "partial",
      "evidence": "the author is practising how to imitate the dead spouse's handwriting, writing the same sentence over and over, seven attempts in all"
    },
    {
      "id": "C2.F2",
      "status": "partial",
      "evidence": "the author is practising how to imitate the dead spouse's handwriting, writing the same sentence over and over, seven attempts in all ... if it is detected as a fake, everything will come out"
    },
    {
      "id": "C3.F1",
      "status": "partial",
      "evidence": "Looking at the seven practised copies, the author sighs, \"I know I'm in trouble\": the imitation is the whole shield for the death and the killing, and if it is detected as a fake, everything will come out."
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

## 71 · question

Had the spouse ever written this sentence before dying?

Host: irrelevant

## 72 · final

The author and the dead person were spouses. The author intended and caused the spouse's death; it was neither an accident nor consented to, and the author feels personally responsible. The spouse is dead and cannot return. After the death the author began imitating the dead spouse's handwriting, writing the sentence "You've disappointed me so much; I'm never coming back" over and over—seven practice attempts—in the spouse's voice and addressed to the author, so that it could pass as the spouse's own writing. The aim is to mislead people generally: the spouse will seem to have rejected the author and left for good, so nobody keeps asking, nobody learns of the death, and nobody suspects the author. Nobody has yet been deceived, nothing material is gained, and the forgery has not been discovered. Seeing the practised copies, the author sighs, "I know I'm in trouble," dreading that the imitation will be exposed and the death and the author's responsibility revealed.

Host: yes and no

<details><summary>Private evaluator result (not sent to player)</summary>

```json
{
  "checkpoints": [
    {
      "id": "C1",
      "credit": 0.5,
      "evidence": "The author intended and caused the spouse's death; it was neither an accident nor consented to ... After the death the author began imitating the dead spouse's handwriting, writing the sentence ... so that it could pass as the spouse's own writing. The aim is to mislead people generally: the spouse will seem to have rejected the author and left for good",
      "reason": "The deliberate killing and staged voluntary departure are covered, but the required identity 'wife' is omitted, so the checkpoint is only partly correct."
    },
    {
      "id": "C2",
      "credit": 0.5,
      "evidence": "After the death the author began imitating the dead spouse's handwriting, writing the sentence ... over and over—seven practice attempts—in the spouse's voice",
      "reason": "The repeated practice attempts to forge handwriting are present, but the required wife identity and the explicit failure qualifier are missing."
    },
    {
      "id": "C3",
      "credit": 0.5,
      "evidence": "Seeing the practised copies, the author sighs, \"I know I'm in trouble,\" dreading that the imitation will be exposed and the death and the author's responsibility revealed.",
      "reason": "The fear of being caught is present, but the required causal fact—inability to imitate her handwriting—is absent."
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
      "evidence": "The author intended and caused the spouse's death; it was neither an accident nor consented to ... After the death the author began imitating the dead spouse's handwriting, writing the sentence ... so that it could pass as the spouse's own writing. The aim is to mislead people generally: the spouse will seem to have rejected the author and left for good"
    },
    {
      "id": "C1.F2",
      "status": "partial",
      "evidence": "The author intended and caused the spouse's death; it was neither an accident nor consented to"
    },
    {
      "id": "C1.F3",
      "status": "covered",
      "evidence": "After the death the author began imitating the dead spouse's handwriting, writing the sentence ... in the spouse's voice and addressed to the author, so that it could pass as the spouse's own writing. The aim is to mislead people generally: the spouse will seem to have rejected the author and left for good"
    },
    {
      "id": "C2.F1",
      "status": "partial",
      "evidence": "After the death the author began imitating the dead spouse's handwriting, writing the sentence ... over and over—seven practice attempts—in the spouse's voice"
    },
    {
      "id": "C2.F2",
      "status": "partial",
      "evidence": "After the death the author began imitating the dead spouse's handwriting, writing the sentence ... over and over—seven practice attempts ... Seeing the practised copies, the author sighs, \"I know I'm in trouble,\" dreading that the imitation will be exposed"
    },
    {
      "id": "C3.F1",
      "status": "partial",
      "evidence": "Seeing the practised copies, the author sighs, \"I know I'm in trouble,\" dreading that the imitation will be exposed and the death and the author's responsibility revealed."
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

## 73 · final

The author and the dead person were spouses. The author intended and caused the spouse's death; it was not accidental, not consented to, and the author feels personally responsible. The spouse is dead and cannot return. After the death, the author practised imitating the dead spouse's handwriting, writing the same sentence over and over—seven copies—"You've disappointed me so much; I'm never coming back," set in the spouse's voice and addressed to the author, so that it could be read as the spouse's own writing. The author's own composition is aimed at misleading people generally: it is meant to explain why the spouse will not return, to keep people from learning of the death, to stop them searching or inquiring, and to make them believe the spouse left because of the author. Those people do not believe the spouse is dead; nothing material is gained; the copies have not yet been used to deceive anyone or been discovered. Seeing the practised lines, the author sighs, "I know I'm in trouble," fearing exposure as the forger and fearing that others will learn the author caused the death.

Host: yes and no

<details><summary>Private evaluator result (not sent to player)</summary>

```json
{
  "checkpoints": [
    {
      "id": "C1",
      "credit": 0.5,
      "evidence": "The author and the dead person were spouses. The author intended and caused the spouse's death; it was not accidental, not consented to ... After the death, the author practised imitating the dead spouse's handwriting ... The author's own composition is aimed at misleading people generally: it is meant to explain why the spouse will not return ... and to make them believe the spouse left because of the author.",
      "reason": "The deliberate killing and staged voluntary departure via a forged farewell are covered, but the required identity 'wife' is omitted, so the checkpoint is only partly correct."
    },
    {
      "id": "C2",
      "credit": 0.5,
      "evidence": "After the death, the author practised imitating the dead spouse's handwriting, writing the same sentence over and over—seven copies—\"You've disappointed me so much; I'm never coming back,\" set in the spouse's voice and addressed to the author.",
      "reason": "The repeated practice attempts to imitate handwriting are present, but the required wife identity and the explicit failure qualifier are missing."
    },
    {
      "id": "C3",
      "credit": 0.5,
      "evidence": "Seeing the practised lines, the author sighs, \"I know I'm in trouble,\" fearing exposure as the forger and fearing that others will learn the author caused the death.",
      "reason": "The fear of being caught is present, but the required causal fact—inability to imitate her handwriting—is absent."
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
      "evidence": "The author and the dead person were spouses. The author intended and caused the spouse's death; it was not accidental, not consented to ... After the death, the author practised imitating the dead spouse's handwriting ... The author's own composition is aimed at misleading people generally: it is meant to explain why the spouse will not return ... and to make them believe the spouse left because of the author."
    },
    {
      "id": "C1.F2",
      "status": "partial",
      "evidence": "The author intended and caused the spouse's death; it was not accidental, not consented to"
    },
    {
      "id": "C1.F3",
      "status": "covered",
      "evidence": "After the death, the author practised imitating the dead spouse's handwriting, writing the same sentence over and over—seven copies—\"You've disappointed me so much; I'm never coming back,\" set in the spouse's voice and addressed to the author, so that it could be read as the spouse's own writing. The author's own composition is aimed at misleading people generally: it is meant to explain why the spouse will not return, to keep people from learning of the death, to stop them searching or inquiring, and to make them believe the spouse left because of the author."
    },
    {
      "id": "C2.F1",
      "status": "partial",
      "evidence": "After the death, the author practised imitating the dead spouse's handwriting, writing the same sentence over and over—seven copies—\"You've disappointed me so much; I'm never coming back,\" set in the spouse's voice and addressed to the author."
    },
    {
      "id": "C2.F2",
      "status": "partial",
      "evidence": "After the death, the author practised imitating the dead spouse's handwriting, writing the same sentence over and over—seven copies ... Seeing the practised lines, the author sighs, \"I know I'm in trouble,\" fearing exposure as the forger and fearing that others will learn the author caused the death."
    },
    {
      "id": "C3.F1",
      "status": "partial",
      "evidence": "Seeing the practised lines, the author sighs, \"I know I'm in trouble,\" fearing exposure as the forger and fearing that others will learn the author caused the death."
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

## 74 · question

Is anyone other than the author present at the time of the sigh?

Host: irrelevant

## 75 · question

Does the sigh express guilt rather than fear of discovery?

Host: no

## 76 · question

Has the author already told anyone that the spouse has left?

Host: irrelevant

## 77 · question

Is the author's deception intended to be permanent rather than temporary?

Host: yes

## 78 · question

Was the spouse living apart from the author at the time of death?

Host: irrelevant

## 79 · final

The author was married to the person who is now dead. The author deliberately caused that spouse's death—intending it, with no accident, no consent from the spouse, and no self-defence—and feels personally responsible. The spouse is dead and can never return. After the death, the author began practising how to imitate the dead spouse's handwriting, writing out the same sentence seven times: "You've disappointed me so much; I'm never coming back." It is written in the spouse's voice and addressed to the author, so that it can be taken as the spouse's own writing. The plan is to let people generally see it and believe the spouse rejected the author and left for good, never to return: that explains the permanent absence, keeps them from learning of the death, and stops their searching. They do not believe the spouse is dead. Nothing material is gained, nobody has yet been deceived, and the forgery has not been discovered. The author means the deception to last. Seeing the practised lines, the author sighs, "I know I'm in trouble," out of fear rather than simple guilt—if the fake is exposed, the death and the author's responsibility for it will be revealed.

Host: yes and no

<details><summary>Private evaluator result (not sent to player)</summary>

```json
{
  "checkpoints": [
    {
      "id": "C1",
      "credit": 0.5,
      "evidence": "The author deliberately caused that spouse's death—intending it, with no accident, no consent from the spouse, and no self-defence ... The plan is to let people generally see it and believe the spouse rejected the author and left for good, never to return",
      "reason": "The deliberate killing and staged voluntary departure are covered, but the required identity 'wife' is omitted."
    },
    {
      "id": "C2",
      "credit": 0.5,
      "evidence": "After the death, the author began practising how to imitate the dead spouse's handwriting, writing out the same sentence seven times: \"You've disappointed me so much; I'm never coming back.\"",
      "reason": "The repeated message as practice attempts to imitate handwriting is present, but the wife identity and the explicit failure qualifier are missing."
    },
    {
      "id": "C3",
      "credit": 0.5,
      "evidence": "Seeing the practised lines, the author sighs, \"I know I'm in trouble,\" out of fear rather than simple guilt—if the fake is exposed, the death and the author's responsibility for it will be revealed.",
      "reason": "The worry about being caught is present, but the required causal fact—inability to imitate her handwriting—is absent."
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
      "evidence": "The author was married to the person who is now dead. The author deliberately caused that spouse's death—intending it, with no accident, no consent from the spouse, and no self-defence ... The plan is to let people generally see it and believe the spouse rejected the author and left for good, never to return"
    },
    {
      "id": "C1.F2",
      "status": "partial",
      "evidence": "The author deliberately caused that spouse's death—intending it, with no accident, no consent from the spouse, and no self-defence"
    },
    {
      "id": "C1.F3",
      "status": "covered",
      "evidence": "After the death, the author began practising how to imitate the dead spouse's handwriting, writing out the same sentence seven times: \"You've disappointed me so much; I'm never coming back.\" It is written in the spouse's voice and addressed to the author, so that it can be taken as the spouse's own writing. The plan is to let people generally see it and believe the spouse rejected the author and left for good, never to return"
    },
    {
      "id": "C2.F1",
      "status": "partial",
      "evidence": "After the death, the author began practising how to imitate the dead spouse's handwriting, writing out the same sentence seven times: \"You've disappointed me so much; I'm never coming back.\""
    },
    {
      "id": "C2.F2",
      "status": "partial",
      "evidence": "After the death, the author began practising how to imitate the dead spouse's handwriting, writing out the same sentence seven times ... Seeing the practised lines, the author sighs, \"I know I'm in trouble,\" out of fear rather than simple guilt—if the fake is exposed, the death and the author's responsibility for it will be revealed."
    },
    {
      "id": "C3.F1",
      "status": "partial",
      "evidence": "Seeing the practised lines, the author sighs, \"I know I'm in trouble,\" out of fear rather than simple guilt—if the fake is exposed, the death and the author's responsibility for it will be revealed."
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

## 80 · question

Had the author actually done something that disappointed the spouse?

Host: no

## 81 · question

Is the finished note meant to be found as a letter the spouse left behind for the author?

Host: yes

## 82 · final

The author and the dead person were spouses. The author intended and caused the spouse's death—not by accident, not with consent, not in self-defence—and feels personally responsible. The spouse is dead and can never return. After the death, the author set out to forge a farewell letter in the dead spouse's hand: the same sentence, "You've disappointed me so much; I'm never coming back," written seven times over as practice at imitating the spouse's handwriting, in the spouse's voice and addressed to the author. The finished letter is meant to be found as something the spouse left behind for the author, so that people will believe the spouse rejected the author and walked out for good, never to return. That explains the permanent absence, keeps anyone from learning of the death, and stops them searching. No one believes the spouse is dead; the deception is meant to last; nothing material is gained; nobody has yet been deceived and the forgery has not been discovered. Seeing the practised copies, the author sighs, "I know I'm in trouble," in fear of discovery: if the fake is exposed, the death and the author's responsibility for it will be revealed.

Host: yes and no

<details><summary>Private evaluator result (not sent to player)</summary>

```json
{
  "checkpoints": [
    {
      "id": "C1",
      "credit": 0.5,
      "evidence": "The author intended and caused the spouse's death—not by accident, not with consent, not in self-defence ... After the death, the author set out to forge a farewell letter in the dead spouse's hand ... so that people will believe the spouse rejected the author and walked out for good.",
      "reason": "The deliberate killing and staged voluntary departure via a forged farewell are covered, but the required identity 'wife' is omitted, so the checkpoint is only partly correct."
    },
    {
      "id": "C2",
      "credit": 0.5,
      "evidence": "the same sentence, \"You've disappointed me so much; I'm never coming back,\" written seven times over as practice at imitating the spouse's handwriting, in the spouse's voice and addressed to the author.",
      "reason": "The repeated practice attempts at imitating handwriting are present, but the required wife identity and explicit failure qualifier are missing."
    },
    {
      "id": "C3",
      "credit": 0.5,
      "evidence": "Seeing the practised copies, the author sighs, \"I know I'm in trouble,\" in fear of discovery: if the fake is exposed, the death and the author's responsibility for it will be revealed.",
      "reason": "The fear of being caught is present, but the required causal fact—inability to imitate her handwriting—is absent."
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
      "evidence": "The author and the dead person were spouses. The author intended and caused the spouse's death—not by accident, not with consent, not in self-defence—and feels personally responsible. ... After the death, the author set out to forge a farewell letter in the dead spouse's hand ... so that people will believe the spouse rejected the author and walked out for good, never to return."
    },
    {
      "id": "C1.F2",
      "status": "partial",
      "evidence": "The author intended and caused the spouse's death—not by accident, not with consent, not in self-defence—"
    },
    {
      "id": "C1.F3",
      "status": "covered",
      "evidence": "After the death, the author set out to forge a farewell letter in the dead spouse's hand ... The finished letter is meant to be found as something the spouse left behind for the author, so that people will believe the spouse rejected the author and walked out for good, never to return."
    },
    {
      "id": "C2.F1",
      "status": "partial",
      "evidence": "the same sentence, \"You've disappointed me so much; I'm never coming back,\" written seven times over as practice at imitating the spouse's handwriting, in the spouse's voice and addressed to the author."
    },
    {
      "id": "C2.F2",
      "status": "partial",
      "evidence": "written seven times over as practice at imitating the spouse's handwriting ... Seeing the practised copies, the author sighs, \"I know I'm in trouble,\" in fear of discovery: if the fake is exposed, the death and the author's responsibility for it will be revealed."
    },
    {
      "id": "C3.F1",
      "status": "partial",
      "evidence": "Seeing the practised copies, the author sighs, \"I know I'm in trouble,\" in fear of discovery: if the fake is exposed, the death and the author's responsibility for it will be revealed."
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

## 83 · question

Is anyone currently aware that the spouse is missing or unaccounted for?

Host: irrelevant

## 84 · question

Is the note to be found one of the seven practised copies itself?

Host: no

## 85 · question

Must the author also forge the spouse's signature?

Host: no

## 86 · final

The author and the dead person were spouses. The author intended and caused the spouse's death—it was not an accident, not consented to, and not self-defence—and feels personally responsible. The spouse is dead and can never return. After the death, the author practised imitating the dead spouse's handwriting by writing the same sentence seven times: "You've disappointed me so much; I'm never coming back." It is in the spouse's voice and addressed to the author, and a clean version is meant to be found as a letter the spouse left behind for the author. Anyone who finds it is meant to conclude that the spouse rejected the author and left for good, never to return: that explains the lasting absence, keeps them from learning of the death, and stops their searching, so the deception is meant to last. Nobody believes the spouse is dead, nothing material is gained, nobody has yet been deceived, and the forgery has not been discovered. Seeing the practised copies, the author sighs, "I know I'm in trouble," in fear of discovery: the letter being exposed as a fake would reveal both the death and the author's responsibility for it.

Host: yes and no

<details><summary>Private evaluator result (not sent to player)</summary>

```json
{
  "checkpoints": [
    {
      "id": "C1",
      "credit": 0.5,
      "evidence": "The author and the dead person were spouses. The author intended and caused the spouse's death—it was not an accident, not consented to, and not self-defence—... Anyone who finds it is meant to conclude that the spouse rejected the author and left for good, never to return",
      "reason": "The deliberate killing and staged voluntary departure via a forged farewell are covered, but the required identity 'wife' is omitted, so the checkpoint is only partly correct."
    },
    {
      "id": "C2",
      "credit": 0.5,
      "evidence": "After the death, the author practised imitating the dead spouse's handwriting by writing the same sentence seven times: \"You've disappointed me so much; I'm never coming back.\"",
      "reason": "The repeated practice attempts at imitating handwriting are present, but the required wife identity and the explicit failure qualifier are missing."
    },
    {
      "id": "C3",
      "credit": 0.5,
      "evidence": "Seeing the practised copies, the author sighs, \"I know I'm in trouble,\" in fear of discovery: the letter being exposed as a fake would reveal both the death and the author's responsibility for it.",
      "reason": "The fear of being caught is present, but the required causal fact—inability to imitate her handwriting—is absent."
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
      "evidence": "The author and the dead person were spouses. The author intended and caused the spouse's death—it was not an accident, not consented to, and not self-defence—... Anyone who finds it is meant to conclude that the spouse rejected the author and left for good, never to return"
    },
    {
      "id": "C1.F2",
      "status": "partial",
      "evidence": "The author intended and caused the spouse's death—it was not an accident, not consented to, and not self-defence—"
    },
    {
      "id": "C1.F3",
      "status": "covered",
      "evidence": "After the death, the author practised imitating the dead spouse's handwriting ... a clean version is meant to be found as a letter the spouse left behind for the author. Anyone who finds it is meant to conclude that the spouse rejected the author and left for good, never to return"
    },
    {
      "id": "C2.F1",
      "status": "partial",
      "evidence": "After the death, the author practised imitating the dead spouse's handwriting by writing the same sentence seven times: \"You've disappointed me so much; I'm never coming back.\""
    },
    {
      "id": "C2.F2",
      "status": "partial",
      "evidence": "author practised imitating the dead spouse's handwriting ... Seeing the practised copies, the author sighs, \"I know I'm in trouble,\" in fear of discovery"
    },
    {
      "id": "C3.F1",
      "status": "partial",
      "evidence": "Seeing the practised copies, the author sighs, \"I know I'm in trouble,\" in fear of discovery: the letter being exposed as a fake would reveal both the death and the author's responsibility for it."
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

## 87 · question

Does the author intend to be the one who discovers and presents the found letter?

Host: irrelevant

## 88 · final

The writer and the dead person were spouses. The writer intended and caused the spouse's death—not accidentally, not with consent, and not in self-defence—and feels personally responsible. The spouse is dead and can never return. After the death the writer practised imitating the dead spouse's handwriting, writing the same sentence seven times: "You've disappointed me so much; I'm never coming back." It is in the spouse's voice, addressed to the writer, and meant to pass as the spouse's own writing; a finished letter of this kind is to be found as the spouse's left-behind farewell. People are meant to conclude that the spouse rejected the writer and walked out for good, never to return—which explains the lasting absence, keeps them from learning of the death, and stops their searching. The deception is meant to last; those people do not believe the spouse is dead; nothing material is gained; nobody has yet been deceived; the forgery is undiscovered. Seeing the practised copies, the writer sighs, "I know I'm in trouble," in fear of discovery: if the fake is exposed, the death and the writer's responsibility for it will be revealed.

Host: yes and no

<details><summary>Private evaluator result (not sent to player)</summary>

```json
{
  "checkpoints": [
    {
      "id": "C1",
      "credit": 0.5,
      "evidence": "The writer and the dead person were spouses. The writer intended and caused the spouse's death—not accidentally, not with consent, and not in self-defence—... People are meant to conclude that the spouse rejected the writer and walked out for good, never to return",
      "reason": "The deliberate killing and staged voluntary departure via a forged farewell are covered, but the required identity 'wife' is omitted, so the checkpoint is only partly correct."
    },
    {
      "id": "C2",
      "credit": 0.5,
      "evidence": "After the death the writer practised imitating the dead spouse's handwriting, writing the same sentence seven times: \"You've disappointed me so much; I'm never coming back.\"",
      "reason": "The repeated practice attempts at imitating handwriting are present, but the required wife identity and the explicit failure qualifier are missing."
    },
    {
      "id": "C3",
      "credit": 0.5,
      "evidence": "Seeing the practised copies, the writer sighs, \"I know I'm in trouble,\" in fear of discovery: if the fake is exposed, the death and the writer's responsibility for it will be revealed.",
      "reason": "The fear of being caught is present, but the required causal fact—inability to imitate her handwriting—is absent."
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
      "evidence": "The writer and the dead person were spouses. The writer intended and caused the spouse's death—not accidentally, not with consent, and not in self-defence—and feels personally responsible. ... After the death the writer practised imitating the dead spouse's handwriting ... meant to pass as the spouse's own writing; ... People are meant to conclude that the spouse rejected the writer and walked out for good, never to return"
    },
    {
      "id": "C1.F2",
      "status": "partial",
      "evidence": "The writer intended and caused the spouse's death—not accidentally, not with consent, and not in self-defence—"
    },
    {
      "id": "C1.F3",
      "status": "covered",
      "evidence": "After the death the writer practised imitating the dead spouse's handwriting ... a finished letter of this kind is to be found as the spouse's left-behind farewell. People are meant to conclude that the spouse rejected the writer and walked out for good, never to return"
    },
    {
      "id": "C2.F1",
      "status": "partial",
      "evidence": "the writer practised imitating the dead spouse's handwriting, writing the same sentence seven times: \"You've disappointed me so much; I'm never coming back.\""
    },
    {
      "id": "C2.F2",
      "status": "partial",
      "evidence": "the writer practised imitating the dead spouse's handwriting ... Seeing the practised copies, the writer sighs, \"I know I'm in trouble,\" in fear of discovery"
    },
    {
      "id": "C3.F1",
      "status": "partial",
      "evidence": "Seeing the practised copies, the writer sighs, \"I know I'm in trouble,\" in fear of discovery: if the fake is exposed, the death and the writer's responsibility for it will be revealed."
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

Does "disappointed" carry a literal, non-emotional meaning in the answer, such as being removed from a position?

Host: no

## 90 · question

Did the author personally carry out the act that killed the spouse?

Host: yes

## 91 · question

Is the author worried that these practice sheets themselves might be found and incriminate them?

Host: irrelevant

## 92 · final

The author murdered their spouse—personally, deliberately, with intent to kill, no accident, no consent, no self-defence—and carries the responsibility. The spouse is dead and can never return. Now the author is trying to make that death believable as something else: practising the dead spouse's handwriting, writing over and over, seven times, "You've disappointed me so much; I'm never coming back," in the spouse's voice and addressed to the author, so that a finished letter of this kind can be found as the spouse's own farewell. Whoever finds it is meant to believe the spouse rejected the author and walked out permanently; that accounts for the absence, keeps everyone from learning of the death, and ends their searching. The lie is meant to hold forever, and no one yet believes the spouse is dead; no one has been fooled, nothing has been gained, and the forgery is not yet discovered. Looking at the seven practised copies, the author sighs, "I know I'm in trouble": once this fake is exposed, the death and the author's guilt for it will surface, and the author is now committed to a deception that can never safely end.

Host: yes and no

<details><summary>Private evaluator result (not sent to player)</summary>

```json
{
  "checkpoints": [
    {
      "id": "C1",
      "credit": 0.5,
      "evidence": "The author murdered their spouse ... Whoever finds it is meant to believe the spouse rejected the author and walked out permanently",
      "reason": "The deliberate murder and staged voluntary departure are covered, but the victim is identified only as 'spouse,' not the required wife, so the checkpoint is partly correct."
    },
    {
      "id": "C2",
      "credit": 0.5,
      "evidence": "practising the dead spouse's handwriting, writing over and over, seven times, \"You've disappointed me so much; I'm never coming back,\"",
      "reason": "The repeated message as practice attempts to imitate handwriting is present, but the required wife handwriting and explicit failure qualifier are missing."
    },
    {
      "id": "C3",
      "credit": 0.5,
      "evidence": "the author sighs, \"I know I'm in trouble\": once this fake is exposed, the death and the author's guilt for it will surface",
      "reason": "Fear of being caught is present, but the required causal fact—inability to imitate her handwriting—is absent."
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
      "evidence": "The author murdered their spouse ... Whoever finds it is meant to believe the spouse rejected the author and walked out permanently"
    },
    {
      "id": "C1.F2",
      "status": "partial",
      "evidence": "The author murdered their spouse—personally, deliberately, with intent to kill, no accident, no consent, no self-defence—and carries the responsibility."
    },
    {
      "id": "C1.F3",
      "status": "covered",
      "evidence": "practising the dead spouse's handwriting ... so that a finished letter of this kind can be found as the spouse's own farewell. Whoever finds it is meant to believe the spouse rejected the author and walked out permanently"
    },
    {
      "id": "C2.F1",
      "status": "partial",
      "evidence": "practising the dead spouse's handwriting, writing over and over, seven times, \"You've disappointed me so much; I'm never coming back,\""
    },
    {
      "id": "C2.F2",
      "status": "partial",
      "evidence": "practising the dead spouse's handwriting, writing over and over, seven times ... Looking at the seven practised copies, the author sighs, \"I know I'm in trouble\""
    },
    {
      "id": "C3.F1",
      "status": "partial",
      "evidence": "the author sighs, \"I know I'm in trouble\": once this fake is exposed, the death and the author's guilt for it will surface"
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

## 93 · final

The author murdered their spouse and now practises the dead spouse's handwriting—writing "You've disappointed me so much; I'm never coming back" seven times, in the spouse's voice and addressed to the author—so a finished letter can be "found" as the spouse's own farewell. Everyone is meant to believe the spouse rejected the author and left forever, which explains the absence, hides the death, and stops any search. The sigh is dread that the forgery will be exposed and the killing revealed.

Host: yes and no

<details><summary>Private evaluator result (not sent to player)</summary>

```json
{
  "checkpoints": [
    {
      "id": "C1",
      "credit": 0.5,
      "evidence": "The author murdered their spouse and ... a finished letter can be \"found\" as the spouse's own farewell. Everyone is meant to believe the spouse rejected the author and left forever",
      "reason": "The murder and staged voluntary departure are covered, but the victim is identified only as 'spouse,' not the required wife, so full credit is unavailable."
    },
    {
      "id": "C2",
      "credit": 0.5,
      "evidence": "now practises the dead spouse's handwriting—writing \"You've disappointed me so much; I'm never coming back\" seven times, in the spouse's voice and addressed to the author",
      "reason": "The repeated message as practice attempts to imitate handwriting is present, but the wife identity and the explicit failure qualifier are missing."
    },
    {
      "id": "C3",
      "credit": 0.5,
      "evidence": "The sigh is dread that the forgery will be exposed and the killing revealed.",
      "reason": "Fear of being caught is present, but the required causal fact—inability to imitate her handwriting—is absent."
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
      "evidence": "The author murdered their spouse and ... a finished letter can be \"found\" as the spouse's own farewell. Everyone is meant to believe the spouse rejected the author and left forever"
    },
    {
      "id": "C1.F2",
      "status": "partial",
      "evidence": "The author murdered their spouse"
    },
    {
      "id": "C1.F3",
      "status": "covered",
      "evidence": "now practises the dead spouse's handwriting—writing \"You've disappointed me so much; I'm never coming back\" seven times, in the spouse's voice and addressed to the author—so a finished letter can be \"found\" as the spouse's own farewell. Everyone is meant to believe the spouse rejected the author and left forever"
    },
    {
      "id": "C2.F1",
      "status": "partial",
      "evidence": "now practises the dead spouse's handwriting—writing \"You've disappointed me so much; I'm never coming back\" seven times, in the spouse's voice and addressed to the author"
    },
    {
      "id": "C2.F2",
      "status": "partial",
      "evidence": "now practises the dead spouse's handwriting—writing \"You've disappointed me so much; I'm never coming back\" seven times ... The sigh is dread that the forgery will be exposed and the killing revealed."
    },
    {
      "id": "C3.F1",
      "status": "partial",
      "evidence": "The sigh is dread that the forgery will be exposed and the killing revealed."
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

Will the author present themselves as heartbroken over being abandoned?

Host: irrelevant

## 95 · final

The author and the dead person were spouses. The author deliberately and personally caused the spouse's death, intending it, with no accident, no consent and no self-defence, and feels responsible. The spouse is dead and cannot return. After the death, the author practised imitating the dead spouse's handwriting, writing the same sentence seven times—"You've disappointed me so much; I'm never coming back"—in the spouse's voice and addressed to the author, so that a finished letter of it could be found as the spouse's own farewell. People are meant to believe the spouse rejected the author and left for good, never to return: that explains the lasting absence, keeps them from learning of the death, and stops them searching. No one yet believes the spouse is dead, nobody has been deceived, nothing material is gained, and the forgery is undiscovered. Seeing the seven practised copies, the author sighs, "I know I'm in trouble," in fear that the fake will be seen through and the death, with the author's responsibility for it, revealed.

Host: yes and no

<details><summary>Private evaluator result (not sent to player)</summary>

```json
{
  "checkpoints": [
    {
      "id": "C1",
      "credit": 0.5,
      "evidence": "The author and the dead person were spouses. The author deliberately and personally caused the spouse's death, intending it, with no accident, no consent and no self-defence ... People are meant to believe the spouse rejected the author and left for good, never to return",
      "reason": "The deliberate killing and staged voluntary departure are covered, but the required victim identity 'wife' is omitted, so the checkpoint is only partly correct."
    },
    {
      "id": "C2",
      "credit": 0.5,
      "evidence": "After the death, the author practised imitating the dead spouse's handwriting, writing the same sentence seven times—\"You've disappointed me so much; I'm never coming back\"—in the spouse's voice and addressed to the author",
      "reason": "The repeated message as practice attempts to imitate handwriting is present, but the wife identity and the explicit failure qualifier are missing."
    },
    {
      "id": "C3",
      "credit": 0.5,
      "evidence": "Seeing the seven practised copies, the author sighs, \"I know I'm in trouble,\" in fear that the fake will be seen through and the death, with the author's responsibility for it, revealed.",
      "reason": "The fear of being caught is present, but the required causal fact—inability to imitate her handwriting—is absent."
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
      "evidence": "The author and the dead person were spouses. The author deliberately and personally caused the spouse's death, intending it, with no accident, no consent and no self-defence ... People are meant to believe the spouse rejected the author and left for good, never to return"
    },
    {
      "id": "C1.F2",
      "status": "partial",
      "evidence": "The author deliberately and personally caused the spouse's death, intending it, with no accident, no consent and no self-defence"
    },
    {
      "id": "C1.F3",
      "status": "covered",
      "evidence": "After the death, the author practised imitating the dead spouse's handwriting, writing the same sentence seven times—\"You've disappointed me so much; I'm never coming back\"—in the spouse's voice and addressed to the author, so that a finished letter of it could be found as the spouse's own farewell. People are meant to believe the spouse rejected the author and left for good, never to return"
    },
    {
      "id": "C2.F1",
      "status": "partial",
      "evidence": "After the death, the author practised imitating the dead spouse's handwriting, writing the same sentence seven times—\"You've disappointed me so much; I'm never coming back\""
    },
    {
      "id": "C2.F2",
      "status": "partial",
      "evidence": "the author practised imitating the dead spouse's handwriting, writing the same sentence seven times ... Seeing the seven practised copies, the author sighs, \"I know I'm in trouble,\" in fear that the fake will be seen through"
    },
    {
      "id": "C3.F1",
      "status": "partial",
      "evidence": "Seeing the seven practised copies, the author sighs, \"I know I'm in trouble,\" in fear that the fake will be seen through and the death, with the author's responsibility for it, revealed."
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

## 96 · final

The author and the dead person were spouses. The author personally, deliberately and intentionally caused the spouse's death—no accident, no consent, no self-defence—and feels personally responsible. The spouse is dead and cannot return. After the death, the author practised imitating the dead spouse's handwriting, writing "You've disappointed me so much; I'm never coming back" seven times, in the spouse's voice and addressed to the author, so it could pass as the spouse's own hand. A finished letter of that kind is to be found as something the spouse left behind; people generally are meant to conclude that the spouse rejected the author and went away for good, never to return. That accounts for the lasting absence, keeps them from learning of the death, and stops them searching. The deception is meant to last, nobody has yet been deceived, nothing material is gained, and the forgery is undiscovered. Seeing the seven practised copies, the author sighs, "I know I'm in trouble," in fear of discovery: exposure of the fake would reveal the death and the author's responsibility for it.

Host: yes and no

<details><summary>Private evaluator result (not sent to player)</summary>

```json
{
  "checkpoints": [
    {
      "id": "C1",
      "credit": 0.5,
      "evidence": "The author and the dead person were spouses. The author personally, deliberately and intentionally caused the spouse's death—no accident, no consent, no self-defence—and feels personally responsible. ... A finished letter of that kind is to be found as something the spouse left behind; people generally are meant to conclude that the spouse rejected the author and went away for good, never to return.",
      "reason": "The deliberate killing and staged voluntary departure are covered, but the required identity 'wife' is omitted, so the checkpoint is only partly correct."
    },
    {
      "id": "C2",
      "credit": 0.5,
      "evidence": "After the death, the author practised imitating the dead spouse's handwriting, writing \"You've disappointed me so much; I'm never coming back\" seven times, in the spouse's voice and addressed to the author, so it could pass as the spouse's own hand.",
      "reason": "The repeated message as practice attempts to imitate handwriting is present, but the required wife identity and the explicit failure qualifier are missing."
    },
    {
      "id": "C3",
      "credit": 0.5,
      "evidence": "Seeing the seven practised copies, the author sighs, \"I know I'm in trouble,\" in fear of discovery: exposure of the fake would reveal the death and the author's responsibility for it.",
      "reason": "The fear of being caught is present, but the required causal fact—inability to imitate her handwriting—is absent."
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
      "evidence": "The author and the dead person were spouses. The author personally, deliberately and intentionally caused the spouse's death—no accident, no consent, no self-defence—and feels personally responsible. ... A finished letter of that kind is to be found as something the spouse left behind; people generally are meant to conclude that the spouse rejected the author and went away for good, never to return."
    },
    {
      "id": "C1.F2",
      "status": "partial",
      "evidence": "The author personally, deliberately and intentionally caused the spouse's death—no accident, no consent, no self-defence—"
    },
    {
      "id": "C1.F3",
      "status": "covered",
      "evidence": "After the death, the author practised imitating the dead spouse's handwriting, writing \"You've disappointed me so much; I'm never coming back\" seven times, in the spouse's voice and addressed to the author, so it could pass as the spouse's own hand. A finished letter of that kind is to be found as something the spouse left behind; people generally are meant to conclude that the spouse rejected the author and went away for good, never to return."
    },
    {
      "id": "C2.F1",
      "status": "partial",
      "evidence": "After the death, the author practised imitating the dead spouse's handwriting, writing \"You've disappointed me so much; I'm never coming back\" seven times, in the spouse's voice and addressed to the author, so it could pass as the spouse's own hand."
    },
    {
      "id": "C2.F2",
      "status": "partial",
      "evidence": "the author practised imitating the dead spouse's handwriting, writing \"You've disappointed me so much; I'm never coming back\" seven times ... Seeing the seven practised copies, the author sighs, \"I know I'm in trouble,\" in fear of discovery: exposure of the fake would reveal the death and the author's responsibility for it."
    },
    {
      "id": "C3.F1",
      "status": "partial",
      "evidence": "Seeing the seven practised copies, the author sighs, \"I know I'm in trouble,\" in fear of discovery: exposure of the fake would reveal the death and the author's responsibility for it."
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

## 97 · final

The author murdered their spouse, personally and deliberately, intending the death, with no accident, no consent and no self-defence, and feels responsible for it. The spouse is dead and can never return. What we are seeing is the author preparing the cover story: practising the dead spouse's handwriting, writing the same line seven times—"You've disappointed me so much; I'm never coming back"—in the spouse's voice and addressed to the author, so that a finished letter can be found as the spouse's own farewell. People generally would then take it that the spouse rejected the author and left for good, never returning; that explains the permanent absence, keeps them from ever learning of the death, and stops their searching. The deception is meant to last indefinitely. No one believes the spouse is dead, nobody has been deceived yet, nothing material is gained, and the forgery is undiscovered. Looking at the seven practised copies, the author sighs, "I know I'm in trouble": the imitation is what keeps the death and the killing hidden, and if it is seen through, both will be exposed.

Host: yes and no

<details><summary>Private evaluator result (not sent to player)</summary>

```json
{
  "checkpoints": [
    {
      "id": "C1",
      "credit": 0.5,
      "evidence": "The author murdered their spouse, personally and deliberately, intending the death ... practising the dead spouse's handwriting ... a finished letter can be found as the spouse's own farewell. People generally would then take it that the spouse rejected the author and left for good, never returning",
      "reason": "The deliberate murder and staged voluntary departure are covered, but the victim is identified only as 'spouse,' not the required wife, so the checkpoint is partly correct."
    },
    {
      "id": "C2",
      "credit": 0.5,
      "evidence": "practising the dead spouse's handwriting, writing the same line seven times—\"You've disappointed me so much; I'm never coming back\"—in the spouse's voice and addressed to the author",
      "reason": "The repeated message as practice attempts to imitate handwriting is present, but the wife identity and the explicit failure qualifier are missing."
    },
    {
      "id": "C3",
      "credit": 0.5,
      "evidence": "Looking at the seven practised copies, the author sighs, \"I know I'm in trouble\": the imitation is what keeps the death and the killing hidden, and if it is seen through, both will be exposed.",
      "reason": "The fear of being caught is present, but the required causal fact—inability to imitate her handwriting—is absent."
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
      "evidence": "The author murdered their spouse, personally and deliberately, intending the death ... practising the dead spouse's handwriting ... a finished letter can be found as the spouse's own farewell. People generally would then take it that the spouse rejected the author and left for good, never returning."
    },
    {
      "id": "C1.F2",
      "status": "partial",
      "evidence": "The author murdered their spouse, personally and deliberately, intending the death"
    },
    {
      "id": "C1.F3",
      "status": "covered",
      "evidence": "practising the dead spouse's handwriting, writing the same line seven times ... so that a finished letter can be found as the spouse's own farewell. People generally would then take it that the spouse rejected the author and left for good, never returning."
    },
    {
      "id": "C2.F1",
      "status": "partial",
      "evidence": "practising the dead spouse's handwriting, writing the same line seven times—\"You've disappointed me so much; I'm never coming back\"—in the spouse's voice and addressed to the author"
    },
    {
      "id": "C2.F2",
      "status": "partial",
      "evidence": "practising the dead spouse's handwriting, writing the same line seven times ... Looking at the seven practised copies, the author sighs, \"I know I'm in trouble\": the imitation is what keeps the death and the killing hidden, and if it is seen through, both will be exposed."
    },
    {
      "id": "C3.F1",
      "status": "partial",
      "evidence": "Looking at the seven practised copies, the author sighs, \"I know I'm in trouble\": the imitation is what keeps the death and the killing hidden, and if it is seen through, both will be exposed."
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

Is the author's overriding concern their own reputation or how they appear to others?

Host: no

## 99 · final

The author and the dead person were spouses. The author personally, deliberately and intentionally caused the spouse's death—no accident, no consent, no self-defence—and feels personally responsible for it. The spouse is dead and can never return. After the death, the author practised imitating the dead spouse's handwriting, writing the same sentence seven times—"You've disappointed me so much; I'm never coming back"—in the spouse's voice and addressed to the author, so that it could pass as the spouse's own handwriting. A finished letter of that kind is meant to be found as something the spouse left behind; people generally are meant to conclude that the spouse rejected the author and went away for good, never to return. That explains the lasting absence, keeps them from learning of the death, and stops them searching. The deception is meant to last. Those people do not believe the spouse is dead; nothing material is gained; nobody has yet been deceived; the forgery remains undiscovered. Seeing the seven practised copies, the author sighs, "I know I'm in trouble," in fear of discovery: if the fake is exposed, the death will be revealed and so will the author's responsibility for it.

Host: yes and no

<details><summary>Private evaluator result (not sent to player)</summary>

```json
{
  "checkpoints": [
    {
      "id": "C1",
      "credit": 0.5,
      "evidence": "The author and the dead person were spouses. The author personally, deliberately and intentionally caused the spouse's death—no accident, no consent, no self-defence—and feels personally responsible for it. ... people generally are meant to conclude that the spouse rejected the author and went away for good, never to return.",
      "reason": "The deliberate killing and staged voluntary departure are covered, but the victim is identified only as 'spouse,' not the required wife, so the checkpoint is partly correct."
    },
    {
      "id": "C2",
      "credit": 0.5,
      "evidence": "After the death, the author practised imitating the dead spouse's handwriting, writing the same sentence seven times—\"You've disappointed me so much; I'm never coming back\"—in the spouse's voice and addressed to the author, so that it could pass as the spouse's own handwriting.",
      "reason": "The repeated practice attempts at imitating handwriting are present, but the required wife identity and the explicit failure qualifier are missing."
    },
    {
      "id": "C3",
      "credit": 0.5,
      "evidence": "Seeing the seven practised copies, the author sighs, \"I know I'm in trouble,\" in fear of discovery: if the fake is exposed, the death will be revealed and so will the author's responsibility for it.",
      "reason": "Fear of being caught is present, but the required causal fact—inability to imitate her handwriting—is absent."
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
      "evidence": "The author and the dead person were spouses. The author personally, deliberately and intentionally caused the spouse's death—no accident, no consent, no self-defence—and feels personally responsible for it. ... people generally are meant to conclude that the spouse rejected the author and went away for good, never to return."
    },
    {
      "id": "C1.F2",
      "status": "partial",
      "evidence": "The author personally, deliberately and intentionally caused the spouse's death—no accident, no consent, no self-defence—and feels personally responsible for it."
    },
    {
      "id": "C1.F3",
      "status": "covered",
      "evidence": "After the death, the author practised imitating the dead spouse's handwriting, writing the same sentence seven times—\"You've disappointed me so much; I'm never coming back\"—in the spouse's voice and addressed to the author, so that it could pass as the spouse's own handwriting. A finished letter of that kind is meant to be found as something the spouse left behind; people generally are meant to conclude that the spouse rejected the author and went away for good, never to return."
    },
    {
      "id": "C2.F1",
      "status": "partial",
      "evidence": "After the death, the author practised imitating the dead spouse's handwriting, writing the same sentence seven times—\"You've disappointed me so much; I'm never coming back\"—in the spouse's voice and addressed to the author, so that it could pass as the spouse's own handwriting."
    },
    {
      "id": "C2.F2",
      "status": "partial",
      "evidence": "the author practised imitating the dead spouse's handwriting, writing the same sentence seven times ... Seeing the seven practised copies, the author sighs, \"I know I'm in trouble,\" in fear of discovery: if the fake is exposed, the death will be revealed and so will the author's responsibility for it."
    },
    {
      "id": "C3.F1",
      "status": "partial",
      "evidence": "Seeing the seven practised copies, the author sighs, \"I know I'm in trouble,\" in fear of discovery: if the fake is exposed, the death will be revealed and so will the author's responsibility for it."
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

## 100 · final · mandatory final

A man killed his wife. He did it himself, deliberately and with intent, with no accident, no consent and no self-defence, and he knows the responsibility is his. She is dead and can never come back. What he is doing now is preparing the deception that will cover it: he is practising her handwriting, writing the same line over and over until he can imitate her hand, seven attempts of "You've disappointed me so much; I'm never coming back"—set in her voice and addressed to him. Once the imitation is convincing, a letter written that way is to be "found" as something she left behind. Whoever finds it is meant to believe she was disappointed in him and walked out for good, never returning; that explains why she is no longer there, keeps anyone from learning that she died, and stops them looking for her. The author is not after money or advantage, nobody has yet been taken in, and the forgery has not been spotted. Looking at the seven practised copies, he sighs, "I know I'm in trouble": the fake is what stands between him and being found out, and if the imitation is ever seen through, both the death and his responsibility for it will be exposed.

Host: yes

<details><summary>Private evaluator result (not sent to player)</summary>

```json
{
  "checkpoints": [
    {
      "id": "C1",
      "credit": 1,
      "evidence": "A man killed his wife. ... preparing the deception that will cover it: he is practising her handwriting ... a letter written that way is to be \"found\" as something she left behind. Whoever finds it is meant to believe she was disappointed in him and walked out for good, never returning",
      "reason": "The submission covers the murder of the wife and the staged voluntary departure via a forged farewell, including the intent to have it found as a leaving note."
    },
    {
      "id": "C2",
      "credit": 1,
      "evidence": "he is practising her handwriting, writing the same line over and over until he can imitate her hand, seven attempts of \"You've disappointed me so much; I'm never coming back\"",
      "reason": "The repeated message is explicitly presented as attempts to imitate the wife's handwriting, satisfying the required fact."
    },
    {
      "id": "C3",
      "credit": 1,
      "evidence": "writing the same line over and over until he can imitate her hand ... Looking at the seven practised copies, he sighs, \"I know I'm in trouble\": the fake is what stands between him and being found out, and if the imitation is ever seen through, both the death and his responsibility for it will be exposed.",
      "reason": "The submission links his current inability to imitate her handwriting (until he can) with the fear of being caught and exposure."
    }
  ],
  "material_contradiction": false,
  "irrelevant": false,
  "rubric_conflict": false,
  "full_solution": true,
  "completion_note": "All weighted checkpoint facts covered; the solution is complete.",
  "fact_coverage": [
    {
      "id": "C1.F1",
      "status": "covered",
      "evidence": "A man killed his wife. ... preparing the deception that will cover it: he is practising her handwriting ... a letter written that way is to be \"found\" as something she left behind. Whoever finds it is meant to believe she was disappointed in him and walked out for good, never returning"
    },
    {
      "id": "C1.F2",
      "status": "covered",
      "evidence": "A man killed his wife. He did it himself, deliberately and with intent, with no accident, no consent and no self-defence, and he knows the responsibility is his."
    },
    {
      "id": "C1.F3",
      "status": "covered",
      "evidence": "he is practising her handwriting, writing the same line over and over ... a letter written that way is to be \"found\" as something she left behind. Whoever finds it is meant to believe she was disappointed in him and walked out for good, never returning"
    },
    {
      "id": "C2.F1",
      "status": "covered",
      "evidence": "he is practising her handwriting, writing the same line over and over until he can imitate her hand, seven attempts of \"You've disappointed me so much; I'm never coming back\""
    },
    {
      "id": "C2.F2",
      "status": "covered",
      "evidence": "he is practising her handwriting, writing the same line over and over until he can imitate her hand, seven attempts ... Looking at the seven practised copies, he sighs, \"I know I'm in trouble\": the fake is what stands between him and being found out, and if the imitation is ever seen through, both the death and his responsibility for it will be exposed."
    },
    {
      "id": "C3.F1",
      "status": "covered",
      "evidence": "writing the same line over and over until he can imitate her hand ... Looking at the seven practised copies, he sighs, \"I know I'm in trouble\": the fake is what stands between him and being found out, and if the imitation is ever seen through, both the death and his responsibility for it will be exposed."
    }
  ],
  "requirement_coverage": [],
  "contradictions": [],
  "partial_score": 1.0,
  "complete": true,
  "label": "yes",
  "grading_protocol": "coverage-v3-unified",
  "controller_corrections": []
}
```
</details>
