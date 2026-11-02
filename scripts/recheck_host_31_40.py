#!/usr/bin/env python3
"""Apply the 2026-10-31 source-based second review and export only human decisions.

Usage: python -m scripts.recheck_host_31_40 --apply --out NEW.xlsx
Subsequent exports omit --apply. Existing workbooks and review versions are protected.
Requires openpyxl. Original audits, source answers and run snapshots are immutable.
"""
import argparse
import collections
import copy
import hashlib
import json
import re
from pathlib import Path
from scripts.audit_host_references_20261030 import ROOT, read, save, digest
from turtle_loop.host_context import build_story_context

OUTDIR=ROOT/'data/host_reference/reviews/recheck_20261031'
MANIFEST=OUTDIR/'resolution.json'
VERSION='host-v8.1-reviewed-20261031'
HUMAN_SCOPE={f'TS{n:03d}' for n in [2,7,12,13,14,15,16,19,21,22,26,28,31,32,33,34,35,38,42,45,46,47]}
GROUPS={1:[13,14,15,16,28],2:[34,35,33,12],3:[22,47,45,19],4:[7,26,21,31],5:[38,46,32,45,28]}
OWNERS={2:'Kelly',14:'Amy',22:'April',38:'Aurora',42:'Shirley'}
# These are explicit controls, revealed answers or requests to reformulate, not
# uncertain four-label judgments. All remain inert source evidence in the inbox.
PROTOCOL_CLOSED={'INBOX_TS002_084','INBOX_TS007_032','INBOX_TS012_036','INBOX_TS012_046','INBOX_TS042_077',
                 'INBOX_TS022_037','INBOX_TS026_014'}  # self-reported question counts are not used as metrics


def issues():
    rows=[copy.deepcopy(r) for r in read(ROOT/'data/host_reference/reviews/audit_20261030/review.json')['rows'] if r['decision']=='needs_review']
    for r in read(ROOT/'data/host_reference/reviews/chatgpt_share_issues_20261026.json')['issues']:
        rows.append(dict(case_id=r['issue_id'],source_case=r['case_id'],puzzle_id=r['puzzle_id'],
            question=r['question'],observed=r['observed'],reason=r['analysis'],suggestion=r['recommendation'],
            proposed_label='',severity=r['priority'],source=r['source_url'],active_action='not_imported',origin='user_supplied_history'))
    return rows


def decisions():
    resolved={};pending={}
    def done(cid,label,why,question=None,history=None):
        resolved[cid]=dict(label=label,reason=why,question=question,public_history=history or [])
    def hold(ids,topic,why,choice):
        for cid in ids:pending[cid]=dict(topic=topic,reason=why,human_question=choice)
    def ids(pid,ns):return [f'RUN_{pid}_{n:03d}' for n in ns]
    done('SHARE_6adf3775_120','no','上轮已将错误因果改为 no；核实当前实际加载的标签，不再列为待办。')
    for n,why in [(6,'宽泛地使用橡皮和铅笔完成写字流程成立；没有断言橡皮直接画字。'),(15,'需要用铅芯写留言这一宽泛目的成立，不表示铅芯起初可用。'),(48,'替换铅芯本来是独立补充材料，装入笔内后由笔夹持；问句没有说外置装置。')]:done(f'RUN_TS031_{n:03d}','yes',why)
    done('RUN_TS031_016','no','展示橡皮附有铅笔不是写留言的解释；当前已有该 no 示例。')
    hold(ids('TS031',[3,11]),'橡皮是被拆下的盖，还是被当作工具？','同一个 use/pick up 既可泛指补铅芯流程，也可指直接操作写字；两种读法标签不同。','若泛指拆橡皮后补芯写字：yes；若指橡皮作为写字工具或只拿起一支可用铅笔：no。原问 intended meaning 选哪种？')
    hold(ids('TS031',[13,20]),'ordinary／unusual 的比较对象','自动铅笔是普通文具，但不是木制铅笔；unusual 没有给比较基准。','ordinary pencil 是否专指木制铅笔？unusual 是否只指这支笔需要补芯？请定统一释义，或允许混合标签。')
    hold(ids('TS031',[57,69,77,79,82,83,84,85,95]),'后半段的 tool／support 指什么？','玩家逐步假设外置支撑装置；汤底只有笔内铅芯。部分问句又能被读成内部结构，原 yes/no 无法固定指代。','把 object/tool 固定为玩家提出的额外装置（相关机制 no），还是允许改指内部铅芯（某些问句 yes）？建议固定前者；请确认这个语境边界。')
    done('RUN_TS035_008','irrelevant','此前其他坟墓是否遭袭未说明；当前已有正确示例。')
    done('RUN_TS035_019','yes and no','担忧其他坟墓被吃成立；正式 village cemetery 的限定未说明。该词不允许扩写为设有正式墓园。')
    done('RUN_TS035_054','yes','问家属因发现遗体遭吃而悲痛，是合理普通含义；未断言熊对所有活人绝无危险。')
    done('RUN_TS035_056','yes and no','悲痛成立，但绝对零危险强于题面的 rarely；保留两分句的差别。')
    hold(ids('TS035',[60,68,70,71]),'是否区分“怕尸体被吃”和“怕家属悲痛”？','汤底确定前者，并合理蕴含后者；没有规定 chiefly 的心理优先级。Q68=yes 与 Q70=no 近义冲突。','两种说法都视为可接受概括，还是必须严格回答尸体受损才是首要担忧？请先定口径，再统一这些标签。')
    hold(ids('TS035',[83]),'expect 是担心可能，还是认定会发生？','担忧风险明确；主观概率和确信程度没有明说。expect 不一定等于 certainty，不能机械改成 no。','这里 expect 是否允许表达“担心会发生”（可 yes），还是要求比可能性更强的预期（未定）？')
    hold(ids('TS035',[91]),'风险揭示给父亲，还是食物信息揭示给其他熊？','revealed ... to bears generally 的修饰范围不清；两种读法给出不同因果。','若仅指父亲意识到尸体可被熊吃：yes；若指该熊使其他熊知道食物：no。原问采取哪一种？')
    hold(ids('TS038',[1,2,16]),'写字、读字和暴露秘密是否被混为一谈？','来源确定反复练字伪造及担心暴露；没有实际阅读或已向收信人揭密的事件。原问可描述文本内容，也可描述已发生事件。','reading/reveals 是“文字可供看出问题”，还是“已经有人读到/秘密已曝光”？后者未说明。请确认再标。')
    done('RUN_TS038_009','yes','反复练习伪造的句子可称尚未交付的草稿；不据此推断未来一定寄出。')
    done('RUN_TS038_012','yes','worried because 描述怕草稿暴露秘密，符合伪造失败风险；不推导已经有人看到。')
    done('RUN_TS038_014','no','妻子是被冒名的作者；给他人看的妻子离家字条不是伪称由收信人本人写的信。')
    done('RUN_TS038_018','no','隐瞒的是杀妻，妻子是伪造署名者而非欺骗的收信人；不需要猜收信人的具体身份。')
    hold(ids('TS038',[30]),'alibi 是严格不在场证明还是泛指掩饰？','严格 alibi 要证明案发时人在别处；本题仅用假离家字条掩盖死亡。口语可能混用。','采用严格定义则 no；泛指 cover story 则 yes。建议严格定义，是否同意？')
    for n in [47,49,51]:done(f'RUN_TS038_{n:03d}','irrelevant','汤底没有规定具体暴露渠道、左右手或字母系统；这些是未定细节，不是已经被否定的事实。')
    d=read(ROOT/'data/host_reference/sources/model_simulated_20261030/TS038.json')['actions']
    history=[dict(question=x['text'],answer=x['feedback']) for x in d if 74<=x['index']<=79 and x['type']=='question']
    done('RUN_TS038_080','irrelevant','紧接 Q74–79 的“字条之外的冒名通信”追问，额外通信计划未说明；携带原局部语境，不作脱离上下文的标签。',history=history)
    done('RUN_TS038_083','irrelevant','will send 问实际未来寄出；写过草稿不确定将来交付，手写这个已知属性不让寄出成为事实。')
    for n in [88,94]:done(f'RUN_TS038_{n:03d}','yes and no','假离家字条掩盖死亡成立，额外后续消息不确定；混合标签不表示确认消息存在。',history=history)
    # Older shared conversations, independently adjudicated against the current story.
    for n in [1,2,3,4,5,6]:done(f'NEW{n:03d}','no','遗体用于解剖教学不等于学生入学、受雇工作或作为在职试验对象。拒绝这个身份/因果前提。')
    done('NEW007','irrelevant','汤底没有额外研究试验或身体改造细节；缺失细节不构成一次已确认试验。',question='Does the story specify any alteration of the boy’s body in a research experiment, beyond its use as an anatomy-class cadaver?')
    # The rewrite is an evidence question: not specified => no, not irrelevant.
    resolved['NEW007']['label']='no'
    done('NEW008','yes','遗体在女孩认出时已死；去掉不存在的 research role 前提。',question='Was the boy already dead when the girl recognized him as the anatomy-class cadaver?')
    done('NEW009','irrelevant','遗体进入课堂的捐献手续/途径未说明；不能由使用目的推断 donation。',question='Was donation the route by which the boy’s body reached the university?')
    for n in [10,11]:done(f'NEW{n:03d}','irrelevant','个人捐献安排、求死动机及具体死因均未说明；不是题目必须还原的事实。')
    done('NEW012','yes','换顶层真钞的目的是让表面检查不易发现假包；并非只追求提高真钱金额。')
    hold(['NEW013','NEW014'],'赎金能否称为 purchase？','支付赎金是交易，但普通商品购买和比喻“买自由”不是同一命题。','purchase 允许比喻买回自由（yes），还是按买商品解释（no）？请统一这两问口径。')
    done('NEW015','no','没有按某个商品已知价格购买的解释。')
    hold(['NEW016'],'amount 指实际真钱还是外观名义金额？','包看似全额赎金，但实际真钱没有补足全额。','实际真钱总额：no；只指外观看起来足额：yes。请确认玩家问句指哪一种。')
    done('NEW017','yes and no','需求大于一百万为真，增加到全部实额赎金为假。')
    hold(['NEW018','NEW023'],'粗查假包还是清点实额？','真钞替换用于掩盖假包；问句把“金额不足被发现”与“造假被发现”混在一起。','是否允许将 count/金额不足解释为泛指检查造假？若要求清点实额/补足全额，此解释应拒绝。')
    done('NEW019',None,'原记录已是 final_submission、no 且不进入 Host 示例；模型自评分/问数不用于实验指标。关闭记录问题，保留原文。')
    done('NEW020','no','这不是保护女儿免遭嫌穷杀害的既定原因；来源是怕发现假包后攻击自己。')
    done('NEW021','no','特定一百万来自父亲省钱做假包，不是绑匪给出的金额指令。')
    hold(['NEW022'],'照片／视频是随口举例还是必须确认的事件？','为绑架准备赎金成立，证明人质的照片视频未说明；括号又声明只问宏观准备。','按括号主旨回答 yes，还是对未定照片视频也判混合？请确认包含 e.g. 的问句口径。')
    done('NEW024','no','最初只装一百万不是偶然；“不恰好足额就杀孩子”的解释也未建立。')
    done('NEW025','no','被绑的孩子不是把一百万放进包的行动者，具体造假由父亲选择。')
    hold(['NEW026'],'故意举报，还是故意让 B 转学？','A主动举报，但导致B转学不等于A举报的目的。','intentionally 修饰举报行为：yes；修饰让B转学这个目的：no。原问用哪个范围？')
    done('NEW027','yes and no','父母犯罪成立；被欺凌/孤立未说明。保留混合标签，并禁止把未知部分当线索。')
    done('NEW028','no','不知举报者身份是知识状态，不等于相爱的原因；不能代替 genuine love 的叙事。')
    done('NEW029','yes','B主动离开并留下离婚文件，广义离开A/结束婚姻成立；不推导A曾施暴。')
    done('NEW030','yes','B害怕父母犯罪被A知晓后遭拒绝，宽泛 hide something 可以概括；不要因为A其实已知就否定B的主观动机。')
    done('NEW031','no','不猜 mo 是什么；按汤底独立重标：B的离开不是奉别人命令。原 mo 不改写。')
    done('NEW032','irrelevant','all along 的起点和持续知情时间未说明；已知B后来知道父母犯罪不补出这段时间。',question='Had B known about the parent’s murder from the moment it happened?')
    done('NEW033','irrelevant','B是否在场目击是未说明的获知方式；原 irrelevant 可保留。')
    hold(['NEW034'],'guilt 是否可以概括羞耻与怕拒绝？','来源强调认出A后的羞耻和怕被拒绝，不是B参与犯罪；guilt 可有宽泛心理含义。','允许作为负担/羞耻的概括（yes），还是严格读为犯罪知情负罪感这一替代动机（no）？')
    done('NEW035','yes','宽泛逃避秘密带来的婚姻后果符合怕被拒绝而离开；不把 consequences 偷换为法律制裁。')
    done('NEW036','yes and no','独立重标而非猜原 typo：主动离家为真，原因与秘密无关为假。')
    done('NEW037','yes','父亲确实担心女儿来交赎金后遇害；原问没限定当前正被挟持。')
    hold(['NEW038'],'同一通电话：谁的听觉视角？','人类后来已把 Q6 改为 yes，但父亲现场听与女儿电话听不是同一声音来源。纠错已正确挂到Q6。','请确认该问默认听者是父亲、女儿还是通话整体；再决定原句是否作为无条件参考。')
    done('NEW039',None,'导入器已把此回复标为 correction_not_feedback，label_observed=null，并挂到Q6；无需人工重新修一次。')
    hold(['NEW040'],'come alone 是否等于无任何警方保护？','独自赴约明确；便衣、远程保护等未说明。这个修饰也可只指不带警察到场。','若只是独自到场：yes；若指任何形式警方保护都没有：混合或未定。请确认 without police protection 的范围。')
    done('NEW041',None,'当前 rubric 明确要求富有、唯一亲人及双方灭口风险；历史 yes 仅记录核心接受，已作为 final_submission 排除于普通问答示例，不映射严格成功。')
    done('NEW042','no','不是按剩余天数倒数；月份由3月跳到生日7月。')
    done('NEW043','no','跳数是提前陪孩子庆生的善意谎言，不是通过数字改变肉体寿命。')
    hold(['NEW044'],'跳过4–6月的动机应怎样表述？','这段时间预计母亲已不在与提前庆生有关，但不是人为把死亡月份编码进去。','是否接受“跳过预计无法陪伴的月份”作为生日提前的概括（yes），还是要求明确“为了过7月生日”，原句视作错误因果（no）？')
    return resolved,pending


def apply(rows,resolved,pending):
    if MANIFEST.exists():raise SystemExit('Review version already applied; export without --apply.')
    bank={p['id']:p for p in read(ROOT/'data/annotations/turtle50_v4/private.json')['puzzles']}
    bindings=read(ROOT/'configs/host_bindings.json');before={p:build_story_context(v)['context_sha256'] for p,v in bank.items()}
    save(OUTDIR/'baseline/bindings.json',bindings)
    packs={};changes=[];dispositions=[]
    rowsby={r['case_id']:r for r in rows}
    for cid,d in resolved.items():
        r=rowsby[cid];pid=r['puzzle_id']
        if d['label'] is None:
            dispositions.append(dict(case_id=cid,status='resolved_existing_pipeline',reason=d['reason']));continue
        if pid not in packs:
            path=ROOT/f'data/host_packs/active/{pid}.json';packs[pid]=read(path);save(OUTDIR/f'baseline/{pid}.json',packs[pid])
        pack=packs[pid]
        q=d['question'] or re.sub(r'^\*\*Question\s+\d+[^:]*:\*\*\s*','',r['question'])
        # Q11 contains a speculative preamble; take only its actual question.
        if cid=='NEW011':q=r['question'].split('**Question 28:**',1)[-1].strip()
        key=(q.strip().casefold(),json.dumps(d['public_history'],sort_keys=True))
        matches=[e for e in pack['host_examples'] if (e['question'].strip().casefold(),json.dumps(e.get('public_history',[]),sort_keys=True))==key]
        if matches and all(e['answer']==d['label'] for e in matches):
            dispositions.append(dict(case_id=cid,status='resolved_already_active',active_case_id=matches[0]['case_id'],reason=d['reason']));continue
        example=dict(case_id='RECHECK_20261031_'+cid,question=q,answer=d['label'],public_history=d['public_history'],
            rationale=d['reason'],review_status='reviewed_reference_pending_human',provenance=dict(
            source_case=r.get('source_case',cid),audit_case=cid,source=r['source'],source_kind=r['origin'],
            answer_origin='ai_source_based_adjudication',original_question=r['question'],original_answer=r['observed'],
            question_origin='reviewer_rewrite' if q!=r['question'] else 'source_verbatim',reviewer='codex_root',human_confirmed=False))
        for e in matches:pack['host_examples'].remove(e)
        pack['host_examples'].append(example)
        changes.append(dict(puzzle_id=pid,source_case=cid,example=example,replaced=matches))
        dispositions.append(dict(case_id=cid,status='resolved_applied',active_case_id=example['case_id'],reason=d['reason']))
    boundaries={
      'TS031':'Use together can describe the overall remove/refill/write process without asserting that the eraser marks the paper. Separate replacement lead can be inserted inside the pencil; separate alone does not entail an external machine.',
      'TS032':'Separate intentional reporting from intent to make B transfer. B leaves and leaves divorce papers; broadly hiding the family secret or escaping its feared relationship consequences can describe B’s motive even though A already knows. Unknown witness status and when B first learned the crime are not additional facts.',
      'TS033':'Ransom demand, nominal appearance and genuine cash total are different. Extra genuine top bundles camouflage paper bundles; they do not fill the bag with the full genuine ransom. The child did not place the cash; saving money was a deliberate choice.',
      'TS034':'An unqualified question about the father fearing danger to his daughter includes his feared future ransom meeting, not only present hostage status. Historical acceptance of a core reconstruction does not override current full-story completion requirements.',
      'TS035':'Distress at a relative’s remains being eaten is an ordinary implication and may be affirmed broadly. Do not infer absolute safety of the living or a specified ranking of grief versus harm to remains. A formal cemetery is not specified by forest graves.',
      'TS037':'Skipping 4/5/6 represents bringing July’s birthday after March, not a countdown of days to death or a way to prolong physical life.',
      'TS038':'The wife is the forged author, not the intended reader being deceived. Worry about revelation does not assert actual discovery. Handedness and alphabet causing imitation difficulty are unspecified. Contextual questions about ADDITIONAL messages beyond the note are irrelevant; do not affirm delivery from handwritten drafts.',
      'TS039':'A cadaver at anatomy class is neither an admitted student nor an employee/test-subject job. Donation route, voluntary arrangements and suicide are unspecified; do not add them. At recognition the boy is already dead, irrespective of imprecise player wording about his role.',
    }
    for pid,p in packs.items():
        p['version']=VERSION;p['review_status']='reviewed_reference_pending_human'
        p.setdefault('label_boundaries',[]).append(boundaries[pid])
        save(ROOT/f'data/host_packs/active/{pid}.json',p);bindings[pid].update(version=VERSION,review_status=p['review_status'])
    save(ROOT/'configs/host_bindings.json',bindings)
    after={p:build_story_context(v)['context_sha256'] for p,v in bank.items()}
    source_paths=['data/host_reference/reviews/audit_20261030/review.json','data/host_reference/reviews/chatgpt_share_issues_20261026.json',
                  'data/host_reference/sources/chatgpt_shares_20261026/qa_pairs.json']
    save(MANIFEST,dict(version=VERSION,date='2026-10-31',human_confirmed=False,changes=changes,dispositions=dispositions,
        pending=pending,reviewed_puzzle_ids=[f'TS{n:03d}' for n in range(31,41)],
        no_previous_flagged_cases=['TS036','TS040'],source_sha256={p:digest(ROOT/p) for p in source_paths},
        context_sha256_before=before,context_sha256_after=after,packs=list(packs),
        unresolved_original_cases=len(pending),resolved_original_cases=len(resolved)))


def human_rows(rows,pending,resolved):
    groups=collections.OrderedDict()
    for r in rows:
        cid=r['case_id']
        if cid in resolved or r['puzzle_id'] not in HUMAN_SCOPE or cid in PROTOCOL_CLOSED:continue
        d=pending.get(cid)
        if d:
            topic,reason,question=d['topic'],d['reason'],d['human_question']
        else:
            topic='原答与当前故事／规则的适用性'
            reason=r['reason']
            question=('建议标签：'+r['proposed_label']+'。请确认这是否符合你提供的本题版本；若有额外设定，请写出。' if r.get('proposed_label') else
                '请确认原问中哪些断言是你的题目明确设定的，哪些只是猜测；填入认可的四类标签。')
            if '不是当前四种标签' in reason:
                topic='原记录缺少合法标签';question='请确认该回复是跳过／结束／揭晓，还是确实要给当前问题一个标签；若是后者，请补标签。'
        key=(r['puzzle_id'],topic,reason,question)
        groups.setdefault(key,[]).append(r)
    out=[]
    for (pid,topic,reason,question),rs in sorted(groups.items(),key=lambda x:(int(x[0][0][2:]),x[0][1])):
        # Small groups keep every original Q/A readable within Excel row-height limits.
        for start in range(0,len(rs),2):
            part=rs[start:start+2]
            out.append(dict(puzzle_id=pid,topic=topic,reason=reason,human_question=question,cases=part))
    return out


def export(path,rows,pending,resolved):
    from openpyxl import Workbook,load_workbook
    from openpyxl.comments import Comment
    from scripts.export_host_review import add_sheet
    if path.exists():raise SystemExit('Refusing to overwrite filled review workbook. Choose a new --out.')
    bank={p['id']:p for p in read(ROOT/'data/annotations/turtle50_v4/private.json')['puzzles']}
    cases=human_rows(rows,pending,resolved)
    wb=Workbook();wb.remove(wb.active)
    content=[]
    for g in cases:
        pid=g['puzzle_id'];pack=read(ROOT/f'data/host_packs/active/{pid}.json')
        qa='\n\n'.join(f"[{r['case_id']}]\nQ: {r['question']}\nHost: {r['observed']}" for r in g['cases'])
        number=int(pid[2:]);assignment=' / '.join([f'Set {n}' for n,ids in GROUPS.items() if number in ids]+([OWNERS[number]] if number in OWNERS else []))
        content.append([number,assignment,g['topic'],qa,g['reason'],g['human_question'],'','','',bank[pid]['opening'],pack['solution'],
            '\n'.join(r['case_id']+' → '+r['source'] for r in g['cases'])])
    ws=add_sheet(wb,'待人工确认',['题号','所属组／复核人','需要决定的事项','可疑原问答（原文未改）','为什么还不能确定','具体请你确认什么','人工决定','人工标签','人工备注／补充设定','汤面','当前完整汤底','来源定位'],content,[9,24,32,90,58,70,16,18,45,75,100,65])
    ws.freeze_panes='C2';ws.sheet_view.zoomScale=80
    ws['C1'].comment=Comment('只含用户指定22题范围内尚需人工决定的条目。31–40已逐项复核，可确定项已应用或确认既有处理并移出本清单；原审核历史保留。其他题保留待人工复核项。同类至多两条原问答合并为一行。没有疑点行不等于所有模型轨迹都已认证。','Review')
    ws['H1'].comment=Comment('同一行多条问题若标签不同，请在“人工备注”按案例ID分别填写；不要以一个标签覆盖全部。','Review')
    # Raw long explanatory replies are not four-label answers. Keep full text in
    # cell/comment, but use a wider row instead of truncating the evidence.
    for n,g in enumerate(cases,2):
        ws.cell(n,4).comment=Comment('完整来源与前后问答在 L 列定位。原始文件未改；已排除可自动关闭的31–40问题。','Review')
    path.parent.mkdir(parents=True,exist_ok=True);wb.save(path)
    check=load_workbook(path);assert check.sheetnames==['待人工确认']
    assert check.active.max_row==len(content)+1
    for i,row in enumerate(content,2):
        for j,value in enumerate(row,1):assert check.active.cell(i,j).value==(value or None)
    listed={r['case_id'] for g in cases for r in g['cases']}
    assert not listed.intersection(resolved)
    expected={r['case_id'] for r in rows if r['puzzle_id'] in HUMAN_SCOPE}-set(resolved)-PROTOCOL_CLOSED
    assert listed==expected
    save(OUTDIR/'human_checklist.json',dict(workbook=str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
         rows=len(cases),original_cases=len(listed),target_cases=len(set(pending)&listed),scope=sorted(HUMAN_SCOPE),
         excluded_protocol_records=sorted(PROTOCOL_CLOSED),case_ids=sorted(listed),groups=cases))
    print(json.dumps(dict(sheet_count=1,rows=len(cases),original_cases=len(listed),target_unresolved=len(set(pending)&listed),resolved=len(resolved),workbook=str(path)),ensure_ascii=False))


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--apply',action='store_true',help='Apply this one-time review to active Host packs; refuses if already applied')
    ap.add_argument('--out',type=Path,default=ROOT/'outputs/20261031_host_human_check/人工复核疑点_指定22题.xlsx',help='New single-sheet workbook for the specified 22 puzzle IDs; never overwrites existing files')
    args=ap.parse_args();rows=issues();resolved,pending=decisions()
    target={r['case_id'] for r in rows if 'TS031'<=r['puzzle_id']<='TS040'}
    assert set(resolved).isdisjoint(pending)
    assert set(resolved)|set(pending)==target,(target-(set(resolved)|set(pending)))
    if args.apply:apply(rows,resolved,pending)
    if not MANIFEST.exists():raise SystemExit('Apply the reviewed changes before exporting a reduced checklist.')
    export(args.out,rows,pending,resolved)


if __name__=='__main__':main()
