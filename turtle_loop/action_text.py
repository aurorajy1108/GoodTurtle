"""Plain text model action protocol; runtime records remain structured JSON."""
import re

PREFIX_ACTION_HEAD = re.compile(
    r'(?mi)^[ \t]*(?P<kind>QUESTION|FINAL|DISCUSS|PASS)'
    r'(?P<handoff>[ \t]+NEXT=[AB])?[ \t]*'
    r'(?:(?P<colon>[:：])[ \t]*(?P<inline>[^\r\n]*)|\r?$)')
GLUED_ACTION_HEAD = re.compile(r'(?m)(?<=[.!?。！？"”’])[ \t]*(QUESTION|FINAL)\r?$')
TEST_LABEL = re.compile(r'(?i)(?<!\w)test:[ \t]+')
TRY_LABEL = re.compile(r'(?i)(?<!\w)try:[ \t]+')
TERMINAL_TEST_QUESTION = re.compile(r'(?i)(?<!\w)(?P<label>test|try):[ \t]+(?P<text>[^\r\n?]+\?)[ \t\r\n]*\Z')


def parse_prefix_action(raw):
    header, separator, body = raw.strip().partition('\n')
    match = re.fullmatch(r'(QUESTION|FINAL|DISCUSS|PASS)(?: NEXT=([AB]))?', header.rstrip('\r'))
    if not match or not separator or not body.strip():
        raise ValueError('Expected one action header and nonempty body')
    # Multiple action blocks are ambiguous: never silently choose one.
    test = TERMINAL_TEST_QUESTION.search(body)
    if (PREFIX_ACTION_HEAD.search(body) or GLUED_ACTION_HEAD.search(body)
            or (test and body[:test.start()].strip())):
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
    headers=[(m.start(),m,'line') for m in PREFIX_ACTION_HEAD.finditer(raw)]
    headers += [(m.start(),m,'glued') for m in GLUED_ACTION_HEAD.finditer(raw)]
    headers.sort(key=lambda x:x[0])
    test_labels=list(TEST_LABEL.finditer(raw))
    try_labels=list(TRY_LABEL.finditer(raw))
    terminal_test=TERMINAL_TEST_QUESTION.search(raw)
    if headers and re.search(r'(?mi)^[ \t]*(?:test|try):[ \t]+[^\r\n?]+\?[ \t]*\r?$',raw):
        raise ValueError('Multiple action blocks require review')
    if terminal_test:
        labels = test_labels if terminal_test.group('label').lower()=='test' else try_labels
        other = r'try' if terminal_test.group('label').lower()=='test' else r'test'
        if headers or len(labels)!=1 or re.search(r'(?mi)^[ \t]*'+other+r':[ \t]+',raw):
            raise ValueError('Ambiguous or incomplete test question requires review')
        if '```' in raw or re.search(r'["\']type["\']\s*:',raw[:terminal_test.start()]):
            raise ValueError('Mixed or fenced action envelopes require review')
        body=terminal_test.group('text')
        return {'type':'question','text':body}, {
            'method':'unique_terminal_'+terminal_test.group('label').lower()+'_question',
            'selected_span':[terminal_test.start(),len(raw.rstrip())],
            'text_span':list(terminal_test.span('text')),
            'discarded_prefix_chars':terminal_test.start(),
            'raw_sha256':hashlib.sha256(raw.encode()).hexdigest()}
    if (test_labels or try_labels) and not headers:
        raise ValueError('Incomplete test question requires review')
    if not headers:
        return None
    if len(headers)!=1:
        raise ValueError('Multiple action blocks require review')
    start,head,kind=headers[0]
    preamble=raw[:start]
    # Never hide a second structured action or a markdown envelope.
    if '```' in raw or re.search(r'["\']type["\']\s*:',preamble):
        raise ValueError('Mixed or fenced action envelopes require review')
    body_start=head.start('inline') if kind=='line' and head.group('colon') else head.end()+1
    header=(head.group('kind').upper()+(head.group('handoff') or '').upper()
            if kind=='line' else head.group(1))
    action=parse_prefix_action(header+'\n'+raw[body_start:])
    return action, {'method':'unique_prefix_action','selected_span':[start,len(raw.rstrip())],
                    'text_span':[body_start,len(raw.rstrip())],
                    'discarded_prefix_chars':start,
                    'raw_sha256':hashlib.sha256(raw.encode()).hexdigest()}
