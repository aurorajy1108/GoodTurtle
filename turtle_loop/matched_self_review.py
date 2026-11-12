"""One solver, one persistent lane, with preregistered MAS-sized solver budgets.

Only the actor's observed completions and generated tokens constrain this budget.
Input/cache tokens and Host/Grader usage are still recorded, never claimed equal.
"""
import json
import re
from dataclasses import replace
from pathlib import Path

from .engine import ProtocolError, dump, parse_action
from .providers import Client, Reply

INSTRUCTIONS = '''
SINGLE-SOLVER SELF-REVIEW CONTROL (prefix-v1)
You are ONE solver in ONE ongoing conversation, with no teammate or second agent.
The controller supplies phase_control on each call. Follow its current phase:
- draft: write a short working hypothesis and ONE candidate next question or final.
- review: critically check your own hypothesis/candidate using public feedback.
  List established facts separately from guesses, check ambiguous conjunctions,
  overlooked identities and causal links, and recommend ONE useful next action.
  Your earlier draft/review notes are tentative hypotheses, never Host evidence.
- action: output exactly QUESTION followed by a newline and one atomic question,
  or FINAL followed by a newline and a single coherent explanation. No preamble,
  review, second action block, teammate labels or NEXT field in action outputs.
Draft/review calls are private working notes and are NOT submitted to the Host.
Keep notes within the requested word target; do not fill space to use a budget.
When phase_control.force_final is true you MUST output FINAL now, even if unsure.
Use only the current opening, public feedback and your own tentative notes.
Do not request private answers, rubric, scores or reference game information.
'''


def extra_calls(slot, call_cap, limit=100):
    """Spread extra work deterministically; the last public slot has only FINAL."""
    if not 1 <= slot <= limit or limit < 2 or call_cap < limit:
        raise ValueError('Invalid matching quota')
    extras = call_cap - limit
    return 0 if slot == limit else slot*extras//(limit-1) - (slot-1)*extras//(limit-1)


def action_text(raw, force=False):
    """Losslessly accept an explicit single inline QUESTION/FINAL header."""
    if len(re.findall(r'(?m)^[ \t]*(?:QUESTION|FINAL|DISCUSS|PASS)(?=[ \t\r\n:]|$)', raw)) > 1:
        raise ProtocolError('Multiple action headers require review')
    try:
        parse_action(raw, force)
        return raw
    except ProtocolError:
        match = re.fullmatch(r'(QUESTION|FINAL)[ \t]+([^\r\n][\s\S]*)', raw.strip())
        if not match:
            raise
        normalized = match[1]+'\n'+match[2]
        parse_action(normalized, force)
        return normalized


def saved_action_recovery(previous, calls, turns, config, folder):
    """Authorize a local envelope fix, without generating or choosing an answer."""
    from .sessions import GameSession
    from .transport_recovery import digest
    if (previous.get('status') != 'error' or previous.get('stop_reason') != 'ProtocolError'
            or config.get('session_mode') != 'persistent' or not calls
            or calls[-1].get('role') != 'player' or calls[-1].get('self_review_phase') != 'action'
            or any(c.get('status') != 'ok' for c in calls)
            or any('label' not in t for t in turns)):
        return None
    sessions = []
    try:
        for role in ('player', 'host', 'grader'):
            session = GameSession(role, folder, lambda *a, **kw: None)
            sessions.append(session)
            session.restore_chat(calls)
        last = calls[-1]
        lane = next(l for l in sessions[0].lanes.values() if l['id'] == last['session_lane_id'])
        payload = lane['previous']
        phase = payload['phase_control']
        if (phase['submission_slot'] != len(turns)+1 or phase['submission_slot'] > config['max_questions']
                or phase['phase'] != 'action' or payload['visible_history'] != [
                    {'type': t['type'], 'text': t['text'], 'feedback': t['label']} for t in turns]):
            return None
        plan = json.loads((Path(folder)/'self_review_plan.json').read_text())[last['self_review_key']]
        if plan['user'] != payload:
            return None
        normalized = action_text(last['text'], phase['force_final'])
        return {'calls_sha256': digest(calls), 'response_id': last['response_id'],
                'submission': len(turns)+1, 'normalized': normalized,
                'method': 'explicit_inline_header_only', 'model_calls': 0}
    except (ValueError, KeyError, TypeError, OSError, StopIteration):
        return None
    finally:
        for session in sessions:
            session.close()


def solver_usage(calls):
    actors = [c for c in calls if c.get('role') in ('player', 'partner')]
    observed = [c for c in actors if c.get('status') in ('ok', 'mock')]
    outputs = [c.get('usage', {}).get('completion_tokens', c.get('usage', {}).get('output_tokens'))
               for c in observed]
    if any(type(n) is not int or n < 0 for n in outputs):
        raise ProtocolError('Solver token usage missing; pause rather than assume a free call')
    return {'generations': len(observed), 'output_tokens': sum(outputs),
            'input_tokens': sum(c.get('accounting', {}).get('input_tokens') or 0 for c in observed),
            'cached_input_tokens': sum(c.get('accounting', {}).get('cached_input_tokens') or 0 for c in observed),
            'known_cost_usd': sum(c.get('accounting', {}).get('estimated_cost_usd') or 0 for c in actors),
            'unknown_cost_calls': sum(c.get('accounting', {}).get('estimated_cost_usd') is None for c in actors)}


def submitted_review_actions(calls):
    """Count executed actor actions for checked Grader checkpoint recovery.

    Reconstruct each request's logical phase instead of trusting an audit tag.
    Notes stay in the original role history; only the action-count check filters
    them. Invalid actions require an explicit same-slot correction link.
    """
    from .sessions import restore_context
    selected = [c for c in calls if c.get('role') == 'player']
    previous, requests, actions = {}, [], []
    for c in selected:
        lane = c['session_lane_id']
        payload = restore_context(previous.get(lane), c['request']['messages'][-1]['content'])
        previous[lane] = payload
        phase = payload.get('phase_control', {})
        if phase.get('phase') != c.get('self_review_phase') or phase.get('submission_slot') != c.get('self_review_slot'):
            raise ValueError('Self-review phase metadata differs from original request')
        if phase.get('phase') not in ('draft', 'review', 'action'):
            raise ValueError('Unknown self-review phase')
        requests.append(payload)
    for index, (c, payload) in enumerate(zip(selected, requests)):
        if c['self_review_phase'] != 'action':
            continue
        if (index+1 < len(requests) and requests[index+1].get('format_correction', {}).get('invalid_response') == c['text']
                and requests[index+1]['phase_control']['submission_slot'] == c['self_review_slot']):
            continue
        try:
            action_text(c['text'], payload['phase_control']['force_final'])
        except ProtocolError:
            if (index+1 >= len(requests) or requests[index+1].get('format_correction', {}).get('invalid_response') != c['text']
                    or requests[index+1]['phase_control']['submission_slot'] != c['self_review_slot']):
                raise ValueError('Invalid action lacks an explicit same-slot correction')
            continue
        actions.append(c)
    return actions


class MatchedSelfReviewPlayer:
    """Stable system prompt; phases change only the current user payload.

    Planned request payload/cap is saved BEFORE each API call. On recovery,
    already observed phases are reused; the pending phase is sent identically.
    The same persistent Client owns draft, review, action and format corrections.
    """
    role = 'player'

    def __init__(self, profile, recorder, budget):
        self.recorder, self.budget = recorder, budget
        self.limit = budget.get('submission_cap', 100)
        if (type(budget['generation_cap']) is not int or budget['generation_cap'] < self.limit
                or type(budget['output_token_cap']) is not int or budget['output_token_cap'] < 1024):
            raise ValueError('Invalid solver budget')
        self.active = {}
        self.client = Client(dict(profile), 'player', self.audit)
        self.profile = self.client.profile
        self.base_output_cap = profile['max_output_tokens']
        self.plans_path = recorder.folder/'self_review_plan.json'
        self.plans = json.loads(self.plans_path.read_text()) if self.plans_path.exists() else {}
        self.compute_budget_final = False

    @property
    def expected_recovery_request(self):
        return getattr(self.client, 'expected_recovery_request', None)

    @expected_recovery_request.setter
    def expected_recovery_request(self, request):
        self.client.expected_recovery_request = request

    def begin_game(self, folder, event):
        self.client.begin_game(folder, event)

    def restore_game(self, folder, event, calls):
        self.client.restore_game(folder, event, calls)

    def close_game(self):
        self.client.close_game()

    def status(self):
        usage = solver_usage(self.recorder.calls)
        return {**usage, 'generation_cap': self.budget['generation_cap'],
                'output_token_cap': self.budget['output_token_cap'],
                'remaining_generations': self.budget['generation_cap']-usage['generations'],
                'remaining_output_tokens': self.budget['output_token_cap']-usage['output_tokens'],
                'matching': 'equal available generation/output budgets; actual input/cache/cost need not match'}

    def audit(self, record):
        self.recorder.audit({**record, **self.active})
        status = self.status()
        dump(self.recorder.folder/'solver_compute.json', status)
        if status['remaining_generations'] < 0 or status['remaining_output_tokens'] < 0:
            raise ProtocolError('Provider exceeded solver budget; stop and review the raw usage')

    def phase(self, system, payload, slot, phase, index, force=False, correction=None):
        key = f'{slot}:{index}:{phase}'
        saved = [c for c in self.recorder.calls if c.get('self_review_key') == key and c.get('status') == 'ok']
        if saved:
            if len(saved) != 1:
                raise ProtocolError('Duplicate observed self-review phase')
            c = saved[0]
            return Reply(c['text'], c.get('usage', {}), response_id=c.get('response_id', ''),
                         finish_reason=c.get('finish_reason', 'stop'))
        if key not in self.plans:
            status = self.status()
            calls_left, tokens_left = status['remaining_generations'], status['remaining_output_tokens']
            if calls_left < 1 or tokens_left < 1:
                raise ProtocolError('No solver budget remains; no unbudgeted retry permitted')
            # Every non-final phase leaves room for a final generation. Normal
            # action calls also leave that reserve until the final public slot.
            reserve = 0 if force else 768
            cap = min(self.base_output_cap, 1536 if phase != 'action' else 1024,
                      tokens_left-reserve)
            if cap < 128:
                raise ProtocolError('Insufficient token reserve for this planned phase')
            user = {**payload, 'action_protocol': 'prefix-v1', 'phase_control': {
                'phase': phase, 'submission_slot': slot, 'force_final': force,
                'note_word_target': min(160, cap//5), 'generations_remaining': calls_left,
                'output_tokens_remaining': tokens_left}}
            if correction:
                user['format_correction'] = {'instruction': 'Previous action was not executed. Return exactly ONE typed action now. Obey force_final.',
                                           'invalid_response': correction}
            self.plans[key] = {'max_output_tokens': cap, 'user': user}
            dump(self.plans_path, self.plans)
        plan = self.plans[key]
        # No private puzzle/rubric or reference trajectory enters this payload.
        self.active = {'self_review_key': key, 'self_review_phase': phase, 'self_review_slot': slot}
        self.profile['max_output_tokens'] = plan['max_output_tokens']
        response = self.client.complete(system, json.dumps(plan['user'], ensure_ascii=False))
        self.recorder.event('self_review_phase', slot=slot, phase=phase,
                            response_id=response.response_id, text=response.text)
        return response

    def complete(self, system, user):
        payload = json.loads(user)
        if set(payload)-{'opening', 'visible_history', 'turn_control', 'action_protocol'}:
            raise ProtocolError('Self-review control accepts only public current-game context')
        slot = len(payload['visible_history']) + 1
        self.compute_budget_final = False
        system = system + INSTRUCTIONS  # Identical bytes for all phases.
        extras = extra_calls(slot, self.budget['generation_cap'], self.limit)
        if extras > 2:
            raise ValueError('This control supports at most draft + review + action per slot')
        phases = (['draft'] if extras == 2 else []) + (['review'] if extras else []) + ['action']
        for index, phase in enumerate(phases):
            key = f'{slot}:{index}:{phase}'
            cached = key in self.plans
            status = self.status()
            if phase != 'action':
                # Format repairs consume extra calls; never let scheduled notes
                # spend the remaining action/final reserve.
                future_slots = self.limit-slot+1
                if not cached and (status['remaining_generations'] <= future_slots
                                   or status['remaining_output_tokens'] < 2304 + future_slots*32):
                    continue
                self.phase(system, payload, slot, phase, index)
                continue
            force = slot == self.limit or status['remaining_generations'] <= 1 or status['remaining_output_tokens'] < 1792
            if cached:
                force = self.plans[key]['user']['phase_control']['force_final']
            self.compute_budget_final = force and slot < self.limit
            reply = self.phase(system, payload, slot, phase, index, force)
            # Already observed corrections are part of this same conversation.
            # Submit the last returned correction, never resurrect its proposal.
            correction_key = f'{slot}:{index+1}:action'
            if any(c.get('self_review_key') == correction_key and c.get('status') == 'ok' for c in self.recorder.calls):
                force = self.plans[correction_key]['user']['phase_control']['force_final']
                self.compute_budget_final = force and slot < self.limit
                reply = self.phase(system, payload, slot, 'action', index+1, force)
            for retry in range(2):
                try:
                    normalized = action_text(reply.text, force)
                    if normalized != reply.text:
                        self.recorder.event('self_review_action_normalized', response_id=reply.response_id,
                                            slot=slot, method='inline_header_to_newline', model_calls=0)
                    return replace(reply, text=normalized)
                except ProtocolError:
                    status = self.status()
                    if retry or status['remaining_generations'] < 1 or status['remaining_output_tokens'] < 256:
                        raise ProtocolError('Invalid action; matched budget forbids an unbounded format retry')
                    force = force or status['remaining_generations'] <= 1 or status['remaining_output_tokens'] < 1792
                    self.compute_budget_final = force and slot < self.limit
                    reply = self.phase(system, payload, slot, 'action', index+1, force, correction=reply.text)
        raise ProtocolError('Missing action phase')
