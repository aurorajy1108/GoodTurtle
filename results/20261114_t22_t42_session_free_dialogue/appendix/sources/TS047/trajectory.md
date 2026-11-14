# Turtle Soup trajectory

The Guesthouse Portrait. A reporter visiting the countryside stays in a shabby guesthouse. In the dim room, there is a picture opposite her bed. The next morning, she is stunned. Why?

Status: completed | counted questions: 100 | submissions: 100 | final partial score: 0.8

[Token usage and estimated costs](token_costs.csv)

## 1 · question

Is the picture a portrait of the reporter herself?

Host: no

## 2 · question

Is the picture changed or different in the morning compared to what she saw the night before?

Host: yes

## 3 · question

Was the picture in the dim room difficult to see clearly the night before?

Host: yes

## 4 · question

In the morning, does the picture appear to depict something disturbing or gruesome that she could not discern in the dim light?

Host: no

## 5 · question

In the morning, does the picture show something that was not visible in the dim light, such as a hidden figure or detail?

Host: yes

## 6 · question

Is that newly visible detail related to the guesthouse or its owners in a way that frightens her?

Host: irrelevant

## 7 · question

Was the picture actually a window or mirror rather than a painting?

Host: yes

## 8 · question

Was it actually a window (rather than a mirror)?

Host: yes

## 9 · question

Was there something outside the window, visible in daylight, that she could not see the night before?

Host: yes

## 10 · question

Was the thing outside the window a person?

Host: yes

## 11 · question

Was the person outside the window someone the reporter recognized?

Host: irrelevant

## 12 · question

Was the person outside dead or otherwise alarming, such as a corpse or hanging figure?

Host: yes

## 13 · question

Was the person a corpse?

Host: no

## 14 · question

Was the person hanging (e.g., from a gallows or tree) outside the window?

Host: no

## 15 · question

Was the alarming person outside the window still alive but in grave danger?

Host: yes and no

## 16 · question

Did the person outside the window appear to be dead in a way other than being a corpse or hanging (for example, a ghost or figure in a graveyard)?

Host: no

## 17 · question

Was the person outside the window a figure depicted on a tombstone or grave marker?

Host: no

## 18 · question

Was the "person" outside actually a statue or figure that merely looked like a person?

Host: no

## 19 · question

Was the person outside in a state of distress, such as trapped, injured, or dying?

Host: no

## 20 · question

Was the person outside actually a live human being who was unaware they were being observed?

Host: yes and no

## 21 · question

Was the alarming quality due to the person being unable to see or be seen (e.g., the reporter realizes the person is on the other side of a glass but not a real window)?

Host: no

## 22 · question

Is the "window" actually looking into another interior room rather than outdoors?

Host: no

## 23 · question

Is the newly visible person outside someone who died or was killed in the guesthouse, making the scene uncanny?

Host: no

## 24 · question

Was the person outside actually the reporter's own reflection visible only in daylight?

Host: no

## 25 · question

Is the picture/window actually painted or boarded so that it only appears to be a view, and in the morning she sees it is a painting?

Host: no

## 26 · question

Was the person outside alive and moving, and alarming because they were behaving strangely (such as staring in at her)?

Host: yes

## 27 · question

Was the person outside staring in at her through the window?

Host: yes

## 28 · question

Had the person outside been watching her while she slept during the night?

Host: yes

## 29 · question

Was the person outside someone connected to the guesthouse (an owner or staff member)?

Host: irrelevant

## 30 · question

Did the reporter mistake the window for a picture because it was dark and perhaps curtained or framed?

Host: yes

## 31 · question

Was the window framed in a way that made it look specifically like a framed picture hanging on the wall?

Host: irrelevant

## 32 · question

Was there also a real painting or portrait in the room, so that the "picture" she saw at night was a painting but in the morning the window revealed the person?

Host: no

## 33 · question

Does the word "picture" in the story refer to the window viewed as if it were a picture?

Host: yes

## 34 · question

Was the window covered or curtained at night so it truly looked like a picture, and in the morning the curtain was open revealing the scene outside?

Host: no

## 35 · question

Is it simply that the "picture" is a window, through which in dim light she saw only a dark pane (perhaps her own dim reflection), and in daylight she sees a stranger's face staring in at her?

Host: no

## 36 · question

At night, did the window appear to show an outdoor scene (landscape), like a painted picture, while in the morning she saw it was a person at the glass?

Host: no

## 37 · question

Was the person outside actually pressed against or very close to the window, so that in the dark she saw only a reflection of the room, not the person?

Host: no

## 38 · question

Did the reporter at first believe the window was a painted portrait of a person (a face), and in the morning realize it was a real person looking in?

Host: yes

## 39 · question

At night, was the glass acting as a mirror, so what she took to be a painted face in a "picture" was actually the reflection of the watcher's (or her own) face?

Host: no

## 40 · question

In the dim light, could she see a face in the "picture," and in the morning she realized that face was a real person outside the window?

Host: yes

## 41 · final

The "portrait" opposite the reporter's bed was not a painting but a window. In the dim light of the shabby room, she saw a face in what she took to be a picture. In the morning, with better light and the scene now clear, she was stunned to realize the face belonged to a real person outside the window, who had been staring in at her—and had been watching her as she slept during the night.

Host: yes and no

<details><summary>Private evaluator result (not sent to player)</summary>

```json
{
  "checkpoints": [
    {
      "id": "C1",
      "credit": 1,
      "evidence": "\"portrait\" ... was not a painting but a window ... face belonged to a real person outside the window",
      "reason": "Both required facts are covered: the apparent portrait is a window with a real man outside, and in dim light she mistakes that for a picture/portrait."
    },
    {
      "id": "C2",
      "credit": 1,
      "evidence": "In the dim light of the shabby room, she saw a face in what she took to be a picture",
      "reason": "Covers that dim light causes the window/man to be mistaken for a portrait/picture."
    },
    {
      "id": "C3",
      "credit": 0,
      "evidence": "had been watching her as she slept during the night",
      "reason": "The submission says the man watched her during the night, but it does not state she felt watched or avoided looking at the apparent picture; both required facts are missing."
    },
    {
      "id": "C4",
      "credit": 1,
      "evidence": "In the morning, with better light and the scene now clear, she was stunned to realize the face belonged to a real person outside the window",
      "reason": "Covers that daylight reveals the window/real watcher and explains her shock."
    }
  ],
  "material_contradiction": false,
  "irrelevant": false,
  "rubric_conflict": false,
  "full_solution": false,
  "completion_note": "Scored facts remain missing, partial or contradicted; see fact_coverage.",
  "contradictions": [],
  "fact_coverage": [
    {
      "id": "C1.F1",
      "status": "covered",
      "evidence": "The \"portrait\" opposite the reporter's bed was not a painting but a window. In the morning, with better light and the scene now clear, she was stunned to realize the face belonged to a real person outside the window"
    },
    {
      "id": "C1.F2",
      "status": "covered",
      "evidence": "In the dim light of the shabby room, she saw a face in what she took to be a picture"
    },
    {
      "id": "C2.F1",
      "status": "covered",
      "evidence": "In the dim light of the shabby room, she saw a face in what she took to be a picture"
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
      "id": "C4.F1",
      "status": "covered",
      "evidence": "In the morning, with better light and the scene now clear, she was stunned to realize the face belonged to a real person outside the window"
    },
    {
      "id": "C4.F2",
      "status": "covered",
      "evidence": "In the morning, with better light and the scene now clear, she was stunned to realize the face belonged to a real person outside the window"
    }
  ],
  "requirement_coverage": [],
  "partial_score": 0.8,
  "complete": false,
  "label": "yes and no",
  "grading_protocol": "coverage-v3-unified",
  "controller_corrections": [
    {
      "field": "requirement_coverage",
      "action": "remove_verified_unscored_checkpoint_aliases",
      "model": [
        {
          "id": "C1",
          "status": "covered",
          "evidence": "The \"portrait\" opposite the reporter's bed was not a painting but a window. In the dim light of the shabby room, she saw a face in what she took to be a picture."
        },
        {
          "id": "C2",
          "status": "covered",
          "evidence": "In the dim light of the shabby room, she saw a face in what she took to be a picture"
        },
        {
          "id": "C3",
          "status": "missing",
          "evidence": ""
        },
        {
          "id": "C4",
          "status": "covered",
          "evidence": "In the morning, with better light and the scene now clear, she was stunned to realize the face belonged to a real person outside the window"
        }
      ],
      "effective": [],
      "response_id": "01368966-b23e-4708-b489-3596f4367a3e",
      "judgments_changed": false,
      "source_sha256": "b890829afd61e68ec68490ccc0089c86430a1f6f99481ceb9f339193046c9a15"
    }
  ],
  "coverage_completion": {
    "added_fields": [
      "contradictions",
      "fact_coverage",
      "requirement_coverage"
    ],
    "original_checkpoint_credits": {
      "C1": 1,
      "C2": 1,
      "C3": 0,
      "C4": 1
    },
    "judgments_changed": false,
    "coverage_completion_calls": 1
  }
}
```
</details>

## 42 · question

Was the face she saw in the "picture" at night actually a face painted or printed on the glass itself (such as a decal or painted portrait on the window)?

Host: no

## 43 · question

Was the face in the picture at night a painted portrait that was actually hung on or over the window, which she mistook for the view through it?

Host: no

## 44 · question

Was the "face" actually a real person's face visible through the window, but the person was not a stranger—rather, the guesthouse owner or someone who had a legitimate reason to be there, making the alarm about something else?

Host: no

## 45 · question

Was the person outside the window not simply a peeping observer, but someone in a position that should have been impossible—such as being on an upper floor with no ledge, or suspended outside?

Host: no

## 46 · question

Was the reporter's room on an upper floor?

Host: irrelevant

## 47 · question

Was there only a thin glass between the reporter and the watcher, so the alarming realization was that the watcher could see her clearly while she had thought the "picture" was harmless decor?

Host: yes

## 48 · question

Was the figure she saw at night actually situated inside the room with her (e.g., reflected or framed within the window area), rather than outside?

Host: no

## 49 · question

Was the watcher still there in the morning when she looked?

Host: yes and no

## 50 · question

Was the watcher gone by the morning, leaving only evidence that someone had been there?

Host: yes and no

## 51 · question

Was the face she saw at night a reflection in the glass of someone standing behind her in the room?

Host: no

## 52 · question

Did she in the morning realize that the "picture" had been a window, and that she had been observed—rather than the watcher still being present?

Host: yes

## 53 · question

Was the face in the "picture" at night actually just a face-like image formed by something ordinary (e.g., marks, shadows, or objects behind the glass), rather than a real person?

Host: no

## 54 · question

Was the person outside a man?

Host: yes

## 55 · question

Did the reporter recognize the man's face in the morning?

Host: irrelevant

## 56 · question

Was the man's face visible in the morning because he was outside in daylight, whereas at night only his reflection or a dim shape showed?

Host: yes and no

## 57 · question

In the morning, was the man no longer outside the window?

Host: yes and no

## 58 · question

In the morning, did she see the man outside the window but no longer staring in at her (e.g., he was now doing something ordinary, revealing that he lives/works there)?

Host: yes and no

## 59 · question

Is the key twist that the room's "window" was actually a mirror, and the "portrait" she saw was her own reflection—but in the morning, a man's reflection revealed he was in the room?

Host: no

## 60 · question

Was the window's outside view completely blocked or obscured at night, so the "portrait" was what she saw when looking at the glass—meaning her first interpretation of a face was based on something other than the actual view?

Host: no

## 61 · question

In the morning, did she realize that what she had taken to be a picture was a window, and that a man's face had been at that window—whether still present or not?

Host: yes

## 62 · question

Was the man's face still at the window in the morning?

Host: yes and no

## 63 · question

In the morning, was the man's face visible at that same window as part of the view—such as a face painted on a wall, sign, or object outside—rather than the living man himself?

Host: no

## 64 · question

Did the man die or disappear during the night, so in the morning his face was gone but she understood it had been there?

Host: yes and no

## 65 · question

Was the "picture" fitted with glass that reflected the man standing behind the reporter in the room, so in the morning she realized someone had been inside her room?

Host: no

## 66 · question

Did she in the morning notice that the window (which she had thought a picture) overlooked a graveyard or cemetery?

Host: irrelevant

## 67 · question

Was the reporter's sense of alarm in the morning primarily because she realized she had been watched through the night by a man at the window?

Host: yes

## 68 · question

Was the man at the window in fact not a stranger, but someone visible from the room's other side—such as a companion or the guesthouse keeper's relative—making the initial "portrait" interpretation a genuine mistake?

Host: yes and no

## 69 · question

Was the man outside the window a patient or inmate from a nearby institution (e.g., an asylum)?

Host: irrelevant

## 70 · question

In the morning, did she realize the man was a real person rather than part of a picture—and that he had been watching her while she slept—even if he was no longer there?

Host: yes

## 71 · final

The picture opposite the bed was not a painting but a window, its glass and dimness making it look like a framed portrait in the poor light. What she took for a painted face was a real man outside the glass. He had been staring in at her, and had watched her while she slept through the night. In the morning, the better light and the changed appearance of the "picture" revealed the truth: it was a window, and the face belonged to a real intruder-observer, so she was stunned to realize she had been watched.

Host: yes and no

<details><summary>Private evaluator result (not sent to player)</summary>

```json
{
  "checkpoints": [
    {
      "id": "C1",
      "credit": 1,
      "evidence": "\"not a painting but a window ... a real man outside the glass\"",
      "reason": "Both required facts are covered: the apparent portrait is a window with a real man outside, and in poor light she mistakes that for a painted face/portrait."
    },
    {
      "id": "C2",
      "credit": 1,
      "evidence": "\"its glass and dimness making it look like a framed portrait in the poor light\"",
      "reason": "Covers that dim light makes the window/man seem a portrait."
    },
    {
      "id": "C3",
      "credit": 0,
      "evidence": "\"He had been staring in at her, and had watched her while she slept through the night\"",
      "reason": "The submission says the man watched her during the night, but it does not state she felt watched or avoided looking at the apparent picture; both required facts are missing."
    },
    {
      "id": "C4",
      "credit": 1,
      "evidence": "\"In the morning, the better light and the changed appearance of the \\\"picture\\\" revealed the truth ... so she was stunned to realize she had been watched\"",
      "reason": "Covers that daylight reveals the window/real watcher and explains her shock."
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
      "evidence": "not a painting but a window ... a real man outside the glass"
    },
    {
      "id": "C1.F2",
      "status": "covered",
      "evidence": "its glass and dimness making it look like a framed portrait in the poor light ... What she took for a painted face was a real man outside the glass"
    },
    {
      "id": "C2.F1",
      "status": "covered",
      "evidence": "its glass and dimness making it look like a framed portrait in the poor light"
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
      "id": "C4.F1",
      "status": "covered",
      "evidence": "In the morning, the better light and the changed appearance of the \"picture\" revealed the truth ... so she was stunned to realize she had been watched"
    },
    {
      "id": "C4.F2",
      "status": "covered",
      "evidence": "In the morning, the better light and the changed appearance of the \"picture\" revealed the truth: it was a window, and the face belonged to a real intruder-observer, so she was stunned to realize she had been watched"
    }
  ],
  "requirement_coverage": [],
  "contradictions": [],
  "partial_score": 0.8,
  "complete": false,
  "label": "yes and no",
  "grading_protocol": "coverage-v3-unified",
  "controller_corrections": []
}
```
</details>

## 72 · question

Was the man outside the window actually a dead body propped up or positioned to stare in, which she only recognized as dead in the morning?

Host: no

## 73 · question

Was the man at the window actually a living person who was unaware he was being seen—so he was not deliberately watching the reporter, and her fear of being watched was a misunderstanding?

Host: no

## 74 · question

Was the man outside the window in some way unable to leave that spot—such as being trapped, stuck, or otherwise immobilized there—so that he had been there all night?

Host: no

## 75 · question

Was the man outside the window a real person who was still there in the morning, but no longer with his face at the window—so she saw him doing something else and realized he was not a portrait?

Host: yes and no

## 76 · question

Was the man in the morning no longer in the same position because he had moved on or left, and what remained at the window was not him but evidence of him (such as a smudge, handprint, or marks on the glass)?

Host: yes and no

## 77 · question

Did the man outside the window leave behind physical evidence on or around the window that proved he had been there?

Host: irrelevant

## 78 · question

Was the man outside the window in the morning in a completely different, ordinary context that revealed a mundane explanation—such as a workman on a ladder or scaffold, whose face had been close to the glass at night?

Host: no

## 79 · question

Was the man visible at the window actually a figure who was there only briefly—present when she first looked at night, but gone by morning—so the "picture" changed from showing him to showing an empty view?

Host: yes and no

## 80 · question

Was the man outside the window still there watching her in the morning when she looked, and that is why she was stunned?

Host: yes and no

## 81 · question

Did the reporter in the morning realize that the face she had seen at night was her own reflection—that the "portrait" was a mirror, and a man had been standing behind her?

Host: no

## 82 · question

Was the face she mistook for a portrait the face of a man who was outside during the night looking in, but by morning the "picture" revealed something different—such as that the window looked directly onto a spot where a man had died or been killed?

Host: yes

## 83 · question

Had the man died or been killed during the night while at that spot outside the window?

Host: no

## 84 · question

Did the window look onto a spot where the man had died or been killed before the reporter's stay—so his face at the glass was not a live watcher but something connected to that earlier death?

Host: no

## 85 · question

In daylight, did she see that the view from the window included a grave, tombstone, or memorial connected to a man—so the “face” at the glass was a coincidence mistaken for a portrait?

Host: no

## 86 · question

Was the "picture" actually a window, and the man she saw at night was not looking in at all—he was visible through the window as someone on the grounds, and what stunned her was the realization that the "portrait" was actually a view of a man who had been there outside?

Host: yes and no

## 87 · question

Did the reporter believe at night that the face belonged to a portrait hanging in her room, and in the morning realize that the room had no such portrait—that it was a window and a real man had been outside it?

Host: yes

## 88 · question

Had the man outside the window gone away by morning, so that the window no longer showed a face and she was left with the realization of what she had seen?

Host: yes and no

## 89 · question

In the morning, was the man still outside the window but in a position or state that made clear he was not merely a portrait—for example, moving, working, or looking in?

Host: yes and no

## 90 · question

Is the core reason she was stunned that she realized she had mistaken a window for a picture, and that the face she saw in it was a real man outside?

Host: yes

## 91 · question

Did she also realize that the man she had seen had been looking directly at her, so she had been watched?

Host: yes

## 92 · question

Had the man been watching her specifically while she slept, as opposed to only while she was awake and looking at the window?

Host: irrelevant

## 93 · final

The shabby guesthouse room was dim, and opposite the bed was what the reporter took to be a framed picture—actually a window. In the poor light the glass showed a face, which she assumed was a painted portrait. In the morning she realized there was no portrait: it was a window, and the face had belonged to a real man outside. He had been staring in at her, and his scrutiny meant she had been watched through the window she mistook for harmless wall decor. That realization—that the “portrait” was a real observer—was what stunned her.

Host: yes and no

<details><summary>Private evaluator result (not sent to player)</summary>

```json
{
  "checkpoints": [
    {
      "id": "C1",
      "credit": 1,
      "evidence": "opposite the bed was what the reporter took to be a framed picture—actually a window ... the face had belonged to a real man outside",
      "reason": "Both required facts are covered: the apparent portrait is a window with a real man outside, and in poor light she mistakes that for a painted portrait."
    },
    {
      "id": "C2",
      "credit": 1,
      "evidence": "In the poor light the glass showed a face, which she assumed was a painted portrait",
      "reason": "Covers that dim light makes the window/man seem a portrait."
    },
    {
      "id": "C3",
      "credit": 0,
      "evidence": "He had been staring in at her, and his scrutiny meant she had been watched through the window",
      "reason": "The submission says the man watched her, but it does not state she felt watched or avoided looking at the apparent picture; both required facts are missing."
    },
    {
      "id": "C4",
      "credit": 1,
      "evidence": "In the morning she realized there was no portrait: it was a window, and the face had belonged to a real man outside ... That realization ... was what stunned her",
      "reason": "Covers that daylight reveals the window/real watcher and explains her shock."
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
      "evidence": "opposite the bed was what the reporter took to be a framed picture—actually a window ... the face had belonged to a real man outside"
    },
    {
      "id": "C1.F2",
      "status": "covered",
      "evidence": "opposite the bed was what the reporter took to be a framed picture—actually a window. In the poor light the glass showed a face, which she assumed was a painted portrait ... the face had belonged to a real man outside"
    },
    {
      "id": "C2.F1",
      "status": "covered",
      "evidence": "In the poor light the glass showed a face, which she assumed was a painted portrait"
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
      "id": "C4.F1",
      "status": "covered",
      "evidence": "In the morning she realized there was no portrait: it was a window, and the face had belonged to a real man outside ... That realization ... was what stunned her"
    },
    {
      "id": "C4.F2",
      "status": "covered",
      "evidence": "In the morning she realized there was no portrait: it was a window, and the face had belonged to a real man outside. He had been staring in at her ... That realization—that the “portrait” was a real observer—was what stunned her"
    }
  ],
  "requirement_coverage": [],
  "contradictions": [],
  "partial_score": 0.8,
  "complete": false,
  "label": "yes and no",
  "grading_protocol": "coverage-v3-unified",
  "controller_corrections": []
}
```
</details>

## 94 · question

Was the absence of a real painting/portrait in the room the specific thing she noticed in the morning—i.e., the “picture” was simply the window and no framed artwork existed?

Host: yes

## 95 · question

Was the thing that stunned her in the morning primarily the fact that she had been observed through the night by a man at the window?

Host: yes

## 96 · question

Was the man still present outside the window in the morning when she made this realization?

Host: yes and no

## 97 · question

Did she become aware in the morning that the man had been very close to the glass—so close that she could see his face clearly enough to mistake it for a painted portrait?

Host: irrelevant

## 98 · question

Did the man outside the window leave by morning, so that when she looked she saw only the ordinary view and understood a real man had been there during the night?

Host: yes and no

## 99 · question

Was the “picture” so positioned that, when she woke in the morning, sunlight or daylight revealed it was a window she had previously seen only as a dark rectangle with a face in it?

Host: yes

## 100 · final · mandatory final

The “picture” opposite the reporter’s bed was not a painting but a window, which in the dim, shabby room looked like a dark framed portrait. In the glass she saw a face and took it to be a painted portrait. In the morning, with daylight, she realized there was no picture or hanging there at all: it was a window, and the face had belonged to a real man outside who had been staring in at her. His face close to the glass had made the “portrait” seem real. The stunning realization was that she had been watched through the night by a living observer, not looking at harmless wall decor.

Host: yes and no

<details><summary>Private evaluator result (not sent to player)</summary>

```json
{
  "checkpoints": [
    {
      "id": "C1",
      "credit": 1,
      "evidence": "The “picture” opposite the reporter’s bed was not a painting but a window ... the face had belonged to a real man outside",
      "reason": "Both required facts are covered: the apparent portrait is a window with a real man outside, and in poor light she mistakes that for a painted portrait."
    },
    {
      "id": "C2",
      "credit": 1,
      "evidence": "in the dim, shabby room looked like a dark framed portrait",
      "reason": "Covers that dim light makes the window/man seem a portrait."
    },
    {
      "id": "C3",
      "credit": 0,
      "evidence": "she had been watched through the night by a living observer",
      "reason": "The submission says she was watched, but it does not state she felt watched or avoided looking at the apparent picture; both required facts are missing."
    },
    {
      "id": "C4",
      "credit": 1,
      "evidence": "In the morning, with daylight, she realized there was no picture or hanging there at all: it was a window, and the face had belonged to a real man outside ... The stunning realization was that she had been watched through the night by a living observer",
      "reason": "Covers that daylight reveals the window/real watcher and explains her shock."
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
      "evidence": "not a painting but a window ... the face had belonged to a real man outside"
    },
    {
      "id": "C1.F2",
      "status": "covered",
      "evidence": "in the dim, shabby room looked like a dark framed portrait. In the glass she saw a face and took it to be a painted portrait ... the face had belonged to a real man outside"
    },
    {
      "id": "C2.F1",
      "status": "covered",
      "evidence": "in the dim, shabby room looked like a dark framed portrait"
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
      "id": "C4.F1",
      "status": "covered",
      "evidence": "In the morning, with daylight, she realized ... The stunning realization was that she had been watched through the night by a living observer"
    },
    {
      "id": "C4.F2",
      "status": "covered",
      "evidence": "In the morning, with daylight, she realized there was no picture or hanging there at all: it was a window, and the face had belonged to a real man outside ... The stunning realization was that she had been watched through the night by a living observer"
    }
  ],
  "requirement_coverage": [],
  "contradictions": [],
  "partial_score": 0.8,
  "complete": false,
  "label": "yes and no",
  "grading_protocol": "coverage-v3-unified",
  "controller_corrections": []
}
```
</details>
