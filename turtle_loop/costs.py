"""Auditable token accounting. Estimates never claim to be actual billed charges."""
import csv
import hashlib
import json
import math
from collections import defaultdict
from copy import deepcopy
from decimal import Decimal
from pathlib import Path

TOKEN_FIELDS = ('input_tokens', 'cached_input_tokens', 'cache_write_tokens',
                'output_tokens', 'reasoning_tokens', 'total_tokens')


def pricing_config(value=None):
    book = deepcopy(value) if value is not None else json.loads(Path(__file__).with_name('token_prices.json').read_text())
    if book.get('schema_version') != 1 or book.get('currency') != 'USD' or not isinstance(book.get('models'), list):
        raise ValueError('pricing requires schema_version=1, currency=USD and models list')
    seen = set()
    for rate in book['models']:
        if not isinstance(rate.get('providers'), list) or not rate['providers'] or not rate.get('model') or not rate.get('source'):
            raise ValueError('Each price needs providers, exact model and source')
        for provider in rate['providers']:
            key = (provider, rate['model'])
            if key in seen:
                raise ValueError('Duplicate provider/model pricing')
            seen.add(key)
        for name in ('input_per_million', 'output_per_million'):
            if name not in rate:
                raise ValueError('Missing '+name)
        for name, number in rate.items():
            if name.endswith(('_per_million', '_multiplier')) or name == 'long_context_threshold':
                if type(number) not in (int, float) or not math.isfinite(number) or number < 0:
                    raise ValueError('Invalid price '+name)
        if 'long_context_threshold' in rate and not all(k in rate for k in ('long_input_multiplier', 'long_output_multiplier')):
            raise ValueError('Long-context threshold requires both multipliers')
    return book


def _count(value):
    return value if type(value) is int and value >= 0 else None


def normalize_usage(provider, usage):
    u = usage if isinstance(usage, dict) else {}
    details = u.get('input_tokens_details') or u.get('prompt_tokens_details') or {}
    output_details = u.get('output_tokens_details') or u.get('completion_tokens_details') or {}
    details = details if isinstance(details, dict) else {}
    output_details = output_details if isinstance(output_details, dict) else {}
    inp = _count(u.get('input_tokens', u.get('prompt_tokens')))
    out = _count(u.get('output_tokens', u.get('completion_tokens')))
    cached = _count(u.get('cached_input_tokens', u.get('prompt_cache_hit_tokens', details.get('cached_tokens'))))
    writes = _count(u.get('cache_creation_input_tokens', u.get('cache_write_input_tokens', details.get('cache_write_tokens', 0))))
    if provider == 'anthropic':
        # Anthropic input_tokens excludes both cache reads and cache creation.
        cached = _count(u.get('cache_read_input_tokens', 0)) if inp is not None else None
        inp = inp + cached + writes if None not in (inp, cached, writes) else None
    reasoning = _count(u.get('reasoning_tokens', u.get('reasoning_output_tokens', output_details.get('reasoning_tokens'))))
    valid = (inp is not None and out is not None and cached is not None and writes is not None
             and cached + writes <= inp and (reasoning is None or reasoning <= out))
    return dict(input_tokens=inp, cached_input_tokens=cached, cache_write_tokens=writes,
                output_tokens=out, reasoning_tokens=reasoning,
                total_tokens=inp+out if inp is not None and out is not None else None,
                valid_for_pricing=valid)


def account_call(call, book):
    provider = call.get('provider', '')
    model = call.get('model_returned') or call.get('model_requested', '')
    tokens = normalize_usage(provider, call.get('usage'))
    rate = next((r for r in book['models'] if provider in r['providers'] and r['model'] == model), None)
    reason = None
    estimate = None
    if call.get('status') == 'mock':
        reason = 'synthetic_call'
    elif not tokens['valid_for_pricing']:
        reason = 'missing_or_inconsistent_usage'
    elif rate is None:
        reason = 'no_exact_provider_model_price'
    elif provider != 'codex_cli' and (not rate.get('endpoint_prefix') or not call.get('endpoint', '').startswith(rate['endpoint_prefix'])):
        reason = 'endpoint_not_covered_by_price'
    elif provider != 'codex_cli' and (call.get('service_tier') or call.get('request', {}).get('service_tier', 'default')) not in ('default', 'standard', 'auto'):
        reason = 'nonstandard_service_tier'
    else:
        long = tokens['input_tokens'] > rate.get('long_context_threshold', math.inf)
        input_factor = rate.get('long_input_multiplier', 1) if long else 1
        output_factor = rate.get('long_output_multiplier', 1) if long else 1
        pieces = [(tokens['input_tokens']-tokens['cached_input_tokens']-tokens['cache_write_tokens'], 'input_per_million', input_factor),
                  (tokens['cached_input_tokens'], 'cached_input_per_million', input_factor),
                  (tokens['cache_write_tokens'], 'cache_write_per_million', input_factor),
                  (tokens['output_tokens'], 'output_per_million', output_factor)]
        # Mixed cache TTLs need explicit split rates, not a guessed cache-write rate.
        creation = (call.get('usage') or {}).get('cache_creation', {})
        if isinstance(creation, dict) and creation.get('ephemeral_1h_input_tokens', 0):
            reason = 'one_hour_cache_write_rate_not_configured'
        elif any(n and key not in rate for n, key, _ in pieces):
            reason = 'missing_cache_price'
        else:
            estimate = float(sum(Decimal(n)*Decimal(str(rate.get(key, 0)))*Decimal(str(factor))
                                 for n, key, factor in pieces)/Decimal(1000000))
    return {**tokens, 'role':call.get('role', 'unknown'), 'provider':provider, 'model':model,
            'model_basis':'returned' if call.get('model_returned') else 'requested_unverified',
            'call_status':call.get('status'), 'currency':'USD', 'estimated_cost_usd':estimate,
            'cost_status':'estimated' if estimate is not None else 'unknown', 'unknown_reason':reason,
            'cost_basis':'standard_api_equivalent_not_actual_bill', 'actual_billed_cost_usd':None,
            'price_snapshot_sha256':hashlib.sha256(json.dumps(book, sort_keys=True).encode()).hexdigest(),
            'price':deepcopy(rate), 'price_checked_on':book.get('checked_on')}


def summarize_calls(records):
    unknown = sum(r.get('estimated_cost_usd') is None for r in records)
    subtotal = float(sum(Decimal(str(r['estimated_cost_usd'])) for r in records if r.get('estimated_cost_usd') is not None))
    return {'calls':len(records), 'unknown_cost_calls':unknown,
            'known_estimated_cost_usd':subtotal,
            'estimated_cost_usd':subtotal if not unknown else None,
            'actual_billed_cost_usd':None,
            'tokens':{k:sum(r[k] for r in records if r.get(k) is not None) for k in TOKEN_FIELDS},
            'missing_token_calls':{k:sum(r.get(k) is None for r in records) for k in TOKEN_FIELDS}}


def cost_summary(records):
    grouped = defaultdict(list)
    for r in records:
        grouped[(r['role'], r['provider'], r['model'])].append(r)
    return {'schema_version':1, 'currency':'USD', 'basis':'standard_api_equivalent_not_actual_bill',
            'total':summarize_calls(records),
            'by_role_model':[dict(role=k[0],provider=k[1],model=k[2],**summarize_calls(v)) for k,v in sorted(grouped.items())]}


def merge_summaries(summaries):
    """Aggregate all statuses, including failed calls/games, without duplicating A."""
    keys = ('calls', 'unknown_cost_calls', 'known_estimated_cost_usd')
    def merge(items):
        value = {k:sum(x[k] for x in items) for k in keys}
        value['estimated_cost_usd'] = value['known_estimated_cost_usd'] if not value['unknown_cost_calls'] else None
        value['actual_billed_cost_usd'] = None
        for field in ('tokens', 'missing_token_calls'):
            value[field] = {k:sum(x[field][k] for x in items) for k in TOKEN_FIELDS}
        return value
    groups = defaultdict(list)
    for summary in summaries:
        for r in summary['by_role_model']:
            groups[(r['role'], r['provider'], r['model'])].append(r)
    return {'schema_version':1, 'currency':'USD', 'basis':'standard_api_equivalent_not_actual_bill',
            'total':merge([s['total'] for s in summaries]),
            'by_role_model':[dict(role=k[0],provider=k[1],model=k[2],**merge(v)) for k,v in sorted(groups.items())]}


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False)+'\n')


def write_call_costs(folder, records):
    fields = ['call_index','role','provider','model','model_basis','call_status',*TOKEN_FIELDS,
              'estimated_cost_usd','cost_status','unknown_reason','cost_basis','price_snapshot_sha256']
    with (folder/'token_costs.csv').open('w', newline='') as f:
        writer=csv.DictWriter(f, fieldnames=fields, extrasaction='ignore'); writer.writeheader()
        writer.writerows(dict(call_index=i,**r) for i,r in enumerate(records,1))


def write_batch_costs(folder, entries):
    seen=set(); games=[]; summaries=[]; missing=[]
    for row in entries:
        name=row['run_dir']
        if name in seen:
            continue
        seen.add(name)
        cost=row.get('costs')
        if cost is None:
            missing.append(name)
            continue
        summaries.append(cost)
        games.append(dict(run_dir=name,puzzle_id=row.get('puzzle_id'),condition=row.get('condition'),
                          repeat=row.get('repeat'),status=row.get('status'),**cost['total']))
    summary=merge_summaries(summaries)
    summary.update(games_with_accounting=len(games),games_missing_accounting=missing)
    if missing:
        summary['total']['estimated_cost_usd']=None
    write_json(folder/'cost_summary.json',summary)
    fields=['run_dir','puzzle_id','condition','repeat','status','calls',*TOKEN_FIELDS,
            'known_estimated_cost_usd','estimated_cost_usd','unknown_cost_calls','missing_token_calls']
    with (folder/'costs_by_game.csv').open('w', newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');writer.writeheader()
        writer.writerows({**g,**g['tokens'],'missing_token_calls':json.dumps(g['missing_token_calls'])} for g in games)
    return summary
