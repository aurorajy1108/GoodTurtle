#!/usr/bin/env python3
"""Check screening provenance/visible log invariants. Does not judge answer semantics."""
import hashlib,json
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]/'runs/2026-10-09_nonenglish_screening'
LABELS={'yes','no','yes and no'}
def read(p):return json.loads(p.read_text())
def main():
    rows=[]
    for run in sorted(BASE.glob('JP[0-9][0-9][0-9]*')):
        if not run.is_dir():continue
        events=[json.loads(s) for s in (run/'trajectory.jsonl').read_text().splitlines() if s.strip()]
        if (run/'input_manifest.json').exists():
            for name,expected in read(run/'input_manifest.json').items():
                assert hashlib.sha256((run/name).read_bytes()).hexdigest()==expected,(run.name,'changed frozen input',name)
        qs=[e for e in events if e.get('event')=='solver' and e.get('type')!='pending_question_not_sent_to_host'];hs=[e for e in events if e.get('event')=='host'];fs=[e for e in events if e.get('event')=='solver_final_attempt'];gs=[e for e in events if e.get('event')=='grader']
        assert len(qs)==len(hs),(run.name,'unpaired questions')
        assert [e['question_number'] for e in qs]==list(range(1,len(qs)+1)),(run.name,'question numbering')
        for q,h in zip(qs,hs):
            assert (q['question_number'],q['text'],q['submission_number'])==(h['question_number'],h['text'],h['submission_number']),(run.name,'question mismatch')
            assert h['host_answer'] in LABELS,(run.name,'invalid label')
        assert [e['final_attempt_number'] for e in fs]==list(range(1,len(fs)+1)),(run.name,'attempt numbering')
        assert len(gs)==len(fs),(run.name,'missing grader')
        for f,g in zip(fs,gs):assert f['accepted']==g['accepted'],(run.name,'verdict mismatch')
        subs=[e['submission_number'] for e in events if e.get('event') in ('solver','solver_final_attempt')]
        assert subs==list(range(1,len(subs)+1)),(run.name,'submission numbering')
        result=read(run/'result.json') if (run/'result.json').exists() else {}
        if result.get('status')=='completed':
            assert fs and fs[-1]['accepted'],(run.name,'false completion')
            assert result['host_queries']==len(qs) and result['final_attempts']==len(fs),(run.name,'result counts')
            if result.get('retained'):
                assert result['complete_solution'] and len(qs)>30,(run.name,'invalid retained count')
                assert not any(e.get('material_error') for e in hs),(run.name,'contaminated retained run')
                assert not result.get('source_fidelity_hold'),(run.name,'source-held retained run')
        rows.append(dict(puzzle=run.name,questions=len(qs),attempts=len(fs),status=result.get('status','not_completed'),frozen_integrity='pass',structure='pass'))
    print(json.dumps(rows,indent=2))
if __name__=='__main__':main()
