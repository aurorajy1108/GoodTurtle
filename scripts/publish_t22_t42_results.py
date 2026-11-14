#!/usr/bin/env python3
"""Publish the T22/T42 report and 37 audited trajectories without model calls."""
import argparse
import csv
import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def publish(report, frozen_runtime, out):
    report, frozen_runtime, out = (Path(p).resolve() for p in (report, frozen_runtime, out))
    if out.exists():
        raise ValueError('Use a new output directory')
    # Restore using the compatible archived billing/schema recovery adapters.
    sys.path.insert(0, str(frozen_runtime))
    import turtle_loop.engine  # noqa: F401
    import turtle_loop.sessions  # noqa: F401
    import turtle_loop.transport_recovery  # noqa: F401
    import turtle_loop.costs  # noqa: F401
    sys.path.append(str(ROOT))
    from scripts.publish_verified_results import audit_game, export_game

    rows = json.loads((report / 'games.json').read_text())
    summary = json.loads((report / 'summary.json').read_text())
    if len(rows) != 31 or len(summary['original_source_and_session_appendix']) != 6:
        raise ValueError('Expected 31 main games plus six appendix games')
    entries = []
    for row in rows:
        condition = row['condition']
        label = f"after_{row['predecessor_A']}_session" if condition == 'session' else condition
        dest = Path('trajectories') / row['puzzle'] / label / f"r{row['round']:02d}"
        entries.append((Path(row['artifact_dir']), dest, row, 'main'))
    for row in summary['original_source_and_session_appendix']:
        dest = Path('appendix') / ('sources' if row['condition'] == 'source' else 'early_session') / row['source']
        entries.append((Path(row['artifact_dir']), dest, row, 'appendix'))
    if len({str(e[1]) for e in entries}) != 37:
        raise ValueError('Duplicate destinations')
    accepted = []
    for source, dest, row, scope in entries:
        audit, calls = audit_game(source)
        accepted.append((source, dest, row, scope, audit, calls))
    out.mkdir(parents=True)
    replacements = {str(source): dest.as_posix() for source, dest, *_ in accepted}
    (out / '.gitattributes').write_text('# Preserve exact source CSV line endings and whitespace inside model transcripts.\n*.csv whitespace=-trailing-space,cr-at-eol\ntrajectory.md whitespace=-trailing-space\ntrajectory.html whitespace=-trailing-space\nshared_dialogue.html whitespace=-trailing-space\n')
    manifest = []
    for source, dest, row, scope, audit, calls in accepted:
        target = out / dest
        export_game(source, target, audit, calls)
        extra_hashes = {}
        for name in ('host_context.json', 'source_binding.json', 'prior_experience.json', 'transfer_metadata.json', 'partner_config.json'):
            if (source / name).exists():
                shutil.copy2(source / name, target / name)
                extra_hashes[name] = hashlib.sha256((source / name).read_bytes()).hexdigest()
        metadata = {'scope': scope, 'puzzle': row.get('puzzle', 'TS022' if row['condition'] == 'session' else row.get('source')),
                    'condition': row['condition'], 'predecessor_A': row.get('predecessor_A', row.get('source') if row['condition'] == 'session' else None),
                    'round': row.get('round', 1), 'source_prefix_calls_sha256': row.get('source_prefix_calls_sha256')}
        if metadata['predecessor_A']:
            metadata['source_trajectory'] = 'appendix/sources/' + metadata['predecessor_A']
        (target / 'experiment_metadata.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n')
        verification = json.loads((target / 'verification.json').read_text())
        verification['additional_copied_files_sha256'] = extra_hashes
        verification['omitted_source_files_sha256'] = {name: hashlib.sha256((source / name).read_bytes()).hexdigest()
            for name in ('player_continuation.json', 'first_turn_billing_call.json') if (source / name).exists()}
        (target / 'verification.json').write_text(json.dumps(verification, ensure_ascii=False, indent=2) + '\n')
        manifest.append({**metadata, 'trajectory_dir': dest.as_posix(), 'submissions': audit['submissions'],
                         'source_api_calls_sha256': audit['source_api_calls_sha256'],
                         'source_raw_api_bytes': (source / 'api_calls.jsonl').stat().st_size,
                         'verification': 'passed', 'human_semantic_review': 'pending'})
    for name in ('games.csv', 'games.json', 'summary.csv', 'summary.json', 'report.md', 'index.html'):
        text = (report / name).read_text(encoding='utf-8-sig')
        for source, dest in replacements.items():
            text = text.replace(source, dest)
        if name == 'index.html':
            text = text.replace('<p>记录位置：${esc(r.artifact_dir)}</p>',
                '<p><a href="${esc(r.artifact_dir)}/trajectory.html">查看本局完整trajectory</a> · <a href="${esc(r.artifact_dir)}/trajectory.md">Markdown</a></p>')
        (out / name).write_text(text, encoding='utf-8-sig' if name.endswith('.csv') else 'utf-8')
    protocol = out / 'protocol' / 'frozen_runtime'
    for directory in ('turtle_loop', 'configs', 'prompts'):
        shutil.copytree(frozen_runtime / directory, protocol / directory,
                        ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    (protocol / 'data').mkdir()
    shutil.copy2(frozen_runtime / 'data/dataset.json', protocol / 'data/dataset.json')
    protocol_files = {str(p.relative_to(protocol)): hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in protocol.rglob('*') if p.is_file()}
    (out / 'protocol/frozen_files_sha256.json').write_text(json.dumps(protocol_files, indent=2) + '\n')
    manifest_data = {'main_games': 31, 'appendix_source_games': 3, 'appendix_early_session_games': 3,
                     'published_trajectories': 37, 'all_completed': True, 'games': manifest,
                     'raw_request_policy': 'Full repeated request bodies remain in original local archives. Compressed API audits preserve all responses, usage/errors/accounting and request/inheritance hashes.',
                     'validation': 'Counters, feedback uniqueness, weighted scores/completion, role session lineage, costs and MAS public dialogue checked offline; no new model calls.'}
    (out / 'manifest.json').write_text(json.dumps(manifest_data, ensure_ascii=False, indent=2) + '\n')
    (out / 'README.md').write_text('''# T22 / T42：2026-11-14 实验轨迹

[结果浏览页](index.html) · [完整分析](report.md) · [逐局CSV](games.csv) · [汇总CSV](summary.csv)

主分析31局全部完成：T22五轮baseline/after-A session（20局）与五局双agent free_dialogue；T42一局baseline与五局双agent free_dialogue。另收录三个原A及最早三个session，共37份trajectory。

- `trajectories/TS022/`：baseline、after_TS047_session（positive）、after_TS045_session（negative）、after_TS019_session（irrelevant）、free_dialogue。
- `trajectories/TS042/`：baseline、free_dialogue。
- `appendix/sources/`：只保留一份原A。15局主session始终复用这三个固定前缀，没有重跑A。
- `appendix/early_session/`：最早三个session，缺少同轮baseline，未并入主比较。

每局有trajectory的Markdown/HTML/JSONL、原始result、汤面汤底和评分点、配置与提示词、费用及核验记录；MAS另有共享讨论JSONL/HTML。`experiment_metadata.json`明确记录前题A和源trajectory位置，整理轮号不改写原始result轮号。原始result、问答及评分保持不变。

13局充值后续跑的失败调用和恢复事件保留在审计与trajectory中，最终归档替代原中断快照，计数一次。compact `api_audit.jsonl.gz`保留各次返回、用量、错误、完整请求哈希；不含重复HTTP请求body及内嵌A前缀，不能单独重建完整HTTP请求。源文件哈希见逐局verification及manifest。

Player/伙伴是DeepSeek Flash（thinking disabled）；Host/Grader是DeepSeek v4 Pro（thinking enabled/high）。B共用100次外部提交上限，MAS另有内部讨论调用，计算量不匹配。所有语义评分待人工审核。T22 MAS最终均分36%，完整解出1/5；T42 MAS均分63%，完整解出0/5，baseline仅一局50%。

`protocol/frozen_runtime/`保存审计使用的冻结Python模块、配置、提示词及题库；包含原恢复适配器，仅作历史审阅。此目录不是完整可续跑的API原归档；未包含密钥或环境文件。31局的费用单独计，附录原A和早期session未并入主费用。

在保存原本地归档的机器上可离线重建（不调用模型）：

```sh
python3 scripts/publish_t22_t42_results.py \\
  --report reports/t22_t42_20261114 \\
  --frozen-runtime runs/api/t22_t42_20261114_paid_resume13/runtime_snapshot \\
  --out results/NEW_T22_T42_RELEASE
```
''')
    print(json.dumps({'out': str(out), 'main_games': 31, 'trajectories': 37,
                      'files': sum(1 for p in out.rglob('*') if p.is_file()),
                      'bytes': sum(p.stat().st_size for p in out.rglob('*') if p.is_file())}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--frozen-runtime', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    publish(args.report, args.frozen_runtime, args.out)
