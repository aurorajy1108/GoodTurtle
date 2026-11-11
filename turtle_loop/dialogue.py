"""Two persistent solvers in one public conversation, with explicit role ablations."""
import html
import json
from collections import Counter
from dataclasses import replace

from .engine import ProtocolError, ROOT, dump, parse_player_json
from .dialogue_contract import dialogue_contract_text, valid_dialogue_action

ROLE_PROFILES = {
    'investigator': 'Develop and test explanations of identities, setting, event order and the main causal mechanism. Connect confirmed facts into a coherent story; explicitly distinguish hypotheses from host-confirmed facts.',
    'critic': 'Challenge unsupported assumptions, propose alternative interpretations, and test missing causal links, motives and contradictions. Suggest discriminating questions rather than only criticizing. Help complete the story.',
    'generalist': 'Collaboratively investigate identities, setting, event order, causes and motives. Challenge assumptions and combine confirmed facts into a complete story.',
}
DIALOGUE_PROMPT = '''
SHARED DIALOGUE PROTOCOL v3 (prefix-v1).
You are active_speaker, one of two independent solvers in the SAME public chat.
The role_assignment specifies BOTH roles. Your specialty guides attention, but both
agents may ask the host directly, discuss, hand over, or submit a final solution.
shared_dialogue is the complete public conversation, including both agents' messages
and host feedback. Agent discussion is fallible hypothesis, never host evidence.
Cooperate naturally: respond to a useful teammate point, pursue a promising lead,
or ask the teammate to challenge your interpretation. Avoid repeating rejected
finals without new facts. Share concise reasons and hypotheses, not hidden chain of thought.
Return exactly ONE plain text action using dialogue_control.response_contract. If you want to discuss and then ask a question, choose only one
action now; wait for your next turn before returning another action.
question goes directly to the host; final goes to the grader; discuss/pass go only
to your teammate. next_speaker proposes who acts after this message/host feedback;
you may choose yourself to follow a lead. Under alternating scheduling the controller
overrides that proposal. Respect dialogue_control.allowed_actions. When internal
discussion allowance is exhausted, ask a question or submit. On the mandatory last
turn return final immediately. Both agents share ONE external submission quota.
On the mandatory final turn next_speaker is optional, because the game ends.
Do not claim the host has confirmed anything it has not said. No tools.
'''

def dialogue_system_prompt():
    return (ROOT / 'prompts/loop_player_dialogue_v1.txt').read_text() + DIALOGUE_PROMPT


def add_dialogue_arguments(parser):
    parser.add_argument('--dialogue-roles', choices=['complementary','symmetric','swapped'], default='complementary',
                        help='free_dialogue role ablation: investigator/critic, two generalists, or swapped specialties')
    parser.add_argument('--dialogue-scheduling', choices=['adaptive','alternating'], default='adaptive',
                        help='adaptive follows next_speaker; alternating changes speaker after every message')
    parser.add_argument('--dialogue-max-discussion', type=int, default=4,
                        help='Maximum internal discuss/pass messages before each external submission; 0 disables discussion')
    parser.add_argument('--dialogue-start', choices=['A','B'], default='A', help='Initial speaker, independently of role assignment')


def dialogue_settings(args):
    result={name:getattr(args,'dialogue_'+name,default) for name,default in
            [('roles','complementary'),('scheduling','adaptive'),('max_discussion',4),('start','A')]}
    if result['roles'] not in ('complementary','symmetric','swapped') or result['scheduling'] not in ('adaptive','alternating') or result['start'] not in ('A','B'):
        raise ValueError('Invalid dialogue role/scheduling/start setting')
    if type(result['max_discussion']) is not int or not 0 <= result['max_discussion'] <= 10:
        raise ValueError('dialogue-max-discussion must be an integer in [0,10]')
    ids = (['investigator','critic'] if result['roles']=='complementary' else
           ['critic','investigator'] if result['roles']=='swapped' else ['generalist','generalist'])
    result['role_assignment']={actor:{'specialty':specialty,'instruction':ROLE_PROFILES[specialty]}
                               for actor,specialty in zip(('A','B'),ids)}
    result['protocol']='shared-dialogue-v3-prefix-v1'
    result['format_correction_max_retries']=2
    return result


class FreeDialoguePlayer:
    def __init__(self, leader, partner, recorder, settings):
        self.leader,self.partner,self.recorder=leader,partner,recorder
        self.settings=settings
        self.transcript=[]
        self.speaker=settings['start']
        self.turn=0
        self.pending=None
        if getattr(recorder,'resumed',False) and recorder.turns:
            raise ValueError('free_dialogue mid-game recovery is not supported; preserve archive and start a labeled new game')
        dump(recorder.folder/'dialogue_policy.json',settings)

    def _append(self, entry):
        entry={'message_index':len(self.transcript)+1,**entry}
        self.transcript.append(entry)
        self.recorder.append('shared_dialogue.jsonl',entry)
        title='Shared conversation - A: '+self.settings['role_assignment']['A']['specialty']+'; B: '+self.settings['role_assignment']['B']['specialty']
        blocks=''.join('<p><b>'+html.escape(f"{e['speaker']} · {e['type']}")+'</b><br>'+html.escape(e['text'])+'</p>' for e in self.transcript)
        (self.recorder.folder/'shared_dialogue.html').write_text('<meta charset="utf-8"><title>Shared conversation</title><main style="max-width:850px;margin:40px auto;font:16px/1.6 sans-serif;white-space:pre-wrap"><h1>'+html.escape(title)+'</h1>'+blocks+'</main>')
        counts={actor:dict(Counter(e['type'] for e in self.transcript if e['speaker']==actor)) for actor in ('A','B')}
        dump(self.recorder.folder/'dialogue_metrics.json',{'settings':self.settings,'counts_by_actor':counts,
             'external_submissions':sum(e['type'] in ('question','final') and e['speaker'] in ('A','B') for e in self.transcript),
             'internal_messages':sum(e['type'] in ('discuss','pass') for e in self.transcript)})

    def complete(self, system, user):
        if self.pending is not None:
            raise ProtocolError('Dialogue must receive host feedback before the next external submission')
        base=json.loads(user)
        # The shared chat already contains the same public host feedback with
        # speaker attribution, so do not send a second copy as visible_history.
        base.pop('visible_history',None)
        self.turn+=1
        forced='mandatory last turn' in base.get('turn_control','').lower()
        for internal in range(self.settings['max_discussion']+1):
            actor=self.speaker
            allowed=['final'] if forced else ['question','final']
            if not forced and internal < self.settings['max_discussion']:
                allowed+=['discuss','pass']
            payload={**base,'action_protocol':'prefix-v1','active_speaker':actor,'role_assignment':self.settings['role_assignment'],
                     'shared_dialogue':self.transcript,'dialogue_control':{'allowed_actions':allowed,
                     'internal_messages_remaining':self.settings['max_discussion']-internal,
                     'scheduling':self.settings['scheduling'], 'mandatory_final':forced,
                     'response_contract':dialogue_contract_text(allowed,forced)}}
            client=self.leader if actor=='A' else self.partner
            for attempt in range(3):
                reply=client.complete(dialogue_system_prompt(),json.dumps(payload,ensure_ascii=False))
                try:
                    action,recovery=parse_player_json(reply.text)
                    if not valid_dialogue_action(action,allowed,forced):
                        raise ValueError()
                except (ValueError,TypeError):
                    self.recorder.event('dialogue_format_rejected', submission=self.turn,
                                        actor=actor, attempt=attempt+1, raw_output=reply.text)
                    if attempt == 2:
                        raise ProtocolError('Invalid shared-dialogue action after two format corrections') from None
                    payload['format_correction']={
                        'instruction':'Your previous response was invalid and was not executed. Correct it. '+dialogue_contract_text(allowed,forced),
                        'invalid_response':reply.text,
                        'allowed_actions':allowed,
                        'retry':attempt+1}
                    continue
                if attempt:
                    self.recorder.event('dialogue_format_corrected', submission=self.turn,
                                        actor=actor, retries=attempt, corrected_output=reply.text)
                break
            if 'text_note' in action:
                self.recorder.event('player_action_normalized',actor=actor,submission=self.turn,
                                    removed_fields=['text_note'],raw_player_output=reply.text)
            if recovery:
                self.recorder.event('player_format_recovery', submission=self.turn,
                                    actor=actor, strategy='free_dialogue', **recovery)
            next_actor=(None if forced else action['next_speaker'] if self.settings['scheduling']=='adaptive' else ('B' if actor=='A' else 'A'))
            self._append({'speaker':actor,'specialty':self.settings['role_assignment'][actor]['specialty'],
                          'type':action['type'],'text':action['text'],'external_turn':self.turn,
                          'requested_next_speaker':action.get('next_speaker'),'effective_next_speaker':next_actor})
            self.speaker=next_actor
            if action['type'] in ('question','final'):
                public={key:action[key] for key in ('type','text')}
                self.pending={'actor':actor,'action':public,'submission':self.turn}
                self.recorder.append('collaboration.jsonl',{'turn':self.turn,'strategy':'free_dialogue','actor':actor,
                    'internal_messages':internal,'action':json.dumps(public),'next_speaker':next_actor,
                    'roles':self.settings['roles'],'scheduling':self.settings['scheduling']})
                self.recorder.event('team_action',submission=self.turn,actor=actor,
                                    specialty=self.settings['role_assignment'][actor]['specialty'])
                return replace(reply,text=json.dumps(public,ensure_ascii=False))
        raise ProtocolError('Dialogue did not produce an external action')

    def observe_feedback(self, submission, action, label):
        if self.pending is None or self.pending['submission']!=submission or self.pending['action']!=action:
            raise ProtocolError('Dialogue feedback does not match the pending submission')
        actor=self.pending['actor']
        self._append({'speaker':'Host','type':'feedback','text':label,'submission':submission,
                      'in_reply_to':actor,'evaluated_action_type':action['type']})
        self.pending=None
