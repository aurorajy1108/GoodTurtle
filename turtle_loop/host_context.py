"""Build one versioned, private story context for the host and evaluator."""
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LABELS = {'yes', 'no', 'yes and no', 'irrelevant'}


def story_fingerprint(puzzle):
    # Do not match by opening alone: several puzzles intentionally share it.
    text = json.dumps([puzzle['opening'], puzzle['answer']], ensure_ascii=False)
    return hashlib.sha256(text.encode()).hexdigest()


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
    for example in pack.get('host_examples', []):
        if example.get('answer') not in LABELS or not example.get('question'):
            raise ValueError('Invalid host example')
    context = {
        'puzzle_id': puzzle['id'], 'opening': puzzle['opening'], 'reference_answer': puzzle['answer'],
        'canonical_solution': pack.get('solution', puzzle['answer']),
        'canonical_facts': pack.get('canonical_facts', []),
        'explicit_negatives': pack.get('explicit_negatives', []),
        'unknown_details': pack.get('unknown_details', []),
        'irrelevant_details': pack.get('irrelevant_details', []),
        'completion_requirements': puzzle.get('completion_requirements', []),
        'host_examples': pack.get('host_examples', []),
        'review_status': binding.get('review_status', 'pending_human_review') if binding else 'pending_human_review',
        'binding_version': binding.get('version') if binding else None,
        'story_sha256': story_fingerprint(puzzle),
    }
    context['context_sha256'] = hashlib.sha256(json.dumps(context, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    return context


def host_payload(context, history, question):
    return {'active_puzzle': context, 'visible_history': history, 'current_question': question}
