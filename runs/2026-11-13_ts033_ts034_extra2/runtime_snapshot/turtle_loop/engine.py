"""Deterministic counting, score calculation and public/private context separation."""
import csv
import html
import hashlib
import json
import math
import re
import statistics
import shutil
import time
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from .providers import APIError
from .host_context import (build_story_context, host_payload, story_fingerprint, grading_fingerprint,
                           grader_story_context, context_policy, RUNTIME_VERSION)
from .coverage import PROTOCOL, fact_specs, requirement_specs, constrain
from .host import answer_question
from .grader import evaluate_final

LABELS = {'yes', 'no', 'yes and no', 'irrelevant'}
ROOT = Path(__file__).resolve().parents[1]


def controller_fingerprint():
    names=('engine.py','host.py','host_context.py','coverage.py','grader.py','providers.py',
           'codex_client.py','experiments.py','sessions.py','dialogue.py','dialogue_contract.py','player_format.py','action_text.py')
    files=[ROOT/'turtle_loop'/name for name in names]
    files.append(ROOT/'configs/player_format_repair.json')
    return hashlib.sha256(b''.join(p.read_bytes() for p in files if p.exists())).hexdigest()


class ProtocolError(ValueError):
    pass


def now():
    return datetime.now(timezone.utc).isoformat()


def dump(path, data):
    path = Path(path)
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
    temp.replace(path)


def repair_missing_question_quote(text):
    """Repair only one missing quote in a complete two-field question object."""
    if not isinstance(text,str):return None
    match=re.fullmatch(
        r'\s*\{\s*"type"\s*:\s*"question"\s*,\s*"text"\s*:\s*"'
        r'((?:[^"\\{}\x00-\x1f]|\\(?:["\\/bfnrt]|u[0-9a-fA-F]{4}))*)\}\s*',text)
    if not match:return None
    # A question mark and final object brace must already be present. Never
    # repair truncated prose, additional objects, keys, braces, or final answers.
    offset=text.rfind('}')
    candidate=text[:offset]+'"'+text[offset:]
    try:value=json.loads(candidate)
    except ValueError:return None
    if not value['text'].rstrip().endswith('?'):return None
    return value,{'method':'missing_question_text_closing_quote','inserted_character':'"',
                  'insert_offset':offset,'characters_added':1}


def repair_question_inner_quotes(text):
    """Escape one unambiguous quoted phrase inside a complete question value."""
    if not isinstance(text,str):return None
    match=re.fullmatch(r'(\s*\{\s*"type"\s*:\s*"question"\s*,\s*"text"\s*:\s*")'
                      r'([\s\S]*)("\s*\}\s*)',text)
    if not match:return None
    body=match.group(2)
    quotes=[];i=0
    while i<len(body):
        char=body[i]
        if char=='\\':i+=2;continue
        if char in '{}' or ord(char)<32:return None
        if char=='"':quotes.append(i)
        i+=1
    if len(quotes)!=2 or not body.rstrip().endswith('?'):return None
    first,last=quotes;phrase=body[first+1:last].strip()
    # Reject possible keys, delimiters, extra objects, and broken envelopes.
    if (not phrase or not any(c.isalpha() for c in phrase)
            or phrase[0] in ',:[]' or ':' in phrase
            or body[:first].rstrip().endswith((',',':','['))
            or body[last+1:].lstrip().startswith((':',',','[',']'))):
        return None
    offsets=[match.start(2)+i for i in quotes]
    candidate=text
    for at in reversed(offsets):candidate=candidate[:at]+'\\'+candidate[at:]
    try:value=json.loads(candidate)
    except ValueError:return None
    if set(value)!={'type','text'} or value['type']!='question':return None
    return value,{'method':'unescaped_question_inner_quotes','escaped_quote_offsets':offsets,
                  'inserted_character':'\\','characters_added':2}


def repair_escaped_question_closing_quote(text):
    """Remove one stray slash before a complete question's closing delimiter."""
    if not isinstance(text, str):return None
    match = re.fullmatch(
        r'(\s*\{\s*"type"\s*:\s*"question"\s*,\s*"text"\s*:\s*")'
        r'((?:[^"\\{}\x00-\x1f]|\\(?:["\\/bfnrt]|u[0-9a-fA-F]{4}))*\?)'
        r'(\\)("\s*\}\s*)', text)
    if not match:return None
    offset=match.start(3)
    candidate=text[:offset]+text[offset+1:]
    try:value=json.loads(candidate)
    except ValueError:return None
    if set(value)!={'type','text'} or value['type']!='question':return None
    return value, {'method':'escaped_question_text_closing_quote',
                   'removed_character':'\\','remove_offset':offset,'characters_removed':1}


def _unique_player_object(pairs):
    value={}
    for key,item in pairs:
        if key in value:raise ValueError('Duplicate player JSON key')
        value[key]=item
    return value


def escape_json_string_newlines(text):
    """Escape literal CR/LF inside JSON strings without changing decoded text."""
    result = []
    in_string = False
    escaped = False
    changed = 0
    for char in text:
        if in_string:
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char == '"':
                in_string = False
            elif char in ('\n', '\r'):
                result.append('\\n' if char == '\n' else '\\r')
                changed += 1
                continue
        elif char == '"':
            in_string = True
        result.append(char)
    return ''.join(result), changed


def parse_player_json(text):
    # Prefix actions preserve the body verbatim; JSON remains readable for archives.
    if isinstance(text, str) and re.match(r'(?:QUESTION|FINAL|DISCUSS|PASS)(?: NEXT=[AB])?\r?\n',text.lstrip()):
        from .action_text import parse_prefix_action
        try:
            return parse_prefix_action(text), None
        except ValueError as exc:
            raise ProtocolError(str(exc)) from None
    # Structured actions already delimit their body. Do not reinterpret words
    # such as "test:" inside a valid JSON text field as a second action envelope.
    try:
        return json.loads(text, object_pairs_hook=_unique_player_object), None
    except (ValueError, TypeError):
        pass
    from .action_text import recover_prefix_action
    try:
        prefix_recovery=recover_prefix_action(text)
    except ValueError as exc:
        raise ProtocolError(str(exc)) from None
    if prefix_recovery:
        return prefix_recovery
    recovery = None
    try:
        value = json.loads(text,object_pairs_hook=_unique_player_object)
    except (ValueError, TypeError):
        repaired=(repair_escaped_question_closing_quote(text)
                  or repair_missing_question_quote(text) or repair_question_inner_quotes(text))
        if repaired:return repaired
        if not isinstance(text, str):
            raise ProtocolError('Player must return one JSON object, without markdown') from None
        if '```' in text:
            raise ProtocolError('Player JSON must not be wrapped in markdown') from None
        escaped_text, count = escape_json_string_newlines(text)
        if count:
            try:
                candidate = json.loads(escaped_text,object_pairs_hook=_unique_player_object)
            except ValueError:
                candidate = None
            if isinstance(candidate, dict):
                return candidate, {'method': 'escape_string_newlines', 'escaped_characters': count}
        decoder = json.JSONDecoder(object_pairs_hook=_unique_player_object)
        objects = []
        index = 0
        while index < len(text):
            start = text.find('{', index)
            if start < 0:
                break
            try:
                candidate, end = decoder.raw_decode(text, start)
            except ValueError:
                index = start + 1
                continue
            if isinstance(candidate, dict):
                objects.append((candidate, start, end))
            index = end
        if len(objects) != 1:
            raise ProtocolError('Player must return one unambiguous JSON object') from None
        value, start, end = objects[0]
        # Do not silently discard a broken or truncated additional JSON object.
        if any(c in text[:start] + text[end:] for c in '{}'):
            raise ProtocolError('Ambiguous extra JSON content in player response') from None
        recovery = {'method': 'single_embedded_json', 'prefix_chars': start,
                    'suffix_chars': len(text) - end}
    return value, recovery


def parse_action(text, force_final=False, audit=None):
    value, recovery = parse_player_json(text)
    if (not isinstance(value, dict) or not {'type','text'} <= set(value) or
            not set(value)<= {'type','text','text_note'} or
            ('text_note' in value and not isinstance(value['text_note'],str)) or
            value['type'] not in ('question', 'final') or not isinstance(value['text'], str)
            or not value['text'].strip()):
        raise ProtocolError('Player JSON must contain type=question|final and nonempty text')
    if force_final and value['type'] != 'final':
        raise ProtocolError('Player violated mandatory final instruction; no question was sent to host')
    if recovery and audit:
        audit(recovery)
    return {key:value[key] for key in ('type','text')}


def grade_final(text, rubric, requirements=None, submitted_explanation=None):
    try:
        value = json.loads(text)
    except (ValueError, TypeError):
        raise ProtocolError('Evaluator must return JSON, without markdown') from None
    flags = {'material_contradiction', 'irrelevant', 'rubric_conflict'}
    coverage_fields = {'fact_coverage', 'requirement_coverage', 'contradictions'} if requirements is not None else set()
    if not isinstance(value, dict) or set(value) != flags | {'checkpoints', 'full_solution', 'completion_note'} | coverage_fields:
        raise ProtocolError('Invalid evaluator fields')
    if any(type(value[k]) is not bool for k in flags | {'full_solution'}):
        raise ProtocolError('Evaluator flags must be JSON booleans')
    if not isinstance(value['completion_note'], str) or not value['completion_note'].strip():
        raise ProtocolError('Evaluator must explain its full-narrative decision privately')
    checkpoints = value['checkpoints']
    if not isinstance(checkpoints, list) or len(checkpoints) != len(rubric):
        raise ProtocolError('Evaluator must score every checkpoint exactly once')
    indexed = {}
    for row in checkpoints:
        if not isinstance(row, dict) or set(row) != {'id', 'credit', 'evidence', 'reason'}:
            raise ProtocolError('Invalid checkpoint fields')
        if (not isinstance(row['id'], str) or row['id'] in indexed
                or type(row['credit']) not in (int, float) or row['credit'] not in (0, 0.5, 1)
                or any(not isinstance(row[k], str) for k in ('evidence', 'reason'))):
            raise ProtocolError('Invalid/duplicate checkpoint ID or credit; use 0/0.5/1')
        if row['credit'] > 0 and not row['evidence'].strip():
            raise ProtocolError('Positive credit must include submission evidence')
        indexed[row['id']] = row
    if set(indexed) != {r['id'] for r in rubric}:
        raise ProtocolError('Evaluator returned wrong checkpoint IDs')
    corrections = []
    if requirements is not None:
        if not isinstance(submitted_explanation, str):
            raise ProtocolError('Coverage grading requires the actual submitted explanation')
        try:
            value, corrections = constrain(value, rubric, requirements, submitted_explanation)
        except ValueError as exc:
            raise ProtocolError(str(exc)) from None
        checkpoints = value['checkpoints']
        indexed = {row['id']: row for row in checkpoints}
    score = sum(Decimal(str(r['weight'])) * Decimal(str(indexed[r['id']]['credit'])) for r in rubric)
    if value['irrelevant'] and score != 0:
        raise ProtocolError('Irrelevant answer cannot also receive positive credit')
    complete = (value['full_solution'] and all(r['credit'] == 1 for r in checkpoints)
                and not any(value[k] for k in flags))
    label = ('yes' if complete else 'irrelevant' if value['irrelevant'] else
             'yes and no' if score > 0 or value['rubric_conflict'] else 'no')
    result = {**value, 'partial_score': float(score), 'complete': complete, 'label': label}
    if requirements is not None:
        result.update(grading_protocol=PROTOCOL, controller_corrections=corrections)
    return result


def _saved_player_recovery(previous, calls, turns, config, mode, events=()):
    """Recover a complete saved solo action without another model generation."""
    from .sessions import restorable_chat_records
    auxiliary=[c for c in calls if c.get('role')=='format_repair']
    if any(c.get('role') not in ('host','player','grader','format_repair') for c in calls):return None
    session_calls=[c for c in calls if c.get('role')!='format_repair']
    original_call_count=len(session_calls)
    try:calls=restorable_chat_records(session_calls)
    except (ValueError,TypeError,KeyError):return None
    if (previous.get('status')!='error' or previous.get('stop_reason')!='ProtocolError'
            or not calls or any('label' not in t for t in turns)
            or any(t.get('grade',{}).get('complete') for t in turns)
            or len(turns)>=config['max_questions']
            or any(config.get(role,{}).get('provider')!='deepseek' for role in ('host','player','grader'))
            or any(c.get('provider')!='deepseek' or c.get('status')!='ok'
                   or c.get('role') not in ('host','player','grader') for c in calls)):
        return None
    last=calls[-1]
    player_calls=[c for c in calls if c.get('role')=='player']
    ignored = set()
    for event in events:
        if event.get('event') != 'player_format_reprompt': continue
        response_id = event.get('source_response_id')
        matches = [c for c in player_calls if c.get('response_id') == response_id]
        if (len(matches) != 1 or response_id in ignored or event.get('counts_as_submission') is not False
                or event.get('authorization') != 'user_requested_reprompt'
                or hashlib.sha256(matches[0].get('text','').encode()).hexdigest() != event.get('raw_sha256')):
            return None
        ignored.add(response_id)
    player_calls=[c for c in player_calls if c.get('response_id') not in ignored]
    if (last.get('role')!='player' or len(player_calls)!=len(turns)+1
            or len({c.get('session_lane_id') for c in player_calls})!=1):
        return None
    try:
        format_recovery=None
        if mode=='user_reprompt':
            if last.get('finish_reason')!='stop' or not last.get('text','').strip():return None
            try:parse_action(last['text'])
            except ProtocolError:pass
            else:return None
            action=None
            format_recovery={'method':'user_requested_reprompt','raw_sha256':hashlib.sha256(last['text'].encode()).hexdigest()}
        elif mode=='text_note':
            raw=json.loads(last['text'])
            if set(raw)!={'type','text','text_note'} or not isinstance(raw['text_note'],str):return None
        elif mode=='auto_format':
            from .player_format import local_repair, load_policy, verbatim_proof
            policy=load_policy()
            if not policy or last.get('finish_reason')!='stop':return None
            fixed=local_repair(last['text'],False,policy)
            if fixed:
                action,format_recovery=fixed
            else:
                try:json.loads(last['text'])
                except ValueError:pass
                else:return None  # Valid JSON with a wrong schema is not a syntax repair.
                repairs=[c for c in auxiliary if c.get('format_source_response_id')==last.get('response_id')]
                if repairs:
                    call=repairs[-1]
                    if call.get('status')!='ok':return None
                    action=parse_action(call['text'])
                    if not verbatim_proof(last['text'],action):return None
                    format_recovery={'method':'saved_codex_verbatim_format','repair_response_id':call.get('response_id')}
                else:
                    action=None
                    format_recovery={'method':'pending_codex_format','raw_sha256':hashlib.sha256(last['text'].encode()).hexdigest()}
        else:
            raw,format_recovery=parse_player_json(last['text'])
            if (not format_recovery or format_recovery['method'] not in
                    ('missing_question_text_closing_quote','unescaped_question_inner_quotes',
                     'escaped_question_text_closing_quote')
                    or last.get('finish_reason')!='stop'):return None
        forced=len(turns)>=config['max_questions']-1
        if mode not in ('auto_format','user_reprompt'):action=parse_action(last['text'],forced)
        elif action is not None and forced and action['type']!='final':return None
        for call,turn in zip(player_calls[:-1],turns):
            try:prior_action=parse_action(call['text'])
            except ProtocolError:
                from .player_format import local_repair, load_policy, verbatim_proof
                fixed=local_repair(call['text'],False,load_policy())
                if fixed:prior_action=fixed[0]
                else:
                    repairs=[r for r in auxiliary if r.get('format_source_response_id')==call.get('response_id') and r.get('status')=='ok']
                    if not repairs:return None
                    prior_action=parse_action(repairs[-1]['text'])
                    if not verbatim_proof(call['text'],prior_action):return None
            if prior_action!={key:turn[key] for key in ('type','text')}:return None
    except (ValueError,TypeError,KeyError,ProtocolError):
        return None
    # Validate complete message chains before accepting the recovery exception.
    from .sessions import GameSession
    for role in ('host','player','grader'):
        session=GameSession(role, '.', lambda *a,**k:None)
        try:session.restore_chat(calls)
        except (ValueError,KeyError,TypeError):return None
        finally:session.close()
    return {'action':action,'forced':forced,'raw':last['text'],'response_id':last.get('response_id'),
            'format_recovery':format_recovery,
            'verified_pre_send_attempts':original_call_count-len(calls)}


def saved_player_note_recovery(previous, calls, turns, config):
    return _saved_player_recovery(previous,calls,turns,config,'text_note')


def saved_player_json_recovery(previous, calls, turns, config):
    return _saved_player_recovery(previous,calls,turns,config,'question_quote')


def saved_player_auto_recovery(previous, calls, turns, config, events=()):
    return _saved_player_recovery(previous,calls,turns,config,'auto_format',events)


def saved_player_user_reprompt(previous, calls, turns, config, events=()):
    return _saved_player_recovery(previous,calls,turns,config,'user_reprompt',events)


def saved_grader_reason_recovery(previous, calls, turns, config, puzzle):
    """Accept an already returned grade rejected only for explanation metadata."""
    from .sessions import restorable_chat_records
    try:calls=restorable_chat_records(calls)
    except (ValueError,TypeError,KeyError):return None
    if (previous.get('status')!='error' or previous.get('stop_reason')!='ProtocolError'
            or not calls or not turns or turns[-1].get('type')!='final' or 'label' in turns[-1]
            or any('label' not in t for t in turns[:-1])
            or any(config.get(role,{}).get('provider')!='deepseek' for role in ('host','player','grader'))
            or any(c.get('provider')!='deepseek' or c.get('status')!='ok'
                   or c.get('role') not in ('host','player','grader') for c in calls)):
        return None
    last=calls[-1]
    players=[c for c in calls if c.get('role')=='player']
    if (last.get('role')!='grader' or len(players)!=len(turns)
            or len({c.get('session_lane_id') for c in players})!=1):return None
    from .coverage import normalize_coverage_metadata
    from .sessions import GameSession
    payload=None
    try:
        for role in ('host','player','grader'):
            session=GameSession(role,'.',lambda *a,**k:None)
            try:
                session.restore_chat(calls)
                if role=='grader':
                    for lane in session.lanes.values():
                        if lane['response_id']==last.get('response_id'):payload=lane['previous']
            finally:session.close()
        if (not payload or puzzle.get('grading_protocol')!=PROTOCOL
                or payload.get('grading_protocol')!=PROTOCOL
                or payload.get('rubric')!=puzzle['rubric']
                or payload.get('completion_requirements',[])!=puzzle.get('completion_requirements',[])
                or payload.get('submitted_explanation')!=turns[-1]['text']
                or payload.get('required_facts')!=fact_specs(puzzle['rubric'])
                or payload.get('required_completion')!=requirement_specs(puzzle.get('completion_requirements',[]))):
            return None
        raw=json.loads(last['text'])
        if not isinstance(raw,dict):return None
        _,changes=normalize_coverage_metadata(raw)
        if not changes:return None
        grade=grade_final(last['text'],puzzle['rubric'],puzzle.get('completion_requirements',[]),turns[-1]['text'])
        return {'grade':grade,'raw':last['text'],'response_id':last.get('response_id'),
                'removed_fields':[c['field'] for c in changes]}
    except (ValueError,TypeError,KeyError,ProtocolError):return None


def saved_host_transport_recovery(previous, calls, turns, config, events=()):
    """Opt-in replay of one unanswered DeepSeek host request, never a saved reply.

    DeepSeek chat history is local. A failed transmission may still have been
    billed remotely; retain the failed audit record and explicitly disclose that.
    """
    original_calls=calls
    from .sessions import restorable_chat_records, completed_host_replay_records
    try:
        calls=completed_host_replay_records(calls,events)
        if calls:
            # Include the final failed attempt while validating an immediately
            # preceding proven pre-send retry, then retain the real failure.
            calls=restorable_chat_records(calls[:-1]+[{**calls[-1], 'status':'ok'}])[:-1]+[calls[-1]]
    except (ValueError,TypeError,KeyError):return None
    roles = ('host', 'player', 'grader')
    if (previous.get('status') != 'error' or previous.get('stop_reason') != 'APIError'
            or config.get('session_mode') != 'persistent' or not calls or not turns
            or turns[-1].get('type') != 'question' or 'label' in turns[-1]
            or any('label' not in t for t in turns[:-1])
            or any(t.get('grade', {}).get('complete') for t in turns)
            or len(turns) >= config['max_questions']
            or any(config.get(r, {}).get('provider') != 'deepseek' for r in roles)):
        return None
    last = calls[-1]
    if (last.get('role') != 'host' or last.get('provider') != 'deepseek'
            or last.get('status') not in ('transport_error','invalid_response')
            or last.get('text') or last.get('response_id') or last.get('usage')
            or last.get('raw_text')
            or any(c.get('provider') != 'deepseek' or c.get('status') != 'ok'
                   or c.get('role') not in roles for c in calls[:-1])):
        return None
    players = [c for c in calls if c.get('role') == 'player']
    ignored=set()
    for event in events:
        if event.get('event')!='player_format_reprompt':continue
        rid=event.get('source_response_id')
        matches=[c for c in players if c.get('response_id')==rid]
        if (len(matches)!=1 or rid in ignored or event.get('counts_as_submission') is not False
                or event.get('authorization')!='user_requested_reprompt'
                or hashlib.sha256(matches[0].get('text','').encode()).hexdigest()!=event.get('raw_sha256')):
            return None
        ignored.add(rid)
    players=[c for c in players if c.get('response_id') not in ignored]
    prior_hosts = [c for c in calls[:-1] if c.get('role') == 'host']
    if len(players) != len(turns):
        return None
    from .sessions import GameSession, restore_context
    try:
        for c,t in zip(players,turns):
            try: action=parse_action(c['text'])
            except ProtocolError:
                from .player_format import local_repair, load_policy
                fixed=local_repair(c['text'],False,load_policy())
                if not fixed:return None
                action=fixed[0]
            if action != {k:t[k] for k in ('type','text')}:return None
        if sum(c.get('role') == 'host' for c in calls) != sum(t['type'] == 'question' for t in turns):
            return None
        for role in roles:
            session = GameSession(role, '.', lambda *a, **k: None)
            try:
                session.restore_chat(calls[:-1])
                if len(session.lanes) > 1:
                    return None  # No team, repair, or review lanes in this mode.
                if role == 'host':
                    if not session.lanes:
                        return None
                    lane = next(iter(session.lanes.values()))
                    messages = last['request']['messages']
                    if (last.get('game_session_id') != session.id
                            or last.get('session_lane_id') != lane['id']
                            or last.get('session_turn') != lane['turn'] + 1
                            or last.get('previous_response_id') != lane['response_id']
                            or messages[:-1] != [prior_hosts[-1]['request']['messages'][0]] + lane['messages']
                            or messages[-1].get('role') != 'user'
                            or last['request'].get('tools')):
                        return None
                    payload = restore_context(lane['previous'], messages[-1]['content'])
                    history = [{'type': t['type'], 'text': t['text'], 'feedback': t['label']}
                               for t in turns[:-1]]
                    if payload.get('current_question') != turns[-1]['text'] or payload.get('visible_history') != history:
                        return None
            finally:
                session.close()
    except (ValueError, KeyError, TypeError, IndexError, ProtocolError):
        return None
    return {'submission': turns[-1]['index'], 'role': 'host',
            'failed_call_sha256': hashlib.sha256(json.dumps(last, sort_keys=True).encode()).hexdigest(),
            'calls_sha256': hashlib.sha256(json.dumps(original_calls, sort_keys=True).encode()).hexdigest(),
            'possible_duplicate_remote_charge': not last.get('safe_pre_send_retry', False),
            'policy': 'Replay only the identical unanswered request; preserve all observed replies, quotas and failed-call accounting.'}


class Recorder:
    @classmethod
    def restore(cls, folder, puzzle, config, prompts, echo=True):
        """Restore an archived session; never reset budget or resample a submitted action."""
        folder = Path(folder)
        for name, expected in [('puzzle_private.json', puzzle), ('config.json', config), ('prompts.json', prompts)]:
            if json.loads((folder/name).read_text()) != expected:
                raise ValueError('Resume input mismatch: '+name)
        previous = json.loads((folder/'result.json').read_text())
        if previous['evaluation_versions'].get('runtime_context_version') != RUNTIME_VERSION:
            raise ValueError('Runtime context policy changed; resume using the original frozen code or start a new game')
        if previous['status'] not in ('completed', 'error', 'interrupted'):
            raise ValueError('Resume requires a stopped or completed game')
        rec = cls.__new__(cls)
        rec.folder, rec.echo = folder, echo
        rec.opening, rec.simulation = puzzle['opening'], previous.get('simulation', False)
        rec.start = time.monotonic() - previous.get('elapsed_seconds', 0)
        rec.versions = previous['evaluation_versions']
        rec.versions.setdefault('original_controller_sha256',rec.versions.get('controller_sha256'))
        rec.versions['controller_sha256'] = controller_fingerprint()
        format_policy=ROOT/'configs/player_format_repair.json'
        if format_policy.exists():
            rec.versions['player_format_policy_sha256']=hashlib.sha256(format_policy.read_bytes()).hexdigest()
        rec.pricing = json.loads((folder/'pricing_snapshot.json').read_text())
        rec.turns, rec.calls = [], []
        events = [json.loads(line) for line in (folder/'trajectory.jsonl').read_text().splitlines()]
        for event in events:
            if event['event'] == 'submission':
                if event['index'] != len(rec.turns)+1:
                    raise ValueError('Invalid resumed submission order')
                rec.turns.append({k:event[k] for k in ('index','type','text','forced')})
            elif event['event'] in ('host_feedback','evaluation'):
                turn = rec.turns[event['submission']-1]
                if 'label' in turn:
                    raise ValueError('Duplicate feedback in resume history')
                turn['label'] = event['label']
                if event['event'] == 'evaluation':
                    turn['grade'] = {k:v for k,v in event.items() if k not in ('event','timestamp','submission','raw')}
        if any('label' not in t for t in rec.turns[:-1]) or len(rec.turns)>config['max_questions']:
            raise ValueError('Invalid pending turn or exhausted quota in resume history')
        if (folder/'api_calls.jsonl').exists():
            rec.calls = [json.loads(line) for line in (folder/'api_calls.jsonl').read_text().splitlines()]
        from .sessions import completed_host_replay_records
        recovery_calls = completed_host_replay_records(rec.calls, events)
        rec.session_restore_calls = recovery_calls
        player_transport_marker = folder/'player_transport_recovery.json'
        player_transport = None
        if player_transport_marker.exists():
            marker=json.loads(player_transport_marker.read_text())
            count=marker['failed_count']; failed=rec.calls[-count:]
            fields=('role','provider','model_requested','endpoint','game_session_id','session_lane_id','session_turn','previous_response_id','request')
            if (not count or len(failed)!=count or len(rec.turns)!=marker['preserved_submissions']
                    or hashlib.sha256(json.dumps(failed,sort_keys=True).encode()).hexdigest()!=marker['failed_sha256']
                    or any(c.get('role')!='player' or c.get('status')!='transport_error' or c.get('safe_pre_send_retry') is not True
                           or c.get('text') or c.get('response_id') or c.get('usage') for c in failed)
                    or any(any(c.get(k)!=failed[0].get(k) for k in fields) for c in failed)
                    or any('label' not in t for t in rec.turns)):
                raise ValueError('Player transport recovery does not match the saved pre-send failures')
            rec.session_restore_calls=completed_host_replay_records(rec.calls[:-count],events)
            from .sessions import GameSession
            for role in ('host','player','grader'):
                session=GameSession(role,'.',lambda *a,**k:None)
                try:session.restore_chat(rec.session_restore_calls)
                finally:session.close()
            rec.pending_player_request=failed[-1]['request']
            player_transport=marker
            rec.event('player_transport_recovery',**marker)
        recovery=(saved_player_note_recovery(previous,recovery_calls,rec.turns,config)
                  or saved_player_json_recovery(previous,recovery_calls,rec.turns,config))
        if not recovery and (ROOT/'configs/player_format_repair.json').exists():
            recovery=saved_player_auto_recovery(previous,recovery_calls,rec.turns,config,events)
        reprompt_marker = folder/'player_format_reprompt.json'
        reprompt = None
        if reprompt_marker.exists():
            marker = json.loads(reprompt_marker.read_text())
            players = [c for c in recovery_calls if c.get('role') == 'player']
            if ((recovery and recovery['action'] is not None) or not players or len(rec.turns) != marker.get('preserved_submissions')
                    or players[-1].get('response_id') != marker.get('response_id')
                    or hashlib.sha256(players[-1].get('text','').encode()).hexdigest() != marker.get('raw_sha256')):
                raise ValueError('Player format reprompt does not match the saved response')
            filtered = [c for c in recovery_calls if not (c.get('role') == 'format_repair'
                        and c.get('format_source_response_id') == marker['response_id'])]
            reprompt = saved_player_user_reprompt(previous,filtered,rec.turns,config,events)
            if not reprompt or reprompt['action'] is not None:
                raise ValueError('Player format reprompt requires one complete invalid response and an intact session')
            recovery = reprompt
        grade_recovery=saved_grader_reason_recovery(previous,rec.calls,rec.turns,config,puzzle)
        transport_recovery = None
        transport_marker = folder / 'host_transport_recovery.json'
        if transport_marker.exists():
            transport_recovery = saved_host_transport_recovery(previous, rec.calls, rec.turns, config, events)
            if not transport_recovery or json.loads(transport_marker.read_text()) != transport_recovery:
                raise ValueError('Pending host transport recovery does not match the saved archive')
        if config.get('session_mode','replay')=='persistent' and previous['status']!='completed' and not (recovery or grade_recovery or transport_recovery or player_transport):
            raise ValueError('Persistent interrupted sessions require supported saved-response recovery or explicit checked DeepSeek pending-host transport recovery; no fresh-session fallback.')
        if previous['status'] == 'error':
            last = rec.calls[-1] if rec.calls else {}
            diagnostic = json.dumps(last.get('diagnostics', [])).lower()
            recoverable = last.get('status') in ('transport_error','http_error','interrupted') or (
                last.get('status') == 'invalid_response' and not last.get('raw_text',last.get('text','')).strip()
                and any(s in diagnostic for s in ('usage limit','at capacity','rate limit','rate_limit')))
            if not recoverable and not (recovery or grade_recovery or transport_recovery):
                raise ValueError('Refuse to resample a protocol/model-output failure')
        rec.resumed = True
        rec.restore_sessions=bool(recovery or grade_recovery or transport_recovery or player_transport)
        if transport_recovery:
            from .sessions import restorable_chat_records
            normalized=completed_host_replay_records(rec.calls,events)
            rec.session_restore_calls = restorable_chat_records(normalized[:-1]+[{**normalized[-1], 'status':'ok'}])[:-1]
            rec.pending_host_request = rec.calls[-1]['request']
            rec.event('host_transport_recovery', **transport_recovery)
            saved_reply_path=folder/'host_saved_response.json'
            if saved_reply_path.exists():
                saved=json.loads(saved_reply_path.read_text())
                failed=rec.calls[-1]
                fields=('role','provider','model_requested','endpoint','game_session_id','session_lane_id','session_turn','previous_response_id','request')
                if (any(saved.get(k)!=failed.get(k) for k in fields)
                        or saved.get('status')!='ok' or saved.get('finish_reason')!='stop'
                        or saved.get('text','').strip() not in LABELS or not saved.get('response_id')):
                    raise ValueError('Saved Host response does not match the unanswered request')
                replay_event={'event':'host_transport_recovery',**transport_recovery}
                normalized=completed_host_replay_records(rec.calls+[saved],events+[replay_event])
                from .sessions import GameSession
                for role in ('host','player','grader'):
                    session=GameSession(role,'.',lambda *a,**k:None)
                    try:session.restore_chat(normalized)
                    finally:session.close()
                rec.audit(saved)
                turn=rec.turns[-1];turn['label']=saved['text'].strip()
                rec.event('host_feedback',submission=turn['index'],label=turn['label'],raw=saved['text'],
                          recovered_from_response_id=saved['response_id'])
                rec.session_restore_calls=normalized
                del rec.pending_host_request
                transport_marker.unlink()
                saved_reply_path.unlink()
        if recovery:
            if reprompt:
                rec.retry_player_format = marker.get('action_type','question')
                rec.event('player_format_reprompt',source_response_id=reprompt['response_id'],
                          raw_sha256=marker['raw_sha256'],counts_as_submission=False,
                          authorization='user_requested_reprompt')
                return rec
            if recovery['action'] is None:
                rec.pending_player_raw=recovery
                rec.event('pending_player_format_repair',source_response_id=recovery['response_id'])
                return rec
            turn={'index':len(rec.turns)+1,**recovery['action'],'forced':recovery['forced']}
            rec.turns.append(turn)
            if recovery.get('format_recovery'):
                rec.event('player_format_recovery',submission=turn['index'],recovery=True,
                          source_response_id=recovery['response_id'],**recovery['format_recovery'])
            else:
                rec.event('player_action_normalized',submission=turn['index'],removed_fields=['text_note'],
                          recovery=True,source_response_id=recovery['response_id'])
            rec.event('submission',**turn,raw_player_output=recovery['raw'],
                      recovered_from_response_id=recovery['response_id'])
        if grade_recovery:
            turn=rec.turns[-1]
            turn.update(grade=grade_recovery['grade'],label=grade_recovery['grade']['label'])
            rec.event('grader_metadata_recovered',submission=turn['index'],
                      source_response_id=grade_recovery['response_id'],removed_fields=grade_recovery['removed_fields'])
            rec.event('evaluation',submission=turn['index'],**grade_recovery['grade'],raw=grade_recovery['raw'],
                      recovered_from_response_id=grade_recovery['response_id'])
        return rec

    def __init__(self, folder, puzzle, config, prompts, echo=True):
        self.folder = Path(folder)
        self.folder.mkdir(parents=True, exist_ok=False)
        self.turns, self.calls, self.echo = [], [], echo
        from .costs import pricing_config
        self.pricing = pricing_config(config.get('pricing'))
        dump(self.folder / 'pricing_snapshot.json', self.pricing)
        self.opening = puzzle['opening']
        self.simulation = config.get('mode') == 'scripted_demo_NOT_model_performance'
        self.start = time.monotonic()
        self.versions = {'story_sha256':story_fingerprint(puzzle), 'grading_sha256':grading_fingerprint(puzzle),
                         'runtime_context_version': RUNTIME_VERSION,
                         'grading_protocol':puzzle.get('grading_protocol', 'legacy'),
                         'prompts_sha256':hashlib.sha256(json.dumps(prompts,sort_keys=True).encode()).hexdigest()}
        self.versions['controller_sha256'] = controller_fingerprint()
        format_policy=ROOT/'configs/player_format_repair.json'
        if format_policy.exists():
            self.versions['player_format_policy_sha256']=hashlib.sha256(format_policy.read_bytes()).hexdigest()
        dump(self.folder / 'puzzle_private.json', puzzle)
        dump(self.folder / 'config.json', config)
        dump(self.folder / 'prompts.json', prompts)
        dump(self.folder / 'runtime_context_policy.json', {
            'version': RUNTIME_VERSION, 'host_calls_per_question': 1,
            'session_mode': config.get('session_mode', 'replay'),
            'history': 'complete role-visible information; lossless deltas in persistent mode',
            **context_policy(config.get('context_policy'))})
        self.event('start', puzzle_id=puzzle['id'], budget=config['max_questions'])

    def append(self, filename, value):
        with (self.folder / filename).open('a') as stream:
            stream.write(json.dumps({'timestamp': now(), **value}, ensure_ascii=False, allow_nan=False) + '\n')
            stream.flush()

    def event(self, kind, **fields):
        self.append('trajectory.jsonl', {'event': kind, **fields})

    def audit(self, value):
        from .costs import account_call
        value = {**value, 'accounting': account_call(value, self.pricing)}
        self.calls.append(value)
        self.append('api_calls.jsonl', value)

    def report(self, status, stop_reason, error=None):
        from .costs import cost_summary, write_call_costs
        accounting = [c['accounting'] for c in self.calls]
        costs = cost_summary(accounting)
        write_call_costs(self.folder, accounting)
        dump(self.folder / 'cost_summary.json', costs)
        questions = sum(t['type'] == 'question' for t in self.turns)
        finals = [t for t in self.turns if t['type'] == 'final']
        graded = [t['grade'] for t in finals if 'grade' in t]
        rejected = sum(not g['complete'] for g in graded)
        success = any(g['complete'] for g in graded)
        last = finals[-1].get('grade') if finals else None
        usage = {}
        for role in sorted({'player', 'host', 'grader'} | {c['role'] for c in self.calls}):
            calls = [c for c in self.calls if c['role'] == role]
            totals = {}
            for c in calls:
                for k, v in c.get('usage', {}).items():
                    if type(v) in (int, float):
                        totals[k] = totals.get(k, 0) + v
            usage[role] = {'http_attempts': len(calls),
                           'successful_responses': sum(c['status'] in ('ok', 'mock') for c in calls),
                           'seconds': sum(c.get('seconds', 0) for c in calls),
                           'provider_reported_usage': totals}
        result = {'status': status, 'stop_reason': stop_reason, 'simulation': self.simulation,
                  'success': success if status == 'completed' else None,
                  'host_questions': questions, 'final_attempts': len(finals),
                  'rejected_finals': rejected, 'counted_questions': questions + rejected,
                  'submissions': len(self.turns),
                  'pending_feedback': sum('label' not in t for t in self.turns),
                  'forced_final': any(t.get('forced') for t in finals),
                  'final_partial_score': last['partial_score'] if last else None,
                  'best_partial_score': max((g['partial_score'] for g in graded), default=None),
                  'latest_final': finals[-1]['text'] if finals else None,
                  'latest_grade': last, 'elapsed_seconds': time.monotonic()-self.start,
                  'usage': usage, 'costs': costs, 'error': error, 'human_review_status': 'pending',
                  'session_transport': {
                      'session_ids': sorted({c['game_session_id'] for c in self.calls if c.get('game_session_id')}),
                      'logical_input_chars': sum(c.get('logical_input_chars', 0) for c in self.calls),
                      'delta_input_chars': sum(c.get('delta_input_chars', 0) for c in self.calls),
                      'note': 'Character counters cover caller input, not billed tokens or replay-provider wire history; see costs.'},
                  'evaluation_versions': self.versions}
        dialogue_metrics = self.folder/'dialogue_metrics.json'
        if dialogue_metrics.exists():
            result['dialogue_metrics'] = json.loads(dialogue_metrics.read_text())
        dump(self.folder / 'result.json', result)
        self.render(result)
        if status != 'running' and not (self.folder/'human_review.csv').exists():
            shutil.copyfile(self.folder/'review_template.csv', self.folder/'human_review.csv')
        return result

    def render(self, result):
        lines = ['# Turtle Soup trajectory', '', self.opening, '',
                 f"Status: {result['status']} | counted questions: {result['counted_questions']} | "
                 f"submissions: {result['submissions']} | final partial score: {result['final_partial_score']}", '']
        lines.extend(['[Token usage and estimated costs](token_costs.csv)', ''])
        cards = []
        review = []
        for turn in self.turns:
            label = turn.get('label', '[pending]')
            lines.extend([f"## {turn['index']} · {turn['type']}" + (' · mandatory final' if turn['forced'] else ''),
                          '', turn['text'], '', f'Host: {label}', ''])
            details = ''
            if 'grade' in turn:
                private = json.dumps(turn['grade'], ensure_ascii=False, indent=2)
                lines.extend(['<details><summary>Private evaluator result (not sent to player)</summary>',
                              '', '```json', private, '```', '</details>', ''])
                details = '<details><summary>Private evaluation</summary><pre>' + html.escape(private) + '</pre></details>'
            cards.append(f"<article><h2>{turn['index']} · {html.escape(turn['type'])}"
                         + (' · mandatory final' if turn['forced'] else '') + '</h2><pre>'
                         + html.escape(turn['text']) + '</pre><p>Host: <strong>' + html.escape(label)
                         + '</strong></p>' + details + '</article>')
            review.append({'submission': turn['index'], 'type': turn['type'], 'text': turn['text'],
                           'host_label': label, 'reviewer_label': '', 'notes': ''})
        (self.folder / 'trajectory.md').write_text('\n'.join(lines))
        refresh = '<meta http-equiv="refresh" content="5">' if result['status'] == 'running' else ''
        (self.folder / 'trajectory.html').write_text(
            '<!doctype html><meta charset="utf-8">' + refresh + '<title>Turtle Soup trajectory</title>'
            '<style>body{font:16px/1.6 system-ui;max-width:1000px;margin:32px auto;padding:0 20px;background:#f6f7fa}'
            'article{background:white;padding:18px;margin:16px 0;border:1px solid #ddd;border-radius:10px}'
            'pre{white-space:pre-wrap;overflow-wrap:anywhere;font:inherit}summary{cursor:pointer}</style>'
            '<h1>Turtle Soup trajectory</h1>'
            + ('<p><strong>SCRIPTED DEMO — not model performance</strong></p>' if result['simulation'] else '')
            + '<pre>' + html.escape(self.opening) + '</pre><p>'
            + html.escape(f"{result['status']} · count {result['counted_questions']} · score {result['final_partial_score']}")
            + '</p>' + ('<p><a href="shared_dialogue.html">Full shared chat: agents A/B and Host</a></p>'
                         if (self.folder/'shared_dialogue.html').exists() else '')
            + '<p><a href="token_costs.csv">Token usage and estimated costs</a> · '
              '<a href="cost_summary.json">Cost summary (USD estimate, not actual bill)</a></p>' + ''.join(cards))
        # Model-owned snapshot: never overwrite a human's separate annotation file.
        with (self.folder / 'review_template.csv').open('w', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=['submission', 'type', 'text', 'host_label', 'reviewer_label', 'notes'])
            writer.writeheader()
            writer.writerows(review)


def load_prompts():
    return {role: (ROOT / f'prompts/loop_{role}_v1.txt').read_text() for role in ('player', 'host', 'grader', 'host_review')}


def play(puzzle, config, recorder, clients, prompts, player_context=None, player_continuation=None):
    """Own all role sessions for exactly one game, including team subroles."""
    opened = []
    def initialize(client):
        if hasattr(client, 'leader') and hasattr(client, 'partner'):
            initialize(client.leader)
            initialize(client.partner)
        elif hasattr(client, 'begin_game') and client not in opened:
            if getattr(recorder,'restore_sessions',False):
                client.restore_game(recorder.folder,recorder.event,
                                    getattr(recorder,'session_restore_calls',recorder.calls))
                if getattr(client, 'role', None) == 'host' and hasattr(recorder, 'pending_host_request'):
                    client.expected_recovery_request = recorder.pending_host_request
                if getattr(client, 'role', None) == 'player' and hasattr(recorder, 'pending_player_request'):
                    client.expected_recovery_request = recorder.pending_player_request
            elif getattr(client,'role',None)=='player' and player_continuation is not None:
                client.inherit_game(recorder.folder,recorder.event,
                                    player_continuation['calls'],player_continuation['boundary'])
            else:
                client.begin_game(recorder.folder, recorder.event)
            opened.append(client)
    try:
        if config.get('session_mode', 'replay') == 'persistent':
            for client in clients.values():
                initialize(client)
        return _play(puzzle, config, recorder, clients, prompts, player_context)
    finally:
        for client in opened:
            client.close_game()


def _play(puzzle, config, recorder, clients, prompts, player_context=None):
    limit = config['max_questions']
    if type(limit) is not int or not 1 <= limit <= 100:
        raise ValueError('max_questions must be an integer from 1 to 100')
    history = [{'type':t['type'],'text':t['text'],'feedback':t['label']}
               for t in recorder.turns if 'label' in t]
    counted = sum(t['type']=='question' or (t.get('grade') and not t['grade']['complete'])
                  for t in recorder.turns if 'label' in t)
    pending = recorder.turns[-1] if recorder.turns and 'label' not in recorder.turns[-1] else None
    if recorder.turns and recorder.turns[-1].get('grade',{}).get('complete'):
        return recorder.report('completed','solved')
    if counted >= limit and pending is None:
        return recorder.report('completed','budget_exhausted')
    recorder.report('running', None)
    # A stale fingerprint or missing host pack must not leave a batch looking
    # permanently running. No model calls have been made at this point.
    try:
        story_context = build_story_context(puzzle)
        saved_context = recorder.folder/'host_context.json'
        if getattr(recorder,'resumed',False) and saved_context.exists() and json.loads(saved_context.read_text()) != story_context:
            raise ValueError('Resumed Host context differs from frozen context')
        recorder.versions['host_context_sha256'] = story_context['context_sha256']
        recorder.versions['host_binding_version'] = story_context.get('binding_version')
        dump(recorder.folder / 'host_context.json', story_context)
    except (ValueError, KeyError, OSError) as exc:
        recorder.event('error', phase='host_context', error_type=type(exc).__name__, message=str(exc))
        return recorder.report('error', 'host_context_error', str(exc))
    try:
        while True:
            forced = counted >= limit - 1
            final_instruction=('FINAL followed by a newline and your complete explanation'
                               if 'prefix-v1' in prompts['player'] else 'type=final')
            control = (f'Total limit: {limit} submissions including questions and unsuccessful finals. '
                       f'Used question-equivalents: {counted}. '
                       + (f'This is the mandatory last turn. Return {final_instruction} NOW, even if uncertain.'
                          if forced else f'At slot {limit}, you MUST submit a final explanation.'))
            if pending is not None:
                turn = pending
                action = {'type':turn['type'],'text':turn['text']}
                forced = turn['forced']
                pending = None
            else:
                payload = {'opening': puzzle['opening'], 'visible_history': history, 'turn_control': control}
                if getattr(recorder,'retry_player_format',False):
                    kind=recorder.retry_player_format
                    if kind=='final':
                        payload['format_correction'] = ('Your preceding response contained multiple actions and did not count. '
                            'Submit exactly one final explanation: FINAL on the first line, then a newline and the explanation; no other action.')
                    else:
                        payload['format_correction'] = ('Your preceding response did not contain an actionable question. '
                            'That response did not count as a submission. Ask a question now using exactly '
                            'QUESTION on the first line followed by a newline and the question; no other text.')
                    del recorder.retry_player_format
                # An explicit controller overlay may resume an archived JSON
                # prompt. Do not silently switch that experiment's protocol.
                if 'prefix-v1' in prompts['player']:
                    payload['action_protocol']='prefix-v1'
                if player_context is not None:
                    payload['prior_experience'] = player_context
                player_input = json.dumps(payload, ensure_ascii=False)
                if hasattr(recorder,'pending_player_raw'):
                    from .providers import Reply
                    saved=recorder.pending_player_raw
                    reply=Reply(saved['raw'],{},response_id=saved['response_id'],finish_reason='stop')
                    del recorder.pending_player_raw
                else:
                    reply = clients['player'].complete(prompts['player'], player_input)
                    if hasattr(recorder,'pending_player_request'):
                        (recorder.folder/'player_transport_recovery.json').unlink(missing_ok=True)
                        del recorder.pending_player_request
                # User-approved handling for multiple QUESTION blocks: retain
                # every response, request one question and do not spend quota.
                if (recorder.folder/'auto_reprompt_questions.enabled').exists() and not forced:
                    from .action_text import PREFIX_ACTION_HEAD, GLUED_ACTION_HEAD
                    for _ in range(3):
                        heads=[m.group('kind').upper() for m in PREFIX_ACTION_HEAD.finditer(reply.text)]
                        heads += [m.group(1).upper() for m in GLUED_ACTION_HEAD.finditer(reply.text)]
                        if len(heads)<2 or any(h!='QUESTION' for h in heads) or reply.finish_reason not in ('stop','completed','end_turn'):
                            break
                        recorder.event('player_format_reprompt',source_response_id=reply.response_id,
                            raw_sha256=hashlib.sha256(reply.text.encode()).hexdigest(),counts_as_submission=False,
                            authorization='user_requested_reprompt')
                        payload['format_correction']=('Your preceding response contained multiple questions and did not count. '
                            'Ask exactly one question: QUESTION on the first line, followed by the question; no other text or action.')
                        reply=clients['player'].complete(prompts['player'],json.dumps(payload,ensure_ascii=False))
                try:
                    action = parse_action(reply.text, forced, lambda details: recorder.event(
                        'player_format_recovery', submission=len(recorder.turns)+1, **details))
                except ProtocolError:
                    if reply.finish_reason not in ('stop','completed','end_turn') or not (ROOT/'configs/player_format_repair.json').exists():raise
                    from .player_format import load_policy, repair
                    action,details=repair(reply.text,forced,load_policy(),recorder.audit,recorder.event,
                        reply.response_id,sum(c.get('role')=='format_repair' for c in recorder.calls))
                    recorder.event('player_format_recovery',submission=len(recorder.turns)+1,**details)
                try:has_note='text_note' in parse_player_json(reply.text)[0]
                except ProtocolError:has_note=False
                if has_note:
                    recorder.event('player_action_normalized',submission=len(recorder.turns)+1,
                                   removed_fields=['text_note'],recovery=False)
                turn = {'index': len(recorder.turns)+1, **action, 'forced': forced}
                recorder.turns.append(turn)
                recorder.event('submission', **turn, raw_player_output=reply.text)
                recorder.report('running', None)
            if action['type'] == 'question':
                counted += 1
                response = answer_question(clients['host'], prompts['host'],
                                           host_payload(story_context, history, action['text'],
                                               config.get('context_policy'),
                                               lambda selection: recorder.event('reference_selection',
                                                   role='host', submission=turn['index'], **selection)),
                                           prompts.get('host_review',''),
                                           lambda decision:recorder.event('host_review', submission=turn['index'], **decision))
                label = response.text.strip()
                if label not in LABELS:
                    raise ProtocolError('Host returned an invalid label; raw output saved in api_calls.jsonl')
                turn['label'] = label
                recorder.event('host_feedback', submission=turn['index'], label=label, raw=response.text)
                if hasattr(recorder, 'pending_host_request'):
                    (recorder.folder / 'host_transport_recovery.json').unlink(missing_ok=True)
                    del recorder.pending_host_request
            else:
                grader_payload = {'opening': puzzle['opening'], 'reference_answer': puzzle['answer'],
                                           'story_context': grader_story_context(story_context, action['text'],
                                               config.get('context_policy'),
                                               lambda selection: recorder.event('reference_selection',
                                                   role='grader', submission=turn['index'], **selection)),
                                           'rubric': puzzle['rubric'],
                                           'completion_requirements': puzzle.get('completion_requirements', []),
                                           'grading_notes': puzzle.get('grading_notes', ''),
                                           'submitted_explanation': action['text']}
                coverage_mode = puzzle.get('grading_protocol') == PROTOCOL
                if coverage_mode:
                    grader_payload.update(grading_protocol=PROTOCOL,
                                          required_facts=fact_specs(puzzle['rubric']),
                                          required_completion=requirement_specs(puzzle.get('completion_requirements', [])))
                grade, raw_grade = evaluate_final(clients['grader'],prompts['grader'],grader_payload,
                                                 lambda repair:recorder.event('grader_evidence_repair', submission=turn['index'], **repair))
                turn.update(grade=grade, label=grade['label'])
                recorder.event('evaluation', submission=turn['index'], **grade, raw=raw_grade)
                if not grade['complete']:
                    counted += 1
            history.append({'type': action['type'], 'text': action['text'], 'feedback': turn['label']})
            if hasattr(clients['player'], 'observe_feedback'):
                clients['player'].observe_feedback(turn['index'], action, turn['label'])
            if recorder.echo:
                print(f"[{puzzle['id']} #{turn['index']} {action['type']}] {action['text']}\nHost: {turn['label']}", flush=True)
            if action['type'] == 'final':
                if grade['rubric_conflict']:
                    return recorder.report('needs_review', 'rubric_conflict')
                if grade['complete']:
                    return recorder.report('completed', 'solved')
                if forced:
                    return recorder.report('completed', 'budget_exhausted')
            recorder.report('running', None)
    except KeyboardInterrupt:
        recorder.event('interrupted', reason='user_interrupt')
        return recorder.report('interrupted', 'user_interrupt')
    except (APIError, ProtocolError) as exc:
        recorder.event('error', error_type=type(exc).__name__, message=str(exc))
        return recorder.report('error', type(exc).__name__, str(exc))


def summarize_batch(folder, entries):
    from .costs import write_batch_costs
    costs = write_batch_costs(Path(folder), entries)
    completed = [r for r in entries if r['status'] == 'completed']
    solved = [r for r in completed if r['success']]
    def stats(values):
        return {'n': len(values), 'mean': statistics.mean(values) if values else None,
                'population_variance': statistics.pvariance(values) if values else None,
                'sample_variance': statistics.variance(values) if len(values) > 1 else None}
    summary = {'simulation': any(r.get('simulation', False) for r in entries), 'runs': entries, 'attempted_games': sum(r['status'] != 'dry_run' for r in entries),
               'error_games': sum(r['status'] == 'error' for r in entries),
               'interrupted_games': sum(r['status'] == 'interrupted' for r in entries),
               'needs_review_games': sum(r['status'] == 'needs_review' for r in entries),
               'completed_games': len(completed), 'solved_games': len(solved),
               'success_rate_completed': len(solved)/len(completed) if completed else None,
               'counted_questions_completed': stats([r['counted_questions'] for r in completed]),
               'counted_questions_success_only': stats([r['counted_questions'] for r in solved]),
               'final_partial_scores_completed': stats([r['final_partial_score'] for r in completed
                                                        if r['final_partial_score'] is not None]),
               'costs': costs,
               'note': 'Errors, interrupted and needs_review runs remain visible and are excluded from completed-game rates. Costs include all statuses. Scores are provisional model judgments.'}
    dump(Path(folder)/'summary.json', summary)
    columns = ['puzzle_id', 'story_family', 'quality_status', 'repeat', 'status', 'success', 'host_questions', 'rejected_finals',
               'counted_questions', 'submissions', 'final_partial_score', 'best_partial_score', 'stop_reason', 'run_dir']
    with (Path(folder)/'performance.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(entries)
    items = ''.join('<li><a href="' + html.escape(r['run_dir'], quote=True) + '/trajectory.html">'
                    + html.escape(f"{r['puzzle_id']} repeat {r['repeat']}: {r['status']} / score {r['final_partial_score']} / count {r['counted_questions']}")
                    + '</a></li>' for r in entries)
    (Path(folder)/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Turtle Soup runs</title>'
                                        '<h1>Turtle Soup experiment</h1>'
                                        + ('<p>SCRIPTED DEMO — not model performance</p>' if summary['simulation'] else '')
                                        + '<ul>' + items + '</ul>')
    return summary
