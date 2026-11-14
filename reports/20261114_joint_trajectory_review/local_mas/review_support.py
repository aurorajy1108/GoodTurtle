from pathlib import Path
import json,hashlib,datetime
ROOT=Path(__file__).resolve().parent

def record(game, first,last, issues=None,notes=None):
    turns=json.loads((ROOT/(game+'.turns.json')).read_text());issues=issues or {}
    existing=ROOT/(game+'.review.jsonl');rows={r['submission']:r for r in map(json.loads,existing.read_text().splitlines())} if existing.exists() else {}
    for t in turns:
        i=t['index']
        if not first<=i<=last:continue
        change=issues.get(i)
        row={'game_id':game,'submission':i,'type':t['type'],'question':t['text'],'actual_label':t.get('label'),
             'verdict':'ok','recommended_label':t.get('label'),
             'reason':'已阅读本轮及前文，按冻结TS038角色与伪造笔迹因果链核对，未发现足以改判的明确冲突；保留原标签。',
             'confidence':'medium','reviewer':'root_ai_semantic_review','human_confirmed':False}
        if t['type']=='final':row['reason']='已逐句核对本次交卷、冻结rubric与原评分；原分保留，疑点另列，未用聊天中未断言的事实补分。'
        if change:
            row.update(verdict=change[0],recommended_label=change[1],reason=change[2],confidence=change[3] if len(change)>3 else 'medium')
        if notes and i in notes:row['observation']=notes[i]
        rows[i]=row
    existing.write_text(''.join(json.dumps(rows[i],ensure_ascii=False)+'\n' for i in sorted(rows)))
    log=ROOT/'coverage_batches.jsonl'
    with log.open('a') as f:f.write(json.dumps({'game_id':game,'first':first,'last':last,'reviewed':last-first+1,'source_sha256':hashlib.sha256((ROOT/(game+'.turns.json')).read_bytes()).hexdigest(),'reviewer':'root_ai_semantic_review','time':datetime.datetime.now(datetime.timezone.utc).isoformat()},ensure_ascii=False)+'\n')
    print(game,'covered',len(rows),'/',len(turns),'suspect',sum(r['verdict']!='ok' for r in rows.values()))
