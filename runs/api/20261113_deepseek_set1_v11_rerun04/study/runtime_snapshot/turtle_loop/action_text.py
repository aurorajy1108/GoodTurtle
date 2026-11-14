"""Plain text model action protocol; runtime records remain structured JSON."""
import re


def parse_prefix_action(raw):
    header, separator, body = raw.strip().partition('\n')
    match = re.fullmatch(r'(QUESTION|FINAL|DISCUSS|PASS)(?: NEXT=([AB]))?', header.rstrip('\r'))
    if not match or not separator or not body.strip():
        raise ValueError('Expected one action header and nonempty body')
    # Multiple action blocks are ambiguous: never silently choose one.
    if re.search(r'(?m)^(QUESTION|FINAL|DISCUSS|PASS)(?: NEXT=[AB])?\r?$', body):
        raise ValueError('Multiple action blocks are not allowed')
    action = {'type': match[1].lower(), 'text': body}
    if match[2]:
        action['next_speaker'] = match[2]
    return action
