# CL Set1 completed four-repeat analysis

As of Hong Kong: 2026-11-13T10:35:02+08:00

Source games: 3/3; target games: 36/36; target successes: 0.

Only the latest archive is counted. Recovery copies are not extra repetitions. All scores below are provisional model judgments.

| A | Matched completed repeats | Direct B | Answer only | A session → B | Session − direct |
| --- | --- | ---: | ---: | ---: | ---: |
| TS014 | 1,2,3,4 | 40.00% | 33.75% | 6.25% | -33.75 pp |
| TS015 | 1,2,3,4 | 36.25% | 56.25% | 45.00% | +8.75 pp |
| TS028 | 1,2,3,4 | 36.25% | 48.75% | 31.25% | -5.00 pp |

Scores use identical repeat IDs within each row. Rows with different numbers of completed repeats are not a balanced cross-relation comparison.

## Balanced comparison across all three source relations

Completed repeat IDs: 1,2,3,4.

| Condition | n | Mean score | Sample SD |
| --- | ---: | ---: | ---: |
| direct | 12 | 37.50% | 22.81% |
| answer_only | 12 | 46.25% | 18.72% |
| session | 12 | 27.50% | 24.73% |

## Interpretation

TS015 is the prespecified positive source, TS014 negative, and TS028 neutral; relation types are hypotheses. The target is always TS013. The source answer is revealed before B even when A was not solved.

On the balanced completed repeats, answer_only minus session mean score is +18.75 pp.
This contrasts canonical answer exposure with answer plus dialogue/history length; it does not isolate the effect of context length alone.

The completed four-repeat TS014 row, when available, describes performance conditional on one academic-story prefix. Inspect its repeat vectors rather than inferring a universal negative-transfer effect from a mean.

If every completed B reaches 100 submissions without solving, the observed count is budget consumption, not time to a successful solution. Partial scores, checkpoint coverage and trajectories remain informative; question-count means alone cannot rank efficiency.

## Limits

- Only completed games enter outcome means; missing/running scores are never filled with zero.
- Per-source comparisons use the same completed repeat IDs for all three conditions.
- Pooled comparisons use only repeat IDs completed across every source and condition.
- One fixed A prefix per source; B repetitions are conditional on it, not independent A experiences.
- Model grades are descriptive outcomes, not human-verified successes. No Host judgments are changed.
- Historical and new repetitions used recorded parser/controller overlays; preserve that cohort distinction.

See runs.csv for all planned/completed/running cases, and summary.json for score vectors and paired differences.
