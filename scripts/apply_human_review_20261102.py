"""One-time human spreadsheet import plus delegated TS031–040 adjudication.

python -m scripts.apply_human_review_20261102
Inputs are versioned source rows and the immutable workbook. Does not run models.
"""
import copy
import json
import re
from scripts.audit_host_references_20261030 import ROOT, read, save, digest
from scripts.recheck_host_31_40 import issues, decisions
from turtle_loop.host_context import build_story_context

DEST=ROOT/'data/host_reference/reviews/human_20261102'
SOURCE=ROOT/'data/host_reference/sources/human_review_20261102'
VERSION='host-v9-human-20261102'

# The user explicitly delegated the remaining material ambiguities in 31–40.
# Mixed answers are reserved for a real ambiguity/mixed proposition, not a default.
AUTO={
 'RUN_TS031_003':('yes and no','橡皮参与补芯流程，但不是施加书写材料的工具；原问工具角色有重要歧义。'),
 'RUN_TS031_011':('yes and no','与铅笔相连为真；拿橡皮的关键目的是打开补芯口，不是只拿起可用的铅笔。'),
 'RUN_TS031_013':('yes and no','附带橡皮为真，ordinary pencil可指木制铅笔或普通自动铅笔；保留此身份歧义。'),
 'RUN_TS031_020':('yes','这支笔当时缺可用铅芯的状态对动作有意义；不表示罕见型号或特殊机器。'),
 'RUN_TS031_057':('yes and no','another object or part可指内部夹芯部件，也可指另一台装置；不得静默换指代。'),
 'RUN_TS031_069':('yes and no','内部夹芯结构与玩家外部支撑物假设混淆；原句重要指代未定。'),
 'RUN_TS031_077':('yes and no','可解释为内部铅芯接触纸，也可延续额外装置，不能无条件肯定后者。'),
 'RUN_TS031_079':('yes and no','铅芯施压为真，前提“间接支撑的另一个工具”不明确。'),
 'RUN_TS031_082':('yes','书写铅芯移动并接触纸；以明确改写采纳人工yes，不肯定外置支架。'),
 'RUN_TS031_083':('yes and no','若tool指铅芯，摩擦纸成立；若指先前假设的另一装置，其存在不成立。'),
 'RUN_TS031_084':('yes and no','是铅芯材料，但不是游离于笔外、由额外装置支撑的书写工具。'),
 'RUN_TS031_085':('yes and no','可指笔内夹芯结构，也可指错误的外置导向器，不能确认额外装置。'),
 'RUN_TS031_095':('yes and no','object无确定指代；笔内结构存在接触，先前外置支撑物并不存在。'),
 'NEW026':('yes','intentionally修饰A做的举报行为，不是其导致转学的后果；举报是主动的。'),
 'NEW034':('no','问题提出无法承受知晓谋杀的负罪感作为离开原因；标准是认出A后羞耻并怕被拒绝。'),
 'NEW013':('no','purchase按物品购买读；不把支付赎金隐喻成在购买某物。'),
 'NEW014':('no','同上，赎金而非伪装成商品采购款。'),
 'NEW016':('no','amount of money按实际真钱总额读；未补足全额，只有外观伪装全额。'),
 'NEW018':('no','精确点钞发现只有一百万不是换顶层真钞能解决的机制；主因是粗查发现假包。'),
 'NEW023':('yes and no','交付前加钱、原有一百万为真；若将问题归为数额不足而非假包暴露，则因果不完整。'),
 'NEW022':('yes and no','绑架促使备款为真，但照片视频等证据交付未说明；明确保留未定细节。'),
 'NEW038':('yes and no','同一绑架电话事件为真；绑匪声音对父亲是现场，对女儿来自电话，原句缺听者。'),
 'NEW040':('yes and no','要求独自赴约为真；排除所有远程或隐蔽警方保护未说明。'),
 'RUN_TS035_060':('yes and no','相同悲痛成立，但rather than harm to bodies否定/弱化了核心遗体遭吃风险。'),
 'RUN_TS035_068':('yes','家属因发现遗体被吃而悲痛是核心担忧的合理概括，未明确否认遗体风险。'),
 'RUN_TS035_070':('yes','与Q68同义采用同一口径，不要求逐字复述汤底。'),
 'RUN_TS035_071':('yes and no','怕遗体被吃成立；把此与家属悲痛排为互斥主次无依据。'),
 'RUN_TS035_083':('yes and no','父亲预期有风险，但rather than merely possible要求更强主观确信，来源未给。'),
 'RUN_TS035_091':('yes and no','事件向父亲揭示风险为真；向其他熊传播食物信息未建立。'),
 'RUN_TS038_001':('yes and no','可读的练字文字为真，但听到/读到作为重复句出现的解释不同于自己反复书写。'),
 'RUN_TS038_002':('yes','自己写下并检查字迹的文字可供自己看，普通蕴含；不暗示另一个写字者。'),
 'RUN_TS038_016':('yes and no','字迹可暴露伪造与杀人是风险；直接陈述已经向特定收信人揭露不成立/未说明。'),
 'RUN_TS038_030':('no','alibi采用严格案发不在场证明；本题仅伪造妻子主动离家。'),
 'NEW044':('yes and no','4–6对应被跳过月份为真；主要动机是提前过7月生日，不能把它们当死亡月份编码。'),
}


def main():
    manifest=DEST/'manifest.json'
    if manifest.exists():raise SystemExit('Already applied. Create a new review version instead.')
    allissues={r['case_id']:r for r in issues()}
    pending=decisions()[1]
    assert set(AUTO)==set(pending)
    rows=read(SOURCE/'rows.json'); bank={p['id']:p for p in read(ROOT/'data/annotations/turtle50_v4/private.json')['puzzles']}
    bindings=read(ROOT/'configs/host_bindings.json');before={p:build_story_context(v)['context_sha256'] for p,v in bank.items()}
    save(DEST/'baseline/bindings.json',bindings)
    packs={};changes=[];records=[]
    def pack(pid):
        if pid not in packs:
            packs[pid]=read(ROOT/f'data/host_packs/active/{pid}.json');save(DEST/f'baseline/{pid}.json',packs[pid])
        return packs[pid]
    def adopt(cid,answer,reason,human=False,row=None,question=None,history=None):
        r=allissues[cid];p=pack(r['puzzle_id']);q=question or re.sub(r'^\*\*Question\s+\d+[^:]*:\*\*\s*','',r['question'])
        history=history or []
        key=(q.strip().casefold(),json.dumps(history,sort_keys=True))
        matches=[e for e in p['host_examples'] if (e['question'].strip().casefold(),json.dumps(e.get('public_history',[]),sort_keys=True))==key]
        e=dict(case_id='HUMAN_20261102_'+cid if human else 'ADJ_20261102_'+cid,question=q,answer=answer,
          public_history=history,rationale=reason,review_status='human_confirmed_label' if human else 'delegated_adjudication',
          provenance=dict(source_case=r.get('source_case',cid),audit_case=cid,answer_origin='human_spreadsheet' if human else 'ai_delegated_adjudication',
          source_kind=r['origin'],source_file=str((SOURCE/'review.xlsx').relative_to(ROOT)),source_sha256=digest(SOURCE/'review.xlsx'),
          workbook_row=row,human_confirmed=human,original_question=r['question'],original_answer=r['observed'],
          question_origin='reviewer_rewrite' if question else 'source_question',reviewer='human_spreadsheet' if human else 'codex_root'))
        for old in matches:p['host_examples'].remove(old)
        p['host_examples'].append(e);changes.append(dict(puzzle_id=r['puzzle_id'],audit_case=cid,example=e,replaced=matches))
    # Exact manual cell interpretation for combined rows; no LLM parsing in import.
    note_labels={'INBOX_TS019_003':'irrelevant','INBOX_TS019_006':'yes and no','INBOX_TS019_007':'yes and no',
                 'INBOX_TS042_012':'yes and no','INBOX_TS042_016':'yes and no','INBOX_TS042_018':'no'}
    source_rows={}
    for row in rows:
        for cid in row['cases']:
            if cid not in allissues:raise ValueError('Unknown case '+cid)
            if allissues[cid]['puzzle_id']!=row['puzzle_id']:raise ValueError('Puzzle mismatch')
            if cid in source_rows:raise ValueError('Duplicate workbook case '+cid)
            source_rows[cid]=row
            if cid in AUTO:continue
            state=row['decision'];answer=row['label'];note=row['note'] or ''
            if state=='暂缓':
                records.append(dict(case_id=cid,row=row['row'],status='human_deferred',proposed_label=answer,note=note));continue
            if cid in note_labels:answer=note_labels[cid]
            if answer in {'yes','no','yes and no','irrelevant'}:
                adopt(cid,answer,note or '按人工标签列应用；“非问题”不当作删除问句的指令。',True,row['row'])
                records.append(dict(case_id=cid,row=row['row'],status='human_label_applied',label=answer,note=note));continue
            # Non-issue is an acceptance of the source label, not a request to erase a question.
            if state=='非问题':
                raw=allissues[cid]['observed'].lower().replace('&','and')
                if raw in {'yes','no','yes and no','irrelevant'}:
                    # This note specifies ONLY the first question; do not apply it to its neighbour.
                    if row['row']==79 and cid=='INBOX_TS042_013':
                        records.append(dict(case_id=cid,row=row['row'],status='unlabelled_sibling',note='备注只指定Q12，Q13未给裁决'));continue
                    adopt(cid,raw,'人工标为非问题，保留原标签。'+note,True,row['row'])
                    records.append(dict(case_id=cid,row=row['row'],status='human_accepts_original',label=raw,note=note));continue
            records.append(dict(case_id=cid,row=row['row'],status='not_decided',note=note))
    for cid,(answer,reason) in AUTO.items():
        row=source_rows.get(cid);q=None;history=None
        if cid=='RUN_TS031_082':q='Did A move the refilled mechanical pencil’s graphite tip across the paper while pressing it to write?'
        if cid=='NEW038':
            reason+=' 原人工曾更正Q6=yes；这里裁定含混原句，原更正仍保留，不冒称人工确认新标签。'
        adopt(cid,answer,reason,False,row['row'] if row else None,q,history)
        records.append(dict(case_id=cid,row=row['row'] if row else None,status='delegated_resolved',label=answer,note=reason))
    # Author-supplied expansions: stay in the current private Host solution, not the public opening or required scoring rubric.
    expansions={
      'TS007':('In the human-reviewed version, the young tiger is larger than a human. The visitor voluntarily exits despite rules requiring visitors to remain in vehicles.','Human workbook row 19'),
      'TS012':('Here hall means a residential hall and pantry means its small shared kitchen plus food storage. The narrator enters before starting to cook, rather than fetching an ingredient from another room. The pan is initially empty before oil and food are added. Both the smoke detector and alarm are inside the pantry.','Human workbook rows 22–29'),
      'TS013':('The narrator successfully booked the dinner choices and received confirmation of that dinner allocation; this is not academic enrolment. Dishes are served as individual portions. The narrator tastes each dish before asking for the disliked leftovers to be removed, and does not leave before all courses are served. Removed dishes do not reappear.','Human workbook rows 30–34'),
      'TS021':('The researchers led her to believe the basement was the whole world accessible to her. Opening the door is her first view of the normal outside world.','Human workbook rows 51–52'),
      'TS022':('In this human-reviewed version the window is uncovered, without curtains obscuring the watcher.','Human workbook row 55'),
    }
    for pid,(text,src) in expansions.items():
        p=pack(pid);p['solution']+='\n\n'+text;p.setdefault('canonical_facts',[]).append(text)
        p.setdefault('fact_provenance',[]).append(dict(text=text,source=src,workbook_sha256=digest(SOURCE/'review.xlsx'),human_supplied=True))
    p=pack('TS012');p['unknown_details']=[s.replace('detector position and ','') for s in p['unknown_details']]
    # Existing paraphrases must agree with new authored hall/kitchen facts.
    for cid in ['AUDIT_038','AUDIT_044','AUDIT_055']:
        e=next(e for e in p['host_examples'] if e['case_id']==cid);old=copy.deepcopy(e)
        e.update(answer='yes',rationale='人工说明hall是宿舍，pantry是共享小厨房；此前未定状态已被作者补全。',review_status='human_fact_based_repair')
        e['provenance'].update(answer_origin='ai_application_of_human_fact',human_confirmed=False,workbook_rows=[22,24],original_answer=old['answer'])
        changes.append(dict(puzzle_id='TS012',audit_case='human_hall_definition',example=copy.deepcopy(e),replaced=[old]))
    # Keep known contradictory/raw branches out; human example labels may be local conventions.
    for pid in ['TS002','TS042']:
        pack(pid).setdefault('label_boundaries',[]).append('For the exact human_spreadsheet examples, use the reviewed label as this puzzle’s local convention. A yes and no label does NOT establish the false subtype (arm, skin covering, fan or hammer). Do not promote it into canonical facts. For other questions follow the ordinary causal/identity rules.')
    pack('TS035').setdefault('label_boundaries',[]).append('Broad grief at finding eaten relatives is an acceptable paraphrase of the concern. Only an explicit exclusion/ranking of grief versus body damage is undetermined; match Q68 and Q70 consistently as yes.')
    pack('TS033').setdefault('label_boundaries',[]).append('Unqualified amount means genuine cash, not nominal face value. Purchase means an ordinary acquisition of an item, not an unannounced metaphor for ransom.')
    pack('TS038').setdefault('label_boundaries',[]).append('Use alibi in its strict elsewhere-at-the-time sense unless the player explicitly defines it as cover story. Material ambiguity in reading/revealing must not assert a new writer or a discovery event.')
    for pid,p in packs.items():
        p['version']=VERSION;p['review_status']='human_labels_and_delegated_adjudication'
        save(ROOT/f'data/host_packs/active/{pid}.json',p);bindings[pid].update(version=VERSION,review_status=p['review_status'])
    save(ROOT/'configs/host_bindings.json',bindings)
    after={p:build_story_context(v)['context_sha256'] for p,v in bank.items()}
    save(manifest,dict(version=VERSION,source_workbook=str((SOURCE/'review.xlsx').relative_to(ROOT)),source_sha256=digest(SOURCE/'review.xlsx'),
        records=records,changes=changes,packs=sorted(packs),context_sha256_before=before,context_sha256_after=after,
        delegated_cases=sorted(AUTO),notes=['Blank and deferred cells are not human gold.','Human annotations override exact reference examples; no public story/rubric silently edited.','Question absent from edited sheet (RUN_TS031_083) adjudicated from preserved source under explicit 31–40 delegation.']))
    from collections import Counter
    print(json.dumps(dict(changes=len(changes),statuses=Counter(x['status'] for x in records),packs=sorted(packs)),ensure_ascii=False))


if __name__=='__main__':main()
