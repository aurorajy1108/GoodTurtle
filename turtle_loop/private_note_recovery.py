"""Keep a saved truncated private note; never regenerate it or execute its text."""
import json
from pathlib import Path
from .sessions import GameSession,completed_host_replay_records
from .transport_recovery import digest,replay_records


def saved_private_note_recovery(previous,calls,turns,config,folder):
    folder=Path(folder)
    if (previous.get('status')!='error' or previous.get('stop_reason')!='APIError'
            or config.get('session_mode')!='persistent' or not calls
            or len(turns)>=config['max_questions'] or any('label' not in t for t in turns)
            or any(t.get('grade',{}).get('complete') for t in turns)):
        return None
    last=calls[-1];role=last.get('role');phase=last.get('reflection_phase');slot=len(turns)+1
    if (role not in ('player','partner') or last.get('provider')!='deepseek' or last.get('status')!='ok'
            or last.get('finish_reason')!='length' or phase not in ('draft','review')
            or not isinstance(last.get('text'),str) or not last['text'].strip() or not last.get('response_id')
            or last.get('reflection_slot')!=slot):return None
    actor='A' if role=='player' else 'B'
    if last.get('reflection_actor')!=actor:return None
    try:
        key=last['reflection_key'];plan=json.loads((folder/'solver_phase_plan.json').read_text())
        pending=plan['calls'][key];user=pending['user'];control=user['solver_phase']
        if (key!=plan['owners'][str(slot)]+'/'+phase or key.count('/')!=1
                or control['phase']!=phase or control['slot']!=slot or control['actor']!=actor
                or control['force_final'] is not False or pending['max_output_tokens']!=last['request']['max_tokens']
                or type(last.get('usage',{}).get('completion_tokens')) is not int
                or last['usage']['completion_tokens']<=0):return None
        events=[json.loads(l) for l in (folder/'trajectory.jsonl').read_text().splitlines()]
        normalized=replay_records(completed_host_replay_records(calls,events),events)
        for who in ('player','partner','host','grader'):
            session=GameSession(who,folder,lambda *a,**k:None)
            try:
                session.restore_chat(normalized)
                if who!=role:continue
                if len(session.lanes)!=1:return None
                lane=next(iter(session.lanes.values()))
                if (lane['response_id']!=last['response_id'] or lane['previous']!=user
                        or lane['messages'][-1]!=dict(role='assistant',content=last['text'])):return None
            finally:session.close()
        dialogue=None
        if (folder/'dialogue_policy.json').exists():
            policy=json.loads((folder/'dialogue_policy.json').read_text())
            transcript=[{k:v for k,v in json.loads(l).items() if k!='timestamp'}
                        for l in (folder/'shared_dialogue.jsonl').read_text().splitlines()]
            public=[e for e in transcript if e['speaker'] in ('A','B') and e['type'] in ('question','final')]
            feedback=[e for e in transcript if e['speaker']=='Host']
            if (len(public)!=len(turns) or len(feedback)!=len(turns)
                    or [e['message_index'] for e in transcript]!=list(range(1,len(transcript)+1))):return None
            for t,p,f in zip(turns,public,feedback):
                if (p['text']!=t['text'] or p['type']!=t['type'] or p['external_turn']!=t['index']
                        or f['text']!=t['label'] or f['submission']!=t['index'] or f['in_reply_to']!=p['speaker']):return None
            if (user['shared_dialogue']!=transcript or user['active_speaker']!=actor
                    or user['role_assignment']!=policy['role_assignment']):return None
            internal=[]
            for e in reversed(transcript):
                if e['speaker']=='Host':break
                internal.append(e)
            if any(e['type'] not in ('discuss','pass') or e['external_turn']!=slot for e in internal):return None
            if user['dialogue_control']['internal_messages_remaining']!=policy['max_discussion']-len(internal):return None
            retry=user.get('format_correction',{}).get('retry',0)
            if type(retry) is not int or not 0<=retry<=2:return None
            base={k:v for k,v in user.items() if k!='solver_phase'}
            dialogue={'speaker':actor,'actor':actor,'turn':len(turns),'pending_feedback':False,
                      'transcript_sha256':digest(transcript),'resume_payload':base,
                      'internal_start':len(internal),'format_attempt':retry}
        elif role!='player' or user['visible_history']!=[
                {'type':t['type'],'text':t['text'],'feedback':t['label']} for t in turns]:return None
        return {'role':role,'actor':actor,'phase':phase,'submission':slot,'response_id':last['response_id'],
                'reflection_key':key,'calls_sha256':digest(calls),'request_sha256':digest(last['request']),
                'text_sha256':digest(last['text']),'additional_model_calls':0,'dialogue':dialogue,
                'policy':'Retain original incomplete private note in its own session. Never execute or regenerate it; keep all tokens and quota.'}
    except (ValueError,KeyError,TypeError,IndexError,StopIteration,OSError):return None
