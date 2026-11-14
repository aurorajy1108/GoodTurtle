# Turtle Soup trajectory

Over a smartphone, a daughter begs for a life to be spared and a kidnapper shouts: bring one hundred million yen alone by noon tomorrow, or this hostage dies; no police. Hearing the demand, her father decides the ransom should not be paid. Why?

Status: completed | counted questions: 100 | submissions: 100 | final partial score: 0.475

[Token usage and estimated costs](token_costs.csv)

## 1 · final

The father refuses to pay because paying would not save his daughter: the call is not a real kidnapping but a scam in which the “daughter’s” voice is fabricated or the caller is an impostor. He recognizes the demand as an extortion attempt and decides not to hand over the money.

Host: no

<details><summary>Private evaluator result (not sent to player)</summary>

```json
{
  "checkpoints": [
    {
      "id": "C1",
      "credit": 0,
      "evidence": "the call is not a real kidnapping but a scam in which the “daughter’s” voice is fabricated or the caller is an impostor",
      "reason": "Directly contradicts the required father-as-hostage and free-daughter-receives-the-call roles by asserting the call is not a real kidnapping and the daughter’s voice is fabricated."
    },
    {
      "id": "C2",
      "credit": 0,
      "evidence": "The father refuses to pay because paying would not save his daughter: the call is not a real kidnapping but a scam",
      "reason": "Omits the required conditional fear that the daughter’s arrival with the ransom alone may get both killed to eliminate witnesses; the scam explanation is a central incompatible alternative."
    },
    {
      "id": "C3",
      "credit": 0,
      "evidence": "He recognizes the demand as an extortion attempt and decides not to hand over the money.",
      "reason": "Does not state refusal to protect the daughter or communication not to pay/come; instead gives an incompatible fraud/extortion motive."
    },
    {
      "id": "C4",
      "credit": 0,
      "evidence": "",
      "reason": "No mention or entailment that the daughter is wealthy."
    },
    {
      "id": "C5",
      "credit": 0,
      "evidence": "",
      "reason": "No mention or entailment that the daughter is his only family."
    }
  ],
  "material_contradiction": true,
  "irrelevant": false,
  "rubric_conflict": false,
  "full_solution": false,
  "completion_note": "The submission asserts the call is not a real kidnapping but a scam with a fabricated daughter voice/impostor, directly contradicting the canonical account that the father is the hostage and his free daughter receives the call. It omits the required conditional fear of witness killing, protective refusal/communication and acceptance of personal risk, and the wealth/only-family details.",
  "fact_coverage": [
    {
      "id": "C1.F1",
      "status": "contradicted",
      "evidence": "the call is not a real kidnapping but a scam"
    },
    {
      "id": "C1.F2",
      "status": "contradicted",
      "evidence": "the “daughter’s” voice is fabricated or the caller is an impostor"
    },
    {
      "id": "C2.F1",
      "status": "contradicted",
      "evidence": "The father refuses to pay because paying would not save his daughter: the call is not a real kidnapping but a scam"
    },
    {
      "id": "C3.F1",
      "status": "contradicted",
      "evidence": "He recognizes the demand as an extortion attempt and decides not to hand over the money."
    },
    {
      "id": "C3.F2",
      "status": "missing",
      "evidence": ""
    },
    {
      "id": "C4.F1",
      "status": "missing",
      "evidence": ""
    },
    {
      "id": "C5.F1",
      "status": "missing",
      "evidence": ""
    }
  ],
  "requirement_coverage": [
    {
      "id": "R1",
      "status": "contradicted",
      "evidence": "the call is not a real kidnapping but a scam"
    },
    {
      "id": "R2",
      "status": "contradicted",
      "evidence": "the “daughter’s” voice is fabricated or the caller is an impostor"
    },
    {
      "id": "R3",
      "status": "contradicted",
      "evidence": "The father refuses to pay because paying would not save his daughter: the call is not a real kidnapping but a scam"
    },
    {
      "id": "R4",
      "status": "contradicted",
      "evidence": "He recognizes the demand as an extortion attempt and decides not to hand over the money."
    },
    {
      "id": "R5",
      "status": "missing",
      "evidence": ""
    },
    {
      "id": "R6",
      "status": "missing",
      "evidence": ""
    },
    {
      "id": "R7",
      "status": "missing",
      "evidence": ""
    }
  ],
  "contradictions": [
    {
      "quote": "the call is not a real kidnapping but a scam in which the “daughter’s” voice is fabricated or the caller is an impostor",
      "reference": "The father is the kidnapped hostage; his daughter is free and receives the ransom call.",
      "checkpoint_ids": [
        "C1"
      ]
    },
    {
      "quote": "The father refuses to pay because paying would not save his daughter: the call is not a real kidnapping but a scam",
      "reference": "He fears that if his daughter brings the ransom alone, both of them may be killed to eliminate witnesses.",
      "checkpoint_ids": [
        "C2"
      ]
    },
    {
      "quote": "He recognizes the demand as an extortion attempt and decides not to hand over the money.",
      "reference": "He refuses the ransom to protect his daughter.",
      "checkpoint_ids": [
        "C3"
      ]
    }
  ],
  "partial_score": 0.0,
  "complete": false,
  "label": "no",
  "grading_protocol": "coverage-v2",
  "controller_corrections": [],
  "completion_policy": "rubric_aligned_v1"
}
```
</details>

## 2 · question

Is the daughter actually being held hostage?

Host: no

## 3 · question

Is the father able to pay the ransom?

Host: yes

## 4 · question

Is the father present with his daughter at the time of the call?

Host: no

## 5 · question

Does the father know where his daughter is at the time of the call?

Host: irrelevant

## 6 · question

Does the daughter herself want the ransom not to be paid?

Host: irrelevant

## 7 · question

Does the father suspect the caller is not actually a kidnapper?

Host: no

## 8 · question

Is the daughter in on the kidnapping plot?

Host: no

## 9 · question

Does the father believe paying the ransom would not result in his daughter's release?

Host: no

## 10 · question

Does the father's decision relate to the money itself—such as where it came from or what paying it would cause?

Host: yes

## 11 · question

Would paying the ransom require the father to commit a crime?

Host: no

## 12 · question

Is the father unable to gather the full ransom money in time?

Host: no

## 13 · question

Does the father believe that paying the ransom would cause harm beyond the loss of money?

Host: yes

## 14 · question

Would paying the ransom bring harm to someone other than the daughter?

Host: yes

## 15 · question

Would the harm from paying fall on other members of the father's family?

Host: no

## 16 · question

Does the father worry that paying one ransom would encourage further kidnappings or extortion?

Host: no

## 17 · question

Is the father a public official or someone whose paying a ransom would enable a criminal or terrorist group?

Host: no

## 18 · question

Would the ransom money, if paid, be needed to pay for the daughter's own medical treatment or survival?

Host: no

## 19 · question

Is the father himself the intended victim of a trap set by the kidnapper?

Host: no

## 20 · question

Is the father's refusal based on knowing the kidnapper's identity or motive?

Host: no

## 21 · question

Would paying the ransom cause financial ruin that would harm the daughter's future?

Host: irrelevant

## 22 · question

Does the father believe the kidnapper will harm the daughter regardless of whether the ransom is paid?

Host: no

## 23 · question

Does the father's decision protect someone who is also being threatened by the kidnapper?

Host: no

## 24 · question

Would paying the ransom put the father himself in danger?

Host: yes

## 25 · question

Would the danger to the father come during the act of delivering the money?

Host: yes

## 26 · question

Is the danger during delivery because the kidnapper intends to kill or capture the father when he brings the money?

Host: no

## 27 · question

Is the delivery dangerous because the police must be avoided and the father would be acting alone against armed criminals?

Host: no

## 28 · question

Would the father be endangered because the money is being used as bait to catch the kidnapper?

Host: no

## 29 · question

Is the money itself dangerous to possess or deliver—for example, stolen, marked, or otherwise traceable?

Host: no

## 30 · question

Does the father plan to involve the police despite the "no police" warning?

Host: no

## 31 · question

Is the danger to the father related to where he must go or to whom he must meet to deliver the money?

Host: no

## 32 · question

Is the danger to the father caused by the kidnapper having leverage over him—such as a threat to accuse or expose him—if he delivers the money?

Host: no

## 33 · question

Is the father's own health or physical condition a reason that delivering the money would endanger him?

Host: no

## 34 · question

Is the danger to the father caused by another criminal or third party who would target him once he is known to have access to such a large sum?

Host: no

## 35 · question

Is the father endangered because the ransom money is not actually his own money?

Host: no

## 36 · question

Is the father's refusal based on a mistaken belief—that is, does he wrongly think paying would endanger him?

Host: no

## 37 · question

Does the "no police" condition itself create the danger—so that if he paid without police the kidnapper would be free to harm him, but involving police would be safer?

Host: no

## 38 · question

Is the danger to the father a consequence of the money being physically heavy or bulky to transport?

Host: no

## 39 · question

Would the father have to obtain the money by doing something dangerous, such as withdrawing it from a location that exposes him?

Host: no

## 40 · question

Is the father's decision influenced by the fact that his daughter is an adult or otherwise independent?

Host: no

## 41 · question

Is the father a police officer or otherwise officially forbidden from paying ransoms?

Host: irrelevant

## 42 · question

Would the father's act of paying the ransom expose a secret that would endanger him?

Host: no

## 43 · question

Does the father have a genuine reason to believe his daughter is already dead?

Host: no

## 44 · question

Is the father's refusal because paying the ransom would violate a principle or agreement he values more than his daughter's life?

Host: no

## 45 · question

Is the "danger to the father" actually a danger of being arrested or detained?

Host: no

## 46 · question

Is the father physically unable to deliver the money, such as being hospitalized or disabled?

Host: yes

## 47 · question

Is the father hospitalized at the time of the call?

Host: no

## 48 · question

Would delivering the money physically endanger the father's life because of his health condition?

Host: no

## 49 · question

Is the father disabled in a way that prevents him from traveling to deliver the ransom?

Host: no

## 50 · question

Does the father's physical condition mean that someone else would have to deliver the money in his place?

Host: yes

## 51 · question

Is the father bedridden or otherwise unable to leave home?

Host: irrelevant

## 52 · question

Would the person who must deliver the money in the father's place be someone the father wants to protect from danger?

Host: yes

## 53 · question

Is the person who would have to deliver the money the daughter herself?

Host: yes

## 54 · question

Is the father's decision a way of refusing to let his daughter take on the dangerous task of delivering the ransom?

Host: yes

## 55 · question

Is the daughter the one making the delivery because the father cannot, and would she be endangered by doing so?

Host: yes

## 56 · final

The father is physically unable to leave and deliver the ransom himself. His daughter is the person able to carry the money to the kidnapper. Paying would therefore require sending his daughter into the dangerous delivery, so instead of exposing her to that danger he decides the ransom should not be paid.

Host: yes and no

<details><summary>Private evaluator result (not sent to player)</summary>

```json
{
  "checkpoints": [
    {
      "id": "C1",
      "credit": 0.5,
      "evidence": "The father is physically unable to leave and deliver the ransom himself. His daughter is the person able to carry the money to the kidnapper.",
      "reason": "Identifies the father as unable to leave, implying he is the hostage, but omits that the daughter is free and receives the ransom call."
    },
    {
      "id": "C2",
      "credit": 0.5,
      "evidence": "Paying would therefore require sending his daughter into the dangerous delivery, so instead of exposing her to that danger he decides the ransom should not be paid.",
      "reason": "Danger to the daughter is identified, but the alone-arrival, witness-elimination, and both-person fear are incomplete."
    },
    {
      "id": "C3",
      "credit": 0.5,
      "evidence": "so instead of exposing her to that danger he decides the ransom should not be paid.",
      "reason": "Protective refusal is identified, but communication that she must not pay or come and acceptance of danger to his own life are omitted."
    },
    {
      "id": "C4",
      "credit": 0,
      "evidence": "",
      "reason": "No mention or entailment that the daughter is wealthy."
    },
    {
      "id": "C5",
      "credit": 0,
      "evidence": "",
      "reason": "No mention or entailment that the daughter is his only family."
    }
  ],
  "material_contradiction": false,
  "irrelevant": false,
  "rubric_conflict": false,
  "full_solution": false,
  "completion_note": "The submitted explanation captures a protective refusal based on the danger of sending the daughter to the delivery and implies the father cannot leave, consistent with his being the hostage. However, it omits that the daughter is free and received the ransom call, the specific conditional fear that both may be killed to eliminate witnesses if she arrives alone, explicit communication that she must not pay or come and acceptance of his own risk, and that the daughter is wealthy and his only family.",
  "fact_coverage": [
    {
      "id": "C1.F1",
      "status": "covered",
      "evidence": "The father is physically unable to leave and deliver the ransom himself"
    },
    {
      "id": "C1.F2",
      "status": "missing",
      "evidence": ""
    },
    {
      "id": "C2.F1",
      "status": "partial",
      "evidence": "Paying would therefore require sending his daughter into the dangerous delivery, so instead of exposing her to that danger he decides the ransom should not be paid."
    },
    {
      "id": "C3.F1",
      "status": "covered",
      "evidence": "so instead of exposing her to that danger he decides the ransom should not be paid."
    },
    {
      "id": "C3.F2",
      "status": "missing",
      "evidence": ""
    },
    {
      "id": "C4.F1",
      "status": "missing",
      "evidence": ""
    },
    {
      "id": "C5.F1",
      "status": "missing",
      "evidence": ""
    }
  ],
  "requirement_coverage": [
    {
      "id": "R1",
      "status": "covered",
      "evidence": "The father is physically unable to leave and deliver the ransom himself"
    },
    {
      "id": "R2",
      "status": "missing",
      "evidence": ""
    },
    {
      "id": "R3",
      "status": "partial",
      "evidence": "Paying would therefore require sending his daughter into the dangerous delivery, so instead of exposing her to that danger he decides the ransom should not be paid."
    },
    {
      "id": "R4",
      "status": "covered",
      "evidence": "so instead of exposing her to that danger he decides the ransom should not be paid."
    },
    {
      "id": "R5",
      "status": "missing",
      "evidence": ""
    },
    {
      "id": "R6",
      "status": "missing",
      "evidence": ""
    },
    {
      "id": "R7",
      "status": "missing",
      "evidence": ""
    }
  ],
  "contradictions": [],
  "partial_score": 0.475,
  "complete": false,
  "label": "yes and no",
  "grading_protocol": "coverage-v2",
  "controller_corrections": [],
  "completion_policy": "rubric_aligned_v1"
}
```
</details>

## 57 · question

Is the daughter the hostage being held by the kidnapper?

Host: no

## 58 · question

Is the person begging over the phone the daughter speaking on the kidnapper's behalf to relay the demand, rather than herself being the captive?

Host: no

## 59 · question

Is someone other than the daughter the actual hostage?

Host: yes

## 60 · question

Is the hostage someone the daughter cares about, so that the daughter is the one relaying the kidnapper's demand?

Host: yes and no

## 61 · question

Is the hostage the daughter's boyfriend or husband?

Host: no

## 62 · question

Is the hostage the daughter's child?

Host: no

## 63 · question

Is the hostage a friend of the daughter?

Host: no

## 64 · question

Is the hostage the father's own child other than the daughter?

Host: no

## 65 · question

Is the hostage the daughter's mother?

Host: no

## 66 · question

Is the daughter unrelated to the hostage, with the daughter instead being an accomplice or intermediary for the kidnapper?

Host: no

## 67 · question

Is the hostage the daughter's sibling?

Host: no

## 68 · question

Is the hostage a pet or animal that the daughter cares about?

Host: no

## 69 · question

Is the hostage the kidnapper himself—that is, is the kidnapper in a life-threatening situation and using the demand as a plea for help?

Host: no

## 70 · question

Is the hostage someone the daughter has a professional or caretaking relationship with, such as a patient or client?

Host: no

## 71 · question

Is the hostage the father's wife or partner (the daughter's mother or stepmother figure)?

Host: no

## 72 · question

Is the hostage someone related to the father rather than to the daughter?

Host: no

## 73 · question

Is the "kidnapping" actually staged—are the daughter and the hostage involved in a deception or performance rather than a genuine abduction?

Host: no

## 74 · question

Is the daughter calling not to plead for the hostage's life but because she is being forced to relay the kidnapper's demand?

Host: no

## 75 · question

Is the hostage a stranger to both the father and the daughter, abducted to pressure the father into paying?

Host: no

## 76 · question

Is the hostage someone the father has a caring relationship with but the daughter does not personally know well?

Host: no

## 77 · question

Is the hostage the daughter's pet or companion animal that the father is not attached to?

Host: no

## 78 · question

Is the hostage a person the daughter knows through work, such as a coworker or employer?

Host: no

## 79 · question

Is the hostage the daughter's lover who is not a boyfriend or husband—for example, a married man or secret partner?

Host: no

## 80 · question

Is the hostage a child the daughter is responsible for, such as through babysitting or adoption?

Host: no

## 81 · question

Is the hostage a famous person, public figure, or someone the daughter knows only indirectly through media or fandom?

Host: no

## 82 · question

Is the hostage a woman?

Host: no

## 83 · question

Is the hostage a child?

Host: no

## 84 · question

Is the daughter's plea based on concern for the hostage because she witnessed the abduction?

Host: no

## 85 · question

Is the daughter's plea about sparing the hostage based on the daughter having been threatened too, so that she pleads for both their lives?

Host: no

## 86 · question

Is the hostage an animal other than a pet—such as livestock or a zoo animal?

Host: no

## 87 · question

Is the hostage a human being?

Host: yes

## 88 · question

Is the hostage the daughter's acquaintance but not a close loved one—for example, a neighbor or classmate?

Host: no

## 89 · question

Did the daughter arrange or agree to the kidnapping of the hostage herself?

Host: no

## 90 · question

Is the hostage the daughter's doctor, therapist, or someone with whom she has a confidential relationship?

Host: no

## 91 · question

Is the daughter being held captive as well, even though she is not the hostage whose life is threatened?

Host: no

## 92 · question

Is the hostage the father's employee or subordinate, for whom the father feels responsible?

Host: no

## 93 · question

Is the hostage the daughter's teacher or mentor?

Host: no

## 94 · question

Was the daughter present when the hostage was abducted?

Host: yes and no

## 95 · question

Is the hostage the daughter's relative by marriage rather than blood?

Host: no

## 96 · question

Is the hostage the daughter's father—that is, the very man receiving the demand?

Host: yes

## 97 · final

The “hostage” is actually the father himself. He is physically unable to go out and deliver the ransom, and the daughter is the one able to carry the money to the kidnapper. Paying would therefore require sending the daughter into a dangerous delivery. At the same time, the demand is framed as a threat to the hostage’s life—the father—and he chooses that the ransom should not be paid rather than expose his daughter to that danger.

Host: yes and no

<details><summary>Private evaluator result (not sent to player)</summary>

```json
{
  "checkpoints": [
    {
      "id": "C1",
      "credit": 0.5,
      "evidence": "The “hostage” is actually the father himself. He is physically unable to go out and deliver the ransom, and the daughter is the one able to carry the money to the kidnapper.",
      "reason": "Identifies the father as hostage, but omits that the daughter is free and receives the ransom call."
    },
    {
      "id": "C2",
      "credit": 0.5,
      "evidence": "Paying would therefore require sending the daughter into a dangerous delivery.",
      "reason": "Danger to the daughter is identified, but the alone-arrival, witness-elimination, and both-person fear are incomplete."
    },
    {
      "id": "C3",
      "credit": 0.5,
      "evidence": "he chooses that the ransom should not be paid rather than expose his daughter to that danger",
      "reason": "Protective refusal is identified, but communication that she must not pay or come and acceptance of danger to his own life are omitted."
    },
    {
      "id": "C4",
      "credit": 0,
      "evidence": "",
      "reason": "No mention or entailment that the daughter is wealthy."
    },
    {
      "id": "C5",
      "credit": 0,
      "evidence": "",
      "reason": "No mention or entailment that the daughter is his only family."
    }
  ],
  "material_contradiction": false,
  "irrelevant": false,
  "rubric_conflict": false,
  "full_solution": false,
  "completion_note": "The submission reconstructs the father-as-hostage and a protective refusal based on keeping the daughter away from the dangerous delivery. It omits that the daughter is free and received the ransom call, the conditional fear that both may be killed to eliminate witnesses if she arrives alone, explicit communication that she must not pay or come with acceptance of his own danger, and the wealth/only-family details. The added physical inability is unsupported but not materially contradictory.",
  "fact_coverage": [
    {
      "id": "C1.F1",
      "status": "covered",
      "evidence": "The “hostage” is actually the father himself"
    },
    {
      "id": "C1.F2",
      "status": "missing",
      "evidence": ""
    },
    {
      "id": "C2.F1",
      "status": "partial",
      "evidence": "Paying would therefore require sending the daughter into a dangerous delivery."
    },
    {
      "id": "C3.F1",
      "status": "covered",
      "evidence": "he chooses that the ransom should not be paid rather than expose his daughter to that danger"
    },
    {
      "id": "C3.F2",
      "status": "partial",
      "evidence": "The “hostage” is actually the father himself... the demand is framed as a threat to the hostage’s life—the father—and he chooses that the ransom should not be paid rather than expose his daughter to that danger."
    },
    {
      "id": "C4.F1",
      "status": "missing",
      "evidence": ""
    },
    {
      "id": "C5.F1",
      "status": "missing",
      "evidence": ""
    }
  ],
  "requirement_coverage": [
    {
      "id": "R1",
      "status": "covered",
      "evidence": "The “hostage” is actually the father himself"
    },
    {
      "id": "R2",
      "status": "missing",
      "evidence": ""
    },
    {
      "id": "R3",
      "status": "partial",
      "evidence": "Paying would therefore require sending the daughter into a dangerous delivery."
    },
    {
      "id": "R4",
      "status": "covered",
      "evidence": "he chooses that the ransom should not be paid rather than expose his daughter to that danger"
    },
    {
      "id": "R5",
      "status": "partial",
      "evidence": "The “hostage” is actually the father himself... the demand is framed as a threat to the hostage’s life—the father—and he chooses that the ransom should not be paid rather than expose his daughter to that danger."
    },
    {
      "id": "R6",
      "status": "missing",
      "evidence": ""
    },
    {
      "id": "R7",
      "status": "missing",
      "evidence": ""
    }
  ],
  "contradictions": [],
  "partial_score": 0.475,
  "complete": false,
  "label": "yes and no",
  "grading_protocol": "coverage-v2",
  "controller_corrections": [],
  "completion_policy": "rubric_aligned_v1"
}
```
</details>

## 98 · question

Is the father the one speaking with the kidnapper, while the kidnapped hostage is elsewhere?

Host: no

## 99 · question

Is the father already dead or dying, so that paying the ransom cannot save him?

Host: no

## 100 · final · mandatory final

The father is himself the hostage whose life the kidnapper is threatening, yet he is physically unable to leave and deliver the ransom. The daughter is the person who would have to carry the money to the kidnapper in his place, which would expose her to serious danger. The father therefore rejects the ransom demand: paying would not be a safe rescue but would put his daughter in harm’s way, so he decides that no ransom should be paid.

Host: yes and no

<details><summary>Private evaluator result (not sent to player)</summary>

```json
{
  "checkpoints": [
    {
      "id": "C1",
      "credit": 0.5,
      "evidence": "The father is himself the hostage whose life the kidnapper is threatening... The daughter is the person who would have to carry the money to the kidnapper in his place",
      "reason": "Father-as-hostage is identified, but the daughter being free and receiving the ransom call is omitted."
    },
    {
      "id": "C2",
      "credit": 0.5,
      "evidence": "which would expose her to serious danger... paying would not be a safe rescue but would put his daughter in harm’s way",
      "reason": "Danger to the daughter is identified, but the alone-arrival, witness-elimination, and both-person fear are incomplete."
    },
    {
      "id": "C3",
      "credit": 0.5,
      "evidence": "The father therefore rejects the ransom demand: paying would not be a safe rescue but would put his daughter in harm’s way, so he decides that no ransom should be paid.",
      "reason": "Protective refusal is identified, but communication that she must not pay or come and acceptance of danger to his own life are omitted."
    },
    {
      "id": "C4",
      "credit": 0,
      "evidence": "",
      "reason": "No mention or entailment that the daughter is wealthy."
    },
    {
      "id": "C5",
      "credit": 0,
      "evidence": "",
      "reason": "No mention or entailment that the daughter is his only family."
    }
  ],
  "material_contradiction": false,
  "irrelevant": false,
  "rubric_conflict": false,
  "full_solution": false,
  "completion_note": "The submission reconstructs the father-as-hostage and a protective refusal based on keeping the daughter away from the dangerous delivery. It omits that the daughter is free and received the ransom call, the specific conditional fear that both may be killed to eliminate witnesses if she arrives alone, explicit communication that she must not pay or come with acceptance of his own danger, and the wealth/only-family details.",
  "fact_coverage": [
    {
      "id": "C1.F1",
      "status": "covered",
      "evidence": "The father is himself the hostage whose life the kidnapper is threatening"
    },
    {
      "id": "C1.F2",
      "status": "missing",
      "evidence": ""
    },
    {
      "id": "C2.F1",
      "status": "partial",
      "evidence": "which would expose her to serious danger... paying would not be a safe rescue but would put his daughter in harm’s way"
    },
    {
      "id": "C3.F1",
      "status": "covered",
      "evidence": "The father therefore rejects the ransom demand: paying would not be a safe rescue but would put his daughter in harm’s way, so he decides that no ransom should be paid."
    },
    {
      "id": "C3.F2",
      "status": "partial",
      "evidence": "The father is himself the hostage whose life the kidnapper is threatening... The father therefore rejects the ransom demand... he decides that no ransom should be paid."
    },
    {
      "id": "C4.F1",
      "status": "missing",
      "evidence": ""
    },
    {
      "id": "C5.F1",
      "status": "missing",
      "evidence": ""
    }
  ],
  "requirement_coverage": [
    {
      "id": "R1",
      "status": "covered",
      "evidence": "The father is himself the hostage whose life the kidnapper is threatening"
    },
    {
      "id": "R2",
      "status": "missing",
      "evidence": ""
    },
    {
      "id": "R3",
      "status": "partial",
      "evidence": "which would expose her to serious danger... paying would not be a safe rescue but would put his daughter in harm’s way"
    },
    {
      "id": "R4",
      "status": "covered",
      "evidence": "The father therefore rejects the ransom demand: paying would not be a safe rescue but would put his daughter in harm’s way, so he decides that no ransom should be paid."
    },
    {
      "id": "R5",
      "status": "partial",
      "evidence": "The father is himself the hostage whose life the kidnapper is threatening... The father therefore rejects the ransom demand... he decides that no ransom should be paid."
    },
    {
      "id": "R6",
      "status": "missing",
      "evidence": ""
    },
    {
      "id": "R7",
      "status": "missing",
      "evidence": ""
    }
  ],
  "contradictions": [],
  "partial_score": 0.475,
  "complete": false,
  "label": "yes and no",
  "grading_protocol": "coverage-v2",
  "controller_corrections": [],
  "completion_policy": "rubric_aligned_v1"
}
```
</details>
