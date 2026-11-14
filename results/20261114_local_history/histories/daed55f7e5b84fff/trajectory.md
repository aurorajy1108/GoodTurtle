# Turtle Soup trajectory

I usually follow the same route to enter and exit the school campus. There are no staircases nearby but I often use the stairs. Why?

Status: completed | counted questions: 3 | submissions: 3 | final partial score: 0.0

## 1 · question

Are the stairs the narrator often uses inside a building on the school campus?

Host: irrelevant

## 2 · final

The narrator rides a bus to school. They use the same route to enter and leave campus, but the stairs they often use are the steps on the bus—not staircases near the campus.

Host: no

<details><summary>Private evaluator result (not sent to player)</summary>

```json
{
  "checkpoints": [
    {
      "id": "C1",
      "credit": 0,
      "evidence": "“the steps on the bus—not staircases near the campus”",
      "reason": "Identifies the stairs as bus steps rather than a stopped escalator, contradicting the checkpoint."
    },
    {
      "id": "C2",
      "credit": 0,
      "evidence": "“not staircases near the campus”",
      "reason": "Mentions no nearby staircases but does not identify escalators as the means of campus access; the explanation instead attributes the steps to a bus."
    },
    {
      "id": "C3",
      "credit": 0,
      "evidence": "",
      "reason": "Does not mention escalators, maintenance, or the other escalator being stopped."
    }
  ],
  "material_contradiction": true,
  "irrelevant": false,
  "rubric_conflict": false,
  "full_solution": false,
  "completion_note": "The explanation replaces the escalator explanation with bus steps and omits the pair of access escalators, the frequent maintenance, and the other escalator being stopped for walking in both directions.",
  "fact_coverage": [
    {
      "id": "C1.F1",
      "status": "contradicted",
      "evidence": "“the steps on the bus—not staircases near the campus”"
    },
    {
      "id": "C2.F1",
      "status": "partial",
      "evidence": "“not staircases near the campus”"
    },
    {
      "id": "C3.F1",
      "status": "missing",
      "evidence": ""
    }
  ],
  "requirement_coverage": [
    {
      "id": "R1",
      "status": "partial",
      "evidence": "“not staircases near the campus”"
    },
    {
      "id": "R2",
      "status": "missing",
      "evidence": ""
    },
    {
      "id": "R3",
      "status": "missing",
      "evidence": ""
    }
  ],
  "contradictions": [
    {
      "quote": "“the steps on the bus—not staircases near the campus”",
      "reference": "The stairs are a stopped escalator; a pair of escalators provides access to campus.",
      "checkpoint_ids": [
        "C1",
        "C2"
      ]
    }
  ],
  "partial_score": 0.0,
  "complete": false,
  "label": "no",
  "grading_protocol": "coverage-v2",
  "controller_corrections": []
}
```
</details>

## 3 · final · mandatory final

The narrator enters and leaves the school campus by the same route. The stairs they often use aren’t near that route or the campus entrance; they use stairs elsewhere in their routine, unrelated to getting onto campus. The clues don’t establish exactly where those stairs are.

Host: no

<details><summary>Private evaluator result (not sent to player)</summary>

```json
{
  "checkpoints": [
    {
      "id": "C1",
      "credit": 0,
      "evidence": "they use stairs elsewhere in their routine, unrelated to getting onto campus",
      "reason": "This rejects the reference’s central identification of the stairs used for campus access as a stopped escalator."
    },
    {
      "id": "C2",
      "credit": 0,
      "evidence": "they use stairs elsewhere in their routine, unrelated to getting onto campus",
      "reason": "The explanation contradicts campus access relying on escalators."
    },
    {
      "id": "C3",
      "credit": 0,
      "evidence": "",
      "reason": "It does not mention maintenance or the other escalator being stopped for people to walk on."
    }
  ],
  "material_contradiction": true,
  "irrelevant": false,
  "rubric_conflict": false,
  "full_solution": false,
  "completion_note": "The explanation replaces the escalator-based campus access with unrelated stairs elsewhere. It omits the maintenance and the other escalator being stopped for walking.",
  "fact_coverage": [
    {
      "id": "C1.F1",
      "status": "contradicted",
      "evidence": "they use stairs elsewhere in their routine, unrelated to getting onto campus"
    },
    {
      "id": "C2.F1",
      "status": "contradicted",
      "evidence": "they use stairs elsewhere in their routine, unrelated to getting onto campus"
    },
    {
      "id": "C3.F1",
      "status": "missing",
      "evidence": ""
    }
  ],
  "requirement_coverage": [
    {
      "id": "R1",
      "status": "contradicted",
      "evidence": "they use stairs elsewhere in their routine, unrelated to getting onto campus"
    },
    {
      "id": "R2",
      "status": "missing",
      "evidence": ""
    },
    {
      "id": "R3",
      "status": "missing",
      "evidence": ""
    }
  ],
  "contradictions": [
    {
      "quote": "they use stairs elsewhere in their routine, unrelated to getting onto campus",
      "reference": "A pair of escalators provides access to campus; when one escalator is under maintenance, the other is stopped so people can walk on its steps.",
      "checkpoint_ids": [
        "C1",
        "C2"
      ]
    }
  ],
  "partial_score": 0.0,
  "complete": false,
  "label": "no",
  "grading_protocol": "coverage-v2",
  "controller_corrections": []
}
```
</details>
