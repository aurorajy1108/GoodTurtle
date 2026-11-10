"""Private evidence coverage and conservative deterministic grading constraints."""
import copy
import re

PROTOCOL = 'coverage-v2'
STATUSES = ('covered', 'partial', 'missing', 'contradicted')


def fact_specs(rubric):
    return [{'id': f"{point['id']}.F{i}", 'checkpoint_id': point['id'], 'fact': fact}
            for point in rubric
            for i, fact in enumerate(point.get('required_facts') or
                                     [point.get('full_credit', point['criterion'])], 1)]


def requirement_specs(requirements):
    return [{'id': f'R{i}', 'fact': fact} for i, fact in enumerate(requirements, 1)]


def coverage_schema():
    def obj(fields):
        return {'type':'object', 'properties':fields, 'required':list(fields), 'additionalProperties':False}
    string = {'type':'string'}
    row = obj({'id':string, 'status':{'type':'string','enum':list(STATUSES)}, 'evidence':string})
    return {
        'fact_coverage':{'type':'array','items':row},
        'requirement_coverage':{'type':'array','items':row},
        'contradictions':{'type':'array','items':obj({'quote':string,'reference':string,
                          'checkpoint_ids':{'type':'array','items':string}})},
    }


def evidence_is_verbatim(quote, submission):
    if not isinstance(quote,str) or not quote.strip():
        return False
    # Models often cite several sentences or use ellipses. Verify each quoted
    # span in order, ignoring typography only; never fuzzy-match changed words.
    source = re.findall(r'\w+', submission.casefold())
    spans = re.split(r'\.{3}|…|(?<=[.!?])\s+', quote)
    cursor = 0
    matched = False
    for span in spans:
        tokens = re.findall(r'\w+', span.casefold())
        if not tokens:
            continue
        for start in range(cursor, len(source)-len(tokens)+1):
            if source[start:start+len(tokens)] == tokens:
                cursor = start+len(tokens)
                matched = True
                break
        else:
            return False
    return matched


def normalize_coverage_metadata(value):
    """Drop only optional string explanations, without changing any judgments."""
    value=copy.deepcopy(value)
    changes=[]
    for name in ('fact_coverage','requirement_coverage'):
        items=value.get(name)
        if not isinstance(items,list):continue  # The strict validator reports this.
        for row in items:
            if not isinstance(row,dict):continue
            for field in ('reason', 'reference'):
                if field not in row:continue
                if not isinstance(row[field],str):
                    raise ValueError(f'{name}: optional {field} must be a string')
                metadata=row.pop(field)
                changes.append({'field':f"{name}.{row.get('id','?')}.{field}",'action':'ignored_metadata',
                                'model':metadata,'effective':None})
    return value,changes

def constrain(value, rubric, requirements, submission):
    """Validate evidence IDs, cap credit and reconcile flags. Never increase credit."""
    value, corrections = normalize_coverage_metadata(value)
    def quote_exists(quote):
        return evidence_is_verbatim(quote, submission)
    def rows(name, specs):
        items = value.get(name)
        if not isinstance(items, list) or len(items) != len(specs):
            raise ValueError(f'{name}: every supplied fact must be assessed once')
        indexed = {}
        for row in items:
            if (not isinstance(row, dict) or set(row) != {'id','status','evidence'}
                    or not isinstance(row['id'],str) or row['id'] in indexed
                    or row['status'] not in STATUSES or not isinstance(row['evidence'],str)):
                raise ValueError(f'{name}: invalid or duplicate coverage row')
            if row['status'] != 'missing' and not quote_exists(row['evidence']):
                raise ValueError(f'{name}: evidence must consist of ordered verbatim excerpts from this submission')
            indexed[row['id']] = row
        if set(indexed) != {s['id'] for s in specs}:
            raise ValueError(f'{name}: wrong fact IDs')
        return indexed
    specs = fact_specs(rubric)
    facts = rows('fact_coverage', specs)
    completion = rows('requirement_coverage', requirement_specs(requirements))
    contradictions = value.get('contradictions')
    if not isinstance(contradictions, list):
        raise ValueError('contradictions must be a list')
    ids = {p['id'] for p in rubric}
    affected = set()
    for item in contradictions:
        if (not isinstance(item,dict) or set(item) != {'quote','reference','checkpoint_ids'}
                or not quote_exists(item['quote']) or not isinstance(item['reference'],str)
                or not item['reference'].strip() or not isinstance(item['checkpoint_ids'],list)
                or any(not isinstance(x,str) or x not in ids for x in item['checkpoint_ids'])):
            raise ValueError('Invalid material contradiction evidence/checkpoint IDs')
        affected.update(item['checkpoint_ids'])
    for point in value['checkpoints']:
        statuses = [facts[s['id']]['status'] for s in specs if s['checkpoint_id']==point['id']]
        cap = (0 if point['id'] in affected or 'contradicted' in statuses or all(s=='missing' for s in statuses)
               else 1 if all(s=='covered' for s in statuses) else 0.5)
        rule = next(r for r in rubric if r['id'] == point['id'])
        gates = rule.get('half_credit_requires', [])
        if cap < 1 and any(facts[fid]['status'] != 'covered' for fid in gates):
            cap = 0
        if point['credit'] > cap:
            corrections.append({'field':point['id']+'.credit','model':point['credit'],'effective':cap})
            point['credit'] = cap
    if contradictions or any(x['status']=='contradicted' for x in [*facts.values(),*completion.values()]):
        if not value['material_contradiction']:
            corrections.append({'field':'material_contradiction','model':False,'effective':True})
        value['material_contradiction'] = True
    complete = (all(x['status']=='covered' for x in [*facts.values(),*completion.values()])
                and not any(value[k] for k in ('material_contradiction','rubric_conflict','irrelevant')))
    if value['full_solution'] and not complete:
        corrections.append({'field':'full_solution','model':True,'effective':False})
        value['full_solution'] = False
    return value, corrections
