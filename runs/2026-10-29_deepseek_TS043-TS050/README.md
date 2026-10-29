# TS043–TS050 trajectories — 2026-10-29

Player, Host, and grader: DeepSeek Flash; thinking disabled. One initial solo run per puzzle, 100-submission limit. No CL or multiagent comparison was run. Human review remains pending.

Original failures and continuations are preserved. Recovery replays prior responses without new player/host sampling, re-evaluates the malformed grade once with explicit schema instructions, and continues. These are continuations, not independent repeats. Replay token usage is zeroed in continuation logs; original usage remains in originals. TS048 additionally removes one stray JSON quote without changing grading judgments. API logs are losslessly gzip-compressed.

| Puzzle | Final state | Counted questions | Partial score | Fully solved | Trajectory |
|---|---|---:|---:|---|---|
| TS043 | completed / budget_exhausted | 100 | 0.15 | False | [Open](20261029_deepseek_recovery/TS043/trajectory.md) |
| TS044 | error / ProtocolError | 99 | None | None | [Open](20261029_deepseek_recovery/TS044/trajectory.md) |
| TS045 | error / ProtocolError | 76 | None | None | [Open](20261029_deepseek_recovery/TS045/trajectory.md) |
| TS046 | error / ProtocolError | 99 | None | None | [Open](20261029_deepseek_recovery/TS046/trajectory.md) |
| TS047 | completed / budget_exhausted | 100 | 0.8 | False | [Open](20261029_deepseek_recovery/TS047/trajectory.md) |
| TS048 | error / ProtocolError | 74 | None | None | [Open](20261029_deepseek_syntax_recovery/TS048/trajectory.md) |
| TS049 | completed / budget_exhausted | 100 | 0.825 | False | [Open](20261029_deepseek_restart43/batches/TS049/TS049_r01_solo/trajectory.md) |
| TS050 | completed / solved | 17 | 1.0 | True | [Open](20261029_deepseek_remaining/batches/TS050/TS050_r01_solo/trajectory.md) |

## Review notes

- TS043 original turn 21: host agrees that the dog triggered the medical emergency, but the canonical answer says the dog prevented CPR after a heart attack. This can contaminate subsequent search; do not attribute failure purely to the player.
- TS048 original turns 24/40/52: host affirms a location-discovery story not established in the canonical answer. Turn 27 rejects the girlfriend working with police even though she secretly called for help; wording may need adjudication.
- TS046 original turn 4 marks narrator contribution irrelevant despite the canonical clothing-swap deception. Needs review.
- Scores are unreviewed model assessments. Final-format errors are infrastructure failures, not successful or failed solution observations. Budget exhaustion is not a measured time-to-solution.
- Earlier human-host TS041/TS042 and stopped TS043 remain under data/host_reference/inbox/ with original feedback, skips, and quit preserved. These are separate from this automated run archive.
