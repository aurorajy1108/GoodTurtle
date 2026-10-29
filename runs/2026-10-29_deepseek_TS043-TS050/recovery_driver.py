"""Replay frozen responses, then re-evaluate the malformed last grade once and continue.
Original runs are never changed. Recovery is not an independent replicate.
"""
import json,sys,concurrent.futures
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from turtle_loop.engine import Recorder,play,dump
from turtle_loop.providers import Client,Reply,APIError
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'runs/api/20261029_deepseek_recovery'
STRICT='''\nReturn exactly these top-level keys: checkpoints, material_contradiction, irrelevant, rubric_conflict, full_solution, completion_note, fact_coverage, requirement_coverage, contradictions. Include all keys. completion_note must be a nonempty string. Each coverage row has ONLY id,status,evidence, one per required ID, no duplicates. Checkpoint rows have ONLY id,credit,evidence,reason. Contradiction rows have ONLY quote,reference,checkpoint_ids. Do not add reason or missing_note to coverage rows. Copy verbatim evidence from the submitted explanation. Use empty evidence only for missing. Return a JSON object, without markdown.'''

def run(folder, preserve_last=False):
    puzzle=json.loads((folder/'puzzle_private.json').read_text());config=json.loads((folder/'config.json').read_text());prompts=json.loads((folder/'prompts.json').read_text())
    records=[json.loads(l) for l in (folder/'api_calls.jsonl').read_text().splitlines()]
    tapes={r:[d for d in records if d['role']==r and d['status']=='ok'] for r in ['player','host','grader']}
    rejected=None if preserve_last else tapes['grader'].pop()
    rec=Recorder(OUT/puzzle['id'],puzzle,config,prompts,echo=False)
    dump(rec.folder/'recovery.json',{'source_run':str(folder.relative_to(ROOT)),'independent_replicate':False,'operation':'Replay all recorded responses before malformed final grading; re-evaluate the invalid final once with explicit schema reminder, then continue. Original failure retained.','discarded_invalid_response':rejected})
    class Replay:
        def __init__(self,role):
            self.role=role;self.tape=tapes[role];self.i=0;self.live=Client(config[role],role,rec.audit)
        def complete(self,system,user):
            if self.i<len(self.tape):
                d=self.tape[self.i];self.i+=1
                expected=d['request']['messages']
                allowed_systems=[system,system+STRICT] if self.role=='grader' else [system]
                if len(expected)!=2 or expected[0].get('content') not in allowed_systems or expected[1].get('content')!=user:
                    raise APIError('Replay input mismatch; no continuation permitted')
                if preserve_last and self.role=='grader':
                    original=d['text']
                    d=dict(d);d['text']=original.replace(',\"},{\"id\":\"C3.F1\"', '},{\"id\":\"C3.F1\"')
                    if d['text']!=original:rec.event('syntax_repair',original_text=original,effective_text=d['text'],judgments_changed=False)
                rec.audit({**d,'replayed_from_original':True,'usage':{},'seconds':0})
                return Reply(d['text'],{},d.get('response_id',''),d.get('model_returned',''),d.get('finish_reason','stop'),0)
            if self.role=='grader' and 'evidence_repair' not in user:
                system+=STRICT
            return self.live.complete(system,user)
    result=play(puzzle,config,rec,{r:Replay(r) for r in tapes},prompts)
    dump(rec.folder/'replay_counts.json',{r:len(v) for r,v in tapes.items()})
    print(puzzle['id'],result['status'],result.get('error'),result.get('final_partial_score'),flush=True)
    return result

if __name__=='__main__':
    OUT.mkdir(parents=True,exist_ok=False)
    folders=[]
    for name in ['20261029_deepseek_restart43','20261029_deepseek_remaining']:
        for p in (ROOT/'runs/api'/name).glob('batches/*/*/result.json'):
            if json.loads(p.read_text())['status']=='error':folders.append(p.parent)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(run,folders))
