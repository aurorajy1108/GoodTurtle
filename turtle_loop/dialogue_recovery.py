"""Fail-closed recovery of one explicit saved MAS action; no new solver call."""
import hashlib
import json
from pathlib import Path
from .action_text import recover_prefix_action
from .dialogue_contract import valid_dialogue_action
from .sessions import GameSession


def saved_dialogue_action_recovery(previous,calls,turns,config,folder):
    folder=Path(folder)
    if (previous.get('status')!='error' or previous.get('stop_reason')!='ProtocolError'
            or config.get('session_mode')!='persistent' or not calls or not turns
            or len(turns)>=config['max_questions'] or any('label' not in t for t in turns)
            or any(t.get('grade',{}).get('complete') for t in turns)
            or any(c.get('status')!='ok' or c.get('provider')!='deepseek'
                   or c.get('role') not in ('player','partner','host','grader') for c in calls)):
        return None
    last=calls[-1]
    if last.get('role') not in ('player','partner') or last.get('finish_reason')!='stop':return None
    actor='A' if last['role']=='player' else 'B'
    try:
        fixed=recover_prefix_action(last['text'])
        if not fixed or fixed[1]['method']!='explicit_placeholder_wrapper':return None
        action=fixed[0]
        transcript=[{k:v for k,v in json.loads(x).items() if k!='timestamp'}
                    for x in (folder/'shared_dialogue.jsonl').read_text().splitlines()]
        if not transcript or [e['message_index'] for e in transcript]!=list(range(1,len(transcript)+1)):return None
        public=[e for e in transcript if e['speaker'] in ('A','B') and e['type'] in ('question','final')]
        feedback=[e for e in transcript if e['speaker']=='Host']
        if len(public)!=len(turns) or len(feedback)!=len(turns) or transcript[-1]['speaker']!='Host':return None
        for t,p,f in zip(turns,public,feedback):
            if (p['type']!=t['type'] or p['text']!=t['text'] or p['external_turn']!=t['index']
                    or f['submission']!=t['index'] or f['text']!=t['label'] or f['in_reply_to']!=p['speaker']):return None
        payload=None
        for role in ('player','partner','host','grader'):
            session=GameSession(role,folder,lambda *a,**k:None)
            try:
                session.restore_chat(calls)
                if role in ('player','partner') and len(session.lanes)>1:return None
                if role==last['role']:
                    lane=next(iter(session.lanes.values()))
                    if lane['response_id']!=last['response_id']:return None
                    payload=lane['previous']
            finally:session.close()
        control=payload['dialogue_control']
        if (payload['active_speaker']!=actor or payload['shared_dialogue']!=transcript
                or not valid_dialogue_action(action,control['allowed_actions'],control['mandatory_final'])):return None
        return {'action':action,'actor':actor,'raw':last['text'],'response_id':last['response_id'],
            'submission':len(turns)+1,'method':fixed[1]['method'],
            'calls_sha256':hashlib.sha256(json.dumps(calls,sort_keys=True).encode()).hexdigest(),
            'transcript_sha256':hashlib.sha256(json.dumps(transcript,sort_keys=True).encode()).hexdigest()}
    except (ValueError,KeyError,TypeError,StopIteration,OSError):return None
