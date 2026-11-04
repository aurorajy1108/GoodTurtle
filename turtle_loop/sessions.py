"""Game-scoped role sessions and lossless, deterministic JSON context deltas."""
import copy
import hashlib
import json
import tempfile
import uuid
from pathlib import Path

SESSION_INSTRUCTIONS = '''
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
Follow the same response schema on every turn. Do not describe context updates.
'''


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


class GameSession:
    """Each system-prompt lane is isolated (proposal, selection, review, repair)."""
    def __init__(self, role, folder, event):
        self.role, self.folder, self.event = role, Path(folder), event
        self.id = str(uuid.uuid4())
        self.lanes = {}
        self.closed = False
        self.failed = False
        self.event('session_open', role=role, session_id=self.id)

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
        data = payload if lane['previous'] is None else delta(lane['previous'], payload)
        wire_user = json.dumps(data, ensure_ascii=False)
        metadata = {'game_session_id': self.id, 'session_lane_id': lane['id'],
                    'session_turn': lane['turn'] + 1, 'previous_response_id': lane['response_id'],
                    'logical_input_chars': len(user), 'delta_input_chars': len(wire_user)}
        return lane, payload, system + SESSION_INSTRUCTIONS, wire_user, metadata

    def accept(self, lane, payload, wire_user, reply):
        lane['previous'] = copy.deepcopy(payload)
        lane['response_id'] = reply.response_id
        lane['messages'].extend([{'role': 'user', 'content': wire_user},
                                 {'role': 'assistant', 'content': reply.text}])
        lane['turn'] += 1
        self.event('session_turn', role=self.role, session_id=self.id, lane_id=lane['id'],
                   turn=lane['turn'], response_id=reply.response_id)

    def close(self):
        if self.closed:
            return
        for lane in self.lanes.values():
            lane['workspace'].cleanup()
        self.closed = True
        self.event('session_close', role=self.role, session_id=self.id,
                   lanes=[{'id': lane['id'], 'turns': lane['turn'], 'last_response_id': lane['response_id']}
                          for lane in self.lanes.values()])
