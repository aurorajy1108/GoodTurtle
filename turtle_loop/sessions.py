"""Game-scoped role sessions and lossless, deterministic JSON context deltas."""
import copy
import hashlib
import json
import tempfile
import uuid
from pathlib import Path

V1_SESSION_INSTRUCTIONS = '''
SESSION PROTOCOL v1: Messages after the initial JSON carry context_update.
Maintain the supplied JSON context: set replaces a top-level field completely;
remove deletes fields; append_visible_history appends to visible_history.
append_shared_dialogue appends speaker-tagged messages to shared_dialogue.
update_objects applies these same rules recursively inside each named object.
For shared_buffer/private exploration, visible_history may be replaced to restore
chronological order at synchronization; no missing teammate answers may be inferred.
Only the current context's question/submission/turn_control is active. Old examples
are historical references, not additional story facts. Never carry a prior submitted
explanation or grade into the current submission's evidence. Judge only its text.
Follow the response schema specified for the current turn. Do not describe context updates.
'''

LEGACY_SESSION_INSTRUCTIONS=V1_SESSION_INSTRUCTIONS.replace(
    'Follow the response schema specified for the current turn.',
    'Follow the same response schema on every turn.')

SESSION_INSTRUCTIONS = V1_SESSION_INSTRUCTIONS.replace('SESSION PROTOCOL v1:', 'SESSION PROTOCOL v2:') + '''
REFERENCE CACHE: active_puzzle/story_context may contain reference_library and
active_example_ids instead of host_examples. reference_library maps content IDs
to complete reference question/answer/history objects. Entries are sent once and
retained; active_example_ids selects the references retrieved for THIS turn.
Inactive entries are not current evidence. Reference histories are hypothetical
examples, never the current public history. The canonical story overrides examples
and earlier mistaken host replies. Never infer a new fact from a cache update.
'''


def cache_references(payload, previous):
    """Each semantic reference is transmitted once per lane, without provenance.

    Keep the controller's full canonical story and current retrieval intact. Only
    repeated reference bodies are interned; no lossy history or story summary.
    """
    result = copy.deepcopy(payload)
    for field in ('active_puzzle', 'story_context'):
        story = result.get(field)
        if not isinstance(story, dict) or 'host_examples' not in story:
            continue
        prior = (previous or {}).get(field, {})
        library = copy.deepcopy(prior.get('reference_library', {}))
        active = []
        for example in story.pop('host_examples'):
            semantic = json.dumps(example, ensure_ascii=False, sort_keys=True)
            key = hashlib.sha256(semantic.encode()).hexdigest()[:16]
            if key in library and library[key] != example:
                raise ValueError('Reference content ID collision')
            library[key] = example
            active.append(key)
        story.update(reference_library=library, active_example_ids=active)
    return result


def delta(previous, current):
    """Exact reconstruction, not model summarization; shared-buffer reorder is a set."""
    updates, removed, appended, nested = {}, sorted(set(previous) - set(current)), {}, {}
    for key, value in current.items():
        if key in previous and previous[key] == value:
            continue
        old = previous.get(key)
        if key in ('visible_history','shared_dialogue') and isinstance(old, list) and isinstance(value, list) and value[:len(old)] == old:
            appended['append_'+key] = value[len(old):]
        elif isinstance(old, dict) and isinstance(value, dict):
            nested[key] = delta(old, value)['context_update']
        else:
            updates[key] = value
    result = {'set': updates, 'remove': removed}
    result.update(appended)
    if nested:
        result['update_objects'] = nested
    return {'context_update': result}


def restore_context(previous, wire):
    """Reconstruct controller JSON from the exact saved messages, without a model."""
    value=json.loads(wire)
    if not isinstance(value,dict):
        raise ValueError('Saved session payload must be an object')
    if 'context_update' not in value:
        if previous is not None:
            raise ValueError('Expected a saved context delta after the first message')
        return value
    if set(value)!={'context_update'} or previous is None:
        raise ValueError('Invalid saved initial context/delta')
    def apply(context, update):
        if (not isinstance(context,dict) or not isinstance(update,dict)
                or not set(update)<= {'set','remove','update_objects','append_visible_history','append_shared_dialogue'}
                or not isinstance(update.get('set'),dict) or not isinstance(update.get('remove'),list)
                or not all(isinstance(k,str) for k in update['remove'])):
            raise ValueError('Invalid saved context update')
        result=copy.deepcopy(context)
        for key in update['remove']:result.pop(key,None)
        result.update(update['set'])
        for key in ('visible_history','shared_dialogue'):
            if 'append_'+key in update:
                if not isinstance(result.get(key),list) or not isinstance(update['append_'+key],list):
                    raise ValueError('Invalid saved history append')
                result[key].extend(update['append_'+key])
        nested=update.get('update_objects',{})
        if not isinstance(nested,dict):raise ValueError('Invalid saved nested update')
        for key, child in nested.items():result[key]=apply(result.get(key),child)
        return result
    return apply(previous,value['context_update'])


class GameSession:
    """Each system-prompt lane is isolated (proposal, selection, review, repair)."""
    def __init__(self, role, folder, event, session_id=None):
        self.role, self.folder, self.event = role, Path(folder), event
        self.id = session_id or str(uuid.uuid4())
        self.lanes = {}
        self.closed = False
        self.failed = False
        self.event('session_reopen' if session_id else 'session_open', role=role, session_id=self.id)

    def prepare(self, system, user):
        if self.closed:
            raise ValueError('Session is closed')
        if self.failed:
            raise ValueError('Session failed; refusing ambiguous retry or fresh-session fallback')
        payload = json.loads(user)
        if not isinstance(payload, dict):
            raise ValueError('Persistent sessions require a JSON object payload')
        key = hashlib.sha256(system.encode()).hexdigest()
        if key not in self.lanes:
            workspace = tempfile.TemporaryDirectory(prefix='turtle-session-')
            self.lanes[key] = {'id': str(uuid.uuid4()), 'workspace': workspace,
                               'previous': None, 'response_id': '', 'messages': [], 'turn': 0}
        lane = self.lanes[key]
        if self.role in ('host', 'grader') and lane.get('session_instructions', SESSION_INSTRUCTIONS) == SESSION_INSTRUCTIONS:
            payload = cache_references(payload, lane['previous'])
        data = payload if lane['previous'] is None else delta(lane['previous'], payload)
        wire_user = json.dumps(data, ensure_ascii=False)
        metadata = {'game_session_id': self.id, 'session_lane_id': lane['id'],
                    'session_turn': lane['turn'] + 1, 'previous_response_id': lane['response_id'],
                    'logical_input_chars': len(user), 'delta_input_chars': len(wire_user)}
        return lane, payload, system + lane.get('session_instructions',SESSION_INSTRUCTIONS), wire_user, metadata

    def accept(self, lane, payload, wire_user, reply):
        lane['previous'] = copy.deepcopy(payload)
        lane['response_id'] = reply.response_id
        lane['messages'].extend([{'role': 'user', 'content': wire_user},
                                 {'role': 'assistant', 'content': reply.text}])
        lane['turn'] += 1
        self.event('session_turn', role=self.role, session_id=self.id, lane_id=lane['id'],
                   turn=lane['turn'], response_id=reply.response_id)

    def restore_chat(self, records):
        """DeepSeek no-tools chat has no hidden remote thread: restore its messages."""
        if self.lanes or self.closed or self.failed:
            raise ValueError('Restore requires a fresh local session')
        calls=[c for c in records if c.get('role')==self.role]
        if not calls:return
        ids={c.get('game_session_id') for c in calls}
        if len(ids)!=1 or None in ids:
            raise ValueError('Saved role has inconsistent session IDs')
        states={}
        for call in calls:
            if call.get('provider')!='deepseek' or call.get('status')!='ok' or not call.get('text'):
                raise ValueError('Only complete DeepSeek chat replies can be restored')
            messages=call.get('request',{}).get('messages',[])
            instruction=next((s for s in (SESSION_INSTRUCTIONS,V1_SESSION_INSTRUCTIONS,LEGACY_SESSION_INSTRUCTIONS)
                              if messages and messages[0].get('content','').endswith(s)),None)
            if (len(messages)<2 or messages[0].get('role')!='system' or messages[-1].get('role')!='user'
                    or instruction is None
                    or call.get('request',{}).get('tools')):
                raise ValueError('Saved chat does not match the local no-tools session protocol')
            system=messages[0]['content'][:-len(instruction)]
            key=hashlib.sha256(system.encode()).hexdigest()
            state=states.setdefault(key,{'previous':None,'messages':[],'turn':0,
                                         'response_id':'','id':call.get('session_lane_id'),
                                         'session_instructions':instruction})
            if (not state['id'] or call.get('session_lane_id')!=state['id']
                    or state['session_instructions']!=instruction
                    or call.get('session_turn')!=state['turn']+1
                    or call.get('previous_response_id')!=state['response_id']
                    or messages[1:-1]!=state['messages']):
                raise ValueError('Saved chat chain is incomplete or inconsistent')
            state['previous']=restore_context(state['previous'],messages[-1]['content'])
            state['messages']=copy.deepcopy(messages[1:])+[{'role':'assistant','content':call['text']}]
            state['response_id']=call.get('response_id','')
            state['turn']+=1
        self.id=next(iter(ids))
        for key,state in states.items():
            state['workspace']=tempfile.TemporaryDirectory(prefix='turtle-restored-session-')
            self.lanes[key]=state
        self.event('session_restored',role=self.role,session_id=self.id,
                   lanes=[{'id':s['id'],'turns':s['turn']} for s in states.values()],
                   method='exact_saved_deepseek_chat_messages')

    def close(self):
        if self.closed:
            return
        for lane in self.lanes.values():
            lane['workspace'].cleanup()
        self.closed = True
        self.event('session_close', role=self.role, session_id=self.id,
                   lanes=[{'id': lane['id'], 'turns': lane['turn'], 'last_response_id': lane['response_id']}
                          for lane in self.lanes.values()])
