# v5: one standard for score and completion

`grading_protocol: coverage-v3-unified`. New team/study/verified-Set1 runs default
to this dataset. v4 and its historical results remain unchanged.

Every mandatory v4 completion requirement is mapped into an existing weighted
checkpoint's `required_facts`, with the full mapping in `completion_mapping.json`.
All 161 checkpoint weights, stories and original checkpoint facts are preserved.
Repeated/overlapping facts inside one checkpoint do not create extra weight.
Interpretation-only instructions (e.g. an unspecified cause of death need not be
explained) become non-scoring grading notes. They prohibit false assertions,
without requiring the player to recite disclaimers. This mapping is AI-reviewed;
it does not claim new human annotations.

The controller validates quoted evidence and derives each credit from fact
coverage: all covered = 1, partly covered = 0.5, all missing or a contradiction = 0.
Existing half-credit prerequisite gates still apply. The exact weighted score of
1 is the only completion standard. `full_solution` remains in the response schema
for compatibility but has no independent veto. Missing even one required fact
prevents full credit for its checkpoint.

A material contradiction zeros the affected checkpoint(s). A contradiction that
cannot be located, an inconsistent irrelevant flag, or a reference/rubric conflict
stops for review with `partial_score: null`, never numeric 100% followed by more
questions. The raw evaluator response and controller corrections remain auditable.
No new hidden completion conditions may be inferred from host examples.

Do not merge v5 performance with v4: the weights are unchanged, but full-credit
requirements are now more explicit. Existing frozen studies keep their own v4
snapshot; adopting v5 requires a new study. Do not silently regrade historical
trajectories or resume a v4 rollout under v5 rules.

Validation: deterministic scoring/loop checks and selected real API regression
cases are described in `docs/unified_scoring_v3.md`. Model grading remains a
judgment task; passing these checks does not prove universal semantic accuracy.
