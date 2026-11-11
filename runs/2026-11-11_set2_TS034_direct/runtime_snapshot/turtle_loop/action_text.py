"""Plain text model action protocol; runtime records remain structured JSON."""
import re

PREFIX_ACTION_HEAD = re.compile(
    r'(?mi)^[ \t]*(?P<kind>QUESTION|FINAL|DISCUSS|PASS)'
    r'(?P<handoff>[ \t]+NEXT=[AB])?[ \t]*'
    r'(?:(?P<colon>[:：])[ \t]*(?P<inline>[^\r\n]*)|\r?$)')


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
    body_start=head.start('inline') if head.group('colon') else head.end()+1
    header=head.group('kind').upper()+(head.group('handoff') or '').upper()
    action=parse_prefix_action(header+'\n'+raw[body_start:])
    return action, {'method':'unique_prefix_action','selected_span':[start,len(raw.rstrip())],
                    'text_span':[body_start,len(raw.rstrip())],
                    'discarded_prefix_chars':start,
                    'raw_sha256':hashlib.sha256(raw.encode()).hexdigest()}
