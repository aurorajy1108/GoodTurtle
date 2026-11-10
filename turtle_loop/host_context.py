"""Build one versioned, private story context for the host and evaluator."""
import copy
import hashlib
import json
import math
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LABELS = {'yes', 'no', 'yes and no', 'irrelevant'}


def story_fingerprint(puzzle):
    # Do not match by opening alone: several puzzles intentionally share it.
    text = json.dumps([puzzle['opening'], puzzle['answer']], ensure_ascii=False)
    return hashlib.sha256(text.encode()).hexdigest()


def grading_fingerprint(puzzle):
    data = {k: puzzle.get(k) for k in ('rubric', 'completion_requirements', 'grading_notes', 'grading_protocol')}
    return hashlib.sha256(json.dumps(data, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def build_story_context(puzzle, root=ROOT):
    root = Path(root)
    bindings = json.loads((root / 'configs/host_bindings.json').read_text())
    binding = bindings.get(puzzle['id'])
    pack = {}
    if binding:
        if story_fingerprint(puzzle) != binding['story_sha256']:
            raise ValueError(f"{puzzle['id']}: host binding does not match opening/answer; review and rebind")
        binding = copy.deepcopy(binding)
        if binding.get('overlay_pack'):
            path = (root / binding['overlay_pack']).resolve()
            if not path.is_relative_to((root / 'data/host_packs').resolve()):
                raise ValueError('Host overlay must be inside data/host_packs')
            binding.update(json.loads(path.read_text()))
        if binding.get('legacy_pack'):
            path = (root / binding['legacy_pack']).resolve()
            if not path.is_relative_to((root / 'data/host_packs').resolve()):
                raise ValueError('Host pack must be inside data/host_packs')
            pack = json.loads(path.read_text())
        pack = copy.deepcopy(pack)
        if binding.get('replace_host_examples', False):
            pack['host_examples'] = []
        examples = pack.get('host_examples', [])
        for example in examples:
            override = binding.get('label_overrides', {}).get(example['case_id'])
            if override:
                example.update(answer=override['answer'], rationale=override['rationale'])
        for key in ('canonical_facts', 'explicit_negatives', 'unknown_details', 'irrelevant_details', 'host_examples'):
            pack[key] = pack.get(key, []) + binding.get(key, [])
        for key in ('solution', 'event_order', 'knowledge_states', 'label_boundaries', 'verification_policy'):
            if key in binding:
                pack[key] = copy.deepcopy(binding[key])
    seen = {}
    if pack.get('verification_policy','single') not in ('single','independent_then_adjudicate_v1'):
        raise ValueError('Unsupported host verification policy')
    for example in pack.get('host_examples', []):
        if example.get('answer') not in LABELS or not example.get('question'):
            raise ValueError('Invalid host example')
        key = (example['question'].strip().casefold(), json.dumps(example.get('public_history', []), sort_keys=True))
        if key in seen and seen[key] != example['answer']:
            raise ValueError('Conflicting labels for the same example question/history')
        seen[key] = example['answer']
    context = {
        'puzzle_id': puzzle['id'], 'opening': puzzle['opening'], 'reference_answer': puzzle['answer'],
        'canonical_solution': pack.get('solution', puzzle['answer']),
        'canonical_facts': pack.get('canonical_facts') or puzzle.get('completion_requirements', []),
        'explicit_negatives': pack.get('explicit_negatives', []),
        'unknown_details': pack.get('unknown_details', []),
        'irrelevant_details': pack.get('irrelevant_details', []),
        'completion_requirements': puzzle.get('completion_requirements', []),
        'host_examples': pack.get('host_examples', []),
        'review_status': binding.get('review_status', 'pending_human_review') if binding else 'pending_human_review',
        'binding_version': binding.get('version') if binding else None,
        'story_sha256': story_fingerprint(puzzle),
        'grading_sha256': grading_fingerprint(puzzle),
        'context_schema': 'story-context-v2',
        'event_order': pack.get('event_order', []),
        'knowledge_states': pack.get('knowledge_states', []),
        'label_boundaries': pack.get('label_boundaries', []),
        'verification_policy': pack.get('verification_policy', 'single'),
    }
    context['context_sha256'] = hashlib.sha256(json.dumps(context, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    return context


RUNTIME_VERSION = 'single-cached-reference-session-v3'
CONTEXT_DEFAULTS = {'host_examples_limit': 6, 'grader_examples_limit': 3,
                    'host_examples_max_chars': 6000, 'grader_examples_max_chars': 3000}
# Whitelist story semantics. Full originals and provenance stay in host_context.json.
STORY_FIELDS = ('puzzle_id', 'opening', 'reference_answer', 'canonical_solution',
                'canonical_facts', 'explicit_negatives', 'unknown_details',
                'irrelevant_details', 'completion_requirements', 'event_order',
                'knowledge_states', 'label_boundaries')
HISTORY_FIELDS = ('question', 'answer', 'type', 'text', 'feedback', 'role', 'content')
STOPWORDS = set('a an the is are was were be been being do does did of to in on at '
                'for from by with as and or that this it its he she they his her their '
                'have has had would could can will some any what which who how why '
                'statement correct false true'.split())


def context_policy(value=None):
    value = {} if value is None else value
    if not isinstance(value, dict) or set(value) - set(CONTEXT_DEFAULTS):
        raise ValueError('Unknown context_policy settings')
    policy = {**CONTEXT_DEFAULTS, **value}
    for key, number in policy.items():
        ceiling = 20 if key.endswith('_limit') else 50000
        if type(number) is not int or not 0 <= number <= ceiling:
            raise ValueError(f'{key} must be an integer in [0, {ceiling}]')
    return policy


def compact_example(example):
    """Never truncate a precedent's question, label or history: meaning is atomic."""
    result = {key: copy.deepcopy(example[key]) for key in ('question', 'answer')}
    if example.get('public_history'):
        result['public_history'] = [
            {key: copy.deepcopy(turn[key]) for key in HISTORY_FIELDS if key in turn}
            for turn in example['public_history']]
    return result


def _terms(text):
    return [word for word in re.findall(r"\w+", text.casefold()) if word not in STOPWORDS]


def retrieve_examples(context, query, history, limit, max_chars):
    """Local BM25, no model calls. Search only this puzzle's bound references.

    Current wording dominates; the last two turns help resolve pronouns. Exact
    questions rank first, but their original history is still shown to the host.
    Oversized examples are skipped whole, never stripped of qualifying history.
    """
    examples = context.get('host_examples', [])
    compact = [compact_example(e) for e in examples]
    documents = [Counter(_terms(e['question'] + ' ' + json.dumps(e.get('public_history', []), ensure_ascii=False)))
                 for e in compact]
    frequencies = Counter(term for doc in documents for term in doc)
    average = sum(sum(doc.values()) for doc in documents) / max(1, len(documents)) or 1
    current = Counter(_terms(query))
    recent = Counter(_terms(json.dumps(history[-2:], ensure_ascii=False)))
    weights = {term: 4 * min(current[term], 2) + min(recent[term], 1)
               for term in current.keys() | recent.keys()}
    ranked = []
    normalized = lambda text: ' '.join(re.findall(r'\w+', text.casefold()))
    for index, (example, doc) in enumerate(zip(examples, documents)):
        score = 0.0
        for term, weight in weights.items():
            tf = doc[term]
            if tf:
                idf = math.log(1 + (len(documents) - frequencies[term] + .5) / (frequencies[term] + .5))
                score += weight * idf * tf * 2.2 / (tf + 1.2 * (.25 + .75 * sum(doc.values()) / average))
        exact = normalized(query) == normalized(example['question'])
        pinned = example.get('runtime_required') is True
        if score > 0 or exact or pinned:
            ranked.append((not exact, not pinned, -score, index))
    selected, records, skipped = [], [], []
    for _, _, negative_score, index in sorted(ranked):
        if len(selected) >= limit:
            break
        candidate = compact[index]
        if len(json.dumps(selected + [candidate], ensure_ascii=False)) > max_chars:
            skipped.append(examples[index].get('case_id', str(index)))
            continue
        selected.append(candidate)
        records.append({'case_id': examples[index].get('case_id', str(index)),
                        'source_index': index, 'score': round(-negative_score, 6)})
    return selected, {'method': 'local_bm25_v1', 'available': len(examples),
                      'selected': records, 'skipped_oversize': skipped,
                      'selected_chars': len(json.dumps(selected, ensure_ascii=False)),
                      'limit': limit, 'max_chars': max_chars}


def runtime_story(context):
    return {key: copy.deepcopy(context[key]) for key in STORY_FIELDS if key in context}


def host_payload(context, history, question, policy=None, audit=None):
    policy = context_policy(policy)
    examples, selection = retrieve_examples(context, question, history,
        policy['host_examples_limit'], policy['host_examples_max_chars'])
    active = runtime_story(context)
    active['host_examples'] = examples
    if audit:
        audit(selection)
    return {'active_puzzle': active, 'visible_history': history, 'current_question': question}


def grader_story_context(context, explanation, policy=None, audit=None):
    policy = context_policy(policy)
    examples, selection = retrieve_examples(context, explanation, [],
        policy['grader_examples_limit'], policy['grader_examples_max_chars'])
    active = runtime_story(context)
    active['host_examples'] = examples
    if audit:
        audit(selection)
    return active
