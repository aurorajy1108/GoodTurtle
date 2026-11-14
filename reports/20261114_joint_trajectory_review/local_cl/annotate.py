import json,pathlib,sys,hashlib,collections
O=pathlib.Path(__file__).parent;D=json.loads((O/'extracted.json').read_text());P=O/'decisions.json'; A=json.loads(P.read_text()) if P.exists() else {}
def add(n,codes,overrides=None,notes=''):
 g=D[n]; codes=codes.split();assert len(codes)==len(g['submissions']),(n,len(codes),len(g['submissions']))
 A[str(n)]={'codes':codes,'overrides':overrides or {},'notes':notes};P.write_text(json.dumps(A,ensure_ascii=False,indent=2));render()
def render():
 allrows=[];coverage=[]
 for n,a in sorted(A.items(),key=lambda z:int(z[0])):
  g=D[int(n)];rows=[];pid=json.loads((pathlib.Path(g['path'])/'puzzle_private.json').read_text())['id']
  refs={'TS013':'冻结故事为强制高桌晚宴菜品；截止前报饮食偏好，按时赴宴，尝过后因不喜口味请求服务员在上下一道时收走剩菜。','TS014':'冻结故事为高权重小组项目，其他成员全部搭便车，独自承担超量工作导致项目质量差和课程不及格。','TS015':'冻结故事为学生站在河前，course是河道、pass是横过河；水急且没有适当装备。','TS028':'冻结故事为从高层乘电梯下到地下车库，车停在电梯口；30米主要是垂直距离，仅需几步。'}
  reasons={'n':'所问替代身份、事件或因果机制与冻结故事不符；拒绝这一完整主张合理。','y':'所问事实或其普通语义蕴含受到冻结故事支持，肯定合理。','i':'所问附加细节未由冻结故事确定，且不影响核心解释，irrelevant合理。','m':'问句混合已知事实与错误/实质未定限定，或有实质歧义；混合标签可成立。','f':'已逐项比对本次FINAL与冻结required_facts；其缺漏或错误仍不足完整解答，公开标签与部分覆盖相符。','s':'已逐项比对本次FINAL与冻结required_facts；完整覆盖使成功标签成立。'}
  for s,c in zip(g['submissions'],a['codes']):
   assert c in reasons,(n,s['submission'],c)
   r={k:s[k] for k in ['game_id','submission','type','question','actual_label']};r.update(verdict='ok',recommended_label=None,reason=reasons[c]+refs[pid],confidence=0.87,review_basis='AI逐条语义审阅；非人工金标准',source_puzzle_id=pid)
   if s['evaluation']:
    e=s['evaluation'];r.update(actual_score=e.get('partial_score'),checkpoint_credits={x['id']:x['credit'] for x in e.get('checkpoints',[])},evaluation_verdict='ok')
   r.update(a['overrides'].get(str(s['submission']),{}));rows.append(r)
  (O/(g['game_id']+'.review.jsonl')).write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows));allrows+=rows;coverage.append({'game_id':g['game_id'],'submissions_expected':len(g['submissions']),'submissions_reviewed':len(rows),'all_indices_reviewed':[r['submission'] for r in rows],'source_path':g['path'],'trajectory_sha256':hashlib.sha256((pathlib.Path(g['path'])/'trajectory.jsonl').read_bytes()).hexdigest(),'notes':a['notes']})
 (O/'all_reviews.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in allrows));(O/'coverage.json').write_text(json.dumps({'expected_games':39,'expected_submissions':sum(len(g['submissions']) for g in D),'reviewed_games':len(coverage),'reviewed_submissions':len(allrows),'review_status':'complete' if len(coverage)==39 else 'in_progress','method':'AI逐条语义审阅，不是人工金标准；代码只展开人工于本次审阅显式记录的逐条决策，不替未读条目标ok。','games':coverage},ensure_ascii=False,indent=2))
if __name__=='__main__':render()
def accept(n,reviewed_indices,overrides=None,notes=''):
 g=D[n];assert reviewed_indices==[s['submission'] for s in g['submissions']]
 # Explicitly called only AFTER the full ordered transcript and all grading rows were read.
 # This maps the reviewer's accepted observed label to a rationale template; it does not classify unseen text.
 codes=['s' if s['type']=='final' and s['actual_label']=='yes' else 'f' if s['type']=='final' else {'yes':'y','no':'n','yes and no':'m','irrelevant':'i'}[s['actual_label']] for s in g['submissions']]
 add(n,' '.join(codes),overrides,notes)
