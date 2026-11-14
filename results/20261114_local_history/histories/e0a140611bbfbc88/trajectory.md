# Turtle Soup trajectory

I usually follow the same route to enter and exit the school campus. There are no staircases nearby but I often use the stairs. Why?

Status: completed | counted questions: 3 | submissions: 3 | final partial score: 0.0

## 1 · question

Are the stairs part of the route you take to enter or leave the campus?

Host: yes

## 2 · final

They commute by a double-decker bus. There are no staircases near the campus entrance, but the bus’s stairs are part of the route: they climb them to reach the upper deck and use them again when getting off, whether they’re going to or leaving school.

Host: no

<details><summary>Private evaluator result (not sent to player)</summary>

```json
{
  "checkpoints": [
    {
      "id": "C1",
      "credit": 0,
      "evidence": "“They commute by a double-decker bus” and “the bus’s stairs”",
      "reason": "It identifies the stairs as bus stairs, not a stopped escalator."
    },
    {
      "id": "C2",
      "credit": 0,
      "evidence": "“There are no staircases near the campus entrance, but the bus’s stairs are part of the route”",
      "reason": "Although it mentions no nearby stairs, it replaces escalator campus access with a bus route."
    },
    {
      "id": "C3",
      "credit": 0,
      "evidence": "",
      "reason": "The explanation does not mention escalator maintenance or the other escalator being stopped."
    }
  ],
  "material_contradiction": true,
  "irrelevant": false,
  "rubric_conflict": false,
  "full_solution": false,
  "completion_note": "The explanation substitutes bus travel and bus stairs for the pair of campus escalators. It omits the maintenance event and the stopping of the other escalator for walking in both directions.",
  "fact_coverage": [
    {
      "id": "C1.F1",
      "status": "contradicted",
      "evidence": "“They commute by a double-decker bus” … “the bus’s stairs are part of the route”"
    },
    {
      "id": "C2.F1",
      "status": "contradicted",
      "evidence": "“There are no staircases near the campus entrance, but the bus’s stairs are part of the route”"
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
      "evidence": "“They commute by a double-decker bus” … “the bus’s stairs are part of the route”"
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
      "quote": "They commute by a double-decker bus. … the bus’s stairs are part of the route",
      "reference": "A pair of escalators provides access to campus, with no nearby ordinary stairs.",
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

The person enters and leaves through the same campus entrance, where there are no stairs. But once inside, they regularly go between floors of the school using its indoor staircases. Those stairs aren’t near the entrance or along the route to the campus, which is why the two details seem contradictory.

Host: no

<details><summary>Private evaluator result (not sent to player)</summary>

```json
{
  "checkpoints": [
    {
      "id": "C1",
      "credit": 0,
      "evidence": "“they regularly go between floors of the school using its indoor staircases”",
      "reason": "Identifies the stairs as ordinary indoor staircases, not a stopped escalator."
    },
    {
      "id": "C2",
      "credit": 0,
      "evidence": "“there are no stairs”",
      "reason": "Does not explain that campus access relies on a pair of escalators."
    },
    {
      "id": "C3",
      "credit": 0,
      "evidence": "",
      "reason": "Does not mention maintenance or the other escalator being stopped for people to walk on."
    }
  ],
  "material_contradiction": true,
  "irrelevant": false,
  "rubric_conflict": false,
  "full_solution": false,
  "completion_note": "The explanation substitutes indoor staircases for the stopped escalator and omits the pair of campus-access escalators, the maintenance, and the other escalator being stopped for walking in both directions.",
  "fact_coverage": [
    {
      "id": "C1.F1",
      "status": "contradicted",
      "evidence": "“they regularly go between floors of the school using its indoor staircases”"
    },
    {
      "id": "C2.F1",
      "status": "partial",
      "evidence": "“there are no stairs”"
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
      "evidence": "“there are no stairs”"
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
      "quote": "“they regularly go between floors of the school using its indoor staircases”",
      "reference": "The stairs are an escalator that is no longer moving.",
      "checkpoint_ids": [
        "C1"
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
