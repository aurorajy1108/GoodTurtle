"""Combine reviewed, frozen experiments; never mutate experiment or Host files.

Run from any directory: python /absolute/path/to/build_joint_report.py
No network, API, credentials, or third-party dependency is used.
"""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def read(path):
    return json.loads(Path(path).read_text())


def lines(path):
    return [json.loads(x) for x in Path(path).read_text().splitlines() if x.strip()]


def sources():
    for cohort in ("local_cl", "coworker_legacy_set2"):
        for g in read(ROOT / cohort / "coverage.json")["games"]:
            yield cohort, g["game_id"], Path(g["source_path"]), g.get("notes", "")
    for cohort in ("local_mas", "coworker_other"):
        for g in read(ROOT / cohort / "inventory.json"):
            yield cohort, g.get("game_id", g.get("run_dir")), Path(g["path"]), ""
    for g in read(ROOT / "coworkers/inventory.json")["games"]:
        yield "coworkers", g["game_id"], Path(g["source_path"]), ""


def review_file(cohort, game):
    if cohort == "coworkers":
        return ROOT / cohort / "games" / (game.replace("/", "__") + ".jsonl")
    return ROOT / cohort / (game.replace("::", "__") + ".review.jsonl")


def normalize_game(cohort, game, path, note):
    events = lines(path / "trajectory.jsonl")
    subs = {e["index"]: e for e in events if e.get("event") == "submission"}
    labels = {e["submission"]: e["label"] for e in events
              if e.get("event") in ("host_feedback", "evaluation") and "label" in e}
    grades = {e["submission"]: e for e in events if e.get("event") == "evaluation"}
    rf = review_file(cohort, game)
    reviews = lines(rf)
    assert sorted(r["submission"] for r in reviews) == sorted(subs), (game, "coverage")
    for r in reviews:
        n = r["submission"]
        assert r["question"] == subs[n]["text"], (game, n, "text")
        assert r["actual_label"] == labels.get(n), (game, n, "label")
        assert r["type"].lower() == subs[n]["type"].lower(), (game, n, "type")
        r.update(cohort=cohort, human_confirmed=False, source_path=str(path),
                 source_review=str(rf.relative_to(ROOT)), forced=bool(subs[n].get("forced")))
        r["actual_evaluation"] = grades.get(n)
    puzzle = read(path / "puzzle_private.json")
    host = read(path / "host_context.json")
    result = read(path / "result.json")
    config = read(path / "config.json")
    # Include only nonsecret configuration fields; never load .env files.
    models = {role: {k: config.get(role, {}).get(k) for k in
              ("provider", "model", "max_output_tokens", "extra_body")}
              for role in ("host", "player", "grader")}
    row = dict(uid=cohort + "::" + game, cohort=cohort, game_id=game,
               path=str(path), review_path=str(rf.relative_to(ROOT)),
               puzzle_id=puzzle["id"], opening=puzzle["opening"], answer=puzzle["answer"],
               rubric=puzzle.get("rubric"), requirements=puzzle.get("completion_requirements"),
               annotation_version=puzzle.get("annotation_version"),
               grading_protocol=puzzle.get("grading_protocol"),
               host_binding=host.get("binding_version", host.get("version")),
               models=models, context_policy=config.get("context_policy"),
               status=result["status"], success=result.get("success"),
               score=result.get("final_partial_score"), best_score=result.get("best_partial_score"),
               submissions=len(reviews), questions=sum(r["type"].lower() == "question" for r in reviews),
               finals=sum(r["type"].lower() == "final" for r in reviews),
               counts=dict(Counter(r["verdict"] for r in reviews)), notes=note,
               raw_trajectory_sha256=hashlib.sha256((path / "trajectory.jsonl").read_bytes()).hexdigest(),
               submission_events_sha256=hashlib.sha256(json.dumps(list(subs.values()),
                     sort_keys=True, ensure_ascii=False).encode()).hexdigest(),
               reviews=reviews, error=result.get("error"), costs=result.get("costs"))
    return row


def write_csv(path, rows):
    fields = ["cohort", "game_id", "submission", "type", "question", "actual_label",
              "verdict", "recommended_label", "reason", "confidence", "human_confirmed",
              "original_score", "original_complete", "evaluation_verdict", "evaluation_reason",
              "observation", "source_review"]
    with path.open("w", encoding="utf-8-sig", newline="") as fp:
        writer = csv.DictWriter(fp, fields, extrasaction="ignore")
        writer.writeheader()
        for r in rows:
            g = r.get("actual_evaluation") or {}
            writer.writerow(dict(r, original_score=g.get("partial_score"),
                                 original_complete=g.get("complete")))


HTML = r'''<!doctype html><html lang="zh-CN"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>GoodTurtle · 逐问联合审阅 · 2026-11-14</title>
<style>
:root{font:15px/1.65 system-ui,sans-serif;color:#202d39;background:#f4f6f8}*{box-sizing:border-box}
body{margin:0}header{background:#193d48;color:white;padding:22px 30px}h1{font-size:24px;margin:0 0 8px}
header p{max-width:1050px;margin:4px 0;color:#d9ecee}.layout{display:grid;grid-template-columns:310px minmax(0,1fr);gap:22px;padding:22px}
aside{position:sticky;top:12px;align-self:start;max-height:96vh;overflow:auto}main{min-width:0}.card,article{background:white;border:1px solid #d9e0e6;border-radius:9px;padding:18px;margin-bottom:14px}
input,select,button{font:inherit;padding:7px 10px;border:1px solid #aebfc9;border-radius:5px;background:white;max-width:100%}aside input,aside select{width:100%;margin-bottom:8px}button{cursor:pointer}
.game{display:block;width:100%;text-align:left;margin:6px 0;padding:9px;font-size:12px;overflow-wrap:anywhere}.chosen{background:#dcecef;border-color:#397784}
.badge{display:inline-block;border-radius:20px;background:#e5edf1;padding:1px 8px;font-size:12px;margin:2px 3px}.suspect{background:#fff0ed;border-left:5px solid #c94c35}.ambiguous{background:#fff9df;border-left:5px solid #b99025}
.ok{border-left:5px solid #73a998}.muted{color:#647583;font-size:13px;overflow-wrap:anywhere}.card,h2{overflow-wrap:anywhere}.q{white-space:pre-wrap;overflow-wrap:anywhere;margin:12px 0}
pre{white-space:pre-wrap;overflow-wrap:anywhere;font:13px/1.6 ui-monospace,monospace;max-height:650px;overflow:auto;background:#f6f8fa;padding:12px}
details{margin:10px 0}summary{cursor:pointer}nav{display:flex;gap:8px;align-items:center;flex-wrap:wrap}.sticky{position:sticky;top:0;background:#f4f6f8ee;padding:8px 0;z-index:2}
@media(max-width:850px){.layout{grid-template-columns:1fr;padding:12px}aside{position:static;max-height:360px}header{padding:18px}}
</style><header><h1>GoodTurtle 联合审阅 · 2026-11-14</h1><p id="coverage"></p>
<p>主 agent + 两位 subagents 逐问 AI 审阅；不是人工 gold。保留原问题、Host 标签和原评分；疑点建议没有写回实验或 active Host。完成局按版本分层比较，技术中断不计失败；重复归档不可当独立重复。</p></header>
<div class="layout"><aside><input id="gamesearch" placeholder="搜索题号、局名…"><select id="cohort"><option value="">所有批次</option></select><div id="games"></div></aside>
<main><div class="card" id="meta"></div><div class="sticky"><nav><select id="verdict"><option value="">全部审阅</option><option value="suspect">疑似问题</option><option value="ambiguous">需裁定边界</option><option value="ok">未见明确冲突</option></select><select id="kind"><option value="">问题 + 交卷</option><option value="question">仅问题</option><option value="final">仅交卷</option></select><input id="search" placeholder="在本局问题/审核理由中搜索"><button id="prev">上一页</button><span id="page"></span><button id="next">下一页</button></nav></div><div id="turns"></div></main></div>
<script id="data" type="application/json">__DATA__</script><script>
'use strict';
const D=JSON.parse(document.getElementById('data').textContent),$=id=>document.getElementById(id);
let selected=D.games[0],page=0;const size=50;
const labels={local_cl:'本机 CL Set1',local_mas:'本机 TS038 2×2',coworkers:'组友 Set2 v17',coworker_legacy_set2:'组友 Set2 历史两轮',coworker_other:'组友 April TS038 / extra2'};
function el(tag,text,cls){const x=document.createElement(tag);if(text!==undefined)x.textContent=text;if(cls)x.className=cls;return x;}
function detail(title,content){const d=el('details');d.append(el('summary',title),el('pre',typeof content==='string'?content:JSON.stringify(content,null,2)));return d;}
function badge(s){return el('span',s,'badge');}
$('coverage').textContent=`${D.games.length} 份物理档案 · ${D.total} 次记录提交均有逐条审阅。原始数据与统计来源见同目录 global_inventory / global_dedup / global_metrics。`;
for(const [k,v] of Object.entries(labels)){const o=el('option',v);o.value=k;$('cohort').append(o);}
function renderGames(){const q=$('gamesearch').value.toLowerCase(),c=$('cohort').value;const box=$('games');box.replaceChildren();D.games.filter(g=>(!c||g.cohort===c)&&`${g.puzzle_id} ${g.game_id}`.toLowerCase().includes(q)).forEach(g=>{const b=el('button',`${labels[g.cohort]} · ${g.game_id}\n${g.status} · ${g.submissions} 次 · score=${g.score??'无最终交卷'} · 疑点 ${g.counts.suspect||0}/${g.counts.ambiguous||0}`,'game'+(g===selected?' chosen':''));b.onclick=()=>choose(g);box.append(b);});}
function choose(g,n){selected=g;page=0;$('search').value='';$('verdict').value='';$('kind').value='';history.replaceState(null,'','#'+encodeURIComponent(g.uid)+(n?'@'+n:''));renderMeta();renderGames();renderTurns();if(n)setTimeout(()=>document.getElementById('q'+n)?.scrollIntoView(),30);}
function renderMeta(){const g=selected,m=$('meta');m.replaceChildren(el('h2',g.puzzle_id+' · '+g.game_id));[labels[g.cohort],g.status,`原始末卷 ${g.score??'无'}`,`原始成功 ${g.success}`,`${g.questions} questions + ${g.finals} finals`,`审阅 ${g.submissions}/${g.submissions}`].forEach(x=>m.append(badge(x)));
if(g.notes)m.append(el('p',g.notes));m.append(el('p',g.path,'muted'),detail('汤面 / 完整汤底',g.opening+'\n\n'+g.answer),detail('冻结评分点 / 完成要求',{rubric:g.rubric,completion_requirements:g.requirements,annotation_version:g.annotation_version,grading_protocol:g.grading_protocol}),detail('冻结模型设置 / 来源哈希',{models:g.models,context_policy:g.context_policy,host_binding:g.host_binding,raw_trajectory_sha256:g.raw_trajectory_sha256,submission_events_sha256:g.submission_events_sha256,review_path:g.review_path,error:g.error,costs:g.costs}));}
function filtered(){const s=$('search').value.toLowerCase(),v=$('verdict').value,k=$('kind').value;return selected.reviews.filter(r=>(!v||r.verdict===v||r.evaluation_verdict===v)&&(!k||r.type.toLowerCase()===k)&&(!s||`${r.submission} ${r.question} ${r.reason} ${r.evaluation_reason||''} ${r.observation||''}`.toLowerCase().includes(s)));}
function renderTurns(){const rs=filtered();const pages=Math.max(1,Math.ceil(rs.length/size));page=Math.min(page,pages-1);$('page').textContent=`${page+1}/${pages} · ${rs.length} 条`;$('prev').disabled=page===0;$('next').disabled=page===pages-1;const b=$('turns');b.replaceChildren();for(const r of rs.slice(page*size,(page+1)*size)){const a=el('article',undefined,r.verdict);a.id='q'+r.submission;const title=el('h3',`#${r.submission} · ${r.type.toUpperCase()} · Host / Grader: ${r.actual_label??'尚无反馈'}`);title.style.margin='0';a.append(title,el('div',r.question,'q'),badge(r.verdict),badge('AI 审阅 · 未经人工确认'),el('p',r.reason));if(r.recommended_label&&r.recommended_label!==r.actual_label)a.append(el('p','建议供复核：'+r.recommended_label));if(r.observation)a.append(el('p','过程观察：'+r.observation));if(r.evaluation_reason)a.append(el('p','评分审阅：'+r.evaluation_reason));if(r.actual_evaluation){const e=r.actual_evaluation;a.append(badge(`原分 ${e.partial_score} / complete=${e.complete}`),detail('原始 grader 评分与证据（未改动）',e));}a.append(el('small',`来源 ${r.source_review} · confidence=${r.confidence}`,'muted'));b.append(a);}}
['search','verdict','kind'].forEach(k=>$(k).oninput=()=>{page=0;renderTurns();});['gamesearch','cohort'].forEach(k=>$(k).oninput=renderGames);$('prev').onclick=()=>{page--;renderTurns();};$('next').onclick=()=>{page++;renderTurns();};
const h=decodeURIComponent(location.hash.slice(1)),at=h.lastIndexOf('@'),uid=at>=0?h.slice(0,at):h,n=at>=0?Number(h.slice(at+1)):0;choose(D.games.find(g=>g.uid===uid)||selected);if(n){page=Math.floor((n-1)/size);renderTurns();setTimeout(()=>document.getElementById('q'+n)?.scrollIntoView(),50);}
</script></html>'''


def main():
    games = [normalize_game(*g) for g in sources()]
    all_rows = [r for g in games for r in g["reviews"]]
    with (ROOT / "all_question_reviews.jsonl").open("w") as f:
        for r in all_rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    write_csv(ROOT / "all_question_reviews.csv", all_rows)
    issues = [r for r in all_rows if r["verdict"] != "ok" or
              r.get("evaluation_verdict") in ("suspect", "ambiguous")]
    write_csv(ROOT / "review_questions_only.csv", issues)
    packed = dict(games=games, total=len(all_rows),
                  reviewer="AI review by root + two subagents; not human gold")
    data = json.dumps(packed, ensure_ascii=False).replace("<", "\\u003c").replace("&", "\\u0026")
    (ROOT / "index.html").write_text(HTML.replace("__DATA__", data))
    validation = dict(games=len(games), submissions=len(all_rows), issues=len(issues),
                      verdicts=dict(Counter(r["verdict"] for r in all_rows)),
                      full_coverage=True, original_text_and_label_match=True,
                      human_confirmed=False, originals_modified=False)
    (ROOT / "portal_validation.json").write_text(json.dumps(validation, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(validation, ensure_ascii=False))


if __name__ == "__main__":
    main()
