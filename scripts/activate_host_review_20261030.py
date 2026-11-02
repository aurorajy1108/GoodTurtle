#!/usr/bin/env python3
"""Apply the dated, source-backed review once; no network or experiment calls.

Refuses to overwrite subsequent work. Originals stay in audit_20261030/baseline.
The JSON activation manifest records every changed example and context hash.
"""
import copy
import json
from pathlib import Path
from scripts.audit_host_references_20261030 import ROOT, REVIEW, read, save, digest, collect, apply_decisions
from turtle_loop.host_context import build_story_context

SELECT = {
    'TS031':[1,2,4,5,7,8,9,10,18,22,27,30,31,32,35,37,44,49,51,55,61],
    'TS035':[1,5,6,7,9,10,13,18,20,23,25,29,30,34,36,39,40,44,46,48,50,55,65,81,86,94],
    'TS038':[3,4,5,6,7,10,19,21,22,23,24,27,28,29,32,34,35,36,38,39,40,41,45,46,48,52,54,57,65,67,74,86,97,99],
}
# Explicit standalone rewrites: original rows remain in the review workbook.
REWRITES = {
 'TS031':[
  (3,'Did removing the eraser provide access for adding pencil lead, rather than using the eraser as a marking tool?','yes','移除盖子是访问步骤，不是拿橡皮作为刻画工具。'),
  (11,'Did A remove the eraser because it covered the mechanical pencil\'s lead-refill opening?','yes','明确真实目的，避免只拿起整个普通铅笔的错误因果。'),
  (13,'Was this a mechanical pencil with a removable eraser covering its refill opening?','yes','消除 ordinary pencil 对木制铅笔的歧义。'),
  (16,'Was the message meant to demonstrate or reveal that the eraser had a pencil attached to it?','no','展示附带铅笔不是写留言的解释性目的。'),
  (48,'Did A insert replacement graphite lead inside the mechanical pencil and then write using that pencil?','yes','铅芯在笔内，非外置独立绘图装置。'),
  (57,'Did A use the pencil to prop up an external apparatus that held a separate piece of graphite for writing?','no','独立外部支撑装置不是汤底。'),
  (85,'Does the story require a separate guide or support apparatus in addition to the refilled mechanical pencil?','no','不将内部笔结构重新解释成第三个装置。'),
 ],
 'TS035':[
  (8,'Had bears already dug up and eaten other villagers’ buried dead before this incident?','irrelevant','此前其他墓的事件未说明。'),
  (19,'Did he fear other bears could reach the other forest graves and eat the bodies buried there?','yes','森林坟墓，不新增正式墓园。'),
  (56,'Would villagers be distressed by bears eating their dead relatives, and is it also established that bears pose absolutely no danger to living people?','yes and no','悲痛合理；绝对零风险不成立。'),
  (68,'Did the father fear other villagers’ buried relatives would also be eaten?','yes','保留核心担忧，不杜撰悲痛与遗体受损孰轻孰重。'),
  (83,'Is it established that other villagers’ buried relatives were subsequently eaten?','irrelevant','担忧不是后来事件已经发生。'),
  (91,'Did the incident reveal the risk to the father, rather than establish that this bear taught other bears to eat humans?','yes','明确认知主体，不传递给其他熊。'),
 ],
 'TS038':[
  (2,'Did the narrator himself repeatedly write the quoted sentence while trying to forge his wife’s handwriting?','yes','区分写字者、假署名者与未定收信人。'),
  (12,'Does the poor handwriting imitation risk exposing the narrator’s attempt to conceal the killing?','yes','是暴露风险，不是已经有人发现。'),
  (30,'Was the forged note intended to prove that the narrator was somewhere else when the killing happened?','no','严格不在场证明与隐瞒死亡不同。'),
  (30,'Was the forged note intended to conceal the killing by making the wife’s disappearance look voluntary?','yes','说明真正掩盖机制。'),
  (51,'Is the exact writing system or alphabet used in the forged note specified?','no','是否已说明是可判定元问题。'),
  (80,'Does the story establish a plan to send additional impersonation messages beyond the forged leaving note?','no','未建立额外通信计划；不等于断言绝不会发生。'),
  (83,'Is the forged leaving note being prepared by hand?','yes','手写已说明，实际寄出尚未说明。'),
  (83,'Was the forged note eventually sent or delivered?','irrelevant','故事停在练习伪造失败，不断言后续执行。'),
 ],
}
BOUNDARIES = {
 'TS031':[
  'Removing the eraser to refill the pencil is not holding a usable ordinary pencil by its eraser. Separate replacement lead goes INSIDE the mechanical pencil.',
  'Resolve tool/support/other object references from the question and its history. Do not silently relabel an asserted external apparatus as internal pencil parts. If genuinely ambiguous, use yes and no; reject a specified external drawing mechanism with no.',
  'A no to removing the eraser TO UNCOVER THE WRITING TIP does not deny removing it TO OPEN THE REFILL PORT. Preserve the causal predicate, not only the verb remove.',
 ],
 'TS035':[
  'Fear of other graves being eaten is established; previous other attacks, actual future attacks, coffins, grave depth and a formal cemetery are not established.',
  'Rarely attacking living people does not mean zero danger to all living people. Do not convert fear or risk into certainty.',
  'The core fear concerns bodies being eaten. Emotional distress is reasonable, but the story does not rank distress versus damage to remains as mutually exclusive chief fears. Do not arbitrarily reverse answers to paraphrases.',
 ],
 'TS038':[
  'The opening explicitly contains disappointment and never returning. This wording is supported; consult the opening as well as the short solution.',
  'The narrator writes, the wife is the forged author, and an actual later reader/recipient is unspecified. Do not infer identity or discovery from a generic mention of a recipient.',
  'Concealing death with a forged departure note is not evidence of an elsewhere-at-the-time alibi. Additional impersonation messages, delivery, discovery and future outcomes are not established.',
 ],
 'TS033':[
  'Do not affirm adding cash BECAUSE the demand exceeded one million. The specific change to the top bundles is to conceal the fake bundles during inspection; a true amount alone does not validate an incorrect causal explanation.',
 ],
}


def main():
    target=REVIEW/'activation.json'
    if target.exists(): raise SystemExit('Already activated; do not overwrite an audited revision.')
    rows,_=collect(); rows=apply_decisions(rows); by={r['case_id']:r for r in rows}
    bank={p['id']:p for p in read(ROOT/'data/annotations/turtle50_v4/private.json')['puzzles']}
    bindings=read(ROOT/'configs/host_bindings.json')
    save(REVIEW/'baseline/bindings.json',bindings)
    before={pid:build_story_context(p)['context_sha256'] for pid,p in bank.items()}
    changes=[]; versions={}; source_hashes={}
    for pid in ['TS031','TS033','TS035','TS038']:
        path=ROOT/f'data/host_packs/active/{pid}.json'
        baseline=REVIEW/f'baseline/{pid}.json'
        if path.read_bytes()!=baseline.read_bytes(): raise ValueError(f'{pid} changed since review')
        pack=read(baseline); seen={(e['question'].strip().casefold(),e['answer']) for e in pack['host_examples']}
        def add(q,a,cid,origin,reason,rewritten=False):
            if (q.strip().casefold(),a) in seen: return
            r=by[cid]
            example=dict(case_id=f'REVIEW_20261030_{pid}_{len(changes)+1:03d}',question=q,answer=a,
                         public_history=[],rationale=reason,review_status='reviewed_reference_pending_human',
                         provenance=dict(source_case=cid,source_file=r['source'],source_sha256=digest(ROOT/r['source']),
                         source_kind=origin,question_origin='reviewer_rewrite' if rewritten else 'source_verbatim',
                         answer_origin='ai_source_based_adjudication',original_question=r['question'],original_answer=r['observed'],
                         reviewer='codex_root',human_confirmed=False))
            pack['host_examples'].append(example);seen.add((q.strip().casefold(),a))
            changes.append(dict(puzzle_id=pid,case_id=example['case_id'],source_case=cid,action='add_rewrite' if rewritten else 'add_reviewed',question=q,answer=a,reason=reason,example=example))
        for n in SELECT.get(pid,[]):
            cid=f'RUN_{pid}_{n:03d}';r=by[cid]
            if r['decision']!='reviewed_no_issue_found': raise ValueError(f'Unresolved source selected: {cid}')
            add(r['question'],r['normalized'],cid,'model_generated','逐项核对汤面、汤底和问句；此问题在独立表述下可保留。')
        for n,q,a,reason in REWRITES.get(pid,[]):
            add(q,a,f'RUN_{pid}_{n:03d}','model_generated',reason,True)
        if pid=='TS033':
            e=next(e for e in pack['host_examples'] if e['case_id']=='SHARE_6adf3775_120');old=copy.deepcopy(e)
            e['answer']='no';e['rationale']=by[e['case_id']]['reason'];e['review_status']='reviewed_reference_pending_human'
            e['provenance'].update(answer_origin='ai_corrected_user_history',original_answer=old['answer'],reviewer='codex_root',human_confirmed=False)
            changes.append(dict(puzzle_id=pid,case_id=e['case_id'],source_case=e['case_id'],action='correct_label',question=e['question'],answer=e['answer'],reason=e['rationale'],before=old,example=copy.deepcopy(e)))
        pack['label_boundaries']=pack.get('label_boundaries',[])+BOUNDARIES[pid]
        pack['version']='host-v8-reviewed-20261030'
        pack['review_status']='reviewed_reference_pending_human'
        bindings[pid].update(version=pack['version'],review_status=pack['review_status'])
        save(path,pack);versions[pid]=dict(before_sha256=digest(baseline),after_sha256=digest(path))
    save(ROOT/'configs/host_bindings.json',bindings)
    after={pid:build_story_context(p)['context_sha256'] for pid,p in bank.items()}
    for p in (REVIEW/'baseline').glob('*.json'):source_hashes[str(p.relative_to(ROOT))]=digest(p)
    for r in rows:source_hashes[r['source']]=digest(ROOT/r['source'])
    save(target,dict(version='host-v8-reviewed-20261030',human_confirmed=False,changes=changes,
        packs=versions,context_sha256_before=before,context_sha256_after=after,source_sha256=source_hashes,
        note='Reviewed references; original source provenance retained. No human confirmation or live accuracy measurement claimed.'))
    print(json.dumps({'changes':len(changes),'packs':list(versions)},ensure_ascii=False))


if __name__=='__main__':main()
