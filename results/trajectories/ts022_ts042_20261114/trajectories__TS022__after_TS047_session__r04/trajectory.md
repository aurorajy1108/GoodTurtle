# Turtle Soup trajectory

A lost girl found an empty house. She was exhausted but couldn't fall asleep.
The next morning, having finally fallen asleep from exhaustion, she woke up, noticed something strange, and fled the house in terror.

Status: completed | counted questions: 100 | submissions: 100 | final partial score: 0.75

[Token usage and estimated costs](token_costs.csv)

## 1 · question

Did the girl flee because she discovered the house was not actually empty?

Host: no

## 2 · question

Did she flee because something about the house itself (its structure, state, or location) had changed or become apparent overnight?

Host: no

## 3 · question

Did she flee because of something she noticed about her own body or person when she woke?

Host: no

## 4 · question

Did she flee because she noticed something about the room she had slept in, such as a change in its contents or appearance?

Host: yes

## 5 · question

Was something in the room missing in the morning that had been there the night before?

Host: yes

## 6 · question

Was the missing thing related to the girl—for example, her shoes, clothing, or belongings?

Host: no

## 7 · question

Was the missing thing a piece of the room's structure or furnishings—such as a door, window, or bed?

Host: no

## 8 · question

Was something new in the room in the morning that had not been there the night before?

Host: no

## 9 · question

Had something in the room moved or been rearranged overnight?

Host: no

## 10 · question

Was the strange thing she noticed that the room appeared different because she was seeing it in daylight for the first time?

Host: no

## 11 · question

Was the missing thing an object that had appeared to be part of the room but was actually a living thing (such as an animal or person) that left overnight?

Host: yes

## 12 · question

Was the living thing a person who had been in the room with her during the night?

Host: no

## 13 · question

Was the living thing an animal (such as a cat, dog, or rat)?

Host: no

## 14 · question

Was the living thing a bird or insect?

Host: no

## 15 · question

Was the "living thing" actually a human corpse that had been mistaken for part of the room and was removed?

Host: no

## 16 · question

Was the missing thing a plant or something botanical?

Host: no

## 17 · question

At night, did she mistake a living person (or part of one) for a lifeless object in the room, and in the morning realize it had been a real person who was now gone?

Host: yes

## 18 · question

Was the “object” she mistook for part of the room a person sitting or standing motionless in the dark?

Host: yes

## 19 · question

Did the person leave during the night, so that by morning the place where they had been was empty?

Host: yes

## 20 · question

Was the motionless person sitting or standing near her bed while she slept?

Host: no

## 21 · question

Was the motionless figure something she had taken for furniture, such as a coat on a chair or a shape in a corner?

Host: no

## 22 · question

Was the motionless person seated in a chair in the room?

Host: no

## 23 · question

Was the motionless person something like a mannequin, statue, or doll that she thought was decor, but it turned out to be a real (living or dead) person?

Host: no

## 24 · question

Was the motionless figure lying down, such as on a sofa, floor, or another bed?

Host: no

## 25 · question

Did she at first think the motionless person was a decoration or fixture mounted on the wall (like the “picture” in the previous puzzle), such as a framed portrait of a person—when it was actually a real person in the room?

Host: yes and no

## 26 · question

Was the person she mistook for part of the room's furnishings/decor actually someone standing or sitting in a dark corner or alcove?

Host: no

## 27 · question

Did she mistake the person for a painted portrait or picture hanging on the wall?

Host: yes

## 28 · question

Was the “portrait” actually a window with a real person outside, similar to the previous puzzle's mechanism?

Host: yes

## 29 · question

Did the person outside the window leave by morning, so the "portrait" was gone and she realized what it had been?

Host: yes

## 30 · question

Was the person outside the window watching her?

Host: yes

## 31 · question

Did the person outside the window appear dangerous or threatening?

Host: yes

## 32 · question

In the morning, did she see the person outside the window was gone and realize the “portrait” had been the watcher, prompting her to flee in terror?

Host: yes

## 33 · final

The lost girl took shelter in what seemed an empty house and, exhausted, could not sleep. In the dark she mistook a window for a framed portrait on the wall; the “portrait’s” face was actually a real person outside, watching her. Eventually she fell asleep from exhaustion. In the morning the watcher was gone—the “portrait” was no longer there—and she realized the truth: there had been no painting, only a window, and a real person had been staring in at her through the night. That realization terrified her, and she fled the house.

Host: yes and no

<details><summary>Private evaluator result (not sent to player)</summary>

```json
{
  "checkpoints": [
    {
      "id": "C1",
      "credit": 1,
      "evidence": "she mistook a window for a framed portrait on the wall; the “portrait’s” face was actually a real person outside, watching her",
      "reason": "Covers that the apparent portrait was a window and that a real person outside was behind it, plus the girl taking shelter and mistaking the window for a portrait."
    },
    {
      "id": "C2",
      "credit": 0.5,
      "evidence": "exhausted, could not sleep. In the dark she mistook a window for a framed portrait on the wall; the “portrait’s” face was actually a real person outside, watching her",
      "reason": "Captures sleeplessness and the watching figure mistaken for a portrait, but omits the explicit causal qualifier that this made her uneasy and that the feeling of being watched kept her awake."
    },
    {
      "id": "C3",
      "credit": 1,
      "evidence": "In the morning the watcher was gone—the “portrait” was no longer there—and she realized the truth: there had been no painting, only a window, and a real person had been staring in at her through the night. That realization terrified her, and she fled the house.",
      "reason": "Covers the morning absence, realization that it was a window with a real watcher, and the terror causing her to flee."
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
      "evidence": "she mistook a window for a framed portrait on the wall; the “portrait’s” face was actually a real person outside, watching her"
    },
    {
      "id": "C1.F2",
      "status": "covered",
      "evidence": "The lost girl took shelter in what seemed an empty house... she mistook a window for a framed portrait on the wall; the “portrait’s” face was actually a real person outside"
    },
    {
      "id": "C2.F1",
      "status": "partial",
      "evidence": "The lost girl took shelter in what seemed an empty house and, exhausted, could not sleep. In the dark she mistook a window for a framed portrait... watching her."
    },
    {
      "id": "C2.F2",
      "status": "partial",
      "evidence": "exhausted, could not sleep. In the dark she mistook a window for a framed portrait... watching her."
    },
    {
      "id": "C3.F1",
      "status": "covered",
      "evidence": "In the morning the watcher was gone—the “portrait” was no longer there—and she realized the truth... That realization terrified her, and she fled the house."
    },
    {
      "id": "C3.F2",
      "status": "covered",
      "evidence": "Eventually she fell asleep from exhaustion. In the morning the watcher was gone—the “portrait” was no longer there"
    },
    {
      "id": "C3.F3",
      "status": "covered",
      "evidence": "she realized the truth: there had been no painting, only a window, and a real person had been staring in at her through the night. That realization terrified her, and she fled the house."
    }
  ],
  "requirement_coverage": [],
  "contradictions": [],
  "partial_score": 0.85,
  "complete": false,
  "label": "yes and no",
  "grading_protocol": "coverage-v3-unified",
  "controller_corrections": []
}
```
</details>

## 34 · question

Was the figure outside the window a man?

Host: irrelevant

## 35 · question

Was the girl's terror mainly because she realized the house was not truly empty—someone had been there or watching?

Host: yes

## 36 · question

Had the person entered the house during the night, rather than merely being outside the window?

Host: no

## 37 · question

Was the missing “portrait” actually the person outside leaving their position at the window, so that in the morning she saw the glass was only a window—proving someone had been there?

Host: yes

## 38 · question

Is there any additional twist beyond the mistaken “portrait” being a window with a real watcher outside—such as the watcher being connected to the girl or the house?

Host: no

## 39 · question

Was the terror specifically because she realized she had been watched while she slept, helpless and unaware?

Host: yes

## 40 · final

The lost girl found what seemed an empty house and, exhausted, could not sleep. In the darkness she mistook a window opposite her for a framed portrait: the “face” in it was actually a real person outside, watching her. Eventually exhaustion made her fall asleep. In the morning the face was gone, the “portrait” was revealed to be only a window, and she understood that the watcher had been a real intruder-observer who had stared in at her—and that she had been watched while she slept, helpless and unaware. That realization terrified her, and she fled the house.

Host: yes and no

<details><summary>Private evaluator result (not sent to player)</summary>

```json
{
  "checkpoints": [
    {
      "id": "C1",
      "credit": 1,
      "evidence": "In the darkness she mistook a window opposite her for a framed portrait: the “face” in it was actually a real person outside, watching her.",
      "reason": "Clearly covers that the apparent portrait was actually a window with a real person behind it, and that the girl took shelter and mistook the window for a portrait."
    },
    {
      "id": "C2",
      "credit": 0.5,
      "evidence": "The lost girl found what seemed an empty house and, exhausted, could not sleep. In the darkness she mistook a window opposite her for a framed portrait: the “face” in it was actually a real person outside, watching her.",
      "reason": "Includes the inability to sleep and the watching figure mistaken for a portrait, but omits the causal qualifier that mistaking the watcher for a portrait made her uneasy and that feeling watched kept her awake."
    },
    {
      "id": "C3",
      "credit": 1,
      "evidence": "In the morning the face was gone, the “portrait” was revealed to be only a window, and she understood that the watcher had been a real intruder-observer who had stared in at her... That realization terrified her, and she fled the house.",
      "reason": "Covers the morning absence, the revelation of the window, and the realization causing terror and flight."
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
      "evidence": "she mistook a window opposite her for a framed portrait: the “face” in it was actually a real person outside, watching her"
    },
    {
      "id": "C1.F2",
      "status": "covered",
      "evidence": "The lost girl found what seemed an empty house ... she mistook a window opposite her for a framed portrait: the “face” in it was actually a real person outside"
    },
    {
      "id": "C2.F1",
      "status": "partial",
      "evidence": "The lost girl found what seemed an empty house and, exhausted, could not sleep. In the darkness she mistook a window opposite her for a framed portrait: the “face” in it was actually a real person outside, watching her."
    },
    {
      "id": "C2.F2",
      "status": "partial",
      "evidence": "The lost girl found what seemed an empty house and, exhausted, could not sleep. ... she mistook a window opposite her for a framed portrait: the “face” in it was actually a real person outside, watching her."
    },
    {
      "id": "C3.F1",
      "status": "covered",
      "evidence": "In the morning the face was gone, the “portrait” was revealed to be only a window ... That realization terrified her, and she fled the house."
    },
    {
      "id": "C3.F2",
      "status": "covered",
      "evidence": "Eventually exhaustion made her fall asleep. In the morning the face was gone, the “portrait” was revealed to be only a window"
    },
    {
      "id": "C3.F3",
      "status": "covered",
      "evidence": "the “portrait” was revealed to be only a window, and she understood that the watcher had been a real intruder-observer who had stared in at her ... That realization terrified her, and she fled the house."
    }
  ],
  "requirement_coverage": [],
  "contradictions": [],
  "partial_score": 0.85,
  "complete": false,
  "label": "yes and no",
  "grading_protocol": "coverage-v3-unified",
  "controller_corrections": []
}
```
</details>

## 41 · question

In the morning, was the strange thing she noticed something other than the window/portrait—for example, a mark or sign on the window showing someone had been there?

Host: no

## 42 · question

Had the girl been sleeping in a room that was not actually part of the house she thought—e.g., a cellar, attic, or sealed room—which became obvious in the morning?

Host: no

## 43 · question

Was the strange thing she noticed that the “window” she had seen at night was now missing or different—e.g., boarded up, walled over, or not actually a window—revealing that the face could not have been outside?

Host: no

## 44 · question

Did she notice in the morning that the face she had seen was her own reflection—that there was no watcher outside, and the “strange thing” was a mirror-like window showing her sleeping self?

Host: no

## 45 · question

Was the strange thing that she was no longer alone in the house because the window had been opened or broken from the outside, showing the watcher had tried to enter?

Host: no

## 46 · question

Did she notice in the morning that the person she had mistaken for a portrait was actually inside the room the entire time—e.g., a corpse or living person who had been present all night?

Host: no

## 47 · question

Did she notice a change in the people or objects visible through the window in the morning—such as a group, vehicle, or structure that had not been evident at night?

Host: yes

## 48 · question

Was the change that the “house” she was in was actually not a house at all—e.g., it was surrounded by something outside (a forest, ruins, or a road) that revealed the truth?

Host: no

## 49 · question

Was the change she saw through the window that there were now other people outside—such as a search party, villagers, or people looking for her?

Host: no

## 50 · question

Was the change outside the window that the watcher was now with other people outside, or that the watcher had been joined by others?

Host: no

## 51 · question

Was the change outside the window something that revealed the location she was in—such as a town, landmark, or recognizable place she recognized and feared?

Host: no

## 52 · question

Was the change outside the window related to the weather or time passing—e.g., realizing she had slept far longer than she thought, or that it was not morning at all?

Host: no

## 53 · question

Was the change outside the window that the view showed something impossible or supernatural—such as the watcher still there though the house was clearly abandoned or ruins?

Host: no

## 54 · question

Was the thing outside the window in the morning a corpse or dead body?

Host: no

## 55 · question

Was the thing she saw outside the window in the morning a vehicle (such as a car, van, or cart) that had not been there before?

Host: no

## 56 · question

In the morning, were there fresh footprints or tracks outside the window showing someone had stood there watching her?

Host: irrelevant

## 57 · question

Was the change she noticed in the morning that the window area now showed a different scene because she had actually been seeing a reflection—e.g., the “outdoors” at night was the room reflected?

Host: no

## 58 · question

Was the thing she saw through the window in the morning the watcher, but now clearly dead, hanged, or otherwise horrifying?

Host: no

## 59 · question

Was the thing outside the window in the morning a group of people conducting some activity—such as a search, a ceremony, or a burial?

Host: no

## 60 · question

Was the thing outside the window in the morning a building, ruin, or structure that revealed the house was not where she thought—e.g., she was in a ruined or abandoned place?

Host: no

## 61 · question

Did she see in the morning that the figure she had taken for a portrait was still outside the window, but was now revealed to be something clearly non-human—such as an animal or a scarecrow?

Host: no

## 62 · question

Did she realize in the morning that the "window" was not a window at all but a mirror, and the person she had seen was inside the room?

Host: no

## 63 · question

Was the change she noticed in the morning that the view through the window showed the house was on a cliff, in a forest, or otherwise somewhere she could not escape from—making her flee in panic?

Host: no

## 64 · question

Was the thing outside the window in the morning the same watcher, but now in a position that made clear he had been watching her all night (such as still standing at the same spot, having stayed there)?

Host: no

## 65 · question

Did she notice in the morning that her own belongings or the room's contents showed signs of having been touched or searched by someone?

Host: no

## 66 · question

Was the change through the window that the watcher was now lying injured or collapsed outside, having been there through the night?

Host: no

## 67 · question

Was there a second figure or different person outside the window in the morning that had not been visible at night?

Host: no

## 68 · question

Was the change she saw that there were now many more windows or openings in the house than she had perceived at night, making the "empty house" feel wrong?

Host: no

## 69 · question

Did the view through the window in the morning reveal a road or path leading away, and something on it that terrified her?

Host: no

## 70 · question

Did the “change” she saw through the window involve the watcher's body being unnaturally positioned or having moved impossibly—e.g., now hanging or floating—since she fell asleep?

Host: no

## 71 · question

Was the thing filling the window in the morning actually a frightening face or figure pressed against the glass from outside, still watching her?

Host: no

## 72 · question

Did she realize the “empty house” was not empty because she found evidence of someone currently living there—such as food, bedding, or fresh signs of habitation—when she woke?

Host: no

## 73 · question

Was the thing she noticed in the morning related to the window showing the face of someone she knew or recognized?

Host: no

## 74 · question

Did she notice in the morning that the face she had seen at night was still outside but had been there so long it was clearly dead—e.g., a body propped up and staring in?

Host: no

## 75 · question

Was the change she noticed that the house's exterior, visible through the window, was different from what she expected—e.g., she was on an upper floor when she thought she was on the ground floor?

Host: no

## 76 · question

Did she notice in the morning that the window through which she had seen the face was now open, or that it had no glass—so the man could have reached in?

Host: no

## 77 · question

Was the "strange thing" she noticed that there was now daylight coming through where the portrait had been—revealing it as a window onto the outside?

Host: no

## 78 · question

Did she in the morning see that the face from the "portrait" belonged to a person who was now inside the house with her?

Host: no

## 79 · question

Was the thing outside the window in the morning a large number of faces or watchers—more than the single figure she had seen at night?

Host: no

## 80 · question

Was the "picture" actually a window, and the figure she saw was a real person outside who was not watching her but was something else—such as a statue, corpse, or figure from the house's history?

Host: yes and no

## 81 · question

Did the figure outside turn out to be someone who was dead by morning—dying or already dead during the night?

Host: no

## 82 · question

Was the “change” she saw that the window no longer showed the face because the figure outside had been a reflection of someone inside the house who had now left?

Host: no

## 83 · question

Was the house actually occupied by someone who was hiding, and in the morning she saw signs that revealed they were there—causing her to flee?

Host: no

## 84 · question

Was the thing she noticed in the morning connected to the window being a mirror—e.g., she saw the room reflected and realized the “watchful face” had been in the room?

Host: no

## 85 · question

Did she notice in the morning that the “window” was still covered with a picture or curtain, meaning the face she thought she saw outside was actually something else entirely?

Host: no

## 86 · question

Did she see in the morning that the face outside the window belonged to someone who was wearing a mask or disguise, and this revealed something sinister?

Host: no

## 87 · question

Was the change outside the window that the figure had been replaced by something that showed the figure could not possibly have been there—such as a sheer drop, a high wall, or a locked courtyard?

Host: no

## 88 · question

Was the change outside the window that the outside world was now clearly a cemetery, with graves, and she had seen a figure among them?

Host: no

## 89 · question

Did she realize in the morning that the “face” was actually a face-shaped hole, mark, or stain in the window/wall, and that the watcher had never been real?

Host: no

## 90 · question

Was the strange thing she noticed the face of someone she had seen before—a person from her past or someone who should be dead?

Host: no

## 91 · question

Was the thing outside the window in the morning something that had been there all night but she only now recognized—such as the watcher being a known criminal or a wanted person?

Host: no

## 92 · question

Was the change she saw through the window that the watcher was now standing next to a vehicle or carrying something that revealed his intentions—such as a weapon or tools to break in?

Host: no

## 93 · question

Was the strange thing she noticed that the room had two windows—or that the “window” was opposite a second opening—so that she had been watched from more than one side?

Host: no

## 94 · question

Was the change she noticed that the “portrait”/window was not outside at all but showed a face in an adjacent room, and in the morning she saw that room was occupied?

Host: no

## 95 · question

Was the strange thing outside the window in the morning that the watcher had been joined by something like an animal or a child?

Host: no

## 96 · question

Was the view outside the window in the morning actually a painted backdrop or mural, revealing that the “outside” was fake and the house was a trap?

Host: no

## 97 · question

Was the strange thing she noticed that the sun rose in a direction or way that revealed she was not in the countryside anymore—i.e., the house was somewhere else?

Host: no

## 98 · question

Was the strange thing she noticed through the window that the watcher's face was actually a death mask or preserved face, not a living person?

Host: no

## 99 · question

Was the strange thing that she could see the watcher's face outside the window in the morning, but there was no ground or space for a person to stand there—meaning he was pressed against the glass from an impossible position?

Host: no

## 100 · final · mandatory final

The lost girl took shelter in what seemed an empty house. Exhausted but unable to sleep, she saw in the dim room what she took to be a portrait—actually a window—with a face in it, which was a real person outside watching her. In the morning, having finally fallen asleep, she noticed something had changed outside that window: the watcher was no longer simply a single face at the glass. The night’s “portrait” had not been decor but a real observer, and the morning view revealed the truth of what she had been looking at through the night. Realizing that someone had been outside staring in at her while she slept, she fled the house in terror.

Host: yes and no

<details><summary>Private evaluator result (not sent to player)</summary>

```json
{
  "checkpoints": [
    {
      "id": "C1",
      "credit": 1,
      "evidence": "The lost girl took shelter in what seemed an empty house. Exhausted but unable to sleep, she saw in the dim room what she took to be a portrait—actually a window—with a face in it, which was a real person outside watching her.",
      "reason": "Covers the apparent portrait as a window with a real person behind it, and the girl taking shelter and mistaking the window for a portrait."
    },
    {
      "id": "C2",
      "credit": 0.5,
      "evidence": "Exhausted but unable to sleep, she saw in the dim room what she took to be a portrait—actually a window—with a face in it, which was a real person outside watching her.",
      "reason": "Includes the inability to sleep and the watching figure mistaken for a portrait, but omits the causal qualifier that mistaking the watcher for a portrait made her uneasy and that feeling watched kept her awake."
    },
    {
      "id": "C3",
      "credit": 0.5,
      "evidence": "In the morning, having finally fallen asleep, she noticed something had changed outside that window: the watcher was no longer simply a single face at the glass. ... Realizing that someone had been outside staring in at her while she slept, she fled the house in terror.",
      "reason": "Covers falling asleep, a morning change, the window realization, and flight, but only partially covers the required fact that the figure/person was gone in the morning; it is left ambiguous rather than explicitly stated."
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
      "evidence": "what she took to be a portrait—actually a window—with a face in it, which was a real person outside watching her"
    },
    {
      "id": "C1.F2",
      "status": "covered",
      "evidence": "The lost girl took shelter in what seemed an empty house. ... she saw in the dim room what she took to be a portrait—actually a window—with a face in it, which was a real person outside watching her."
    },
    {
      "id": "C2.F1",
      "status": "partial",
      "evidence": "Exhausted but unable to sleep, she saw in the dim room what she took to be a portrait—actually a window—with a face in it, which was a real person outside watching her."
    },
    {
      "id": "C2.F2",
      "status": "partial",
      "evidence": "Exhausted but unable to sleep, ... she took to be a portrait ... a real person outside watching her."
    },
    {
      "id": "C3.F1",
      "status": "partial",
      "evidence": "In the morning, having finally fallen asleep, she noticed something had changed outside that window: the watcher was no longer simply a single face at the glass. ... Realizing that someone had been outside staring in at her while she slept, she fled the house in terror."
    },
    {
      "id": "C3.F2",
      "status": "partial",
      "evidence": "In the morning, having finally fallen asleep, ... the watcher was no longer simply a single face at the glass."
    },
    {
      "id": "C3.F3",
      "status": "covered",
      "evidence": "what she took to be a portrait—actually a window—with a face in it ... The night’s “portrait” had not been decor but a real observer ... Realizing that someone had been outside staring in at her while she slept, she fled the house in terror."
    }
  ],
  "requirement_coverage": [],
  "contradictions": [],
  "partial_score": 0.75,
  "complete": false,
  "label": "yes and no",
  "grading_protocol": "coverage-v3-unified",
  "controller_corrections": []
}
```
</details>
