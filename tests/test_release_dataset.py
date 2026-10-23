"""Ensure a clean checkout contains every input required by the 50-puzzle loop."""
import unittest
from pathlib import Path
from turtle_loop.dataset import load_dataset
from turtle_loop.host_context import build_story_context

ROOT = Path(__file__).resolve().parents[1]


class ReleaseDatasetTests(unittest.TestCase):
    def test_complete_bank_rubrics_and_all_host_dependencies(self):
        data = load_dataset(ROOT/'data/annotations/turtle50_v2/private.json')
        self.assertEqual({p['id'] for p in data['puzzles']},
                         {f'TS{i:03d}' for i in range(1, 51)})
        self.assertEqual(sum(len(p['rubric']) for p in data['puzzles']), 161)
        for puzzle in data['puzzles']:
            with self.subTest(puzzle=puzzle['id']):
                self.assertTrue(puzzle['completion_requirements'])
                for point in puzzle['rubric']:
                    for key in ('criterion', 'full_credit', 'half_credit', 'zero_credit'):
                        self.assertTrue(point[key].strip())
                context = build_story_context(puzzle)
                self.assertEqual(context['reference_answer'], puzzle['answer'])
                self.assertEqual(context['completion_requirements'], puzzle['completion_requirements'])
