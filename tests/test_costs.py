import json
import tempfile
import unittest
from pathlib import Path

from turtle_loop.costs import account_call, cost_summary, normalize_usage, pricing_config, write_batch_costs
from turtle_loop.engine import Recorder, load_prompts
from test_loop import PUZZLE


class CostTests(unittest.TestCase):
    def test_deepseek_exact_prices_keep_peak_assumption_and_checked_date(self):
        for model,expected in [('deepseek-flash',.0003612),('deepseek-v4-pro',.0014608)]:
            call=self.call(provider='deepseek',model_requested=model,endpoint='https://api.deepseek.com/chat/completions')
            row=account_call(call,pricing_config())
            self.assertAlmostEqual(row['estimated_cost_usd'],expected)
            self.assertEqual(row['price_checked_on'],'2026-11-11')
            self.assertEqual(row['price']['off_peak_multiplier'],.5)
            self.assertIn('peak_rate_reference',row['estimate_assumption'])
            self.assertIsNone(row['actual_billed_cost_usd'])

    def call(self, **overrides):
        return dict({'provider':'codex_cli','model_requested':'gpt-6.1-sol','role':'host','status':'ok',
                     'usage':{'input_tokens':1000,'cached_input_tokens':200,'output_tokens':100,
                              'output_tokens_details':{'reasoning_tokens':80}}},**overrides)

    def test_cache_discount_and_reasoning_not_double_counted(self):
        r=account_call(self.call(),pricing_config())
        self.assertAlmostEqual(r['estimated_cost_usd'],.00262)
        self.assertEqual(r['total_tokens'],1100)
        self.assertEqual(r['reasoning_tokens'],80)
        self.assertIsNone(r['actual_billed_cost_usd'])
        self.assertEqual(r['model_basis'],'requested_unverified')

    def test_long_context_and_exact_model_endpoint_selection(self):
        book=pricing_config()
        call=self.call(usage={'input_tokens':273000,'cached_input_tokens':1000,'output_tokens':1000})
        self.assertAlmostEqual(account_call(call,book)['estimated_cost_usd'],1.1032)
        for patch in ({'model_returned':'unpriced-version'},
                      {'provider':'openai','endpoint':'https://gateway.example/v1/responses'},
                      {'provider':'openai','endpoint':'https://api.openai.com/v1/responses','service_tier':'priority'}):
            self.assertIsNone(account_call(self.call(**patch),book)['estimated_cost_usd'])

    def test_provider_schemas(self):
        o=normalize_usage('openai_chat',{'prompt_tokens':100,'completion_tokens':20,
            'prompt_tokens_details':{'cached_tokens':40},'completion_tokens_details':{'reasoning_tokens':10}})
        self.assertEqual((o['input_tokens'],o['cached_input_tokens'],o['output_tokens'],o['reasoning_tokens']),(100,40,20,10))
        a=normalize_usage('anthropic',{'input_tokens':100,'output_tokens':20,
                                     'cache_read_input_tokens':40,'cache_creation_input_tokens':10})
        self.assertEqual((a['input_tokens'],a['total_tokens']),(150,170))
        d=normalize_usage('deepseek',{'prompt_tokens':100,'completion_tokens':20,'prompt_cache_hit_tokens':40,'prompt_cache_miss_tokens':60})
        self.assertEqual(d['cached_input_tokens'],40)
        self.assertTrue(d['valid_for_pricing'])

    def test_missing_usage_or_price_never_becomes_zero(self):
        book=pricing_config()
        records=[account_call(self.call(),book),account_call(self.call(status='transport_error',usage={}),book)]
        s=cost_summary(records)['total']
        self.assertEqual(s['calls'],2)
        self.assertEqual(s['unknown_cost_calls'],1)
        self.assertIsNone(s['estimated_cost_usd'])
        self.assertAlmostEqual(s['known_estimated_cost_usd'],.00262)
        self.assertEqual(s['missing_token_calls']['input_tokens'],1)
        self.assertIsNone(account_call(self.call(model_requested='unknown'),book)['estimated_cost_usd'])
        self.assertIsNone(account_call(self.call(usage={'input_tokens':10,'cached_input_tokens':20,'output_tokens':1}),book)['estimated_cost_usd'])

    def test_custom_anthropic_pricing(self):
        book=pricing_config({'schema_version':1,'currency':'USD','models':[{
            'providers':['anthropic'],'model':'fixture','source':'test fixture, not real prices',
            'endpoint_prefix':'https://api.anthropic.com/', 'input_per_million':2,
            'cached_input_per_million':.2,'cache_write_per_million':2.5,'output_per_million':10}]})
        c=self.call(provider='anthropic',model_requested='fixture',endpoint='https://api.anthropic.com/v1/messages',
                    usage={'input_tokens':100,'output_tokens':20,'cache_read_input_tokens':40,'cache_creation_input_tokens':10})
        self.assertAlmostEqual(account_call(c,book)['estimated_cost_usd'],.000433)

    def test_recorder_exports_failed_calls_and_unique_source_cost(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            rec=Recorder(root/'A',PUZZLE,{'max_questions':100},load_prompts(),echo=False)
            rec.audit(self.call(status='invalid_response'))
            rec.audit(self.call(role='partner',usage={}))
            result=rec.report('error','fixture')
            self.assertEqual(result['costs']['total']['calls'],2)
            self.assertEqual(result['costs']['total']['unknown_cost_calls'],1)
            self.assertTrue((root/'A/token_costs.csv').exists())
            self.assertIn('accounting',json.loads((root/'A/api_calls.jsonl').read_text().splitlines()[0]))
            row=dict(result,run_dir='A',puzzle_id='A',condition='source',repeat=1)
            totals=write_batch_costs(root,[row,row])
            self.assertEqual(totals['games_with_accounting'],1)
            self.assertEqual(totals['total']['calls'],2)
            totals=write_batch_costs(root,[row,{'run_dir':'old','status':'completed'}])
            self.assertEqual(totals['games_missing_accounting'],['old'])
            self.assertIsNone(totals['total']['estimated_cost_usd'])

    def test_pricing_snapshot_rejects_invalid_rates(self):
        b=pricing_config();b['models'][0]['input_per_million']=-1
        with self.assertRaises(ValueError):pricing_config(b)


if __name__=='__main__':
    unittest.main()
