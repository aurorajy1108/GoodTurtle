"""Shared solver budgets for a solo/MAS × explicit self-review experiment."""
import json
from copy import deepcopy

from .engine import ProtocolError,dump
from .matched_self_review import extra_calls,solver_usage
from .providers import Client,Reply

PHASE_PROMPT='''
BUDGETED SOLVER PHASE PROTOCOL v1
Follow solver_phase.phase for THIS call. This protocol replaces the base prompt's
action-only output requirement ONLY while the phase is draft or review.
draft: write a concise tentative hypothesis and ONE candidate next action.
review: critically check your own candidate and assumptions. Separate actual Host
feedback from guesses, check identities, missing causal links and repeated questions.
Recommend ONE useful action. Do not treat your earlier notes as confirmed evidence.
During draft/review, do not execute a question, final, discussion or handoff. These
are private notes for the current solver and are NOT messages to the Host/teammate.
action: follow the base action protocol and current allowed actions exactly. Output
ONE explicit typed action with no introductory notes. Use FINAL if force_final=true.
Keep notes within the requested word target; do not pad them to consume tokens.
Use only public puzzle evidence and your own tentative notes. No tools, private
answers, scoring information, or reference-game trajectories are available.
'''


def phase_prompt(mas):
    return PHASE_PROMPT+('''
Only the subsequent typed DISCUSS/PASS/QUESTION/FINAL action is shared. The other
solver cannot see your private notes unless you deliberately communicate useful
conclusions in a shared action. The supplied role assignment remains in effect.
''' if mas else '\nYou are the only Player. There is no teammate or shared-agent dialogue.\n')


class SolverBudget:
    def __init__(self,recorder,budget,review):
        self.recorder,self.budget,self.review=recorder,budget,review
        self.limit=budget.get('submission_cap',100)
        self.path=recorder.folder/'solver_phase_plan.json'
        self.plan=json.loads(self.path.read_text()) if self.path.exists() else {'owners':{},'calls':{}}
        self.forced_final=any(c['user']['solver_phase']['force_final'] for c in self.plan['calls'].values())

    def status(self):
        usage=solver_usage(self.recorder.calls)
        return {**usage,'generation_cap':self.budget['generation_cap'],
                'output_token_cap':self.budget['output_token_cap'],
                'remaining_generations':self.budget['generation_cap']-usage['generations'],
                'remaining_output_tokens':self.budget['output_token_cap']-usage['output_tokens'],
                'review_enabled':self.review,'forced_compute_final':self.forced_final,
                'phase_counts':{p:sum(c.get('reflection_phase')==p and c.get('status')=='ok'
                                    for c in self.recorder.calls) for p in ('draft','review','action')},
                'matching':'Shared actor-generation/output ceilings; actual input/cache/cost are reported separately.'}

    def save(self):
        dump(self.path,self.plan)
        dump(self.recorder.folder/'solver_compute.json',self.status())

    def audit(self,record,metadata):
        self.recorder.audit({**record,**metadata})
        status=self.status()
        dump(self.recorder.folder/'solver_compute.json',status)
        if status['remaining_generations']<0 or status['remaining_output_tokens']<0:
            raise ProtocolError('Provider usage exceeded the shared solver budget')


class BudgetedAgent:
    """Wrap one persistent Client. A/B share a ledger, never their private notes."""
    def __init__(self,profile,role,ledger,actor='A'):
        self.role,self.ledger,self.actor=role,ledger,actor
        self.active={}
        self.client=Client(deepcopy(profile),role,lambda record:ledger.audit(record,self.active))
        self.profile=self.client.profile
        self.base_cap=profile.get('max_output_tokens',8192)
        self.compute_budget_final=False

    def begin_game(self,folder,event):self.client.begin_game(folder,event)
    def restore_game(self,folder,event,calls):self.client.restore_game(folder,event,calls)
    def close_game(self):self.client.close_game()

    @property
    def expected_recovery_request(self):return getattr(self.client,'expected_recovery_request',None)
    @expected_recovery_request.setter
    def expected_recovery_request(self,value):self.client.expected_recovery_request=value

    def phase(self,system,payload,slot,decision,phase):
        key=f'{decision}/{phase}'
        observed=[c for c in self.ledger.recorder.calls if c.get('reflection_key')==key and c.get('status')=='ok']
        if observed:
            if len(observed)!=1:raise ProtocolError('Duplicate observed solver phase')
            c=observed[0]
            return Reply(c['text'],c.get('usage',{}),response_id=c.get('response_id',''),finish_reason=c.get('finish_reason','stop'))
        if key not in self.ledger.plan['calls']:
            status=self.ledger.status()
            force=phase=='action' and (slot==self.ledger.limit or status['remaining_generations']<=1
                                       or status['remaining_output_tokens']<3072)
            if status['remaining_generations']<=0:raise ProtocolError('No shared solver generations remain')
            cap=min(self.base_cap,2048,status['remaining_output_tokens']-(0 if force else 1024))
            if cap<128:raise ProtocolError('Insufficient solver token reserve')
            user=deepcopy(payload)
            user.update(action_protocol='prefix-v1',solver_phase={'phase':phase,'slot':slot,'actor':self.actor,
                        'force_final':force,'note_word_target':160,'remaining_generations':status['remaining_generations'],
                        'remaining_output_tokens':status['remaining_output_tokens']})
            if force:
                user['turn_control']='This is the mandatory last turn because the solver or public budget is ending. Return FINAL now even if uncertain.'
                if 'dialogue_control' in user:
                    from .dialogue_contract import dialogue_contract_text
                    user['dialogue_control'].update(allowed_actions=['final'],mandatory_final=True,
                                                     response_contract=dialogue_contract_text(['final'],True))
            self.ledger.plan['calls'][key]={'user':user,'max_output_tokens':cap}
            self.ledger.forced_final|=force
            self.ledger.save()
        plan=self.ledger.plan['calls'][key]
        self.compute_budget_final=bool(plan['user']['solver_phase']['force_final'])
        self.active={'reflection_key':key,'reflection_phase':phase,'reflection_slot':slot,'reflection_actor':self.actor}
        self.profile['max_output_tokens']=plan['max_output_tokens']
        reply=self.client.complete(system+phase_prompt('dialogue_control' in plan['user']),
                                   json.dumps(plan['user'],ensure_ascii=False))
        self.ledger.recorder.event('solver_phase',slot=slot,actor=self.actor,phase=phase,
                                   response_id=reply.response_id,text=reply.text)
        return reply

    def complete(self,system,user):
        payload=json.loads(user)
        # Never let an accidentally leaked private field reach the actor.
        allowed={'opening','visible_history','turn_control','action_protocol','format_correction',
                 'active_speaker','role_assignment','shared_dialogue','dialogue_control','solver_phase'}
        if set(payload)-allowed:raise ProtocolError('Unexpected private or unsupported solver payload field')
        slot=len(self.ledger.recorder.turns)+1
        correction=payload.get('format_correction',{})
        # A correction is a new, paid generation, but never gains another review.
        import hashlib
        retry=hashlib.sha256(json.dumps(correction,sort_keys=True).encode()).hexdigest()[:12]
        position=len(payload.get('shared_dialogue',payload.get('visible_history',[])))
        decision=f'{slot}:{self.actor}:{position}:{retry}'
        owner=self.ledger.plan['owners'].setdefault(str(slot),decision)
        self.ledger.save()
        if self.ledger.review and owner==decision:
            extras=extra_calls(slot,self.ledger.budget['generation_cap'],self.ledger.limit)
            phases=(['draft'] if extras==2 else [])+(['review'] if extras else [])
            if extras>2:raise ValueError('Review schedule supports at most two extra phases')
            for phase in phases:
                key=f'{decision}/{phase}'
                status=self.ledger.status()
                if key not in self.ledger.plan['calls'] and (status['remaining_generations']<=self.ledger.limit-slot+1
                        or status['remaining_output_tokens']<5120+(self.ledger.limit-slot)*16):
                    continue
                self.phase(system,payload,slot,decision,phase)
        return self.phase(system,payload,slot,decision,'action')
