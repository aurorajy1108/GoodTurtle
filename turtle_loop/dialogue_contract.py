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
    import json
    return ('Return exactly one JSON object and no other text. Follow this schema: '
            + json.dumps(dialogue_schema(allowed, forced), ensure_ascii=False)
            + '. The text must be nonempty.')


def valid_dialogue_action(action, allowed, forced=False):
    schema = dialogue_schema(allowed, forced)
    return (isinstance(action, dict)
            and set(schema['required']) <= set(action) <= set(schema['properties'])
            and action.get('type') in allowed
            and isinstance(action.get('text'), str) and bool(action['text'].strip())
            and ('next_speaker' not in action or action['next_speaker'] in ('A', 'B'))
            and ('text_note' not in action or isinstance(action['text_note'], str)))
