"""Official Codex CLI backend using its existing login; never reads auth tokens."""
import json
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

DISABLED = ('shell_tool','apps','plugins','hooks','multi_agent','browser_use','computer_use',
            'view_image','memories','shell_snapshot','image_generation','code_mode_host',
            'workspace_dependencies','goals','sleep_tool','tool_suggest','skill_search')


def validate(profile):
    allowed={'provider','model','reasoning_effort','timeout','max_retries','usage_scope'}
    if set(profile)-allowed:
        raise ValueError('codex_cli supports only provider, model, reasoning_effort, timeout, max_retries, usage_scope; no API token cap or sampling overrides')
    if profile.get('usage_scope','thread_total') not in ('thread_total','turn'):
        raise ValueError('Codex usage_scope must be thread_total or turn')
    if not isinstance(profile.get('model'),str) or not profile['model'].strip():
        raise ValueError('codex_cli needs an explicit model')
    if profile.get('reasoning_effort','high') not in ('low','medium','high','xhigh','max','ultra'):
        raise ValueError('Invalid Codex reasoning effort')
    if type(profile.get('timeout',240)) not in (int,float) or not 0<profile.get('timeout',240)<=600:
        raise ValueError('Codex timeout must be in (0,600] seconds')
    if type(profile.get('max_retries', 2)) is not int or not 0 <= profile.get('max_retries', 2) <= 5:
        raise ValueError('Codex max_retries must be an integer from 0 to 5')
    if not shutil.which('codex'):
        raise ValueError('Install and log in to the official Codex CLI first')


def command(profile, folder):
    args=['codex','exec','--ignore-user-config','--ephemeral','--skip-git-repo-check',
          '--sandbox','read-only','--json','-m',profile['model'],'-C',str(folder),
          '-c','model_reasoning_effort='+json.dumps(profile.get('reasoning_effort','high')),
          '-c','model_instructions_file='+json.dumps(str(folder/'system.txt')),
          '-c','project_doc_max_bytes=0','-c','web_search="disabled"',
          '-c','model_provider="account"',
          '-c','model_providers.account.name="OpenAI Codex account"',
          '-c','model_providers.account.requires_openai_auth=true',
          '-c','model_providers.account.wire_api="responses"',
          '-c','model_providers.account.supports_websockets=false',
          '-c','suppress_unstable_features_warning=true',
          '--enable','skip_host_skill_discovery']
    for feature in DISABLED:
        args+=['--disable',feature]
    return args+['-']


def output_contract(user):
    """Constrain response format, never supply answer content to a solver."""
    def obj(properties):
        return {'type':'object','properties':properties,'required':list(properties),'additionalProperties':False}
    string={'type':'string'}
    try:
        payload=json.loads(user)
    except (ValueError,TypeError):
        payload={}
    if not isinstance(payload,dict):
        payload={}
    if payload.get('action_protocol') == 'prefix-v1':
        return None, None, ''
    if 'dialogue_control' in payload:
        from .dialogue_contract import dialogue_schema
        control = payload['dialogue_control']
        return dialogue_schema(control['allowed_actions'], control.get('mandatory_final', False)),None,''
    if payload.get('evidence_repair') is True:
        ids=list(payload.get('source_sentences',{}))
        return obj({'repairs':{'type':'array','items':obj({'field':string,
                    'sentence_ids':{'type':'array','items':{'type':'string','enum':ids}}})}}),None,''
    if payload.get('coverage_completion') is True:
        from .coverage import coverage_schema
        fields={k:v for k,v in coverage_schema().items() if k in payload['missing_fields']}
        fields['consistent_with_existing_judgment']={'type':'boolean'}
        return obj(fields),None,''
    if 'current_question' in payload and 'active_puzzle' in payload:
        schema=obj({'label':{'type':'string','enum':['yes','no','yes and no','irrelevant']}})
        return schema,'label','\nTRANSPORT OVERRIDE: Return a JSON object with one field label containing exactly your four-label answer. The controller exposes only that label. No explanations.'
    if 'submitted_explanation' in payload and 'rubric' in payload:
        checkpoint=obj({'id':string,'credit':{'type':'number','enum':[0,0.5,1]},'evidence':string,'reason':string})
        fields={'checkpoints':{'type':'array','items':checkpoint}}
        fields.update({k:{'type':'boolean'} for k in ('material_contradiction','irrelevant','rubric_conflict','full_solution')})
        fields['completion_note']=string
        if payload.get('grading_protocol') in ('coverage-v2','coverage-v3-unified'):
            from .coverage import coverage_schema
            fields.update(coverage_schema())
        return obj(fields),None,''
    if 'turn_control' in payload and 'opening' in payload:
        return obj({'type':{'type':'string','enum':['question','final']},'text':string}),None,''
    return obj({'text':string}),'text','\nTRANSPORT OVERRIDE: Put your entire response in one JSON object with the string field text; no other fields.'


def turn_usage(raw, previous, scope):
    """CLI 0.154.0 emits thread totals on resume; never sum those as turns.

    A different CLI can explicitly declare per-turn usage. Counter regressions
    or missing baseline fields are unknown, not negative costs or guessed zeros.
    """
    if scope == 'turn' or previous is None:
        return dict(raw)
    if any(type(value) is not int or type(previous.get(key)) is not int or value < previous[key]
           for key, value in raw.items()):
        return {}
    return {key: value-previous[key] for key,value in raw.items()}


def complete(profile,role,audit,system,user,attempt=1,session=None,schema_user=None):
    from .providers import APIError,Reply,RetryableAPIError
    start=time.monotonic()
    schema,unwrap,override=output_contract(schema_user if schema_user is not None else user)
    wire_system=system+override
    record={'role':role,'provider':'codex_cli','model_requested':profile['model'],
            'reasoning_effort':profile.get('reasoning_effort','high'),'attempt':attempt,
            'request':{'system':wire_system,'user':user,'output_schema':schema},
            'transport':'official_codex_exec_structured_v2',
           'auth':'existing_codex_login','session_policy':
               'persistent game/role/lane; tools disabled' if session is not None else 'fresh ephemeral session; tools disabled'}
    from contextlib import nullcontext
    workspace = nullcontext(session['workspace'].name) if session is not None else tempfile.TemporaryDirectory(prefix='turtle-role-')
    with workspace as directory:
        folder=Path(directory)
        (folder/'system.txt').write_text(wire_system)
        (folder/'schema.json').write_text(json.dumps(schema))
        args=command(profile,folder)[:-1]
        if schema is not None:
            args+=['--output-schema',str(folder/'schema.json')]
        args+=['--output-last-message',str(folder/'last.txt'),'-']
        if session is not None:
            args.remove('--ephemeral')
            if session['response_id']:
                # Global exec flags (sandbox, cwd, disabled features) remain before
                # the resume subcommand. Never use --last or discover other threads.
                args = args[:-1] + ['resume', session['response_id'], '-']
        (folder/'last.txt').unlink(missing_ok=True)
        try:
            process=subprocess.run(args,input=user,text=True,capture_output=True,
                                   timeout=profile.get('timeout',240),cwd=folder)
        except (subprocess.TimeoutExpired,OSError) as exc:
            audit({**record,'status':'transport_error','error_type':type(exc).__name__,'seconds':time.monotonic()-start})
            raise APIError(f'{role}: Codex CLI {type(exc).__name__}; no resampling') from None
        except KeyboardInterrupt:
            audit({**record,'status':'interrupted','seconds':time.monotonic()-start})
            raise
        last=(folder/'last.txt').read_text() if (folder/'last.txt').exists() else ''
    messages=[];usage={};thread='';events=[];completed=False;tool_use=False;generation_started=False
    for line in process.stdout.splitlines():
        try:
            event=json.loads(line)
        except ValueError:
            continue
        kind=event.get('type')
        if kind=='thread.started':
            thread=event.get('thread_id','')
        elif kind=='turn.completed':
            usage=event.get('usage',{});completed=True
        elif kind in ('error','turn.failed'):
            events.append({'type':kind,'message':event.get('message',event.get('error',{}))})
        elif kind in ('item.started','item.completed'):
            item=event.get('item',{})
            if item.get('type') in ('agent_message', 'reasoning'):
                generation_started=True
            if item.get('type') not in ('agent_message','reasoning','error'):
                tool_use=True
                events.append({'type':'unexpected_tool','item_type':item.get('type')})
            if kind=='item.completed' and item.get('type')=='error':
                events.append({'type':'cli_warning','message':item.get('message','')})
            if kind=='item.completed' and item.get('type')=='agent_message':
                messages.append(item.get('text',''))
    stream_text=messages[-1] if messages else ''
    mismatch=bool(last.strip() and stream_text.strip() and last.strip()!=stream_text.strip())
    raw=last if last.strip() else stream_text
    text=raw
    valid=True
    try:
        parsed=json.loads(raw) if schema is not None else None
        if schema is None:
            from .action_text import recover_prefix_action
            if recover_prefix_action(raw) is None:
                valid=False
        elif unwrap:
            if not isinstance(parsed,dict) or set(parsed)!={unwrap} or not isinstance(parsed[unwrap],str):
                valid=False
            else:
                text=parsed[unwrap]
                if unwrap=='label' and text not in ('yes','no','yes and no','irrelevant'):
                    valid=False
        elif not isinstance(parsed,dict):
            valid=False
    except (ValueError,TypeError):
        valid=False
    ok=process.returncode==0 and completed and bool(text.strip()) and not tool_use and valid and not mismatch
    if session is not None:
        ok = ok and bool(thread) and (not session['response_id'] or thread == session['response_id'])
    raw_usage = dict(usage)
    usage_scope = profile.get('usage_scope','thread_total')
    baseline = session.get('codex_usage_total') if session is not None else None
    usage = turn_usage(raw_usage, baseline, usage_scope)
    audit({**record,'status':'ok' if ok else 'invalid_response','seconds':time.monotonic()-start,
           'response_id':thread,'model_returned':None,'model_verification':'CLI model argument pinned; event stream does not report actual model',
           'text':text,'raw_text':raw,'usage':usage,'raw_usage':raw_usage,
           'usage_scope':usage_scope,'usage_baseline':baseline,
           'usage_normalization':'thread_delta' if baseline is not None and usage_scope=='thread_total' else 'unchanged',
           'returncode':process.returncode,'diagnostics':events,
           'output_channel':'last_message_file' if last.strip() else 'jsonl_event',
           'output_channel_mismatch':mismatch,'finish_reason':'completed' if ok else 'failed'})
    if not ok:
        # Never retry bad formats, partial generations, tool use, or a low-quality answer.
        diagnostic = json.dumps([e for e in events if e['type'] in ('error','turn.failed')]).lower()
        if (process.returncode != 0 and not raw.strip() and not completed and not tool_use and not generation_started
                and any(marker in diagnostic for marker in ('at capacity', 'rate limit', 'rate_limit'))):
            raise RetryableAPIError(f'{role}: capacity/rate limit before response; see api_calls.jsonl')
        raise APIError(f'{role}: Codex CLI failed (exit={process.returncode}, tools={tool_use}, format={valid}); see api_calls.jsonl')
    if session is not None:
        session['codex_usage_total'] = raw_usage
    return Reply(text,usage,thread,profile['model'],'completed',time.monotonic()-start)
