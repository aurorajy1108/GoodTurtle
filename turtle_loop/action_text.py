"""Plain text model action protocol; runtime records remain structured JSON."""
import re

PREFIX_ACTION_HEAD = re.compile(
    r'(?mi)^[ \t]*(?P<kind>QUESTION|FINAL|DISCUSS|PASS)'
    r'(?P<handoff>[ \t]+NEXT=[AB])?[ \t]*'
    r'(?:(?P<colon>[:：])[ \t]*(?P<inline>[^\r\n]*)'
    r'|(?P<spaced>[ \t]+)(?P<space_inline>\S[^\r\n]*)|\r?$)')


def parse_prefix_action(raw):
    header, separator, body = raw.strip().partition('\n')
    match = re.fullmatch(r'(QUESTION|FINAL|DISCUSS|PASS)(?: NEXT=([AB]))?', header.rstrip('\r'))
    if not match or not separator or not body.strip():
        raise ValueError('Expected one action header and nonempty body')
    # Multiple action blocks are ambiguous: never silently choose one.
    if PREFIX_ACTION_HEAD.search(body):
        raise ValueError('Multiple action blocks are not allowed')
    action = {'type': match[1].lower(), 'text': body}
    if match[2]:
        action['next_speaker'] = match[2]
    return action


def recover_prefix_action(raw):
    """Discard only a preamble before one unambiguous, line-delimited action."""
    import hashlib
    if not isinstance(raw, str):
        return None
    # The old prompt's placeholder sometimes wrapped a typed action. Recover
    # only an explicit inner verb and explicit outer handoff, never infer a verb
    # from free prose. Both values and the entire body must remain unchanged.
    outer=re.fullmatch(r'\s*ACTION NEXT=([AB])\r?\n((?:QUESTION|FINAL|DISCUSS|PASS)(?: NEXT=[AB])?\r?\n[\s\S]+)',raw)
    if outer:
        action=parse_prefix_action(outer[2])
        if action.get('next_speaker',outer[1])!=outer[1]:
            raise ValueError('Conflicting outer and inner next speaker')
        action['next_speaker']=outer[1]
        return action,{'method':'explicit_placeholder_wrapper','raw_sha256':hashlib.sha256(raw.encode()).hexdigest(),
                       'discarded_prefix_chars':raw.index(outer[2]),'next_speaker_preserved':True}
    if re.fullmatch(r'\s*```(?:json|text)?[ \t]*\r?\n[\s\S]*?\r?\n```\s*',raw):
        return None  # Existing full-envelope recovery handles this separately.
    headers=list(PREFIX_ACTION_HEAD.finditer(raw))
    if not headers:
        return None
    if len(headers)!=1:
        raise ValueError('Multiple action blocks require review')
    start=headers[0].start()
    preamble=raw[:start]
    # Never hide a second structured action or a markdown envelope.
    if '```' in raw or re.search(r'["\']type["\']\s*:',preamble):
        raise ValueError('Mixed or fenced action envelopes require review')
    head=headers[0]
    body_start=(head.start('inline') if head.group('colon') else
                head.start('space_inline') if head.group('spaced') else head.end()+1)
    header=head.group('kind').upper()+(head.group('handoff') or '').upper()
    action=parse_prefix_action(header+'\n'+raw[body_start:])
    return action, {'method':'unique_prefix_action','selected_span':[start,len(raw.rstrip())],
                    'text_span':[body_start,len(raw.rstrip())],
                    'discarded_prefix_chars':start,
                    'raw_sha256':hashlib.sha256(raw.encode()).hexdigest()}


def recover_last_prefix_action(raw):
    """Explicit opt-in last_complete policy; never choose by puzzle truth.

    The strict parser still rejects multiple actions. This function is used only
    by the existing configured format-repair policy and preserves the entire
    final typed action, including qualifiers and any explicit MAS handoff.
    """
    import hashlib
    if not isinstance(raw,str) or '```' in raw or re.search(r'["\']type["\']\s*:',raw):
        return None
    heads=list(PREFIX_ACTION_HEAD.finditer(raw))
    if len(heads)<2:return None
    head=heads[-1]
    selected=raw[head.start():]
    recovered=recover_prefix_action(selected)
    if not recovered:return None
    action,meta=recovered
    start=head.start()+meta['text_span'][0]
    return action,{'method':'last_complete_prefix_action','candidate_count':len(heads),
        'selected_index':len(heads)-1,'selected_span':[head.start(),len(raw.rstrip())],
        'text_span':[start,len(raw.rstrip())],'raw_sha256':hashlib.sha256(raw.encode()).hexdigest(),
        'selection_policy':'last_complete','model_calls':0}
