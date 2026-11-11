"""Small HTTP adapters; provider/model/endpoint can differ for each role."""
import json
import errno
import http.client
import os
import re
import socket
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from copy import deepcopy
from dataclasses import dataclass

DEFAULTS = {
    'openai': ('https://api.openai.com/v1', 'OPENAI_API_KEY', 'responses'),
    'openai_chat': ('https://api.openai.com/v1', 'OPENAI_API_KEY', 'chat'),
    'openai_compatible': ('https://api.openai.com/v1', 'OPENAI_API_KEY', 'chat'),
    'deepseek': ('https://api.deepseek.com', 'DEEPSEEK_API_KEY', 'chat'),
    'anthropic': ('https://api.anthropic.com/v1', 'ANTHROPIC_API_KEY', 'anthropic'),
}


class APIError(RuntimeError):
    pass


class RetryableAPIError(APIError):
    """Explicit pre-response capacity/rate limit; no usable generation exists."""
    pass


@dataclass
class Reply:
    text: str
    usage: dict
    response_id: str = ''
    model: str = ''
    finish_reason: str = ''
    seconds: float = 0


def resolve_env(value):
    if isinstance(value, str):
        def substitute(match):
            name = match.group(1)
            if not os.getenv(name):
                raise ValueError(f'Missing environment variable: {name}')
            return os.environ[name]
        return re.sub(r'\$\{([A-Za-z_][A-Za-z0-9_]*)\}', substitute, value)
    if isinstance(value, dict):
        return {k: resolve_env(v) for k, v in value.items()}
    if isinstance(value, list):
        return [resolve_env(v) for v in value]
    return value


def validate_profile(profile, require_key=True):
    if profile.get('provider') == 'codex_cli':
        from .codex_client import validate
        validate(profile)
        return '', '', 'codex_cli'
    allowed = {'provider', 'model', 'base_url', 'api_key_env', 'max_output_tokens',
               'temperature', 'extra_body', 'timeout', 'max_retries'}
    if set(profile) - allowed:
        raise ValueError(f'Unknown model settings: {sorted(set(profile)-allowed)}; keys belong in environment variables')
    if profile.get('provider') not in DEFAULTS:
        raise ValueError(f'Unknown API provider: {profile.get("provider")}')
    if not isinstance(profile.get('model'), str) or not profile['model'].strip():
        raise ValueError('Every role needs an exact API model ID')
    url, key_env, kind = DEFAULTS[profile['provider']]
    url = profile.get('base_url', url).rstrip('/')
    parsed = urllib.parse.urlsplit(url)
    if (parsed.scheme not in ('https', 'http') or not parsed.hostname or
            parsed.username or parsed.password or parsed.query or parsed.fragment):
        raise ValueError('base_url must be an API base URL without credentials/query/fragment')
    if parsed.scheme == 'http' and parsed.hostname not in ('localhost', '127.0.0.1', '::1'):
        raise ValueError('Use HTTPS for remote API endpoints')
    key_env = profile.get('api_key_env', key_env)
    if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', key_env):
        raise ValueError('api_key_env must be an environment variable NAME, not a key')
    if require_key and not os.getenv(key_env):
        raise ValueError(f'Missing {key_env}; export your API key before running')
    if type(profile.get('max_output_tokens', 4096)) is not int or profile.get('max_output_tokens', 4096) < 1:
        raise ValueError('max_output_tokens must be positive')
    if type(profile.get('max_retries', 2)) is not int or not 0 <= profile.get('max_retries', 2) <= 5:
        raise ValueError('max_retries must be between 0 and 5')
    if not isinstance(profile.get('timeout', 120), (int, float)) or not 0 < profile.get('timeout', 120) <= 600:
        raise ValueError('timeout must be between 0 and 600 seconds')
    extra = profile.get('extra_body', {})
    locked = {'model', 'messages', 'input', 'instructions', 'system', 'tools', 'tool_choice',
              'stream', 'store', 'previous_response_id', 'conversation', 'api_key',
              'authorization', 'headers', 'max_tokens', 'max_completion_tokens', 'max_output_tokens'}
    if not isinstance(extra, dict) or set(extra) & locked:
        raise ValueError('extra_body may not override prompts, tools, credentials, limits or storage')
    return url, key_env, kind


def build_request(profile, system, user):
    base, key_env, kind = validate_profile(profile, require_key=False)
    key = os.getenv(key_env, '')
    messages = [{'role': 'system', 'content': system}, {'role': 'user', 'content': user}]
    body = deepcopy(profile.get('extra_body', {}))
    body['model'] = profile['model']
    limit = profile.get('max_output_tokens', 4096)
    headers = {'Content-Type': 'application/json'}
    if kind == 'responses':
        suffix = '/responses'
        body.update(input=messages, max_output_tokens=limit, store=False, stream=False)
        headers['Authorization'] = 'Bearer ' + key
    elif kind == 'anthropic':
        suffix = '/messages'
        body.update(system=system, messages=messages[1:], max_tokens=limit, stream=False)
        headers.update({'x-api-key': key, 'anthropic-version': '2023-06-01'})
    else:
        suffix = '/chat/completions'
        token_key = 'max_completion_tokens' if profile['provider'] == 'openai_chat' else 'max_tokens'
        body.update(messages=messages, stream=False, **{token_key: limit})
        headers['Authorization'] = 'Bearer ' + key
    if 'temperature' in profile:
        body['temperature'] = profile['temperature']
    return base + suffix, headers, body, kind


def parse_reply(kind, data):
    if not isinstance(data, dict) or data.get('error'):
        raise APIError('API returned an error or non-object response')
    usage = data.get('usage') or {}
    if kind == 'responses':
        text = ''.join(part.get('text', '') for item in data.get('output', [])
                       if item.get('type') == 'message' for part in item.get('content', [])
                       if part.get('type') == 'output_text')
        finish = data.get('status', '')
    elif kind == 'anthropic':
        text = ''.join(part.get('text', '') for part in data.get('content', []) if part.get('type') == 'text')
        finish = data.get('stop_reason', '')
    else:
        choices = data.get('choices', [])
        if not choices:
            raise APIError('No completion choices')
        text = choices[0].get('message', {}).get('content') or ''
        finish = choices[0].get('finish_reason', '')
    if not isinstance(text, str):
        raise APIError('Expected a text completion')
    return Reply(text, usage, data.get('id', ''), data.get('model', ''), finish)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None  # Never forward credentials to an unexpected host.


class PreSendTLSFailure(OSError):
    """TLS handshake ended before HTTPSConnection could send the HTTP request."""
    def __init__(self, reason):
        super().__init__('TLS connection ended before request transmission')
        self.reason_type = type(reason).__name__
        self.reason_errno = reason.errno if type(reason.errno) is int else None


class PreSendNetworkFailure(OSError):
    """Connection could not be established before the HTTP request was sent."""
    def __init__(self, reason):
        super().__init__('Network unreachable before request transmission')
        self.reason_type = type(reason).__name__
        self.reason_errno = reason.errno if type(reason.errno) is int else None


class TrackedHTTPSConnection(http.client.HTTPSConnection):
    def connect(self):
        try:
            super().connect()
        except ssl.SSLCertVerificationError:
            raise  # Certificate/configuration failures are not transient retries.
        except ssl.SSLError as exc:
            # HTTPConnection.send calls connect before writing the request. A
            # proxy CONNECT may have been sent, but not the application request.
            raise PreSendTLSFailure(exc) from None
        except OSError as exc:
            if not isinstance(exc, ssl.SSLError) and exc.errno in (errno.EHOSTUNREACH, errno.ENETUNREACH):
                raise PreSendNetworkFailure(exc) from None
            raise


class TrackedHTTPSHandler(urllib.request.HTTPSHandler):
    def https_open(self, req):
        options={'context':self._context}
        # Python 3.12+ removed this handler/connection argument; keep the
        # original behavior on older interpreters without passing it to newer ones.
        if hasattr(self,'_check_hostname'):options['check_hostname']=self._check_hostname
        return self.do_open(TrackedHTTPSConnection, req, **options)


def transport_diagnostic(exc, phase):
    """Classify errors without logging exception messages, URLs or response bodies.

    DNS failures and instrumented TLS EOFs during connect precede request
    transmission. Uninstrumented TLS errors have ambiguous transmission state.
    """
    reason = exc.reason if isinstance(exc, urllib.error.URLError) else exc
    if isinstance(reason, PreSendNetworkFailure):
        category = 'network_unreachable_before_send'
    elif isinstance(reason, PreSendTLSFailure):
        category = 'tls_handshake_eof' if reason.reason_type == 'SSLEOFError' else 'tls_handshake_failure'
    elif isinstance(reason, socket.gaierror):
        category = 'dns_resolution'
    elif isinstance(reason, ssl.SSLError):
        category = 'tls'
    elif isinstance(reason, (socket.timeout, TimeoutError)):
        category = 'timeout'
    elif isinstance(reason, ConnectionRefusedError):
        category = 'connection_refused'
    elif isinstance(reason, ConnectionResetError):
        category = 'connection_reset'
    elif isinstance(reason, http.client.HTTPException):
        category = 'http_protocol'
    else:
        category = 'other_transport'
    tracked = isinstance(reason, (PreSendTLSFailure, PreSendNetworkFailure))
    code = reason.reason_errno if tracked else getattr(reason, 'errno', None)
    return {'transport_phase': phase, 'transport_category': category,
            'reason_type': reason.reason_type if tracked else type(reason).__name__,
            'reason_errno': code if type(code) is int else None,
            'safe_pre_send_retry': category in ('dns_resolution', 'tls_handshake_eof', 'tls_handshake_failure', 'network_unreachable_before_send') and phase == 'open'}


class Client:
    def __init__(self, profile, role, audit):
        validate_profile(profile)
        self.profile, self.role, self.audit = profile, role, audit
        self.opener = urllib.request.build_opener(NoRedirect, TrackedHTTPSHandler())
        self.session = None

    def begin_game(self, folder, event):
        from .sessions import GameSession
        if self.session is not None:
            raise ValueError('Client already belongs to a game')
        self.session = GameSession(self.role, folder, event)

    def close_game(self):
        if self.session is not None:
            self.session.close()

    def inherit_game(self, folder, event, calls, boundary):
        """Fork one frozen A Player prefix, then continue its exact role messages."""
        if self.role!='player' or self.profile['provider']=='codex_cli':
            raise ValueError('Raw session continuation requires a supported API Player; use transcript for Codex CLI')
        selected=[c for c in calls if c.get('role')=='player']
        if not selected:raise ValueError('Source has no Player messages')
        base,_,kind=validate_profile(self.profile)
        suffix='/responses' if kind=='responses' else '/messages' if kind=='anthropic' else '/chat/completions'
        if any(c.get('provider')!=self.profile['provider'] or c.get('model_requested')!=self.profile['model']
               or c.get('endpoint')!=base+suffix for c in selected):
            raise ValueError('Source Player provider/model/endpoint differs from target')
        if self.session is not None:raise ValueError('Client already belongs to a game')
        from .sessions import GameSession
        self.session=GameSession(self.role,folder,event,session_id=selected[0]['game_session_id'])
        try:
            self.session.restore_chat(selected)
            seed=self.session.freeze_prefix()
            lane=next(iter(self.session.lanes.values()));lane['inheritance']=seed
            self.inherited_system_sha256=seed['system_sha256']
            self.pending_puzzle_boundary=boundary
            event('player_session_inherited',source_turns=seed['turn'],
                  source_response_id=seed['response_id'],prefix_sha256=seed['messages_sha256'])
        except BaseException:
            self.session.close();raise

    def restore_game(self, folder, event, calls):
        if self.profile.get('provider')!='deepseek':
            raise ValueError('Persistent recovery is restricted to saved DeepSeek chat messages')
        selected=[c for c in calls if c.get('role')==self.role]
        endpoint,_,_=validate_profile(self.profile)
        for call in selected:
            if (call.get('model_requested')!=self.profile['model']
                    or call.get('endpoint')!=endpoint+'/chat/completions'):
                raise ValueError('Saved session model or endpoint differs from the configured role')
        if self.session is not None:
            raise ValueError('Client already belongs to a game')
        from .sessions import GameSession
        self.session=GameSession(self.role,folder,event,
                                 session_id=selected[0].get('game_session_id') if selected else None)
        try:self.session.restore_chat(calls)
        except BaseException:
            self.session.close()
            raise

    def complete(self, system, user):
        try:
            return self._complete(system, user)
        except BaseException:
            if self.session is not None:
                self.session.failed = True
            raise

    def _complete(self, system, user):
        if hasattr(self,'inherited_system_sha256'):
            import hashlib
            if hashlib.sha256(system.encode()).hexdigest()!=self.inherited_system_sha256:
                raise ValueError('Player system prompt changed across A and B; refusing a new lane')
        if hasattr(self,'pending_puzzle_boundary'):
            payload=json.loads(user)
            if payload.get('visible_history') or 'prior_experience' in payload:
                raise ValueError('New B must start with fresh public history and no repackaged A transcript')
            user=json.dumps({'puzzle_boundary':self.pending_puzzle_boundary,**payload},ensure_ascii=False)
            del self.pending_puzzle_boundary
        lane = None
        metadata = {}
        original_user = user
        if self.session is not None:
            lane, payload, system, user, metadata = self.session.prepare(system, user)
        def audit(record):
            self.audit({**record, **metadata})
        if self.profile.get('provider') == 'codex_cli':
            from .codex_client import complete
            retries = self.profile.get('max_retries', 2)
            for attempt in range(1, retries + 2):
                try:
                    reply = complete(self.profile, self.role, audit, system, user, attempt=attempt,
                                     session=lane, schema_user=original_user)
                    if lane is not None:
                        self.session.accept(lane, payload, user, reply)
                    return reply
                except RetryableAPIError:
                    if attempt > retries:
                        raise
                    time.sleep(min(2 ** (attempt - 1), 8))
        url, headers, body, kind = build_request(self.profile, system, user)
        json_action=False
        if self.profile['provider']=='deepseek' and self.role in ('player','partner'):
            try:logical=json.loads(original_user)
            except (ValueError,TypeError):logical={}
            if isinstance(logical,dict) and logical.get('action_protocol') == 'prefix-v1':
                # The current action prompt requires QUESTION/FINAL plain text.
                # A legacy profile's JSON constraint can turn that output into
                # whitespace at the provider. The turn's explicit protocol wins.
                body.pop('response_format', None)
            elif isinstance(logical,dict) and ('dialogue_control' in logical or
                    ('opening' in logical and 'turn_control' in logical)):
                # Typed actions need JSON; teammate prose reviews and source
                # summaries have different envelopes and stay plain text.
                body.setdefault('response_format',{'type':'json_object'})
                json_action=isinstance(body['response_format'],dict) and body['response_format'].get('type')=='json_object'
        if lane is not None:
            if kind == 'responses':
                body['store'] = True
                # Instructions are reapplied, not appended as another system
                # message in the conversation chain on every turn.
                body['instructions'] = system
                body['input'] = [{'role': 'user', 'content': user}]
                if lane['response_id']:
                    body['previous_response_id'] = lane['response_id']
            else:
                messages = lane['messages'] + [{'role': 'user', 'content': user}]
                body['messages'] = messages if kind == 'anthropic' else [{'role': 'system', 'content': system}] + messages
        expected = getattr(self, 'expected_recovery_request', None)
        if expected is not None:
            if body != expected:
                raise ValueError('Recovered request differs from the saved unanswered request')
            del self.expected_recovery_request
        for attempt in range(self.profile.get('max_retries', 2) + 1):
            start = time.monotonic()
            data = None
            response_recorded = False
            phase = 'open'
            record = {**metadata, 'role': self.role, 'provider': self.profile['provider'],
                      'json_action_mode':json_action,
                      'model_requested': self.profile['model'], 'endpoint': url,
                      'attempt': attempt + 1, 'request': body}
            try:
                request = urllib.request.Request(url, json.dumps(body).encode(), headers, method='POST')
                with self.opener.open(request, timeout=self.profile.get('timeout', 120)) as response:
                    phase = 'read'
                    data = json.loads(response.read())
                reply = parse_reply(kind, data)
                reply.seconds = time.monotonic() - start
                self.audit({**record, 'status': 'ok', 'seconds': reply.seconds,
                            'response_id': reply.response_id, 'model_returned': reply.model,
                            'text': reply.text, 'usage': reply.usage, 'service_tier': data.get('service_tier'), 'finish_reason': reply.finish_reason})
                response_recorded = True
                # Truncated/refused outputs are recorded, not silently repaired/re-sampled.
                if not reply.text.strip() or reply.finish_reason in ('length', 'max_tokens', 'incomplete', 'failed', 'refusal', 'content_filter', 'tool_use', 'tool_calls'):
                    raise APIError(f'{self.role}: empty, refused or truncated response ({reply.finish_reason})')
                if lane is not None:
                    if kind == 'responses' and not reply.response_id:
                        raise APIError('Persistent Responses session requires a response ID; no stateless fallback')
                    self.session.accept(lane, payload, user, reply)
                return reply
            except urllib.error.HTTPError as exc:
                code = exc.code
                self.audit({**record, 'status': 'http_error', 'http_status': code,
                            'seconds': time.monotonic()-start})
                retry = code == 429
                # Do not dump vendor error bodies: they can echo credentials/prompts.
                error = APIError(f'{self.role}: HTTP {code}; check endpoint, model access and key')
            except (urllib.error.URLError, TimeoutError, ConnectionError, http.client.HTTPException) as exc:
                diagnostic = transport_diagnostic(exc, phase)
                self.audit({**record, 'status': 'transport_error', 'error_type': type(exc).__name__,
                            **diagnostic, 'seconds': time.monotonic()-start})
                retry = diagnostic['safe_pre_send_retry']
                error = APIError(f"{self.role}: transport failure ({diagnostic['transport_category']}, {phase})")
            except (json.JSONDecodeError, APIError) as exc:
                if not response_recorded:
                    self.audit({**record, 'status': 'invalid_response', 'seconds': time.monotonic()-start,
                                'usage': data.get('usage', {}) if isinstance(data, dict) else {},
                                'model_returned': data.get('model') if isinstance(data, dict) else None})
                raise APIError(f'{self.role}: invalid/empty/truncated provider response') from None
            except KeyboardInterrupt:
                if not response_recorded:
                    self.audit({**record, 'status':'interrupted', 'seconds':time.monotonic()-start})
                raise
            if not retry or attempt >= self.profile.get('max_retries', 2):
                raise error from None
            time.sleep(min(2 ** attempt, 8))
        raise APIError('Unreachable retry state')
