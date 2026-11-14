# CL Set1 interim analysis

As of Hong Kong: 2026-11-12T20:11:31+08:00

Source games: 3/3; target games: 25/36; target successes: 0.

Only the latest archive is counted. Recovery copies are not extra repetitions. All scores below are provisional model judgments.

| A | Matched completed repeats | Direct B | Answer only | A session → B | Session − direct |
| --- | --- | ---: | ---: | ---: | ---: |
| TS014 | 1,2,3,4 | 40.00% | 33.75% | 6.25% | -33.75 pp |
| TS015 | 1,2 | 32.50% | 55.00% | 50.00% | +17.50 pp |
| TS028 | 1,2 | 40.00% | 50.00% | 17.50% | -22.50 pp |

Scores use identical repeat IDs within each row. Rows with different numbers of completed repeats are not a balanced cross-relation comparison.

## Balanced comparison across all three source relations

Completed repeat IDs: 1,2.

| Condition | n | Mean score | Sample SD |
| --- | ---: | ---: | ---: |
| direct | 6 | 35.00% | 23.45% |
| answer_only | 6 | 48.33% | 15.06% |
| session | 6 | 22.50% | 26.97% |

## Interpretation

TS015 is the prespecified positive source, TS014 negative, and TS028 neutral; relation types are hypotheses. The target is always TS013. The source answer is revealed before B even when A was not solved.

On the balanced completed repeats, answer_only minus session mean score is +25.83 pp.
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
