"""Checked recovery of an unexecuted Host label, without changing puzzle truth."""
import json
from pathlib import Path

from .host import normalize_host_label
from .host_context import LABELS
from .sessions import GameSession,completed_host_replay_records,restore_context
from .transport_recovery import POSITION,digest,replay_records


def empty_host(call):
    return (call.get('role')=='host' and call.get('provider')=='deepseek' and call.get('status')=='ok'
            and isinstance(call.get('text'),str) and not call['text'].strip()
            and call.get('finish_reason')=='stop' and bool(call.get('response_id')))


def saved_host_output_recovery(previous,calls,turns,config,folder):
    """Accept one unique label envelope, or at most two retries after no label.

    A visible substantive answer, a truncation/refusal, a changed request, or a
    question that already has public feedback cannot be retried by this path.
    """
    if (previous.get('status')!='error' or previous.get('stop_reason') not in ('APIError','ProtocolError')
            or config.get('session_mode')!='persistent' or config.get('host',{}).get('provider')!='deepseek'
            or not calls or not turns or turns[-1].get('type')!='question' or 'label' in turns[-1]
            or len(turns)>config['max_questions'] or any('label' not in t for t in turns[:-1])
            or any(t.get('grade',{}).get('complete') for t in turns)):
        return None
    sessions=[]
    try:
        folder=Path(folder)
        events=[json.loads(s) for s in (folder/'trajectory.jsonl').read_text().splitlines()]
        normalized=replay_records(completed_host_replay_records(calls,events),events)
        last=normalized[-1]
        if (last.get('role')!='host' or last.get('provider')!='deepseek' or last.get('status')!='ok'
                or last.get('finish_reason')!='stop' or not isinstance(last.get('text'),str)
                or last['text'].strip() in LABELS):return None
        label=normalize_host_label(last['text'])
        mode='normalize' if label is not None else 'retry_empty' if empty_host(last) else None
        if mode is None:return None
        start=len(normalized)-1
        if mode=='retry_empty':
            while start and empty_host(normalized[start-1]) and all(
                    normalized[start-1].get(k)==last.get(k) for k in POSITION):start-=1
            empty_count=len(normalized)-start
            if empty_count>=3:return None
            prefix=normalized[:start]
        else:
            empty_count=0;prefix=normalized
        if any(c.get('provider')!='deepseek' for c in prefix if c.get('role') in ('player','partner','host','grader')):
            return None
        payload=None
        for role in ('player','partner','host','grader'):
            session=GameSession(role,folder,lambda *a,**kw:None);sessions.append(session)
            session.restore_chat(prefix)
            if role!='host':continue
            lane=next(l for l in session.lanes.values() if l['id']==last['session_lane_id'])
            if session.id!=last['game_session_id']:return None
            if mode=='normalize':payload=lane['previous']
            else:
                messages=last['request']['messages']
                if (last['session_turn']!=lane['turn']+1 or last.get('previous_response_id')!=lane['response_id']
                        or messages[1:-1]!=lane['messages'] or messages[-1].get('role')!='user'
                        or last['request'].get('tools')):return None
                prior=next(c for c in reversed(prefix) if c.get('role')=='host' and c.get('session_lane_id')==lane['id'])
                if messages[0]!=prior['request']['messages'][0]:return None
                payload=restore_context(lane['previous'],messages[-1]['content'])
        history=[{'type':t['type'],'text':t['text'],'feedback':t['label']} for t in turns[:-1]]
        if payload.get('current_question')!=turns[-1]['text'] or payload.get('visible_history')!=history:return None
        dialogue=None
        if (folder/'dialogue_policy.json').exists():
            transcript=[{k:v for k,v in json.loads(s).items() if k!='timestamp'}
                        for s in (folder/'shared_dialogue.jsonl').read_text().splitlines()]
            public=[e for e in transcript if e['speaker'] in ('A','B') and e['type'] in ('question','final')]
            feedback=[e for e in transcript if e['speaker']=='Host']
            if len(public)!=len(turns) or len(feedback)!=len(turns)-1 or transcript[-1]!=public[-1]:return None
            if [e['message_index'] for e in transcript]!=list(range(1,len(transcript)+1)):return None
            for i,(t,e) in enumerate(zip(turns,public)):
                if e['type']!=t['type'] or e['text']!=t['text'] or e['external_turn']!=t['index']:return None
                if i<len(feedback) and (feedback[i]['submission']!=t['index'] or feedback[i]['text']!=t['label']
                        or feedback[i]['in_reply_to']!=e['speaker']):return None
            dialogue={'speaker':public[-1]['effective_next_speaker'],'actor':public[-1]['speaker'],
                      'turn':len(turns),'pending_feedback':True,'transcript_sha256':digest(transcript)}
        # Indices refer to the untouched audit, including earlier transport costs.
        empty_indices=[i for i,c in enumerate(calls) if mode=='retry_empty' and
                       any(c is x for x in normalized[start:])]
        return {'mode':mode,'role':'host','submission':len(turns),'calls_count':len(calls),
                'calls_sha256':digest(calls),'response_id':last['response_id'],'request':last['request'],
                'request_sha256':digest(last['request']),'raw':last['text'],'label':label,
                'empty_count':empty_count,'empty_indices':empty_indices,'dialogue':dialogue,
                'additional_host_calls':0 if mode=='normalize' else 1,
                'policy':'Envelope normalization or bounded exact replay after no visible label. Raw records and costs retained; no Player resampling.'}
    except (ValueError,TypeError,KeyError,IndexError,StopIteration,OSError):return None
    finally:
        for session in sessions:session.close()
