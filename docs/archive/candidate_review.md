# English candidate review — 20 drafts

> SPOILERS: curator-only material. All stories are AI-assisted drafts; difficulty, novelty, human labels and release status remain unverified. Reference paths are illustrative, not empirical solver traces.

每题末尾列出重点审查风险；不通过就替换，不能为了凑齐 20 题而保留。JSON 是数据源，运行 `python3 scripts/prepare.py review` 可重新生成此文档。

## GT001 — The uncollected photograph

**Opening (solver-visible)**

A photographer was paid to take the same photograph every morning for a month. On the last morning, her client told her not to take it. She had already set up her camera, and the scene looked exactly as it had the day before. The client paid her in full and immediately ordered a repair. What had he noticed?

**Solution (private)**

The camera watched a mechanical date display in a shop window. The daily photographs were checking whether its automatic calendar advanced correctly. On the last morning, the printed date was still yesterday's date. That unchanged scene was itself evidence of the fault; another photograph was unnecessary for the client to decide to repair the calendar.

**Canonical facts**

- The subject was a mechanical calendar display in a shop window.
- The paid task was to check that its date advanced daily.
- On the final morning it still displayed the previous day's date.
- The client saw the unchanged date before the photographer took that day's picture.

**Explicitly false**

- Neither the camera nor its clock was faulty.
- No photograph was forged or substituted.

**Unspecified**

- The shop's business type is unspecified.

**Required elements — 1 / 0.5 / 0**

- E1: **1:** The photographs monitored an automatically changing date display. **0.5:** Identifies monitoring a changing display but not dates. **0:** Absent, or contradicted by the explanation.
- E2: **1:** The unchanged date across two mornings demonstrated failure to advance. **0.5:** Identifies a frozen display without explaining the two-day comparison. **0:** Absent, or contradicted by the explanation.
- E3: **1:** The client could already see the fault, so stopped documentation and ordered calendar repair. **0.5:** Connects the fault to repair but not stopping the photograph. **0:** Absent, or contradicted by the explanation.

**Illustrative question path**

- Was she documenting a device rather than a person? → `yes`
- Was the device supposed to change each day? → `yes`
- Did it display dates? → `yes`
- Was the camera broken? → `no`

**Mechanisms:** temporal_expectation, evidence_from_absence

**Review risk:** May be too easy once monitoring is guessed; direct-answer screen is essential.

## GT002 — The quiet complaint

**Opening (solver-visible)**

Every weekday, a woman complained about a noisy delivery outside her home. One morning the delivery was made silently. She immediately asked the company to make the noise again, even though she still wanted quiet mornings. Nothing had been delivered to the wrong address. Why?

**Solution (private)**

The company delivered to the shop below her flat. A heavy trolley rattled across a loose metal cover over a service opening in the shared entrance. Her complaints requested that the loose cover be fixed. That morning the company carried the same load across it by hand. She realised they had hidden the warning noise without fixing the unstable cover. She asked for one more trolley crossing while the building manager was present, to demonstrate the fault and obtain a repair.

**Canonical facts**

- The delivery trolley rattled over a loose metal cover in the shared entrance.
- Her complaints were about the fault as well as the resulting noise.
- The silent delivery used hand carrying; the cover was not repaired.
- She requested a demonstration crossing in front of the building manager.

**Explicitly false**

- She did not depend on the noise as an alarm.
- The delivery address was correct.

**Unspecified**

- The contents of the delivery are unspecified.

**Required elements — 1 / 0.5 / 0**

- E1: **1:** A loose cover rattled when the trolley crossed it. **0.5:** Mentions a defective surface but not trolley-induced noise. **0:** Absent, or contradicted by the explanation.
- E2: **1:** Silence came from bypassing the noisy method rather than repairing the cover. **0.5:** Recognises masking a defect without explaining the method. **0:** Absent, or contradicted by the explanation.
- E3: **1:** She wanted a witnessed demonstration to obtain the repair and eventual quiet. **0.5:** Identifies evidence gathering but not the long-term quiet objective. **0:** Absent, or contradicted by the explanation.

**Illustrative question path**

- Was the noise a symptom of a physical defect? → `yes`
- Had the defect been repaired? → `no`
- Was she asking for a demonstration? → `yes`
- Did she use the delivery as an alarm clock? → `no`

**Mechanisms:** symptom_vs_cause, demonstration

**Review risk:** Clarify the observable difference between hand carrying and trolley delivery during human play; avoid making intention an arbitrary guess.

## GT003 — Identical winners

**Opening (solver-visible)**

A sound engineer submitted two anonymous recordings to a listening panel. Every panellist gave the two recordings exactly the same score. The engineer discarded the results without listening to either recording. She had expected the recordings to sound identical. Why was agreement a problem?

**Solution (private)**

She had submitted the very same audio twice to test whether panellists would be influenced by descriptions. The two entries were described as using different equipment, but panellists were required to score each privately before discussion. When she collected the sheets, each panellist had also given identical written comments to the other panellists, including the same unusual crossed-out phrase. These copied comments revealed that the panel had shared one completed answer sheet. The matching scores alone were not the reason for rejection.

**Canonical facts**

- The two files contained identical audio.
- Different equipment descriptions were attached as part of a label-bias test.
- The instructions required independent scoring without discussion.
- All sheets copied the same unusual wording and crossed-out phrase from one completed sheet.
- The copied comments, not score equality by itself, caused rejection.

**Explicitly false**

- No audio fault caused the rejection.
- Equal scores would have been acceptable if independently produced.

**Unspecified**

- The musical content is unspecified.

**Required elements — 1 / 0.5 / 0**

- E1: **1:** Identical audio with different descriptions tested label influence. **0.5:** Recognises duplicate audio as a control. **0:** Absent, or contradicted by the explanation.
- E2: **1:** Independent judgements were required but panellists copied one sheet. **0.5:** Mentions prohibited collaboration without copying. **0:** Absent, or contradicted by the explanation.
- E3: **1:** Copied textual details revealed the violation; equal scores themselves were permissible. **0.5:** Identifies evidence beyond scores without naming comments. **0:** Absent, or contradicted by the explanation.

**Illustrative question path**

- Were the audio files identical? → `yes`
- Would independently equal scores have been acceptable? → `yes`
- Did she inspect written comments? → `yes`
- Did the panellists copy a completed answer sheet? → `yes`

**Mechanisms:** omitted_evidence, measurement_validity

**Review risk:** Key evidence is omitted from the opening; reviewers must check that investigating the rejection yields a fair path rather than arbitrary secret evidence.

## GT004 — The occupied chair

**Opening (solver-visible)**

At a meeting, an empty chair was recorded as occupied. Later, someone sat in it, and the chair was recorded as vacant. The records were accurate, the same chair was involved, and nobody was pretending to be someone else. What was being recorded?

**Solution (private)**

The meeting was a remote-access test. A labelled chair represented a participant's reserved speaking place, and the attendance log tracked who currently held that place in the meeting, not bodies on furniture. Initially its assigned participant was connected remotely, so the place was occupied. After she disconnected and relinquished it, a technician sat there to fix its microphone. The technician was not a participant and did not take the speaking place, so it remained vacant.

**Canonical facts**

- The log tracked assigned participant places, not physical seat occupancy.
- The assigned participant was initially connected remotely and held the place.
- She later disconnected and relinquished the place.
- A non-participant technician then sat in the physical chair to repair its microphone.

**Explicitly false**

- There was no impersonation.
- The chair was not replaced.

**Unspecified**

- The technician's gender is unspecified.

**Required elements — 1 / 0.5 / 0**

- E1: **1:** Occupancy referred to a participant place rather than physical seating. **0.5:** Identifies nonphysical occupancy without its precise meaning. **0:** Absent, or contradicted by the explanation.
- E2: **1:** The absent participant initially held the place through remote participation. **0.5:** Mentions remote attendance without the reserved place. **0:** Absent, or contradicted by the explanation.
- E3: **1:** After the participant left, a technician sat there without becoming a participant. **0.5:** Recognises that the sitter was not a participant but omits the transition. **0:** Absent, or contradicted by the explanation.

**Illustrative question path**

- Did occupied mean physically sitting down? → `no`
- Was a participant joining remotely? → `yes`
- Was the later sitter doing technical work? → `yes`
- Was the chair exchanged? → `no`

**Mechanisms:** reference_shift, institutional_status

**Review risk:** Potential lexical ambiguity: ensure the records' definition is stable and natural, not a post hoc redefinition.

## GT005 — The reversed notices

**Opening (solver-visible)**

Before a building exercise, a coordinator deliberately put the wrong room numbers on two doors. Everyone found the correct destination faster than before. She removed the incorrect numbers immediately afterwards. Why had misleading signs helped?

**Solution (private)**

The exercise trained telephone guides to direct visitors using a floor plan. Earlier guides had relied on visitors reading door numbers instead of describing the route. For a second practice run, the coordinator swapped two temporary number cards and told the guides beforehand that the cards were unreliable. This forced them to use landmarks and turns, which avoided a known confusing detour in their previous instructions. She removed the practice cards so ordinary visitors would not be misled later.

**Canonical facts**

- This was a supervised practice exercise for telephone guides.
- The guides knew before the second run that temporary door numbers were unreliable.
- Earlier number-dependent directions had led visitors on a confusing detour.
- Guides switched to accurate landmark-and-turn directions.
- The incorrect temporary cards were removed after practice.

**Explicitly false**

- This was not an emergency evacuation.
- The visitors did not reach the wrong destination.

**Unspecified**

- The building's location is unspecified.

**Required elements — 1 / 0.5 / 0**

- E1: **1:** The setting was a training exercise with advance warning to the guides. **0.5:** Identifies a drill without advance warning. **0:** Absent, or contradicted by the explanation.
- E2: **1:** Unreliable numbers forced a switch to landmark-based directions. **0.5:** Mentions a change in navigation strategy without why. **0:** Absent, or contradicted by the explanation.
- E3: **1:** The new directions avoided the previous detour; signs were temporary training props. **0.5:** Explains either the improvement or temporary removal, but not both. **0:** Absent, or contradicted by the explanation.

**Illustrative question path**

- Was this a practice exercise? → `yes`
- Did the guides know the signs were unreliable? → `yes`
- Did they start relying on landmarks? → `yes`
- Was anyone escaping a real fire? → `no`

**Mechanisms:** constraint_changes_strategy, training_context

**Review risk:** Hidden training rules are fairly elaborate; reject if humans cannot converge without leading questions.

## GT006 — The heavier empty box

**Opening (solver-visible)**

A woman emptied a box onto a table. She put nothing inside it afterwards, yet it weighed more when she weighed it again. Both measurements used the same accurate scales, and the box had not absorbed anything. Why?

**Solution (private)**

The box was a demonstration device with a false floor holding a small helium balloon on a short tether. At the first weighing the balloon had been released above the open box, pulling upward on the tether and partly supporting the box. She tipped the loose contents onto the table, then untied the balloon and let it float away. Removing that upward pull increased the scale reading by more than the weight of the very light contents she had removed. The balloon had been above the box, not inside it, at both relevant times before release.

**Canonical facts**

- A helium balloon outside and above the box was tethered to its false floor at the first weighing.
- Its upward pull reduced the initial scale reading.
- The woman emptied only very light loose contents.
- She then detached the balloon; its upward force exceeded the weight of the removed contents.
- No material was added to or absorbed by the box.

**Explicitly false**

- The scales did not malfunction.
- The box's material mass did not increase.

**Unspecified**

- The exact weights are unspecified.

**Required elements — 1 / 0.5 / 0**

- E1: **1:** An externally floating tethered balloon exerted upward support at the first weighing. **0.5:** Identifies an external upward force without the balloon arrangement. **0:** Absent, or contradicted by the explanation.
- E2: **1:** Emptying was accompanied by detaching the balloon, not adding mass. **0.5:** Recognises removal of support without explaining the sequence. **0:** Absent, or contradicted by the explanation.
- E3: **1:** Lost upward force exceeded removed contents' weight, increasing apparent weight. **0.5:** Distinguishes mass and scale reading without the force comparison. **0:** Absent, or contradicted by the explanation.

**Illustrative question path**

- Did the mass of the box itself increase? → `no`
- Was an external force supporting it initially? → `yes`
- Was a helium balloon attached outside it? → `yes`
- Was the balloon detached before the second weighing? → `yes`

**Mechanisms:** measurement_vs_property, removed_support

**Review risk:** Check physical plausibility with sufficiently light contents; accept equivalent explicitly compatible buoyant-support explanations for human review.

## GT007 — The unreadable signature

**Opening (solver-visible)**

A clerk rejected a clearly signed form. The applicant returned the same form with the signature completely hidden. The clerk accepted it without uncovering the signature. No rule had been waived. Why?

**Solution (private)**

This was the anonymous first stage of an art competition. The form had a detachable identity flap bearing the required signature. The flap had to be folded inward and sealed so judges could review the attached work without knowing the applicant's identity. The first submission left that flap open. The applicant returned it properly sealed, with the same signature still inside. The clerk checked only that the identity section was sealed; authorised staff would open it after judging.

**Canonical facts**

- The form belonged to an anonymous art competition.
- A signed identity flap had to be folded inward and sealed during judging.
- The original flap was open, exposing the signature.
- The returned flap was properly sealed and was not opened by the intake clerk.
- Authorised staff would check the identity after judging.

**Explicitly false**

- The signature was not erased or replaced.
- The clerk did not make an exception.

**Unspecified**

- The entrant's art medium is unspecified.

**Required elements — 1 / 0.5 / 0**

- E1: **1:** Anonymous judging required concealing identity at intake. **0.5:** Mentions privacy without anonymous judging. **0:** Absent, or contradicted by the explanation.
- E2: **1:** The signature was on a flap that was initially open and later sealed. **0.5:** Identifies covering an identity section without the flap. **0:** Absent, or contradicted by the explanation.
- E3: **1:** Signature verification belonged to a later authorised stage, so intake could accept it unopened. **0.5:** Recognises separate stages without explaining acceptance. **0:** Absent, or contradicted by the explanation.

**Illustrative question path**

- Was anonymity required at that stage? → `yes`
- Was the signature on a sealable identity section? → `yes`
- Was it erased? → `no`
- Would identity be checked later? → `yes`

**Mechanisms:** information_access, stage_dependent_rules

**Review risk:** May be moderately easy; use only if measured quick-solve rate passes.

## GT008 — The extra shadow

**Opening (solver-visible)**

An inspector saw two shadows where she expected one. Instead of removing an object or turning off a lamp, she asked for a wall to be repainted. The shadows were real, and the lamps worked properly. Why?

**Solution (private)**

She was checking a room used to judge paint colours under controlled lighting. It should have had one lamp and neutral matte walls. A newly painted glossy wall reflected the lamp strongly enough to act as a second light source, so a test object cast a second shadow. The wall's reflective finish also spoiled the intended viewing conditions. She ordered it repainted with the specified matte finish; the lamp and object were correct.

**Canonical facts**

- The room was used for controlled visual assessment of paint colours.
- A single direct lamp was intended.
- A newly painted glossy wall reflected light strongly enough to produce a second shadow of the test object.
- The specification required a neutral matte wall finish.

**Explicitly false**

- No second electrical lamp was on.
- No extra test object created the shadow.

**Unspecified**

- The brand of paint is unspecified.

**Required elements — 1 / 0.5 / 0**

- E1: **1:** A glossy wall reflected the lamp and acted as a second light source. **0.5:** Identifies reflected light without the wall. **0:** Absent, or contradicted by the explanation.
- E2: **1:** Both shadows came from the same object under direct and reflected illumination. **0.5:** Mentions a second illumination path without the same-object relationship. **0:** Absent, or contradicted by the explanation.
- E3: **1:** The reflection violated controlled viewing conditions, requiring matte repainting. **0.5:** Recognises an unsuitable finish without the room's purpose. **0:** Absent, or contradicted by the explanation.

**Illustrative question path**

- Was light reflecting from a surface? → `yes`
- Was that surface the wall? → `yes`
- Was an extra electrical lamp switched on? → `no`
- Did the room require controlled lighting? → `yes`

**Mechanisms:** indirect_cause, diagnostic_observation

**Review risk:** Physical setup must plausibly produce a distinguishable reflected shadow; human review should check wording and avoid specialised optics requirements.

## GT009 — The cancelled return

**Opening (solver-visible)**

A courier brought a sealed package back without delivering it. The sender thanked him and cancelled the original order. The address was correct, the intended recipient was willing to accept it, and nothing had happened to the contents. Why was the return good news?

**Solution (private)**

The sender was a theatre director who had ordered a replacement costume because the company's original seemed to be missing. She sent a swatch from the original fabric to the maker so the replacement could match. Before handover, the courier recognised the recipient's display-window costume as the supposedly missing original: its distinctive inside-out repair was visible through an open seam. The maker had borrowed it from another company member and had not connected it to the new order. The courier returned with the swatch and this information, allowing the unnecessary replacement order to be cancelled.

**Canonical facts**

- The package contained a fabric swatch for a replacement costume order.
- The original costume had been misplaced, not destroyed.
- The courier identified the original at the maker's shop by a distinctive repair.
- The maker had borrowed it from another company member without realising it was the supposedly missing costume.
- Finding the original made the replacement unnecessary.

**Explicitly false**

- The sealed package did not contain the missing costume.
- The recipient had not refused delivery.

**Unspecified**

- The play's title is unspecified.

**Required elements — 1 / 0.5 / 0**

- E1: **1:** The parcel carried a reference swatch for a replacement rather than the ordered item. **0.5:** Recognises a reference item without the costume link. **0:** Absent, or contradicted by the explanation.
- E2: **1:** The courier found and identified the missing original at the destination. **0.5:** Mentions finding the original without where/how it was recognised. **0:** Absent, or contradicted by the explanation.
- E3: **1:** The original had been borrowed through a different member, making the new order unnecessary. **0.5:** Explains cancellation after recovery but not the cross-person misunderstanding. **0:** Absent, or contradicted by the explanation.

**Illustrative question path**

- Was the parcel itself the item being ordered? → `no`
- Did it contain a sample for making something? → `yes`
- Did the courier locate the supposedly missing original? → `yes`
- Had another company member lent it to the maker? → `yes`

**Mechanisms:** object_role_shift, new_information

**Review risk:** Specific repair detail should not be required verbatim; recognition by a distinctive feature is sufficient.

## GT010 — The successful wrong answer

**Opening (solver-visible)**

A translator was asked a question in a language she understood perfectly. She answered it incorrectly on purpose. Her client checked the answer, thanked her, and finally agreed to use the service. The client needed accurate communication. Why?

**Solution (private)**

The client was testing whether a remote interpreter was actually listening live or whether an operator was replaying recordings of an earlier session. The translator and client had agreed in advance that, if asked the familiar test question again, she should intentionally give a specified wrong answer instead of the old correct one. That fresh agreed response showed she had received the new instruction and was present live. It was an authentication check before the real interpreting work, not a sample translation used as factual advice.

**Canonical facts**

- The client suspected playback of an earlier interpreting session.
- The client privately agreed a fresh deliberately wrong response with the translator.
- She gave that agreed response to a repeated familiar test question.
- Its purpose was to establish a live responsive connection before accurate interpretation began.

**Explicitly false**

- The translator did not misunderstand the language.
- The client was not relying on the wrong answer as factual advice.

**Unspecified**

- The language and test question are unspecified.

**Required elements — 1 / 0.5 / 0**

- E1: **1:** The client was distinguishing a live interpreter from replayed old audio. **0.5:** Identifies a liveness check without the replay hypothesis. **0:** Absent, or contradicted by the explanation.
- E2: **1:** A newly agreed wrong answer differed from the recorded correct one. **0.5:** Mentions a secret agreed response without why it was wrong. **0:** Absent, or contradicted by the explanation.
- E3: **1:** The error served authentication before accurate translation work. **0.5:** Recognises a test without separating authentication from translation quality. **0:** Absent, or contradicted by the explanation.

**Illustrative question path**

- Was the client testing a live connection? → `yes`
- Had they agreed on the wrong answer beforehand? → `yes`
- Was an old recording a concern? → `yes`
- Did she misunderstand the question? → `no`

**Mechanisms:** authentication, intentional_error

**Review risk:** Close to general challenge-response mechanisms; test contamination at the mechanism level without treating shared mechanisms as duplicate stories.

## GT011 — The shrinking queue

**Opening (solver-visible)**

A librarian asked the last person in a queue to leave. Nobody else joined or left, but the official waiting counter fell by two. The counter correctly reflected the cancellations the librarian had made. Why were there two cancellations for one departure?

**Solution (private)**

There was no second physical person. The queue system combined paper tokens issued inside with online reservations, and had accidentally counted the last person twice: once under each entry. When that person left, the librarian cancelled both linked reservations. The official count represented active waiting records, not a visual headcount. Everyone remaining had exactly one record.

**Canonical facts**

- The displayed count tracked active waiting records.
- One person held a paper token and an online reservation for the same service.
- Those entries had been counted separately by mistake.
- When that person left, both entries were cancelled.
- All remaining people had exactly one entry.

**Explicitly false**

- No second physical person left.
- No unborn baby, concealed person or animal was involved.

**Unspecified**

- The reason the librarian asked the person to leave is unspecified.

**Required elements — 1 / 0.5 / 0**

- E1: **1:** The count measured reservation records rather than bodies. **0.5:** Identifies a nonphysical count without reservation records. **0:** Absent, or contradicted by the explanation.
- E2: **1:** The departing person was represented by an online reservation and a paper token. **0.5:** Recognises duplicate entries without the two channels. **0:** Absent, or contradicted by the explanation.
- E3: **1:** Cancelling both entries reduced the count by two for one departure. **0.5:** Links departure to deduplication without explicit cancellation. **0:** Absent, or contradicted by the explanation.

**Illustrative question path**

- Did the count represent records rather than a visual headcount? → `yes`
- Was one person registered twice? → `yes`
- Were there both paper and online entries? → `yes`
- Did a second physical person leave? → `no`

**Mechanisms:** unit_of_count, duplicate_identity

**Review risk:** Do not describe the initial counter as an accurate count of physical people; it counted records, including a duplicate.

## GT012 — The inaccessible donation

**Opening (solver-visible)**

A charity received a donation of twenty chairs. Its organiser immediately asked the donor to take nineteen back, although twenty people were waiting for somewhere to sit. The remaining chair helped all twenty people, and nobody took turns sitting on it. How?

**Solution (private)**

The charity was making a seating area accessible to twenty wheelchair users. Their own chairs already provided seats, but a heavy self-closing entrance door prevented independent entry. The donated chairs were ordinary loose chairs and would only obstruct the space. During a supervised setup session, the organiser used one as a temporary doorstop so all twenty users could enter the seating area in their own wheelchairs. Nineteen unnecessary chairs were returned; nobody sat on the donated one. The entrance was not a fire door, and the temporary prop was removed after entry.

**Canonical facts**

- The twenty people were wheelchair users seated in their own wheelchairs.
- They were waiting to enter an accessible seating area through a heavy self-closing door.
- Loose donated chairs would obstruct the intended wheelchair spaces.
- One donated chair temporarily held the entrance open during supervised entry.
- It was not a fire door, and the prop was removed after entry.

**Explicitly false**

- Nobody sat on the donated chair.
- The remaining nineteen chairs were not dismantled or combined.

**Unspecified**

- The donor's identity is unspecified.

**Required elements — 1 / 0.5 / 0**

- E1: **1:** The people already sat in wheelchairs and needed access to a seating area. **0.5:** Identifies wheelchair users but not the access problem. **0:** Absent or contradicted.
- E2: **1:** One donated chair served as a temporary doorstop so all twenty could enter. **0.5:** Recognises an alternative use for the chair without explaining entry. **0:** Absent or contradicted.
- E3: **1:** Additional loose chairs would obstruct the wheelchair spaces, so nineteen were returned. **0.5:** Explains that the other chairs were unnecessary without the obstruction. **0:** Absent or contradicted.

**Illustrative question path**

- Were the waiting people already sitting in their own wheelchairs? → `yes`
- Was access to the area the problem? → `yes`
- Was the remaining chair used to hold a door open? → `yes`
- Did anyone sit on the donated chair? → `no`

**Mechanisms:** object_function_shift, access_vs_seating

**Review risk:** May be too easy once wheelchair use is guessed. The phrase somewhere to sit must naturally refer to access to an area, not imply they had no seats.

## GT013 — The duplicate tear

**Opening (solver-visible)**

Looking through glass, a conservator saw what appeared to be a tear in a valuable letter and was relieved. When she saw precisely the same torn edge in a second letter, she became concerned. Neither letter had been damaged recently. Why did the second discovery change the meaning of the first?

**Solution (private)**

The first letter was being checked against an old photograph. A distinctive jagged tear seemed to confirm it was the same physical sheet. The second purportedly separate letter had an identical shape, fibres and shadows at that edge, because both were photographic reproductions printed on intact paper. The apparent tears were images, not current breaks in the paper. The conservator had initially inspected the first through protective glazing; seeing the duplicated edge prompted examination that exposed the reproductions.

**Canonical facts**

- The first apparent tear matched an archival photograph of the original letter.
- Both displayed letters were photographic reproductions on intact sheets.
- The apparent tears, including fibres and shadows, were printed images.
- The conservator initially inspected through glazing and then noticed the identical image on the second letter.

**Explicitly false**

- Neither displayed sheet had an actual tear at that edge.
- No new physical damage had occurred.

**Unspecified**

- Who made the reproductions and with what intent is unspecified.

**Required elements — 1 / 0.5 / 0**

- E1: **1:** A distinctive apparent tear initially seemed to authenticate the first letter against a photograph. **0.5:** Recognises a matching defect as an identity cue. **0:** Absent, or contradicted by the explanation.
- E2: **1:** The same detailed tear image on a separate letter suggested duplicated imagery. **0.5:** Mentions suspiciously identical damage without the image explanation. **0:** Absent, or contradicted by the explanation.
- E3: **1:** Both apparent tears were printed on reproductions, not damage to the displayed paper. **0.5:** Identifies reproductions without distinguishing printed tears from actual tears. **0:** Absent, or contradicted by the explanation.

**Illustrative question path**

- Did the first mark match an archival photograph? → `yes`
- Were the displayed sheets torn at those edges? → `no`
- Were the tears part of printed images? → `yes`
- Is the identity of the reproducer known? → `yes and no`

**Mechanisms:** representation_vs_object, correlated_evidence

**Review risk:** The word tear in the opening is apparent-object language; reviewers should check it does not assert a physical tear contradicted by the solution.

## GT014 — The open lock

**Opening (solver-visible)**

A caretaker was told to keep a locked cabinet secure. She unlocked it, left the key in its lock, and went home. This was exactly what the security supervisor wanted. The cabinet held valuable equipment. Why was leaving it unlocked safer?

**Solution (private)**

The locked cabinet was a movable equipment trolley inside a larger secure store. To fasten the trolley to its floor anchor, staff had to open its door and pass a retaining bar through the frame; with the bar in place the small door could not close. The caretaker installed the bar and locked the outer store. Leaving the trolley's key in its small lock prevented its loss and did not grant access through the locked outer door. The agreed overnight security plan prioritised anchoring the valuable trolley inside the secured room.

**Canonical facts**

- The cabinet was a movable equipment trolley in a separately lockable store.
- A retaining bar through the open frame secured it to a floor anchor.
- The bar prevented the trolley door from closing.
- The caretaker installed the bar and locked the outer store before leaving.
- The supervisor had specified this overnight arrangement.

**Explicitly false**

- The outer store was not left unlocked.
- The trolley was not left unanchored.

**Unspecified**

- The type of equipment is unspecified.

**Required elements — 1 / 0.5 / 0**

- E1: **1:** The cabinet was inside a separately secured outer store. **0.5:** Identifies another security barrier without the room. **0:** Absent, or contradicted by the explanation.
- E2: **1:** Opening the trolley enabled a floor-anchoring bar that prevented closing its door. **0.5:** Mentions anchoring without the open-door constraint. **0:** Absent, or contradicted by the explanation.
- E3: **1:** The installed anchor and locked outer store provided the intended security while the key stayed inside. **0.5:** Recognises alternative security without the whole arrangement. **0:** Absent, or contradicted by the explanation.

**Illustrative question path**

- Was there another locked boundary around it? → `yes`
- Was the cabinet movable? → `yes`
- Did anchoring require its door to stay open? → `yes`
- Was the outer store left open? → `no`

**Mechanisms:** nested_boundaries, competing_constraints

**Review risk:** Custom hardware rule may feel arbitrary; require a clear human-review judgement on plausibility and discoverability.

## GT015 — The wrong destination

**Opening (solver-visible)**

A station employee announced a train's destination incorrectly. A passenger who understood the announcement boarded because of the mistake and reached exactly the place she wanted. She did not want the announced destination. Why did the mistake help her choose?

**Solution (private)**

The passenger was a technician sent to inspect one train's faulty automated announcement system. Several trains served the same route, and she had not been given its vehicle number. She was told that the affected train uniquely played a recording naming the old terminus, even though all the trains now continued to the new terminus. Hearing that wrong recording from the train's station-facing speaker identified the vehicle she needed. Her immediate destination was the faulty train itself, where she would work; the geographic terminus was irrelevant.

**Canonical facts**

- The station employee triggered a prerecorded announcement through the train's speaker.
- One train uniquely played the old terminus announcement because of a fault.
- The passenger was the technician assigned to inspect that train.
- She knew the symptom but not the vehicle number.
- The place she needed to reach was that particular train.

**Explicitly false**

- She did not board in order to travel to the announced terminus.
- The error did not change the train's route.

**Unspecified**

- The city and station names are unspecified.

**Required elements — 1 / 0.5 / 0**

- E1: **1:** Her goal was to locate a particular faulty train for inspection. **0.5:** Recognises maintenance work but not the vehicle as destination. **0:** Absent, or contradicted by the explanation.
- E2: **1:** The wrong old-terminus recording was the uniquely specified symptom. **0.5:** Identifies an announcement fault without its identifying role. **0:** Absent, or contradicted by the explanation.
- E3: **1:** Hearing it selected the needed vehicle regardless of its geographic endpoint. **0.5:** Connects boarding to identification without the endpoint distinction. **0:** Absent, or contradicted by the explanation.

**Illustrative question path**

- Was she travelling for maintenance work? → `yes`
- Was she trying to find a particular train? → `yes`
- Did the incorrect recording identify that train? → `yes`
- Did the announcement change the route? → `no`

**Mechanisms:** diagnostic_error, goal_reinterpretation

**Review risk:** Station employee versus automated announcement must remain consistent: employee triggered the recording, not a spontaneous verbal error.

## GT016 — The unsigned receipt

**Opening (solver-visible)**

A shopkeeper refused to sign a receipt for money she had genuinely received. Instead, she asked the customer to take the money back and give it to her again. The amount and the notes stayed the same. After the second handover she signed. Why?

**Solution (private)**

During the first handover, the customer passed the notes beneath the counter, out of view of a fixed camera recording a demonstration of the shop's cash-handling procedure. The shopkeeper was an actor in that authorised training recording, and the receipt was a prop documenting the completed filmed transaction. She asked for the same handover again above the counter so the camera could capture it before she signed. No real sale or additional payment was required.

**Canonical facts**

- The participants were filming an authorised cash-handling demonstration.
- The first handover occurred below the fixed camera's view.
- The notes were returned and handed over again in view of the camera.
- The signature was the next action in the filmed demonstration.
- The notes really changed hands; the transaction itself was staged.

**Explicitly false**

- No counterfeit notes or incorrect amount were involved.
- No second payment was retained.

**Unspecified**

- The denomination of the notes is unspecified.

**Required elements — 1 / 0.5 / 0**

- E1: **1:** The transaction was a filmed training demonstration. **0.5:** Identifies staging without filming/training. **0:** Absent, or contradicted by the explanation.
- E2: **1:** The first real handover was outside the camera's view. **0.5:** Mentions a recording problem without what was missed. **0:** Absent, or contradicted by the explanation.
- E3: **1:** Returning and repeating the same handover captured the shot before the scripted signature. **0.5:** Explains a retake without why money had to go back. **0:** Absent, or contradicted by the explanation.

**Illustrative question path**

- Was the transaction being filmed? → `yes`
- Was it a real retail sale? → `no`
- Had the camera missed the first handover? → `yes`
- Did the shop keep twice the money? → `no`

**Mechanisms:** real_action_staged_context, observer_visibility

**Review risk:** Film-set solutions are common; likely easier and should be screened rather than marketed as obscure.

## GT017 — The missing red line

**Opening (solver-visible)**

A mapmaker removed a red line from a map after checking the real location. Nothing at the location had moved or disappeared. Removing the line made the map more accurate, even though it no longer showed a route people used every day. Why?

**Solution (private)**

The map was a tactile evacuation plan intended to show continuous step-free routes. The red line represented a shortcut through a passage. Walking staff used it daily, but an inspection found a single fixed step hidden by the door threshold. The path had never met the map's step-free criterion. The mapmaker removed its route marking, while retaining the passage itself as a physical feature, because keeping that line would falsely promise wheelchair access.

**Canonical facts**

- The map showed certified continuous step-free evacuation routes.
- A red route line had incorrectly included a passage with a fixed step at a doorway.
- Walking staff still used the passage daily.
- The step was pre-existing and discovered during verification.
- The physical passage remained on the map, but its step-free route line was removed.

**Explicitly false**

- No route was physically closed or destroyed.
- The step was not newly installed.

**Unspecified**

- The building's purpose is unspecified.

**Required elements — 1 / 0.5 / 0**

- E1: **1:** The line represented a qualified step-free route rather than any used path. **0.5:** Identifies a specialised map without its access criterion. **0:** Absent, or contradicted by the explanation.
- E2: **1:** An existing doorway step made the shortcut unsuitable despite daily pedestrian use. **0.5:** Mentions an accessibility barrier without the existing step. **0:** Absent, or contradicted by the explanation.
- E3: **1:** Removal corrected a false route certification without a physical change or loss of the passage feature. **0.5:** Explains correction without distinguishing route marking from physical feature. **0:** Absent, or contradicted by the explanation.

**Illustrative question path**

- Did the map show routes meeting a particular accessibility requirement? → `yes`
- Was there a pre-existing step? → `yes`
- Could walking people still use the passage? → `yes`
- Was the passage destroyed? → `no`

**Mechanisms:** representation_criterion, hidden_constraint

**Review risk:** Probably moderate difficulty; avoid equating arbitrary red colouring with a universal map convention.

## GT018 — The restored gap

**Opening (solver-visible)**

A repairer carefully reassembled two displaced parts of a broken object. The owner rejected the repair because the pieces now fitted perfectly. The repairer separated them, left a small gap, and was paid. Nothing else was added or removed. Why was the gap necessary?

**Solution (private)**

The object was a damaged model of a drawbridge used in a classroom demonstration. Its two bridge leaves had originally pivoted independently, with a small clearance gap at the centre. Damage to the support had displaced them, and the repairer initially mistook the central meeting edges for a fracture that needed joining. Pressing them together made the bridge look continuous but jammed its opening movement. After the owner explained the demonstration, the repairer repositioned the existing supports so the leaves again had clearance and could open independently. The broken part was their alignment/support, not a missing connection across the centre.

**Canonical facts**

- The object was a classroom model of a two-leaf drawbridge.
- Its existing support components had been displaced by damage.
- The repairer initially joined the central edges, mistakenly treating them as a fracture.
- A small central clearance was necessary for the leaves to pivot independently.
- Repositioning existing supports restored the gap and allowed opening without adding or removing material.

**Explicitly false**

- It was not a jigsaw puzzle or an artwork intended only for display.
- No missing central piece had to be replaced.

**Unspecified**

- The model's material is unspecified.

**Required elements — 1 / 0.5 / 0**

- E1: **1:** The pieces were independently moving leaves of a drawbridge model. **0.5:** Identifies independently moving mechanical parts without the bridge. **0:** Absent or contradicted.
- E2: **1:** The apparent break at the centre was an intended clearance; joining it jammed the movement. **0.5:** Identifies necessary clearance without the mistaken fracture interpretation. **0:** Absent or contradicted.
- E3: **1:** Repositioning displaced existing supports restored clearance and working movement without new material. **0.5:** Explains restored movement without how the repair changed alignment. **0:** Absent or contradicted.

**Illustrative question path**

- Did the object have moving parts? → `yes`
- Were the central edges supposed to be permanently joined? → `no`
- Was it a drawbridge model? → `yes`
- Did the first repair prevent the leaves from moving? → `yes`

**Mechanisms:** functional_vs_visual_repair, misidentified_boundary

**Review risk:** Validate the mechanical arrangement. Both pieces were from a broken assembly, not necessarily fractured themselves; opening must not assert the latter.

## GT019 — The unwanted improvement

**Opening (solver-visible)**

A woman made a recording clearer. Every word became easier to understand, yet the recording could no longer be used for its intended purpose. Nobody's words had changed or been removed. What had she lost?

**Solution (private)**

The recording was material for testing whether listeners could identify which room a speaker was in. Every room sample used the same spoken sentence; echoes and background sounds were the evidence being tested. She applied noise reduction and removed reverberation, producing clearer speech while suppressing the room-specific acoustic cues. The words survived, but the test no longer measured recognition of the original rooms.

**Canonical facts**

- The recording belonged to a room-identification listening test.
- Each room used the same sentence so words were not the distinguishing feature.
- Echoes and background sounds supplied the room-specific evidence.
- Processing reduced background noise and reverberation while preserving all words.

**Explicitly false**

- The recording was not intended primarily to transcribe speech.
- No spoken words were changed or removed.

**Unspecified**

- The exact processing software is unspecified.

**Required elements — 1 / 0.5 / 0**

- E1: **1:** The intended task was to identify the recording room, not understand the words. **0.5:** Identifies a nonspeech-content task without room identification. **0:** Absent, or contradicted by the explanation.
- E2: **1:** Room-specific echoes and background sounds were the useful evidence. **0.5:** Mentions ambient acoustic cues without their room link. **0:** Absent, or contradicted by the explanation.
- E3: **1:** Speech enhancement removed those cues while preserving words, invalidating the test. **0.5:** Recognises useful information lost without explaining preserved speech. **0:** Absent, or contradicted by the explanation.

**Illustrative question path**

- Was understanding the words the main purpose? → `no`
- Did listeners need to identify a location? → `yes`
- Were echoes relevant evidence? → `yes`
- Did any spoken word disappear? → `no`

**Mechanisms:** signal_vs_noise, goal_mismatch

**Review risk:** Shares an audio surface with GT003 but a different mechanism; review for family independence and potential future M3 pairing, not automatic matching.

## GT020 — The second envelope

**Opening (solver-visible)**

A woman received an envelope containing a perfectly legible letter. She asked the sender to post another envelope without a letter inside. When the empty envelope arrived, she finally knew where to send her reply. Nothing was written on either envelope that told her the address. How did the empty envelope help?

**Solution (private)**

The first letter supplied a return address by reference to a place on a small printed street map enclosed with it. The map listed several buildings and addresses but did not identify which one to use. The sender had cut a small viewing hole in an envelope at the position of the chosen building, intending the envelope to act as a selector over the map. He then accidentally sent the map in a different envelope. On learning the problem, he mailed the original envelope empty inside a protective outer envelope. The woman fitted the saved map into that original envelope in the orientation specified by its folds and alignment arrow. The hole exposed the intended building and its printed address. The identifying information came from the hole combined with the map, not an address written on either inner envelope.

**Canonical facts**

- The first letter asked for a reply to a building identified on an enclosed folded street map.
- The printed map listed the possible buildings and postal addresses, but had no visible identifying mark of its own.
- The sender had cut a viewing hole in the original envelope so that it would expose the chosen building on an aligned map.
- He accidentally sent the map in a different envelope.
- He later mailed the original envelope with the viewing hole empty inside a protective outer envelope.
- The map's fold and a printed alignment arrow allowed one unambiguous placement in the original envelope.
- The hole then exposed the one target building whose address was printed on the map.

**Explicitly false**

- The answer did not depend on a postal cancellation mark.
- No return address was written on either relevant inner envelope.

**Unspecified**

- The reason for this unusual address-identification method is unspecified.

**Required elements — 1 / 0.5 / 0**

- E1: **1:** The woman already had a map listing possible buildings and addresses, but lacked the location selector. **0.5:** Identifies incomplete information in the first mailing without the map. **0:** Absent or contradicted.
- E2: **1:** A viewing hole in the mistakenly retained original envelope served as the missing selector. **0.5:** Recognises a non-written envelope feature without the swapped-envelope error. **0:** Absent or contradicted.
- E3: **1:** Aligning the saved map inside the received envelope made the hole identify the correct printed address. **0.5:** Mentions combining the two objects without the alignment mechanism. **0:** Absent or contradicted.

**Illustrative question path**

- Did she need to combine the second envelope with something she already had? → `yes`
- Did the first mailing contain a map? → `yes`
- Was a hole in the original envelope an identifying mark? → `yes`
- Did she use a postmark as the address? → `no`

**Mechanisms:** complementary_information, physical_alignment

**Review risk:** Unusual communication method and alignment constraints need human review. It is explicitly unspecified why the sender chose this method; reject if blind human play needs a hint about the map.
