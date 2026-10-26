"""Offline provenance, privacy filtering and binding checks, not LLM accuracy tests."""
import importlib.util
import json
import hashlib
import unittest
from pathlib import Path
from turtle_loop.dataset import load_dataset
from turtle_loop.host_context import build_story_context
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('share_import',ROOT/'scripts/import_chatgpt_share.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
D=ROOT/'data/human_trajectories/chatgpt_shares_20261026'


def html_fixture(nodes):
    pool=[]
    def put(value):
        index=len(pool);pool.append(None)
        if isinstance(value,dict):pool[index]={'_'+str(put(k)):put(v) for k,v in value.items()}
        elif isinstance(value,list):pool[index]=[put(v) for v in value]
        else:pool[index]=value
        return index
    put({'linear_conversation':nodes})
    return '<script>streamController.enqueue('+json.dumps(json.dumps(pool))+')</script>'


def node(id,role='assistant',channel=None,hidden=False,parts=None):
    return {'message':{'id':id,'author':{'role':role},'channel':channel,'metadata':{'is_visually_hidden_from_conversation':hidden},'content':{'content_type':'text','parts':parts or ['Visible text']}}}


class ShareImportTests(unittest.TestCase):
    def test_filters_hidden_nonpublic_roles_and_analysis(self):
        value=module.extract(html_fixture([node('u','user'),node('a'),node('s','system'),node('t','tool'),node('h',hidden=True),node('r',channel='analysis')]),'https://example.test/share')
        self.assertEqual([m['message_id'] for m in value['messages']],['u','a'])
        self.assertEqual(value['omitted_nonvisible_nodes'],4)

    def test_rejects_error_page_duplicate_ids_and_nontext_parts(self):
        for html in ['<html>Sign in</html>',html_fixture([node('same'),node('same')]),html_fixture([node('bad',parts=[{'image':'not text'}])])]:
            with self.assertRaises(ValueError):module.extract(html,'https://example.test/share')

    def test_archive_covers_roles_feedback_corrections_and_unanswered(self):
        archives={d['source_url']:d for d in (json.loads(p.read_text()) for p in D.glob('*.messages.json'))}
        self.assertEqual(sorted(d['visible_messages'] for d in archives.values()),[138,495])
        pairs=json.loads((D/'qa_pairs.json').read_text());self.assertEqual(len(pairs),311)
        self.assertEqual(len({p['case_id'] for p in pairs}),311)
        for p in pairs:
            messages=archives[p['source_url']]['messages'];m=messages[p['message_index']-1]
            self.assertEqual((m['role'],m['text'],m['message_id']),('assistant',p['player_text'],p['message_id']))
            if p['feedback_message_index'] is not None:
                f=messages[p['feedback_message_index']-1];self.assertEqual((f['role'],f['text'],f['message_id']),('user',p['host_feedback_raw'],p['feedback_message_id']))
            if p['label_observed'] is None:self.assertFalse(p['eligible_for_host_pack'])
        by={p['case_id']:p for p in pairs}
        self.assertEqual(by['SHARE_6adf37d6_012']['label_observed'],'no')
        self.assertEqual(by['SHARE_6adf37d6_012']['later_correction']['corrected_label'],'yes')
        self.assertEqual(by['SHARE_6adf37d6_014']['label_normalization'],'correction_not_feedback')
        self.assertEqual(sum(p['label_normalization']=='unresolved_typo' for p in pairs),2)
        self.assertEqual(sum(p['label_normalization']=='unanswered_at_segment_end' for p in pairs),2)
        self.assertEqual(by['SHARE_6adf37d6_074']['action_type'],'final_submission')

    def test_only_curated_examples_bound_and_existing_contract_unchanged(self):
        audit=json.loads((ROOT/'docs/reviews/chatgpt_share_merge_20261026.json').read_text())
        bank={p['id']:p for p in load_dataset(ROOT/audit['dataset'])['puzzles']}
        pairs={p['case_id']:p for p in json.loads((D/'qa_pairs.json').read_text())}
        approved=set()
        for group in audit['puzzles']:
            basepath=ROOT/group['base_binding']['overlay_pack'];self.assertEqual(hashlib.sha256(basepath.read_bytes()).hexdigest(),group['base_sha256'])
            base=json.loads(basepath.read_text());merged=json.loads((ROOT/group['merged_pack']).read_text());context=build_story_context(bank[group['puzzle_id']])
            for key in base:
                if key not in ('version','review_status','host_examples'):self.assertEqual(base[key],merged[key])
            self.assertEqual(merged['host_examples'][:len(base['host_examples'])],base['host_examples'])
            self.assertEqual(merged['host_examples'][len(base['host_examples']):],group['added_examples'])
            for e in group['added_examples']:
                self.assertIn(e,context['host_examples']);self.assertEqual(e['question'],pairs[e['case_id']]['question']);self.assertEqual(e['answer'],pairs[e['case_id']]['label_observed']);self.assertFalse(e['provenance']['human_confirmed']);approved.add(e['case_id'])
        self.assertEqual(len(approved),21)
        self.assertEqual(approved,{k for k,v in pairs.items() if v['eligible_for_host_pack']})
        self.assertEqual(len(bank),50)
        self.assertNotIn('EXTERNAL_TRAIN_001',bank)
        for p in bank.values():build_story_context(p)

if __name__=='__main__':unittest.main()
