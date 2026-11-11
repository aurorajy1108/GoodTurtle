# Player action protocol: prefix-v1

New games send `action_protocol: prefix-v1`. Player outputs plain text:

```text
QUESTION
Is the person attending a dinner?
```

```text
FINAL
The complete explanation goes here.
```

MAS free_dialogue uses `QUESTION NEXT=B`, `FINAL NEXT=A`, `DISCUSS NEXT=B`,
or `PASS NEXT=A` as its first line; the body follows on the next line.
NEXT identifies the proposed next speaker, not a recipient. QUESTION goes to Host,
FINAL to Grader, DISCUSS/PASS to the public teammate chat. NEXT is required except
on a mandatory final. Alternating scheduling may override it. Speaker identity and
role assignments remain controller-owned. A/B retain independent persistent sessions.

The parser preserves body punctuation and line breaks, rejects empty bodies and
multiple action blocks, and enforces the allowed actions. At slot 100 only FINAL
is accepted. Questions and unsuccessful finals consume quota; discussion does not.
Existing discussion limits still apply. Internal normalized actions, trajectories,
and API envelopes remain JSON; Host's four labels and Grader's JSON are unchanged.
DeepSeek Player/partner no longer request JSON mode for this protocol. Codex action
calls omit the JSON output schema. Legacy JSON actions remain readable for archived
trajectories and older clients. New prefixes do not promise to fix all instruction
violations. No live experiment or frozen snapshot is modified by this change.
