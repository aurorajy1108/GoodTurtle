# 2026-10-24 trajectory fixes and shared-buffer trial

This revision addresses the four-game audit at `runs/api/20261024_four_game_audit` (local experimental artifacts). It does not claim all future host answers are correct.

| Observed issue | Change | Verification |
| --- | --- | --- |
| Invented stunt/crew, inconsistent faction or rescuer | General host source/role/time reminders and new TS023/TS036 packs | Frozen-history host regressions, three repeats |
| Half credit without its required identity; customary cremation confused with honorific cremation | v4 atomic facts and `half_credit_requires` gates; grader instructions | Three-repeat private grader regression plus deterministic gate tests |
| Merger inserts unsupported exclusivity | Independent mode selects a candidate verbatim; deterministic logged fallback when rewritten | Candidate-selection test; full original selector output retained |
| Repeated irrelevant branches and rejected finals | Player initial prompt explicitly tracks excluded branches and seeks new evidence | Behavioral effect must be audited on new runs, not assumed fixed |
| No independently accumulated exploration | New `shared_buffer` mode, different role lenses, four-submission sharing interval | Visibility isolation and final-sync tests |
| Stale running placeholder after model handoff | Non-destructive `superseded.json` and report support | Renderer test; old batch summary rebuilt |
| Different host models and insufficient repeats | Current host/grader Sol high, fixed per snapshot; three conditions × three repeats × two puzzles | Preflight covers all 18 planned games; separate versioned results |
| Hidden inaccuracies despite host self-agreement | New offline trajectory audit command | Original four-game deterministic smoke; model audits recorded separately |

Player/partner remains `gpt-6-luna` high; host/grader is `gpt-6.1-sol` high. No automatic Astra switch. API providers remain configurable outside this specific study.

Strict full-story completion, question accounting and the 100-submission limit remain. A correct final is separately recorded; every rejected/incomplete final counts. Private rubric items are never injected into the shared buffer. Partial-score weights are unchanged. All expanded facts and score rules remain AI reviewed pending human confirmation.

The selected TS023/TS036 regression cases include the defects used to develop the repair. They are not held-out population accuracy measurements. Three repeats give a measure of variation, not proof of bias elimination. The independent condition has three solver calls per turn; solo and shared_buffer have one. Role diversity, periodic information access and model sampling are distinct effects and should be separated in future ablations.

See [experiment guide](experiment_pipelines.md) for all flags, sharing semantics, audit command and output paths. New study progress, trajectory links and audits are indexed locally at `runs/api/20261024_repair_v6_study/index.html`.
