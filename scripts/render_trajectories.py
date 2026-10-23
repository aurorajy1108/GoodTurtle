#!/usr/bin/env python3
"""Embed all recorded games and team discussions in one standalone HTML artifact."""
import argparse
import html
import json
from pathlib import Path


def jsonl(path):
    if not path.exists():
        return []
    text = path.read_text()
    rows = []
    for index, line in enumerate(text.splitlines()):
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            if index == len(text.splitlines()) - 1 and not text.endswith('\n'):
                break  # A live writer may not have finished its last event.
            raise
    return rows


def collect(root):
    games = []
    for path in sorted(root.rglob('trajectory.jsonl')):
        if 'runtime_snapshot' not in path.relative_to(root).parts:
            folder = path.parent
            def read(name, default=None):
                p = folder / name
                return json.loads(p.read_text()) if p.exists() else default
            puzzle = read('puzzle_private.json', {})
            games.append({'name': str(folder.relative_to(root)), 'puzzle_id': puzzle.get('id'),
                          'opening': puzzle.get('opening'), 'answer': puzzle.get('answer'),
                          'result': read('result.json', {}), 'events': jsonl(path),
                          'collaboration': jsonl(folder/'collaboration.jsonl'),
                          'prior_experience': read('prior_experience.json'),
                          'host_context': read('host_context.json')})
    return games


def render(root, output):
    games = collect(root)
    # Escape '<' so model-authored </script> can never terminate the data element.
    payload = json.dumps(games, ensure_ascii=False).replace('<', '\\u003c').replace('&', '\\u0026')
    title = html.escape(root.name)
    page = '''<!doctype html><html lang="zh"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>海龟汤实验完整轨迹</title>
<style>
body{font:16px/1.6 system-ui,sans-serif;background:#f4f6f8;color:#17202b;margin:0}
header,main{max-width:1120px;margin:auto;padding:24px}h1{font-size:26px;margin:0}
.controls{position:sticky;top:0;background:#f4f6f8;padding:12px 0;z-index:1;display:flex;gap:12px;flex-wrap:wrap}
input,select,button{font:inherit;padding:8px;border:1px solid #bbc4cf;border-radius:6px}
input{flex:1;min-width:220px}article,details.game{background:white;padding:18px;border:1px solid #dce1e7;border-radius:10px;margin:14px 0}
summary{cursor:pointer;font-weight:600}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:inherit}
.label{color:#185b42;font-weight:700}.meta{color:#4e5969}.question{border-left:4px solid #376cb5}
.final{border-left:4px solid #aa6b20}.warn{color:#8c4811}details.private{background:#faf3e9;padding:10px;margin-top:12px}
table{border-collapse:collapse;width:100%;font-size:14px}td,th{padding:8px;text-align:left;border-bottom:1px solid #ddd}
</style>
<header><h1>海龟汤实验：完整 trajectory</h1><p>RUN_TITLE</p>
<p class="meta">本文件内嵌全部已记录问答、最终提交、评分和合作讨论，无需访问外部资源。未完成局会明确显示状态。私有答案与评分只供审核，并未发给 player。</p>
<div id="overview"></div></header><main><div class="controls"><select id="filter"><option value="">全部对局</option></select><input id="search" placeholder="搜索问题、答案或讨论"><button id="expand">展开全部轨迹</button></div><div id="games"></div></main>
<script id="data" type="application/json">PAYLOAD</script>
<script>
const games=JSON.parse(document.getElementById('data').textContent);
const el=(tag,text,cls)=>{const e=document.createElement(tag);if(text!==undefined)e.textContent=text;if(cls)e.className=cls;return e};
const detail=(name,value)=>{const d=el('details',undefined,'private');d.append(el('summary',name),el('pre',typeof value==='string'?value:JSON.stringify(value,null,2)));return d};
const table=el('table');const hr=el('tr');['对局','状态','问题数','部分分','完整解出'].forEach(x=>hr.append(el('th',x)));table.append(hr);
for(const g of games){const r=g.result;const tr=el('tr');[g.name,r.status,r.counted_questions,r.final_partial_score??'—',r.success===true?'是':r.success===false?'否':'未完成'].forEach(x=>tr.append(el('td',String(x))));table.append(tr);
const o=el('option',g.name);o.value=g.name;document.getElementById('filter').append(o)}
document.getElementById('overview').append(table);
function draw(){const target=document.getElementById('games');target.replaceChildren();const query=document.getElementById('search').value.toLowerCase();const selected=document.getElementById('filter').value;
for(const g of games){if(selected&&g.name!==selected)continue;if(query&&!JSON.stringify(g).toLowerCase().includes(query))continue;
const box=el('details',undefined,'game');box.open=!!selected||!!query;box.append(el('summary',g.name+' · '+g.result.status),el('pre',g.opening),detail('私有汤底及统一事实',g.host_context??g.answer));
if(g.prior_experience)box.append(detail('传给 B 的 A 题公开经验',g.prior_experience));
const feedback=new Map(g.events.filter(x=>x.event==='host_feedback'||x.event==='evaluation').map(x=>[x.submission,x]));
for(const t of g.events.filter(x=>x.event==='submission')){const f=feedback.get(t.index);const a=el('article',undefined,t.type);a.append(el('h3','#'+t.index+' · '+t.type+(t.forced?' · 强制最终提交':'')),el('pre',t.text),el('p','Host: '+(f?.label??'等待反馈'),'label'));if(f?.event==='evaluation')a.append(detail('私有评分与完整叙事判定',f));box.append(a)}
if(g.collaboration.length)box.append(detail('全部合作讨论（按调用顺序）',g.collaboration));
box.append(detail('性能与问题计数',g.result));target.append(box)}}
document.getElementById('filter').onchange=draw;document.getElementById('search').oninput=draw;document.getElementById('expand').onclick=()=>document.querySelectorAll('details.game').forEach(x=>x.open=true);draw();
</script></html>'''
    # Replace the payload last, never template-process model-owned text.
    page = page.replace('RUN_TITLE', title).replace('PAYLOAD', payload)
    output.write_text(page)
    return {'games': len(games), 'submissions': sum(sum(x['event']=='submission' for x in g['events']) for g in games),
            'collaboration_records': sum(len(g['collaboration']) for g in games), 'output': str(output)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path, help='Experiment root; discovers nested game trajectories, excluding runtime_snapshot')
    parser.add_argument('--out', type=Path, help='Output HTML; default DIRECTORY/trajectories.html')
    args = parser.parse_args()
    print(json.dumps(render(args.directory, args.out or args.directory/'trajectories.html')))
