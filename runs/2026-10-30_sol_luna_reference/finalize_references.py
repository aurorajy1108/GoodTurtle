"""Export completed model runs as explicitly synthetic reference sources, offline."""
import hashlib
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[1]
DEST = ROOT / 'data/host_reference/sources/model_simulated_20261030'
IDS = ('TS031', 'TS035', 'TS038')


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def main():
    games = []
    for pid in IDS:
        folder = RUN / 'batches' / pid / f'{pid}_r01_solo'
        result = json.loads((folder / 'result.json').read_text())
        if result['status'] == 'running':
            raise SystemExit('Still running; do not freeze an unfinished source: ' + pid)
        events = [json.loads(line) for line in (folder / 'trajectory.jsonl').read_text().splitlines()]
        actions = []
        for event in events:
            if event['event'] == 'submission':
                actions.append({k: event[k] for k in ('index', 'type', 'text', 'forced')})
            elif event['event'] in ('host_feedback', 'evaluation'):
                action = next(a for a in actions if a['index'] == event['submission'])
                action['feedback'] = event['label']
        assert len(actions) == result['submissions'] <= 100
        assert sum('feedback' not in a for a in actions) == result['pending_feedback']
        games.append((pid, folder, result, actions))
    DEST.mkdir(parents=True, exist_ok=True)
    manifest = {'source_kind': 'model_simulated_reference', 'human_confirmed': False,
                'review_status': 'pending', 'runtime_host_updated': False, 'games': []}
    lines = ['# 模型模拟参考问答：31、35、38', '',
             '来源为 GPT-6.1-sol Host / grader、GPT-6-luna Player，均 reasoning high。',
             '不是人工原始聊天；未审核标签不会自动进入 active Host。', '',
             '| 题目 | 状态 | 总提交 | 已计数问题 | 失败交卷 | 最终分数 | 完整解出 |',
             '| --- | --- | ---: | ---: | ---: | --- | --- |']
    for pid, folder, result, actions in games:
        relative = folder.relative_to(ROOT)
        puzzle = json.loads((folder / 'puzzle_private.json').read_text())
        record = {'puzzle_id': pid, 'source_kind': 'model_simulated_reference',
                  'opening': puzzle['opening'],
                  'human_confirmed': False, 'review_status': 'pending',
                  'host_model_requested': 'gpt-6.1-sol', 'player_model_requested': 'gpt-6-luna',
                  'reasoning_effort': 'high', 'run_path': str(relative),
                  'trajectory_sha256': hashlib.sha256((folder / 'trajectory.jsonl').read_bytes()).hexdigest(),
                  'status': result['status'], 'actions': actions}
        dump(DEST / f'{pid}.json', record)
        text = [f'# {pid} — model-simulated reference', '',
                'Player: GPT-6-luna; Host/grader: GPT-6.1-sol. Human review pending.', '',
                '## Opening', '', puzzle['opening'], '']
        for a in actions:
            text += [f"## {a['index']} · {a['type']}", '', a['text'], '',
                     'Host: ' + a.get('feedback', '[pending; run ended without feedback]'), '']
        (DEST / f'{pid}.md').write_text('\n'.join(text))
        summary = {k: result[k] for k in ('status', 'stop_reason', 'submissions', 'counted_questions',
                   'rejected_finals', 'pending_feedback', 'final_partial_score', 'success', 'error')}
        manifest['games'].append({'puzzle_id': pid, 'run_path': str(relative), **summary})
        lines.append(f"| [{pid}]({pid}.md) | {result['status']} | {result['submissions']} | "
                     f"{result['counted_questions']} | {result['rejected_finals']} | "
                     f"{result['final_partial_score']} | {result['success']} |")
    dump(DEST / 'manifest.json', manifest)
    lines += ['', '总提交包含成功交卷；已计数问题=普通问题+失败/不完整交卷。',
              '错误或未评分的交卷不补造标签，null 分数不等于零。', '',
              '[完整 HTML 与私有评分](../../../../runs/2026-10-30_sol_luna_reference/trajectories.html)',
              '[审核疑点](../../../../runs/2026-10-30_sol_luna_reference/review_observations.json)']
    (DEST / 'README.md').write_text('\n'.join(lines) + '\n')
    dump(RUN / 'reference_export.json', manifest)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
