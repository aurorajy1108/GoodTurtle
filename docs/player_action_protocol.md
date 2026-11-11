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

## Audited preamble recovery

The Player prompt requires the action header immediately, with no introduction or
reasoning. If an output nevertheless has a preamble followed by exactly one
line-delimited action block, the parser discards only the preamble and retains the
entire body unchanged (apart from the existing outer whitespace normalization).
Recovery records the raw-output hash, selected character span and discarded prefix
length. The same rule applies to MAS and saved-output recovery, without a new
Player generation. Verbatim validation compares the complete extracted action,
including its type and MAS next speaker, not the entire preamble-bearing response.
Multiple blocks, empty bodies and mixed JSON/prefix envelopes require review.
Provider-truncated outputs remain rejected before action execution. A whole fenced
output retains the existing separately audited envelope recovery; a preamble plus
fenced action is not silently accepted. This change does not alter running snapshots.
