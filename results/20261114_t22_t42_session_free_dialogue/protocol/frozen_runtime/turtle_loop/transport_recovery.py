"""Audited exact-request recovery. Never discard an observed model response."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from .sessions import GameSession, restore_context, restorable_chat_records

ROLES = ('player', 'partner', 'host', 'grader')
POSITION = ('role', 'provider', 'model_requested', 'endpoint', 'game_session_id',
            'session_lane_id', 'session_turn', 'previous_response_id', 'request')


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def unobserved(call):
    return not any(call.get(k) for k in ('text', 'response_id', 'usage', 'raw_text'))


def billing_authorized(call):
    if (call.get('provider')!='deepseek' or call.get('status')!='http_error'
            or call.get('http_status')!=402 or not unobserved(call)):
        return False
    path=Path(__file__).resolve().parents[1]/'configs/billing_recovery_authorizations.json'
    if not path.exists():return False
    authorization=json.loads(path.read_text()).get(digest(call))
    return bool(authorization and authorization['request_sha256']==digest(call.get('request')))


def recoverable_transport(call):
    if billing_authorized(call):return True
    if call.get('status') != 'transport_error':
        return False
    if (call.get('safe_pre_send_retry') is True and call.get('transport_phase') == 'open'
            and call.get('transport_category') in ('tls_handshake_failure', 'tls_handshake_eof',
                                                   'dns_resolution', 'network_unreachable_before_send')):
        return True
    # No response was accepted locally. A remote charge remains possible; only
    # judging roles may retry, never resample an actor's action.
    return (call.get('role') in ('host', 'grader') and call.get('transport_phase') == 'read'
            and call.get('transport_category') in ('http_protocol', 'connection_reset', 'timeout'))


def new_read_retry_window(calls, reason):
    """Explicit operator renewal after a paused, exhausted read-retry window."""
    if not isinstance(reason,str) or not reason.strip() or len(reason)>500 or not calls:
        raise ValueError('Read-window renewal requires a short operator reason')
    last=calls[-1]
    count=sum(c.get('status')=='transport_error' and c.get('transport_phase')=='read'
              and all(c.get(k)==last.get(k) for k in POSITION) for c in calls)
    if (not unobserved(last) or last.get('provider')!='deepseek' or not recoverable_transport(last)
            or last.get('transport_phase')!='read' or count<3):
        raise ValueError('Only an exhausted unanswered judging-role read failure may be renewed')
    return {'calls_count':len(calls),'calls_sha256':digest(calls),'request_sha256':digest(last['request']),
            'role':last['role'],'additional_read_failures':3,'reason':reason.strip(),
            'authorized_at':datetime.now(timezone.utc).isoformat()}


def read_retry_window(calls, folder, supplied=None):
    marker=Path(folder)/'transport_read_window.json'
    window=supplied if supplied is not None else (json.loads(marker.read_text()) if marker.exists() else None)
    if window is None:return None
    required={'calls_count','calls_sha256','request_sha256','role','additional_read_failures','reason','authorized_at'}
    if not isinstance(window,dict) or set(window)!=required:raise ValueError('Invalid read-window authorization')
    n=window['calls_count']
    if type(n) is not int or not 0<n<=len(calls) or digest(calls[:n])!=window['calls_sha256']:
        raise ValueError('Read-window authorization does not match original audits')
    reference=new_read_retry_window(calls[:n],window['reason'])
    if any(window[k]!=reference[k] for k in required-{'authorized_at'}):
        raise ValueError('Read-window authorization changed request, role or limit')
    datetime.fromisoformat(window['authorized_at'])
    if all(calls[-1].get(k)==calls[n-1].get(k) for k in POSITION):return window
    return None  # Historical renewal does not apply to another question or role.


def replay_records(calls, events):
    """Only explicit, hash-checked authorizations can remove failed chat attempts.

    These attempts remain in the raw API log and cost accounting. Any subsequent
    retry at that session position must have the identical request.
    """
    skipped = set()
    for event in events:
        if event.get('event') != 'transport_recovery':
            continue
        n = event['calls_count']
        indices = event['failed_call_indices']
        if (not 0 < n <= len(calls) or not indices or len(set(indices)) != len(indices)
                or indices != list(range(indices[0], n))
                or digest(calls[:n]) != event['calls_sha256']):
            raise ValueError('Transport replay proof does not match its original archive')
        failed = calls[n-1]
        if digest(failed['request']) != event['request_sha256']:
            raise ValueError('Transport replay request hash mismatch')
        for index in indices:
            call = calls[index]
            if (not unobserved(call) or (call.get('status') not in ('transport_error','interrupted') and not billing_authorized(call))
                    or any(call.get(k) != failed.get(k) for k in POSITION)):
                raise ValueError('Transport proof contains an observed or changed request')
        # A failed replay may itself be retried in a later authorized archive.
        for call in calls[n:]:
            if any(call.get(k) != failed.get(k) for k in POSITION):
                raise ValueError('First call after transport recovery changed its request or position')
            if call.get('status') == 'ok':
                break
            if not unobserved(call):
                raise ValueError('An observed response cannot be silently replayed')
        skipped.update(indices)
    return [c for i,c in enumerate(calls) if i not in skipped]


def saved_transport_recovery(previous, calls, turns, config, folder, renewed_window=None):
    """Authorize pre-send failures or unanswered judging-role read failures.

    Actor failures must be proven pre-send TLS/DNS failures. No retries after an
    observed answer, HTTP 401/402, truncation, refusal or a grading disagreement.
    """
    folder = Path(folder)
    if ((previous.get('status'), previous.get('stop_reason')) not in
            (('error','APIError'), ('interrupted','user_interrupt'))
            or config.get('session_mode') != 'persistent' or not calls
            or any(t.get('grade',{}).get('complete') for t in turns)):
        return None
    try:
        events = [json.loads(l) for l in (folder/'trajectory.jsonl').read_text().splitlines()]
        # A process may fail a local preflight after authorizing a replay but
        # before making any new call. That pending authorization is not a reply.
        active=digest(calls)
        prior=[e for e in events if not (e.get('event')=='transport_recovery' and
               e.get('calls_count')==len(calls) and e.get('calls_sha256')==active)]
        normalized = replay_records(calls, prior)
        failed = normalized[-1]
        role = failed.get('role')
        if role not in ROLES or failed.get('provider') != 'deepseek' or not unobserved(failed):
            return None
        if failed.get('status') == 'interrupted':
            if previous['status'] != 'interrupted':
                return None
        elif not recoverable_transport(failed):
            return None
        # Count original audits, including previously authorized failed replays.
        # Restarting the supervisor must not reset this per-request limit.
        window=read_retry_window(calls,folder,renewed_window)
        start=window['calls_count'] if window else 0
        read_failures = sum(c.get('status') == 'transport_error' and c.get('transport_phase') == 'read'
                            and all(c.get(k) == failed.get(k) for k in POSITION) for c in calls[start:])
        if failed.get('transport_phase') == 'read' and read_failures >= 3:
            return None
        tail = len(normalized)-1
        while tail and normalized[tail-1].get('status') != 'ok':
            tail -= 1
        for call in normalized[tail:]:
            if (not unobserved(call) or any(call.get(k)!=failed.get(k) for k in POSITION)
                    or (call.get('status')!='interrupted' and not recoverable_transport(call))):
                return None
        prefix = restorable_chat_records(normalized[:tail])
        if any(c.get('provider')!='deepseek' or c.get('role') not in ROLES for c in prefix):
            return None
        pending = bool(turns and 'label' not in turns[-1])
        if any('label' not in t for t in turns[:-1]) or len(turns)>config['max_questions']:
            return None
        if role in ('player','partner') and (pending or len(turns)>=config['max_questions']):
            return None
        if role in ('host','grader') and not pending:
            return None
        payload = None
        for who in ROLES:
            session = GameSession(who, folder, lambda *a,**k: None)
            try:
                session.restore_chat(prefix)
                if who != role:
                    continue
                if who==role and not session.lanes and billing_authorized(failed) and failed.get('session_turn')==1:
                    session.restore_empty_billing_lane(failed)
                lane = next((x for x in session.lanes.values() if x['id']==failed['session_lane_id']), None)
                messages = failed['request']['messages']
                # First-turn recovery is left for explicit review, not a new
                # random lane or a fabricated response used to seed history.
                if (lane is None or session.id != failed['game_session_id']
                        or failed['session_turn'] != lane['turn']+1
                        or failed.get('previous_response_id') != lane['response_id']
                        or messages[1:-1] != lane['messages']
                        or messages[-1].get('role') != 'user' or failed['request'].get('tools')):
                    return None
                prior_system = next((c['request']['messages'][0] for c in reversed(prefix)
                                    if c['role']==role and c['session_lane_id']==lane['id']), messages[0] if billing_authorized(failed) and failed.get('session_turn')==1 else None)
                if messages[0] != prior_system:
                    return None
                payload = restore_context(lane['previous'], messages[-1]['content'])
            finally:
                session.close()
        history = [{'type':t['type'],'text':t['text'],'feedback':t['label']}
                   for t in turns if 'label' in t]
        if role=='host' and (turns[-1]['type']!='question'
                or payload.get('current_question')!=turns[-1]['text'] or payload.get('visible_history')!=history):
            return None
        if role=='grader' and (turns[-1]['type']!='final' or payload.get('evidence_repair')
                or payload.get('submitted_explanation')!=turns[-1]['text']):
            return None
        dialogue = None
        if (folder/'dialogue_policy.json').exists():
            if role not in ('host','player','partner'):return None
            policy=json.loads((folder/'dialogue_policy.json').read_text())
            transcript = [{k:v for k,v in json.loads(l).items() if k!='timestamp'}
                          for l in ((folder/'shared_dialogue.jsonl').read_text().splitlines() if (folder/'shared_dialogue.jsonl').exists() else [])]
            public = [e for e in transcript if e['speaker'] in ('A','B') and e['type'] in ('question','final')]
            feedback = [e for e in transcript if e['speaker']=='Host']
            if (len(public)!=len(turns) or len(feedback)!=len(turns)-int(pending)
                    or [e['message_index'] for e in transcript]!=list(range(1,len(transcript)+1))):
                return None
            for index,(turn,entry) in enumerate(zip(turns,public)):
                if (entry['type']!=turn['type'] or entry['text']!=turn['text']
                        or entry['external_turn']!=turn['index']):return None
                if index<len(feedback):
                    f=feedback[index]
                    if f['submission']!=turn['index'] or f['text']!=turn['label'] or f['in_reply_to']!=entry['speaker']:return None
            if role=='host':
                if not pending or not public or transcript[-1]!=public[-1]:return None
                dialogue={'speaker':public[-1]['effective_next_speaker'],'actor':public[-1]['speaker'],
                          'turn':len(turns),'pending_feedback':True,'transcript_sha256':digest(transcript)}
            else:
                if pending or payload.get('shared_dialogue')!=transcript:return None
                actor='A' if role=='player' else 'B'
                if payload.get('active_speaker')!=actor or payload.get('role_assignment')!=policy['role_assignment']:return None
                tail_entries=[]
                for entry in reversed(transcript):
                    if entry['speaker']=='Host':break
                    tail_entries.append(entry)
                if any(e['type'] not in ('discuss','pass') or e['external_turn']!=len(turns)+1 for e in tail_entries):return None
                internal=len(tail_entries);control=payload['dialogue_control'];retry=payload.get('format_correction',{}).get('retry',0)
                forced=len(turns)>=config['max_questions']-1
                allowed=['final'] if forced else ['question','final']+(['discuss','pass'] if internal<policy['max_discussion'] else [])
                if (control['internal_messages_remaining']!=policy['max_discussion']-internal
                        or control['allowed_actions']!=allowed or control['mandatory_final']!=forced
                        or type(retry) is not int or not 0<=retry<=2):return None
                if retry and payload['format_correction']['invalid_response']!=lane_previous_actor_reply(prefix,failed):return None
                dialogue={'speaker':actor,'actor':actor,'turn':len(turns),'pending_feedback':False,
                          'transcript_sha256':digest(transcript),'resume_payload':payload,
                          'internal_start':internal,'format_attempt':retry}
        elif role=='partner' or (role=='player' and payload.get('visible_history')!=history):
            return None
        indices=[i for i,c in enumerate(calls) if any(c is x for x in normalized[tail:])]
        if indices != list(range(indices[0],len(calls))):
            return None
        result={'role':role,'submission':len(turns) if pending else len(turns)+1,
                'calls_count':len(calls),'calls_sha256':digest(calls),
                'failed_call_indices':indices,'request_sha256':digest(failed['request']),
                'possible_duplicate_remote_charge':not bool(failed.get('safe_pre_send_retry')),
                'dialogue':dialogue}
        if window:result['read_retry_window']=window
        return result
    except (ValueError,TypeError,KeyError,IndexError,StopIteration,OSError):
        return None


def lane_previous_actor_reply(prefix,failed):
    return next(c['text'] for c in reversed(prefix) if c['role']==failed['role'] and c['session_lane_id']==failed['session_lane_id'])
