"""Shared response contract for multi-agent dialogue and transport schemas."""

def dialogue_schema(allowed, forced=False):
    properties = {'type': {'type': 'string', 'enum': allowed},
                  'text': {'type': 'string'},
                  'next_speaker': {'type': 'string', 'enum': ['A', 'B']},
                  'text_note': {'type': 'string'}}
    return {'type': 'object', 'properties': properties,
            'required': ['type', 'text'] if forced else ['type', 'text', 'next_speaker'],
            'additionalProperties': False}


def dialogue_contract_text(allowed, forced=False):
    headers = [kind.upper()+' NEXT='+actor for kind in allowed for actor in ('A', 'B')]
    if forced:
        headers += [kind.upper() for kind in allowed]
    return ('Return exactly one plain text action. Choose one exact first line: '
            + ' | '.join(headers)
            + '. Then a newline and nonempty body. No JSON, fences, or extra action blocks. '
            + ('NEXT is optional on the mandatory final.' if forced else 'NEXT is required.'))



def valid_dialogue_action(action, allowed, forced=False):
    schema = dialogue_schema(allowed, forced)
    return (isinstance(action, dict)
            and set(schema['required']) <= set(action) <= set(schema['properties'])
            and action.get('type') in allowed
            and isinstance(action.get('text'), str) and bool(action['text'].strip())
            and ('next_speaker' not in action or action['next_speaker'] in ('A', 'B'))
            and ('text_note' not in action or isinstance(action['text_note'], str)))
