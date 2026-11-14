# Turtle Soup trajectory

I usually follow the same route to enter and exit the school campus. There are no staircases nearby but I often use the stairs. Why?

Status: completed | counted questions: 100 | submissions: 100 | final partial score: 0.75

[Token usage and estimated costs](token_costs.csv)

## 1 · question

Are the “stairs” not literal building stairs, such as stairs on an escalator or moving walkway?

Host: yes

## 2 · question

Does the person use stairs that are part of a vehicle or transport system rather than a fixed school staircase?

Host: yes

## 3 · question

Is the “staircase nearby” absent because the person enters/exits through a vehicle such as a bus?

Host: no

## 4 · question

Does the person enter or exit the campus by an escalator?

Host: yes

## 5 · question

Is the escalator part of a pedestrian bridge or overpass near the school campus?

Host: irrelevant

## 6 · question

Does the person use the escalator inside a building on the campus route?

Host: irrelevant

## 7 · question

Is the escalator located in a train or subway station?

Host: irrelevant

## 8 · question

Does the person use the escalator as part of a daily commute to school?

Host: yes

## 9 · question

Is the escalator in a shopping mall or commercial building along the commute?

Host: irrelevant

## 10 · question

Is the person physically on the school campus when using the escalator?

Host: no

## 11 · question

Does the person use the escalator to travel between ground level and campus level, since the campus is elevated or the route includes a height change?

Host: yes

## 12 · question

Does the same route require the person to go up or down the escalator both when entering and when exiting the campus?

Host: yes

## 13 · question

Does the person avoid literal staircases because they are carrying something heavy or bulky, such as a backpack or equipment?

Host: no

## 14 · question

Is the escalator outdoors and exposed to the weather along a public pedestrian route?

Host: irrelevant

## 15 · question

Does the person use the escalator because it is part of their normal walking route and avoids stairs due to a physical disability or mobility limitation?

Host: yes and no

## 16 · question

Does the person have a physical disability or mobility limitation that makes the escalator preferable to stairs?

Host: no

## 17 · question

Is the person a student at the school?

Host: irrelevant

## 18 · question

Is the escalator in a public transport station that the person passes through on the commute?

Host: irrelevant

## 19 · question

Is the school campus itself located on an upper level reached by the escalator, such as a hillside or elevated complex?

Host: irrelevant

## 20 · question

Does the person use the escalator as a substitute for walking up or down a slope or hill along the route?

Host: irrelevant

## 21 · question

Is the “same route to enter and exit” on foot, with the campus entrance reached via a level change that has an escalator instead of stairs?

Host: yes

## 22 · question

Is the level change between a footbridge or overpass and the campus entrance?

Host: irrelevant

## 23 · question

Does the level change occur at an entrance to an underground or subway pedestrian passage?

Host: irrelevant

## 24 · question

Is the escalator located at a school gate or campus entrance that serves as a direct entrance point?

Host: yes

## 25 · question

Does the campus entrance itself lie at an upper or lower level than the surrounding public street, with the escalator connecting them?

Host: yes

## 26 · question

Is the person using the escalator because the campus entrance has no ordinary staircase nearby to reach it from the street?

Host: yes

## 27 · final

The person’s usual walking route to and from the school campus involves a change in level between the public street and the campus entrance. At that entrance there is an escalator rather than an ordinary staircase nearby, so the person “uses the stairs” in the sense of riding the escalator up or down both when entering and when exiting the campus.

Host: yes and no

<details><summary>Private evaluator result (not sent to player)</summary>

```json
{
  "checkpoints": [
    {
      "id": "C1",
      "credit": 0,
      "evidence": "riding the escalator up or down",
      "reason": "The submission identifies the escalator as the stairs but says the person is riding it, contradicting the required fact that the escalator is no longer moving and being walked on as stairs."
    },
    {
      "id": "C2",
      "credit": 0.5,
      "evidence": "At that entrance there is an escalator rather than an ordinary staircase nearby",
      "reason": "The submission partially covers the absence of a nearby ordinary staircase and escalator-based access, but omits that a pair of escalators provides access and does not clearly state that campus access relies on escalators."
    },
    {
      "id": "C3",
      "credit": 0,
      "evidence": "",
      "reason": "The submission does not mention one escalator being under maintenance or the other escalator being stopped for people to walk on."
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
      "evidence": "riding the escalator up or down"
    },
    {
      "id": "C2.F1",
      "status": "partial",
      "evidence": "At that entrance there is an escalator rather than an ordinary staircase nearby ... riding the escalator up or down both when entering and when exiting the campus"
    },
    {
      "id": "C2.F2",
      "status": "partial",
      "evidence": "there is an escalator rather than an ordinary staircase nearby"
    },
    {
      "id": "C3.F1",
      "status": "missing",
      "evidence": ""
    },
    {
      "id": "C3.F2",
      "status": "missing",
      "evidence": ""
    },
    {
      "id": "C3.F3",
      "status": "missing",
      "evidence": ""
    }
  ],
  "requirement_coverage": [],
  "contradictions": [
    {
      "quote": "riding the escalator up or down",
      "reference": "The other escalator will be paused so that people can use it as a staircase to enter and exit the campus.",
      "checkpoint_ids": [
        "C1"
      ]
    }
  ],
  "partial_score": 0.15,
  "complete": false,
  "label": "yes and no",
  "grading_protocol": "coverage-v3-unified",
  "controller_corrections": []
}
```
</details>

## 28 · question

Is there a literal staircase elsewhere along the route that the person also uses?

Host: no

## 29 · question

Is the “escalator” actually a staircase that can be converted or used as an escalator, such as at a school entrance with a moving stair mechanism?

Host: no

## 30 · question

Does the person enter and exit the campus by riding the escalator in opposite directions, using the same escalator for both?

Host: no

## 31 · question

Are there two separate escalators—one used when entering the campus and another used when exiting?

Host: yes and no

## 32 · question

Does the person sometimes use a different level-changing method on one direction of the same route?

Host: yes

## 33 · question

Is the different level-changing method an elevator or lift?

Host: no

## 34 · question

Is the different level-changing method a ramp?

Host: no

## 35 · question

Is the different level-changing method a vehicle, such as a car or bus, that takes the person up or down the level change?

Host: no

## 36 · question

Is the different level-changing method a literal staircase?

Host: no

## 37 · question

Is the different level-changing method a moving walkway or travelator?

Host: no

## 38 · question

Does the person use a different escalator in one direction rather than a different type of level-changing method?

Host: yes

## 39 · question

Is the different escalator used because the usual one only runs in one direction at different times of day?

Host: no

## 40 · question

Are there two escalators side by side, one going up and one going down, so the person uses the up escalator when entering and the down escalator when exiting?

Host: yes and no

## 41 · question

Does the person use stairs that are part of an escalator, such as walking up the escalator steps while it is in motion?

Host: yes

## 42 · question

Does the person walk on the escalator instead of standing still, thereby literally using stairs?

Host: yes

## 43 · final

The person’s usual walking route between the public street and the school campus involves a level change at the campus entrance. There is no ordinary staircase nearby; instead the entrance has escalators (with their stepped surfaces). The person uses these escalator stairs by walking up them when entering and walking down them when exiting—possibly choosing the appropriate up/down escalator—so although “no staircases are nearby,” the person often literally uses stairs in the form of escalator steps.

Host: yes and no

<details><summary>Private evaluator result (not sent to player)</summary>

```json
{
  "checkpoints": [
    {
      "id": "C1",
      "credit": 0.5,
      "evidence": "uses these escalator stairs by walking up them when entering and walking down them when exiting",
      "reason": "The submission identifies the stairs as escalator steps and says the person walks on them, but it does not state that the escalator is no longer moving."
    },
    {
      "id": "C2",
      "credit": 0.5,
      "evidence": "There is no ordinary staircase nearby; instead the entrance has escalators ... uses these escalator stairs by walking up them when entering and walking down them when exiting",
      "reason": "It covers the absence of a nearby ordinary staircase and reliance on escalators for access, but it does not clearly state that a pair of escalators provides this access."
    },
    {
      "id": "C3",
      "credit": 0,
      "evidence": "",
      "reason": "The submission does not mention one escalator being under maintenance or the other escalator being stopped for people to walk on."
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
      "evidence": "uses these escalator stairs by walking up them when entering and walking down them when exiting"
    },
    {
      "id": "C2.F1",
      "status": "covered",
      "evidence": "There is no ordinary staircase nearby; instead the entrance has escalators ... uses these escalator stairs by walking up them when entering and walking down them when exiting"
    },
    {
      "id": "C2.F2",
      "status": "partial",
      "evidence": "the entrance has escalators"
    },
    {
      "id": "C3.F1",
      "status": "missing",
      "evidence": ""
    },
    {
      "id": "C3.F2",
      "status": "missing",
      "evidence": ""
    },
    {
      "id": "C3.F3",
      "status": "missing",
      "evidence": ""
    }
  ],
  "requirement_coverage": [],
  "contradictions": [],
  "partial_score": 0.4,
  "complete": false,
  "label": "yes and no",
  "grading_protocol": "coverage-v3-unified",
  "controller_corrections": []
}
```
</details>

## 44 · question

Is the key point that the person is not physically on campus when using the stairs, so the “no staircases nearby” refers to the campus area specifically?

Host: no

## 45 · question

Does the person use the stairs of a double-decker bus or similar vehicle that is part of their commute to and from the campus?

Host: no

## 46 · question

Are the “stairs” that the person uses located outside the school but part of the route between home and campus, while no staircase is near the campus entrance itself?

Host: yes

## 47 · question

Does the person walk up/down a set of literal stairs somewhere along the commute before reaching the vicinity of the campus, even though no staircase is near the campus itself?

Host: no

## 48 · question

Does the person use the escalator stairs—walking on them—rather than ordinary stairs, and is this what “often use the stairs” means?

Host: yes

## 49 · final

The person follows the same on-foot route between the public street and the school campus entrance, where the ground level changes. No ordinary staircase is nearby; instead the entrance has escalators. The person often “uses the stairs” by walking on the stepped escalator surfaces—going up on the appropriate up-escalator when entering and down on the down-escalator when exiting—so the apparent contradiction is resolved because escalator steps are the “stairs” being used, not a conventional fixed staircase.

Host: yes and no

<details><summary>Private evaluator result (not sent to player)</summary>

```json
{
  "checkpoints": [
    {
      "id": "C1",
      "credit": 0.5,
      "evidence": "walking on the stepped escalator surfaces—going up on the appropriate up-escalator when entering and down on the down-escalator when exiting",
      "reason": "The submission identifies the stairs as escalator steps and says the person walks on them, but it does not state that the escalator is no longer moving."
    },
    {
      "id": "C2",
      "credit": 0.5,
      "evidence": "No ordinary staircase is nearby; instead the entrance has escalators",
      "reason": "It covers the absence of a nearby ordinary staircase and implies escalator-based access, but it does not clearly state that a pair of escalators provides the access."
    },
    {
      "id": "C3",
      "credit": 0,
      "evidence": "",
      "reason": "The submission does not mention one escalator being under maintenance or the other escalator being stopped for people to walk on."
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
      "evidence": "walking on the stepped escalator surfaces—going up on the appropriate up-escalator when entering and down on the down-escalator when exiting"
    },
    {
      "id": "C2.F1",
      "status": "covered",
      "evidence": "No ordinary staircase is nearby; instead the entrance has escalators ... walking on the stepped escalator surfaces"
    },
    {
      "id": "C2.F2",
      "status": "partial",
      "evidence": "No ordinary staircase is nearby; instead the entrance has escalators"
    },
    {
      "id": "C3.F1",
      "status": "missing",
      "evidence": ""
    },
    {
      "id": "C3.F2",
      "status": "missing",
      "evidence": ""
    },
    {
      "id": "C3.F3",
      "status": "missing",
      "evidence": ""
    }
  ],
  "requirement_coverage": [],
  "contradictions": [],
  "partial_score": 0.4,
  "complete": false,
  "label": "yes and no",
  "grading_protocol": "coverage-v3-unified",
  "controller_corrections": []
}
```
</details>

## 50 · question

Does the “no staircases nearby” refer specifically to the school campus having no staircases near the route, while the stairs used are escalator stairs at the entrance?

Host: yes

## 51 · question

Is the answer that the “stairs” are escalator steps, and the person walks on them rather than standing still, while the statement “no staircases nearby” excludes escalators?

Host: yes

## 52 · final

The person’s usual route to and from the school passes through a level change at the campus entrance. There is no conventional fixed staircase near that part of the campus; instead there is an escalator. The person often “uses the stairs” in the sense of walking on the escalator’s stepped treads rather than merely standing on them, going up when entering and down when exiting the campus. Thus “no staircases nearby” is not contradicted because an escalator is not an ordinary staircase, even though its steps are the stairs the person uses.

Host: yes and no

<details><summary>Private evaluator result (not sent to player)</summary>

```json
{
  "checkpoints": [
    {
      "id": "C1",
      "credit": 0.5,
      "evidence": "walking on the escalator’s stepped treads rather than merely standing on them",
      "reason": "Identifies the stairs as escalator steps and describes walking on them, but omits the required qualifier that the escalator is no longer moving."
    },
    {
      "id": "C2",
      "credit": 0.5,
      "evidence": "There is no conventional fixed staircase near that part of the campus; instead there is an escalator.",
      "reason": "Covers the absence of nearby conventional stairs and escalator-based access, but omits that a pair of escalators provides the access."
    },
    {
      "id": "C3",
      "credit": 0,
      "evidence": "",
      "reason": "Does not mention one escalator being under maintenance or the other escalator being stopped for people to walk on."
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
      "evidence": "walking on the escalator’s stepped treads rather than merely standing on them ... its steps are the stairs the person uses"
    },
    {
      "id": "C2.F1",
      "status": "covered",
      "evidence": "There is no conventional fixed staircase near that part of the campus; instead there is an escalator. ... walking on the escalator’s stepped treads ... going up when entering and down when exiting the campus"
    },
    {
      "id": "C2.F2",
      "status": "partial",
      "evidence": "There is no conventional fixed staircase near that part of the campus; instead there is an escalator."
    },
    {
      "id": "C3.F1",
      "status": "missing",
      "evidence": ""
    },
    {
      "id": "C3.F2",
      "status": "missing",
      "evidence": ""
    },
    {
      "id": "C3.F3",
      "status": "missing",
      "evidence": ""
    }
  ],
  "requirement_coverage": [],
  "contradictions": [],
  "partial_score": 0.4,
  "complete": false,
  "label": "yes and no",
  "grading_protocol": "coverage-v3-unified",
  "controller_corrections": []
}
```
</details>

## 53 · question

Is there a specific wordplay or ambiguity in the word “stairs” that I have not yet identified?

Host: no

## 54 · question

Does the phrase “no staircases nearby” mean there is no staircase at the specific nearby location where the person enters/exits, even though an escalator is present there?

Host: yes

## 55 · question

Is the person entering and exiting the campus by using an escalator that is located at a school entrance but is not considered a “staircase”?

Host: yes

## 56 · question

Does the person use the escalator by standing on it rather than walking up its steps?

Host: no

## 57 · question

Does the person use the “stairs” only when exiting the campus, not when entering?

Host: no

## 58 · question

Does the person use a set of literal stairs on only part of the same route, so that they use stairs “nearby” the campus in one direction but not the other?

Host: no

## 59 · question

Is the apparent contradiction resolved mainly by the fact that an escalator is a “moving staircase” and its stepped surface counts as stairs?

Host: yes

## 60 · question

Does the person use the escalator as a shortcut or direct route because it is the only practical way to enter and exit the elevated or sunken campus entrance?

Host: yes

## 61 · final

The person’s regular route to and from the school reaches a change in ground level at the campus entrance. There is no ordinary fixed staircase nearby there; instead, the entrance is served by an escalator, a “moving staircase” whose stepped surface counts as stairs. The person frequently uses those escalator steps—walking on them rather than just standing—to go up or down between the street level and the campus entrance, in both directions. Hence the person can say there are no staircases nearby while still often using “the stairs”: the stairs are the escalator steps, and the escalator is also the direct practical way through that level change.

Host: yes and no

<details><summary>Private evaluator result (not sent to player)</summary>

```json
{
  "checkpoints": [
    {
      "id": "C1",
      "credit": 0.5,
      "evidence": "the entrance is served by an escalator, a “moving staircase” whose stepped surface counts as stairs. The person frequently uses those escalator steps—walking on them rather than just standing",
      "reason": "The submission identifies the stairs as escalator steps and says the person walks on them, but it omits the required qualifier that the escalator is no longer moving."
    },
    {
      "id": "C2",
      "credit": 0.5,
      "evidence": "There is no ordinary fixed staircase nearby there; instead, the entrance is served by an escalator ... the escalator is also the direct practical way through that level change.",
      "reason": "The submission covers the absence of nearby ordinary stairs and reliance on an escalator for access, but it omits that a pair of escalators provides the access."
    },
    {
      "id": "C3",
      "credit": 0,
      "evidence": "",
      "reason": "The submission does not mention one escalator being under maintenance or the other escalator being stopped for people to walk on."
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
      "evidence": "the entrance is served by an escalator, a “moving staircase” whose stepped surface counts as stairs. The person frequently uses those escalator steps—walking on them rather than just standing"
    },
    {
      "id": "C2.F1",
      "status": "covered",
      "evidence": "There is no ordinary fixed staircase nearby there; instead, the entrance is served by an escalator ... the escalator is also the direct practical way through that level change."
    },
    {
      "id": "C2.F2",
      "status": "partial",
      "evidence": "There is no ordinary fixed staircase nearby there; instead, the entrance is served by an escalator"
    },
    {
      "id": "C3.F1",
      "status": "missing",
      "evidence": ""
    },
    {
      "id": "C3.F2",
      "status": "missing",
      "evidence": ""
    },
    {
      "id": "C3.F3",
      "status": "missing",
      "evidence": ""
    }
  ],
  "requirement_coverage": [],
  "contradictions": [],
  "partial_score": 0.4,
  "complete": false,
  "label": "yes and no",
  "grading_protocol": "coverage-v3-unified",
  "controller_corrections": []
}
```
</details>

## 62 · question

Is the escalator used by the person actually outside the campus, and does “enter and exit the school campus” mean passing the campus boundary after using it?

Host: yes and no

## 63 · question

Is the escalator itself outside the campus boundary?

Host: irrelevant

## 64 · question

Is the person using the escalator “stairs” only incidentally, while the wording “no staircases nearby” is about the literal campus building having no stairs near the route?

Host: no

## 65 · question

Is the person using an escalator whose treads flatten at the top and bottom, so that it functions like a staircase but is not called one?

Host: no

## 66 · question

Does the person use the escalator to go between a lower street entrance and an elevated pedestrian area that is on the campus route, rather than between campus levels?

Host: yes

## 67 · question

Is the elevated pedestrian area a walkway or concourse that leads directly to the school campus entrance?

Host: irrelevant

## 68 · question

Is the elevated pedestrian area part of a transport hub, such as a station, from which the person then walks to campus?

Host: irrelevant

## 69 · question

Is the elevated pedestrian area a bridge or overpass that crosses a road on the way to campus?

Host: irrelevant

## 70 · question

Is the escalator the person uses an outdoor public escalator connecting a lower street level to a higher pedestrian level as part of the route to campus?

Host: irrelevant

## 71 · question

Is the person carrying a bicycle or other wheeled item up or down the escalator?

Host: irrelevant

## 72 · question

Is the person using the escalator not for transportation but because the escalator steps themselves are a staircase they deliberately exercise on?

Host: no

## 73 · question

Is the person using an escalator at an entrance where ordinary stairs exist but are not “nearby” the route, while the escalator is directly on the route?

Host: irrelevant

## 74 · question

Does the person enter and exit the campus through a building, and is the escalator inside that building rather than close to where the person walks outside?

Host: irrelevant

## 75 · question

Does the person use the escalator at a mall or commercial building adjacent to the campus as a shortcut between street levels?

Host: irrelevant

## 76 · question

Is the person’s use of “the stairs” simply riding the escalator, with no need for them to walk on it?

Host: no

## 77 · question

Is the escalator used as a literal staircase because it is stopped or broken, so the person climbs its steps?

Host: yes

## 78 · question

Is the escalator often stopped or out of service around the time the person commutes, so they frequently climb it as stairs?

Host: yes

## 79 · final

The person regularly walks the same route into and out of the school campus, and that route includes a level change served by an escalator rather than an ordinary fixed staircase. Because the escalator is often stopped or out of service at commuting times, the person frequently has to climb or descend its stationary stepped surface as if it were a staircase. So “there are no staircases nearby” is true in the sense that there is no conventional staircase there, yet the person “often uses the stairs” because the escalator’s steps function as stairs when it is not moving.

Host: yes and no

<details><summary>Private evaluator result (not sent to player)</summary>

```json
{
  "checkpoints": [
    {
      "id": "C1",
      "credit": 1,
      "evidence": "the escalator is often stopped or out of service at commuting times ... climb or descend its stationary stepped surface ... the escalator’s steps function as stairs when it is not moving.",
      "reason": "The submission identifies the stairs as the steps of an escalator when it is stopped/not moving, covering the required fact."
    },
    {
      "id": "C2",
      "credit": 0.5,
      "evidence": "level change served by an escalator rather than an ordinary fixed staircase ... there is no conventional staircase there ... the escalator’s steps function as stairs.",
      "reason": "Covers the absence of nearby ordinary fixed stairs and escalator-based access, but omits that a pair of escalators provides the access."
    },
    {
      "id": "C3",
      "credit": 0.5,
      "evidence": "",
      "reason": "Does not mention one escalator being under maintenance or the other escalator being stopped for people to walk on; the required pair/maintenance qualifiers are absent."
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
      "status": "covered",
      "evidence": "the escalator is often stopped or out of service at commuting times ... climb or descend its stationary stepped surface ... the escalator’s steps function as stairs when it is not moving."
    },
    {
      "id": "C2.F1",
      "status": "covered",
      "evidence": "level change served by an escalator rather than an ordinary fixed staircase ... there is no conventional staircase there ... the escalator’s steps function as stairs."
    },
    {
      "id": "C2.F2",
      "status": "partial",
      "evidence": "an escalator rather than an ordinary fixed staircase"
    },
    {
      "id": "C3.F1",
      "status": "missing",
      "evidence": ""
    },
    {
      "id": "C3.F2",
      "status": "partial",
      "evidence": "the escalator is often stopped or out of service at commuting times"
    },
    {
      "id": "C3.F3",
      "status": "missing",
      "evidence": ""
    }
  ],
  "requirement_coverage": [],
  "contradictions": [],
  "partial_score": 0.75,
  "complete": false,
  "label": "yes and no",
  "grading_protocol": "coverage-v3-unified",
  "controller_corrections": [
    {
      "field": "C3.credit",
      "model": 0,
      "effective": 0.5
    }
  ]
}
```
</details>

## 80 · question

Is the person a maintenance worker or staff member whose job involves the escalator?

Host: irrelevant

## 81 · question

Does the person often use the stairs because the escalator is intentionally switched off or not operating during their usual travel times, rather than being broken?

Host: yes

## 82 · question

Is the escalator switched off outside of certain operating hours, such as early morning or late evening?

Host: no

## 83 · question

Is the escalator switched off during specific scheduled periods, such as outside normal public transport service times or during energy-saving hours?

Host: no

## 84 · question

Is the escalator switched off because it only operates on demand, such as when someone approaches or presses a button?

Host: no

## 85 · question

Is the escalator switched off during periods of low traffic as an energy-saving measure?

Host: no

## 86 · question

Is the escalator switched off at times when the person uses it because of security or safety reasons, such as at night?

Host: no

## 87 · question

Is the escalator switched off because it is not powered, such as during a power outage or load shedding, when the person travels?

Host: no

## 88 · question

Is the escalator usually switched off during the person's commute because the building or station is closed at that time?

Host: no

## 89 · question

Is the escalator turned off on purpose to discourage its use, for example to save costs or because walking is preferred?

Host: no

## 90 · question

Is the escalator switched off at particular times under a published schedule, such as being turned off on weekends or holidays?

Host: no

## 91 · question

Is the escalator switched off specifically during hours when few people use it, but not as a formal published schedule?

Host: no

## 92 · question

Is the escalator switched off because the person arrives before it is turned on each morning?

Host: no

## 93 · question

Is the escalator switched off in the evening when the person leaves the campus?

Host: irrelevant

## 94 · question

Is the escalator switched off because of a rule that it must be stopped when no operator or attendant is present?

Host: no

## 95 · question

Is the escalator switched off only for part of the year, such as during school holidays or a particular season?

Host: irrelevant

## 96 · question

Is the escalator switched off during the person's commute because of a timer setting that does not match their travel times?

Host: no

## 97 · question

Is the escalator switched off at the same time every day as part of a regular maintenance or inspection routine?

Host: no

## 98 · question

Did the host mean “yes and no” to indicate that the escalator is sometimes operating and sometimes switched off, so the person sometimes walks the steps and sometimes rides?

Host: yes

## 99 · question

Is the escalator usually stopped in one direction—say, the down escalator—so the person often has to walk down its steps when leaving campus?

Host: yes

## 100 · final · mandatory final

The person regularly follows the same route between the public street and the school campus, and that route involves a level change at the campus entrance. No ordinary fixed staircase is nearby there; the entrance instead has escalators. The escalators are sometimes operating and sometimes switched off, and in particular the down escalator is usually stopped. So the person often “uses the stairs” by walking up or down the stationary stepped escalator surface—especially walking down it when leaving campus—rather than using a conventional staircase. Thus there are no staircases nearby in the ordinary sense, yet the person often uses stairs: the escalator steps, which serve as stairs when the escalator is not moving.

Host: yes and no

<details><summary>Private evaluator result (not sent to player)</summary>

```json
{
  "checkpoints": [
    {
      "id": "C1",
      "credit": 1,
      "evidence": "walking up or down the stationary stepped escalator surface ... the escalator steps, which serve as stairs when the escalator is not moving",
      "reason": "The submission clearly identifies the stairs as the steps of a stopped/non-moving escalator."
    },
    {
      "id": "C2",
      "credit": 0.5,
      "evidence": "No ordinary fixed staircase is nearby there; the entrance instead has escalators ... walking up or down the stationary stepped escalator surface",
      "reason": "It covers the absence of nearby ordinary fixed stairs and escalator-based access, but it omits the required qualifier that a pair of escalators provides the access."
    },
    {
      "id": "C3",
      "credit": 0.5,
      "evidence": "",
      "reason": "It does not mention one escalator being under maintenance, nor the causal event of the other escalator being stopped for people to walk on during that maintenance. The isolated mention of a stopped down escalator is not enough to cover the required facts."
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
      "status": "covered",
      "evidence": "walking up or down the stationary stepped escalator surface ... the escalator steps, which serve as stairs when the escalator is not moving"
    },
    {
      "id": "C2.F1",
      "status": "covered",
      "evidence": "No ordinary fixed staircase is nearby there; the entrance instead has escalators ... walking up or down the stationary stepped escalator surface"
    },
    {
      "id": "C2.F2",
      "status": "partial",
      "evidence": "No ordinary fixed staircase is nearby there; the entrance instead has escalators"
    },
    {
      "id": "C3.F1",
      "status": "missing",
      "evidence": ""
    },
    {
      "id": "C3.F2",
      "status": "partial",
      "evidence": "in particular the down escalator is usually stopped"
    },
    {
      "id": "C3.F3",
      "status": "missing",
      "evidence": ""
    }
  ],
  "requirement_coverage": [],
  "contradictions": [],
  "partial_score": 0.75,
  "complete": false,
  "label": "yes and no",
  "grading_protocol": "coverage-v3-unified",
  "controller_corrections": [
    {
      "field": "C3.credit",
      "model": 0,
      "effective": 0.5
    }
  ]
}
```
</details>
