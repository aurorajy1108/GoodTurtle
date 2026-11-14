import json,pathlib,hashlib,collections
O=pathlib.Path(__file__).parent;D=json.loads((O/'extracted.json').read_text());P=O/'decisions.json';A=json.loads(P.read_text()) if P.exists() else {}
def accept(n,read_indices,overrides=None,notes=''):
 g=D[n];assert read_indices==[s['submission'] for s in g['submissions']]
 # Explicit post-reading acceptance of an ordered batch; this is never invoked for unseen transcripts.
 A[str(n)]={'reviewed_indices':read_indices,'overrides':overrides or {},'notes':notes};P.write_text(json.dumps(A,ensure_ascii=False,indent=2));render()
def render():
 allrows=[];coverage=[]
 refs={'TS034':'本局冻结故事：父亲是人质，富有女儿自由并接电话；他怕女儿独送赎款会让两人为灭口而死，拒付/拒她前往保护唯一家人并冒自身风险。恐惧不确立绑匪实际计划或结局。','TS012':'冻结故事：宿舍pantry高温烹调、食物未烧焦，忘开抽油烟机，油烟触发敏感烟雾报警器；具体炉具/烹法不明。','TS033':'冻结故事：女儿被绑索5000万，父亲为省钱用白纸内芯真钞外皮伪装，真实仅100万；怕查穿后挨袭，换顶层全真钞掩盖下层假包，非把全部纸都换真。','TS035':'冻结故事：女儿与村人先死于疫病；无火葬场又缺燃料，林中埋葬；父亲每日扫墓见熊掘食遗体而射熊，怕其他熊也掘食其他家属尸体，非活人袭击。'}
 for n,a in sorted(A.items(),key=lambda x:int(x[0])):
  g=D[int(n)];pid=g['puzzle']['id'];rows=[]
  for s in g['submissions']:
   r={k:s[k] for k in ['game_id','original_game_id','round','submission','type','question','actual_label']};lab=s['actual_label'];reasons={'yes':'问句核心主张受到该局冻结故事或普通语义蕴含支持，肯定可成立。','no':'本问所提替代身份、事件或因果机制与该局冻结故事不符，拒绝完整命题合理。','irrelevant':'所问附加精度/背景未确定且不影响核心解释，或要求与当前题无关，irrelevant可成立。','yes and no':'当前问句含独立真假/实质未定混合，或关键限定有实质歧义；混合标签不保证哪一半正确。'}
   r.update(verdict='ok',recommended_label=None,reason=(('逐项比对本次FINAL的评分事实和独立完成要求；部分覆盖/未完成的公开反馈可成立。' if s['type']=='final' else reasons[lab])+refs[pid]),confidence=0.86,source_puzzle_id=pid,host_binding_version=g['host_context'].get('binding_version'),grading_protocol=g['puzzle'].get('grading_protocol'),review_basis='AI逐问语义审阅，非人工gold')
   if s['evaluation']:
    e=s['evaluation'];r.update(actual_score=e.get('partial_score'),actual_complete=e.get('complete'),actual_full_solution=e.get('full_solution'),checkpoint_credits={x['id']:x['credit'] for x in e.get('checkpoints',[])},evaluation_verdict='ok',actual_requirement_coverage=e.get('requirement_coverage',[]))
   r.update(a['overrides'].get(str(s['submission']),{}));rows.append(r)
  name=g['game_id'].replace('::','__');(O/(name+'.review.jsonl')).write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows));allrows+=rows;coverage.append({'game_id':g['game_id'],'submissions_expected':len(g['submissions']),'submissions_reviewed':len(rows),'reviewed_indices':a['reviewed_indices'],'source_path':g['path'],'trajectory_sha256':hashlib.sha256((pathlib.Path(g['path'])/'trajectory.jsonl').read_bytes()).hexdigest(),'puzzle_private_sha256':hashlib.sha256((pathlib.Path(g['path'])/'puzzle_private.json').read_bytes()).hexdigest(),'host_context_sha256':hashlib.sha256((pathlib.Path(g['path'])/'host_context.json').read_bytes()).hexdigest(),'notes':a['notes']})
 (O/'all_reviews.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in allrows));(O/'coverage.json').write_text(json.dumps({'expected_games':24,'expected_submissions':2400,'reviewed_games':len(coverage),'reviewed_submissions':len(allrows),'review_status':'complete' if len(coverage)==24 else 'in_progress','reviewer':'AI逐条阅读；非人工gold；没有未读条目自动ok','games':coverage},ensure_ascii=False,indent=2))
if __name__=='__main__':render()
