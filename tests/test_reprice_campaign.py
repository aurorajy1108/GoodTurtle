import json
import tempfile
import unittest
from pathlib import Path
from scripts.reprice_campaign import reprice


class RepriceTests(unittest.TestCase):
    def test_sidecar_deduplicates_paths_and_never_changes_raw_usage_or_frozen_prices(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);game=root/'task/continual/source';game.mkdir(parents=True)
            manifest={'runner':'fixture','preset':'smoke','jobs':[{'id':'cl-set1-a','folder':'task','kind':'continual',
                'slot':'a','set':1,'repeat_offset':0}]}
            (root/'campaign.json').write_text(json.dumps(manifest))
            row={'condition':'source','target':'TS013','repeat':1,'run_dir':'source'}
            (game.parent/'experiment_runs.json').write_text(json.dumps([row,row]))
            call={'provider':'deepseek','model_returned':'deepseek-flash','role':'player','status':'ok',
                'endpoint':'https://api.deepseek.com/chat/completions','response_id':'fixture',
                'usage':{'prompt_tokens':1000,'completion_tokens':100,'prompt_cache_hit_tokens':200},
                'accounting':{'estimated_cost_usd':None,'unknown_reason':'no_exact_provider_model_price'}}
            file=game/'api_calls.jsonl';file.write_text(json.dumps(call)+'\n');before=file.read_bytes()
            snapshot=game/'pricing_snapshot.json';snapshot.write_text('{"original":true}')
            result=reprice(root,root/'review')
            self.assertEqual(result['recorded_calls'],1)
            self.assertAlmostEqual(result['upper_estimated_cost_usd'],.0003612)
            self.assertAlmostEqual(result['lower_estimated_cost_usd'],.0001806)
            self.assertEqual(file.read_bytes(),before)
            self.assertEqual(snapshot.read_text(),'{"original":true}')
            self.assertIsNone(result['total']['actual_billed_cost_usd'])
            self.assertTrue(result['estimate_assumptions'])
