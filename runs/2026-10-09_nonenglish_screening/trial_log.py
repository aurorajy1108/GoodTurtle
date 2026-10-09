"""Visible-message trial artifacts; never stores private model reasoning."""
import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent
FROZEN = ['config.json', 'solver_task.txt', 'host_context.txt', 'puzzle_private.json', 'grader_rubric.json']

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def init(pid, metadata):
    p = BASE / pid
    f = p / 'input_manifest.json'
    if f.exists():
        raise RuntimeError('Already initialized')
    f.write_text(json.dumps({x: sha(p/x) for x in FROZEN}, indent=2)+'\n')
    (p/'execution_metadata.json').write_text(json.dumps(metadata, indent=2)+'\n')

def record(pid, event):
    p = BASE / pid
    event['recorded_at_utc'] = datetime.now(timezone.utc).isoformat()
    if event['type']=='question':
        emitted=[dict(event='solver', type='question', question_number=event['question_number'], submission_number=event['submission_number'], text=event['text'], recorded_at_utc=event['recorded_at_utc']), dict(event,event='host')]
    elif event['type']=='final':
        emitted=[dict(event,event='solver_final_attempt'), dict(event='grader',type='verdict',final_attempt_number=event['final_attempt_number'],accepted=event['accepted'],rubric_grading=event['rubric_grading'],recorded_at_utc=event['recorded_at_utc'])]
    else:
        emitted=[event]
    with (p/'trajectory.jsonl').open('a') as f:
        for e in emitted:
            f.write(json.dumps(e, ensure_ascii=False)+'\n')

def finalize(pid, extra):
    p = BASE/pid
    events = [json.loads(x) for x in (p/'trajectory.jsonl').read_text().splitlines()]
    qs = [e for e in events if e.get('event')=='host']
    fs = [e for e in events if e.get('event')=='solver_final_attempt']
    issues = [e for e in qs if e.get('audit_status') != 'pass']
    material = any(e.get('material_error', False) for e in issues)
    solved = bool(fs and fs[-1].get('accepted'))
    config = json.loads((p/'config.json').read_text())
    result = dict(config, status='completed' if solved else 'unfinished', solved=solved,
                  question_count=len(qs), final_attempt_count=len(fs), total_submissions=len(qs)+len(fs),
                  retain_provisional=solved and len(qs)>30 and not material,
                  difficulty_validity='contaminated' if material else 'provisional_pending_human_review',
                  human_review_status='pending', host_audit={'material_error':material,'issues':issues},
                  final_attempts=len(fs), final_attempt_records=fs,
                  host_queries=len(qs),complete_solution=solved,
                  retained=solved and len(qs)>30 and not material,
                  host_review_status='material_error_contaminated' if material else 'ai_audited_human_pending',
                  backend_limitations=['Codex collaboration agents, not standalone API.',
                                      'Exact checkpoint, tokens, sampling parameters unavailable.',
                                      'No-tools solver isolation is instructional, not OS sandbox.',
                                      'Single run per puzzle; no distributional difficulty estimate.'])
    result.update(extra)
    (p/'result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    lines = [f'# {pid} visible trajectory', '', '## Opening', '', json.loads((p/'puzzle_private.json').read_text())['opening'], '']
    for e in events:
        if e.get('event')=='host':
            lines.extend([f"Q{e['question_number']} (submission {e['submission_number']}): {e['text']}", f"Host: {e['host_answer']}", ''])
        elif e.get('event')=='solver_final_attempt':
            lines.extend([f"Final attempt {e['final_attempt_number']} (submission {e['submission_number']}): {e['text']}",f"Controller verdict: {'yes' if e['accepted'] else 'no'}",''])
        elif e.get('event') not in ['solver','grader']:
            lines.extend([json.dumps(e,ensure_ascii=False),''])
    (p/'trajectory.md').write_text('\n'.join(lines)+'\n')
    with (p/'human_review.csv').open('w',newline='') as f:
        fields=['question_number','submission_number','question','host_answer','controller_audit','controller_note','reviewer_label','reviewer_material_error','reviewer_notes']
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
        for e in qs:
            w.writerow(dict(question_number=e['question_number'],submission_number=e['submission_number'],question=e['text'],host_answer=e['host_answer'],controller_audit=e.get('audit_status'),controller_note=e.get('audit_note','')))
    with (p/'final_attempt_review.csv').open('w',newline='') as f:
        fields=['final_attempt_number','submission_number','final_text','controller_accepted','rubric_grading','reviewer_accepted','reviewer_notes']
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for e in fs:
            w.writerow(dict(final_attempt_number=e['final_attempt_number'],submission_number=e['submission_number'],final_text=e['text'],controller_accepted=e['accepted'],rubric_grading=json.dumps(e['rubric_grading'],ensure_ascii=False)))
    original=json.loads((p/'input_manifest.json').read_text())
    assert original == {x:sha(p/x) for x in FROZEN}, 'Frozen input modified'
    (p/'SHA256SUMS').write_text(''.join(f'{sha(x)}  {x.name}\n' for x in sorted(p.iterdir()) if x.is_file() and x.name!='SHA256SUMS'))
    print(json.dumps({k:result[k] for k in ['puzzle_id','solved','question_count','final_attempt_count','total_submissions','retain_provisional','difficulty_validity']}))

if __name__ == '__main__':
    globals()[sys.argv[1]](sys.argv[2],json.loads(sys.argv[3]))
