import unittest

from scripts.analyze_latest_results import aggregate


class LatestResultsAnalysisTests(unittest.TestCase):
    def row(self, **changes):
        result = dict(suite='one', puzzle='TS022', source='TS047', condition='answer_only',
                      role='target', primary=True, status='completed', score=.9,
                      success=False, submissions=100, final_attempts=2)
        result.update(changes)
        return result

    def test_rejected_online_grade_is_missing_not_zero_or_offline_replacement(self):
        rows = [self.row(), self.row(score=.1), self.row(status='error', score=None),
                self.row(role='source', score=1), self.row(primary=False, score=1)]
        summary = aggregate(rows, ['suite','condition'])[0]
        self.assertEqual((summary['n_archived'],summary['n_accepted'],summary['n_technical']), (3,2,1))
        self.assertEqual(summary['mean'],.5)
        self.assertEqual(summary['solved'],0)

    def test_batch_and_source_boundaries_are_preserved(self):
        rows = [self.row(), self.row(suite='other'), self.row(source='TS019')]
        summary = aggregate(rows, ['suite','source','condition'])
        self.assertEqual(len(summary),3)
        self.assertTrue(all(r['sample_sd'] is None for r in summary))

    def test_legacy_full_partial_score_does_not_become_a_solved_game(self):
        summary = aggregate([self.row(score=1,success=False)], ['suite'])[0]
        self.assertEqual(summary['mean'],1)
        self.assertEqual(summary['solved'],0)


if __name__ == '__main__':
    unittest.main()
