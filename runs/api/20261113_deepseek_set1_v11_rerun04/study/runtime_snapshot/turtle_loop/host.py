"""One host generation per question; transport retries remain provider-owned.

Host output-length truncation is retried once inside the provider. A second
truncation pauses for an explicit human label so the persistent session can continue.
"""
import json
import sys
import time
from pathlib import Path

from .host_context import LABELS
from .providers import APIError, HostTruncationExhausted, Reply

POLICY = 'single'
LABEL_CHOICES = ', '.join(sorted(LABELS))


def prompt_human_host_label(question, *, folder=None, input_fn=None, output_fn=None,
                            poll_seconds=2.0):
    """Ask for a Host label while always showing the player's question.

    Interactive TTY: stdin prompt. Non-interactive: write a request file under the
    game folder and wait for host_human_label.json {"label": "yes"|"no"|...}.
    """
    input_fn = input if input_fn is None else input_fn
    output_fn = (lambda text: print(text, file=sys.stderr, flush=True)) if output_fn is None else output_fn
    question = question if isinstance(question, str) else ''
    banner = [
        '',
        '=' * 72,
        'HOST OUTPUT TRUNCATED TWICE — human label required to continue',
        '-' * 72,
        'Player question:',
        question if question.strip() else '(missing current_question in host payload)',
        '-' * 72,
        f'Enter one label: {LABEL_CHOICES}',
        '=' * 72,
        '',
    ]
    output_fn('\n'.join(banner))

    def validate(raw):
        label = (raw or '').strip()
        if label in LABELS:
            return label
        output_fn(f'Invalid label {raw!r}; expected one of: {LABEL_CHOICES}')
        return None

    if sys.stdin.isatty() and input_fn is input:
        while True:
            try:
                raw = input_fn('Host label> ')
            except EOFError as exc:
                raise APIError('Host human label input closed before a valid label was provided') from exc
            label = validate(raw)
            if label is not None:
                return label

    folder = Path(folder) if folder else None
    if folder is None:
        raise APIError(
            'Host truncated twice and stdin is not a TTY; rerun in a foreground terminal '
            'or provide game folder for host_human_label.json')
    request_path = folder / 'host_human_label_request.json'
    response_path = folder / 'host_human_label.json'
    request_path.write_text(json.dumps({
        'schema': 'host_human_label_request_v1',
        'question': question,
        'allowed_labels': sorted(LABELS),
        'write_response_to': str(response_path),
        'response_schema': {'label': 'one of allowed_labels'},
    }, ensure_ascii=False, indent=2) + '\n')
    output_fn(f'Waiting for human label file:\n  {response_path}\n'
              f'(request details: {request_path})')
    while True:
        if response_path.exists():
            try:
                data = json.loads(response_path.read_text())
            except (OSError, ValueError, TypeError):
                output_fn(f'Could not parse {response_path}; fix JSON and save again')
                time.sleep(poll_seconds)
                continue
            label = validate(data.get('label') if isinstance(data, dict) else None)
            if label is not None:
                response_path.unlink(missing_ok=True)
                request_path.unlink(missing_ok=True)
                return label
            output_fn('Replace the response file with JSON like {"label": "yes"}')
        time.sleep(poll_seconds)


def answer_question(client, system, payload, review_prompt='', audit=None, notify=None,
                    human_label_fn=None):
    def call(prompt, data):
        reply = client.complete(prompt, json.dumps(data, ensure_ascii=False))
        if reply.text.strip() not in LABELS:
            raise APIError('Host returned an invalid label; raw response remains in API audit')
        return reply

    human_override = False
    try:
        primary = call(system, payload)
        calls = 1
    except HostTruncationExhausted as exc:
        question = payload.get('current_question', '') if isinstance(payload, dict) else ''
        folder = getattr(getattr(client, 'session', None), 'folder', None)
        chooser = human_label_fn or prompt_human_host_label
        label = chooser(question, folder=folder)
        if label not in LABELS:
            raise APIError('Human host label must be one of the four protocol labels')
        primary = Reply(label, {}, finish_reason='human')
        if getattr(client, 'session', None) is not None:
            if exc.lane is None or exc.payload is None:
                client.session.failed = True
                raise APIError('Host truncation exhausted without a session lane to accept a human label')
            client.session.accept(exc.lane, exc.payload, exc.wire_user, primary)
        if hasattr(client, 'audit'):
            client.audit({
                **(exc.metadata or {}),
                'role': getattr(client, 'role', 'host'),
                'provider': (getattr(client, 'profile', {}) or {}).get('provider'),
                'model_requested': (getattr(client, 'profile', {}) or {}).get('model'),
                'endpoint': exc.endpoint,
                'attempt': 'human',
                'status': 'human',
                'finish_reason': 'human',
                'text': label,
                'usage': {},
                'human_override': True,
                'truncated_finish_reason': getattr(exc.last_reply, 'finish_reason', None),
                'request': exc.request_body,
            })
        human_override = True
        calls = 2  # two truncated model attempts already audited; human is the decision
        if notify:
            notify(question=question, label=label, source='human_after_truncation')
    # Historical packs retain their provenance, including the old verification
    # setting. Runtime policy overrides it; never spend a second judgment call.
    if audit:
        audit({'policy': POLICY, 'candidate_labels': [primary.text.strip()],
               'disagreed': False, 'final_label': primary.text.strip(), 'calls': calls,
               'human_override': human_override})
    return primary
