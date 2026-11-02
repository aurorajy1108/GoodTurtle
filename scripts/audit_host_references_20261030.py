#!/usr/bin/env python3
"""Source-preserving reference audit, 2026-10-30. No model calls or experiments.

Build the review JSON and workbook from the frozen baseline and source records.
Activation is a separate, explicit operation performed from the reviewed manifest.
Requires openpyxl; --preview also requires Pillow. Never overwrite human Excel edits.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / 'data/host_reference/reviews/audit_20261030'
LABELS = {'yes', 'no', 'yes and no', 'irrelevant'}


def read(path):
    return json.loads(path.read_text())


def save(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def label(value):
    return re.sub(r'\s+', ' ', value.strip().lower().replace('&', 'and').replace('yes-and-no', 'yes and no'))


def inbox_pairs(folder):
    """Return all visible actions, including non-label replies and unanswered tails."""
    record = folder / 'source_record.json'
    if record.exists():
        d = read(record)
        return [(str(x['question_number']), x['question'], x.get('answer', x.get('host_answer_raw', '')))
                for x in d.get('qa_history', d.get('dialogue', []))], record
    path = folder / 'trajectory.md'
    s = path.read_text()
    # Numbered normalized share exports, followed by an ungraded final.
    matches = list(re.finditer(r'(?ms)^\s*(\d+)\. \*\*Player:\*\* (.*?)\s+\*\*Human host:\*\* ([^\n]+)', s))
    if matches:
        rows = [(m[1], m[2].strip(), m[3].strip()) for m in matches]
        if '## Final submission' in s:
            rows.append((str(len(rows)+1), s.split('## Final submission', 1)[1].split('[FINAL]', 1)[-1].strip(), ''))
        return rows, path
    # Role blocks from interactive runs / unabridged ChatGPT shares.
    pattern = r'(?m)^#{2,3} (?:Turn \d+ — )?(assistant \(player\)|user \(human_host\))\s*\n'
    parts = re.split(pattern, s)
    if len(parts) > 1:
        rows = []; pending = None
        for i in range(1, len(parts), 2):
            text = parts[i+1].strip()
            if parts[i].startswith('assistant'):
                if pending is not None:
                    rows.append((str(len(rows)+1), pending, ''))
                # Readiness is not a game action; retain its existence in source.
                if text.startswith('Ready. Send me'): continue
                pending = text.split('[QUESTION]', 1)[-1].strip() if '[QUESTION]' in text else text
            elif pending is not None:
                rows.append((str(len(rows)+1), pending, text)); pending = None
        if pending is not None: rows.append((str(len(rows)+1), pending, ''))
        return rows, path
    # Markdown role table. TS012 changes from numbered to two-column rows.
    messages = []
    for line in s.splitlines():
        if not line.startswith('|'): continue
        cols = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cols) >= 3 and cols[0].isdigit(): cols = cols[1:]
        if len(cols) != 2: continue
        role, message = cols
        if role.lower() in {'assistant', 'user', 'player', 'human_host'}:
            is_player = role.lower() in ({'user', 'player'} if folder.parent.name == 'TS017' else {'assistant', 'player'})
            messages.append((is_player, message))
    if not messages:
        for m in re.finditer(r'(?ms)^\*\*(Assistant|User):\*\*\s*(.*?)(?=^\*\*(?:Assistant|User):\*\*|\Z)', s):
            messages.append((m[1] == 'Assistant', m[2].strip()))
    rows = []; pending = None
    for is_player, text in messages:
        if is_player:
            if pending is not None: rows.append((str(len(rows)+1), pending, ''))
            pending = text
        elif pending is not None:
            rows.append((str(len(rows)+1), pending, text)); pending = None
    if pending is not None: rows.append((str(len(rows)+1), pending, ''))
    if not rows: raise ValueError(f'Unparsed source: {path}')
    return rows, path


def collect():
    rows = []; sources = []
    def add(pid, cid, q, a, origin, source, n, action='question', history=None):
        rows.append(dict(case_id=cid, puzzle_id=pid, question=q, observed=a,
                         normalized=label(a), origin=origin, source=source, ordinal=n,
                         action_type=action, public_history=history or [],
                         decision='reviewed_no_issue_found', proposed_label='', reason='',
                         severity='', active_action='not_imported', human_confirmed=False))
    for p in sorted((REVIEW/'baseline').glob('TS*.json')):
        for e in read(p)['host_examples']:
            if e.get('provenance', {}).get('answer_origin') == 'user_supplied_history':
                add(p.stem, e['case_id'], e['question'], e['answer'], 'user_supplied_history',
                    str(p.relative_to(ROOT)), e['case_id'], history=e.get('public_history'))
                rows[-1]['active_action'] = 'retained'
    for p in sorted((ROOT/'data/host_reference/sources/model_simulated_20261030').glob('TS*.json')):
        d = read(p)
        for e in d['actions']:
            add(p.stem, f'RUN_{p.stem}_{e["index"]:03d}', e['text'], e['feedback'],
                'model_generated', str(p.relative_to(ROOT)), e['index'], e['type'])
            if e['type'] == 'final':
                rows[-1].update(decision='reviewed_incomplete_submission',
                                reason={'TS031':'末次答案引入外部支架，遗漏移除橡皮、补充铅芯的机制；早期提交只猜到普通铅笔。',
                                        'TS035':'各次均未还原疫病、燃料不足及每日扫墓等完整叙事；不能把核心机制命中当全题解出。',
                                        'TS038':'各次未明确受害者是妻子；后期还加入未说明的后续冒名通信。'}[p.stem])
        sources.append(dict(source=str(p.relative_to(ROOT)), sha256=digest(p), records=len(d['actions']), origin='model_generated', scope='all_actions_reviewed'))
    for meta in sorted((ROOT/'data/host_reference/inbox').glob('*/*/source.json')):
        pairs, source = inbox_pairs(meta.parent); pid = meta.parent.parent.name
        for n, q, a in pairs:
            final = '[FINAL]' in q or 'FINAL:' in q or (not q.rstrip().endswith('?') and len(q)>400)
            add(pid, f'INBOX_{pid}_{int(n):03d}', q, a, 'user_supplied_history', str(source.relative_to(ROOT)), int(n), 'final' if final else 'question')
            if not a:
                rows[-1].update(decision='unanswered', reason='原始记录没有对应 Host 回复；不能补写为人工答案。')
            elif label(a) not in LABELS:
                rows[-1].update(decision='needs_review', severity='中', reason='原回复不是当前四种标签；控制命令、汤底揭晓和纠正说明不能当成标签。')
            elif final:
                rows[-1].update(decision='submission_not_training', reason='包含最终提交，应由完整性评分流程处理，不直接当普通问题示例。')
        sources.append(dict(source=str(source.relative_to(ROOT)), sha256=digest(source), records=len(pairs), origin='user_supplied_history', scope='visible_actions_reviewed'))
    return rows, sources


def apply_decisions(rows):
    by = {r['case_id']: r for r in rows}
    if len(by) != len(rows): raise ValueError('Duplicate review IDs')
    def flag(cid, suggestion, reason, severity='中'):
        r = by[cid]; r.update(decision='needs_review', proposed_label=suggestion, reason=reason, severity=severity)
        if r['active_action'] == 'retained': r['active_action'] = 'superseded'
    def many(prefix, indices, suggestion, reason, severity='中'):
        for n in indices: flag(f'{prefix}_{n:03d}', suggestion, reason, severity)

    flag('SHARE_6adf3775_120', 'no', '因果错配：增加真钞是怕假钞被发现，不是单因索要金额高于一百万。高额赎金为真不等于此因果成立。', '高')
    # New run: semantic uncertainty is preserved, never collapsed into a gold label.
    many('RUN_TS031', [3,6,11,13,15,20,48,57,69,77,79,82,83,84,85,95], '',
         '依赖指代/工具角色：题中橡皮是被移除的盖，补充铅芯在自动铅笔内。不能把“另一个支撑物/工具”暗换为内部铅芯以给 yes；原句暂缓，采用明确改写。', '高')
    flag('RUN_TS031_016', 'no', '问的是写留言的解释性目的；展示“橡皮附带铅笔”是替代动机，不是无关颜色等细节。')
    many('RUN_TS035', [8], 'irrelevant', '未说明此前是否有其他墓遭熊挖食；与 Q10/Q16/Q39 的 irrelevant 保持一致。', '高')
    many('RUN_TS035', [19], '', '森林中的坟墓不自动等于正式 village cemetery；Q22 又将此场所细节答 irrelevant。改写为 forest graves。')
    flag('RUN_TS035_056', 'yes and no', '复合命题中家属悲痛合理，但“熊对活人毫无危险”过强；题面只说很少袭击不熟悉的活人。', '高')
    many('RUN_TS035', [54,60,68,70,71], '', 'Q68=yes 与 Q70=no 基本同义，Q71又确认另一种“chiefly”；汤底核心是尸体被吃，不规定悲痛与遗体损害的主观优先级。避免强行二选一。', '高')
    flag('RUN_TS035_083', '', '把担忧可能发生加强为认定必然/预期会发生；改问是否担心其他坟墓同样有风险。')
    flag('RUN_TS035_091', '', 'revealed ... to bears generally 容易误成向其他熊传播信息；来源只支持父亲意识到风险。')
    many('RUN_TS038', [1,2,9,12,14,16,18], '', '收信人、阅读者与作伪者的角色没有对齐；书写假妻子字条不等于已有特定收信人读到内容。需明确指代后再定标签。', '高')
    flag('RUN_TS038_030', '', 'alibi 若指案发时不在场证明则 no；若泛指掩盖罪行则可 yes。Q31已否认不在场，原句不作无条件 yes 示例。', '高')
    many('RUN_TS038', [47,49,51], '', '原回复 no 将未知的暴露方式/书写困难细节判成明确不存在；与同组字体问题 irrelevant 边界不一致。先区分额外细节与替代核心解释。')
    many('RUN_TS038', [80,83,88,94], '', 'Q74 后的语境已经引入“除此以外的通信”；汤底只有反复练习伪造字条，不支持后来实际寄出或继续冒名发信息。须保持计划/执行及单封/多次通信之分。', '高')
    # Inbox: exact preserved row numbers, including protocol defects and story drift.
    many('INBOX_TS002', [3], 'irrelevant', '切断手不等于已经谋杀；受害者是否死亡未说明。')
    many('INBOX_TS002', [4,37,54], 'irrelevant', 'unknown 不是当前合法输出；此未说明细节应走 irrelevant。')
    many('INBOX_TS002', [8,40,79], 'irrelevant', '汤底没有确定毛巾血迹、凶器行李位置或其他物品组成；不能凭缺省写 no。')
    flag('INBOX_TS002_020', 'no', '已明确正在收拾行李、女方挽留，不能把袭击时是否睡着视为未知。')
    many('INBOX_TS002', [41,47,49,81], '', '切断手不保证特定刺入/同一次刀刺；问题把割断与刺穿/一刀刺中合并，原 yes 过度确认动作细节。', '高')
    many('INBOX_TS002', [50,55,57,59,67,70], '', '“枕头”是手本身；不要按另一个枕头、皮套、自然脱皮等字面实体继续回答。需显式区分人体与比喻物。')
    many('INBOX_TS002', [76,77,82,83], 'no', '本项目要求严格区分 hand 与 arm；原记录肯定 severed arm，与当前 hand 汤底及用户要求不符。改写 hand 后重新判定。', '高')
    flag('INBOX_TS002_078', '', '被叫作枕头不等于伪装外观来骗安检；还含错误的 arm，必须拆开身份与意图。', '高')
    flag('INBOX_TS007_002', '', 'cat 可以是家猫或猫科动物；老虎属于猫科，但不是家猫。改为 domestic cat=no / feline=yes。')
    flag('INBOX_TS007_006', 'yes', '老虎是哺乳动物，与同一记录 Q31 的 tiger cub 直接冲突。', '高')
    flag('INBOX_TS007_018', 'no', '昏迷由麻醉镖导致，电击是错误的替代致昏原因。', '高')
    many('INBOX_TS007', [21,25,29], '', '幼虎体型、游客主观自愿/园规、母亲预知具体惩罚未全部建立；应拆分常识与故事事实。')
    many('INBOX_TS011', [12,14,20], 'irrelevant', '只给出乐队提前停止；是否有意、身体原因或乐器损坏没有写明，不宜无条件否认。')
    flag('INBOX_TS011_015', 'yes', '汤底明确 band；通常由人演奏。yes and no 反而暗示不存在的非人演奏者。', '高')
    many('INBOX_TS012', [16,20,21,25,27,29,30,31,32,34,49], '', '灶具类型/触碰、普通住宅、取食材、空锅与有油、时间顺序或探测器位置的具体断言超出汤底或互相冲突。只确认 pantry 高温烹调、油烟、忘开排风、探测器灵敏。', '高')
    flag('INBOX_TS013_001', 'no', 'enrolled courses 是注册学术课程；汤底是选晚宴菜品，不能肯定这个错误词义。', '高')
    flag('INBOX_TS013_005', 'no', '截止时间不是 courses 消失的原因；侍者收走未吃完的菜才是。', '高')
    flag('INBOX_TS013_008', '', '已获正式课程名额确认没有依据；可改为提前选择晚宴菜品。')
    many('INBOX_TS013', [12,19,23,25], '', '返场、是否提前离席、分餐形式、取走时是否吃过等细节未完全说明；其中 Q25 与末条清理剩菜要区分完全未吃和未吃完。')
    many('INBOX_TS014', [1,8,51,59,67,69,71], 'irrelevant', '汤底只规定小组项目占比高，不规定没有考试、网课/研讨课、院校类型或具体科目。')
    many('INBOX_TS014', [4,46], '', '原 no 容易被误读为与项目无关；汤底是完成质量很差，并非没有交。建议明确改问“完全未完成/未提交=no”“完成质量不足=yes”。')
    many('INBOX_TS015', [13,20], 'no', '当前太急、缺合适设备不等于需要人类无法完成的运动或必须飞机；Q43 已回否飞机属于解答。', '高')
    many('INBOX_TS015', [11,19,44,45,48], '', '缺合适设备不等于完全无设备或必定缺船；不能肯定任意具体装备。应改成是否因水流太急且缺合适设备。')
    many('INBOX_TS017', [7], '', '打开物件释放烟气不是点烟这一机制；yes and no 需拆分 opened 与产生烟气。')
    many('INBOX_TS017', [10,18,23], 'yes', '吸烟确实燃烧非食物烟草并产生供吸入的烟；不能因示例列举蜡烛/纸而否认上位问题。', '高')
    flag('INBOX_TS017_041', 'yes', '香烟烟气就是触发源；还需要通风不足，不会令烟气因果只“半对”。', '高')
    many('INBOX_TS017', [45,48,49,52,54,56], '', '语境漂移到另一个被加热的物件、工艺爱好、干燥烟头；汤底只有和朋友抽烟及通风不足，不能继续补这些事实。', '高')
    many('INBOX_TS019', [3,5,6,7,8,9,12,15,16,17,18,19,20], '', '把 escalator 与 lift/elevator 混为一谈，又凭空确认建筑归属和入口楼层；原记录只支持一部扶梯维修、另一部停用作楼梯。', '高')
    flag('INBOX_TS021_003', '', '被关在地下室是事实，但父母让其相信整个世界只有地下室、长期特定灌输没有明说。需人工定扩展边界。')
    flag('INBOX_TS021_004', '', '看见外界支持；一生第一次见到外界属于新增时间量词，原短汤底未定。')
    many('INBOX_TS022', [2,5,11,12,14,16,23,25], '', '窗口被误认画像、次晨人消失才是核心；缺窗帘、多个物件布局、醒来认出仍在看的人均不应直接肯定。部分问题所指“东西”不清，须拆分。', '高')
    flag('INBOX_TS022_037', '', '末次自报33问，原记录实际有36条有回复问题；且未获最终确认。使用程序计数。')
    flag('INBOX_TS026_014', '', '末次自报12问，原记录实际13条有回复问题；最终解释中的购买地点等不作为事实。')
    many('INBOX_TS041', [9,10,14], 'irrelevant', '书的题材、后续处置或预约状态没有说明，不应随意 no。')
    flag('INBOX_TS041_015', '', 'library patron 是正常潜在读者；no 容易误排除读者。特定身份筛选与任何借阅者应分开。')
    flag('INBOX_TS041_016', '', '主干是希望有人发现且不是送礼，这可成立；括号的丢钱/藏钱举例错误。不能只因举例否认整个上位命题。')
    flag('INBOX_TS041_032', '', '问到 patrons browsing 亦包括读者翻书，与 Q29/Q36 的检验是否被读不一致；需明确借阅 vs 日常整理。')
    many('INBOX_TS041', [39,63], '', '这是作者据钱未动推断无人读，不是“钱没拿=绝对证明没人翻过”的逻辑定理；明确人物推断。')
    flag('INBOX_TS041_052', '', 'Player 只有 Yes. 不是可判定的问题；host no 不能作为训练样例。')
    flag('INBOX_TS041_067', 'no', '未知的展示/归架流程不能作为缺失核心；实际缺的是作者身份。', '高')
    many('INBOX_TS042', [12,13,16,18,25,37,40,41,72], '', '飞刀被抛出击中头部，不是吊顶/旋转装置/悬挂装饰/锤子。部分问题还暗含她横向走入轨迹，原肯定会持续误导。', '高')
    flag('INBOX_TS042_027', '', '同一问先问红色是否必要，又用 i.e. 问换颜色是否仍死，极性相反；单个 no 无法表达两者，应拆成 no 与 yes。', '高')
    flag('INBOX_TS042_031', '', '包含真正增高机制及错误“死于惊吓”解释；虽可判混合，需记录不是确认惊吓致死。')
    many('INBOX_TS043', [12,14,16,18], '', '按动物学把人叫 animal 会误导当前关于非人动物的连续追问；Q16 的 no 与玩家文本里伪写 host=yes 也要分离。医生是人，不能编出野生动物。', '高')
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path, default=ROOT/'outputs/20261030_host_reference_audit/host_reference_audit.xlsx', help='New workbook path; existing file is not overwritten')
    ap.add_argument('--preview', action='store_true', help='Render representative workbook cells using Pillow')
    args = ap.parse_args()
    if args.out.exists(): raise SystemExit('Refusing to overwrite an existing review workbook; choose --out')
    rows, sources = collect(); rows = apply_decisions(rows)
    if (REVIEW/'activation.json').exists():
        by = {r['case_id']:r for r in rows}
        for change in read(REVIEW/'activation.json')['changes']:
            r = by[change['source_case']]
            r['active_action'] = {'add_reviewed':'imported_reviewed','add_rewrite':'rewritten_only','correct_label':'superseded'}[change['action']]
    save(REVIEW/'review.json', dict(date='2026-10-30', reviewer='codex_root', human_confirmed=False,
         scope='109 bound user-history examples; all 300 actions from TS031/035/038; visible actions in 17 inbox sources. Historical share issues carried forward separately, not a fresh certification of all historical raw chats.',
         rows=rows, sources=sources))
    build_workbook(args.out, rows, sources, args.preview)


def build_workbook(out, rows, sources, preview=False):
    from openpyxl import Workbook, load_workbook
    from scripts.export_host_review import add_sheet, cache_formulas, previews
    bank = {p['id']: p for p in read(ROOT/'data/annotations/turtle50_v4/private.json')['puzzles']}
    packs = {p.stem: read(p) for p in (ROOT/'data/host_packs/active').glob('TS*.json')}
    old = read(ROOT/'data/host_reference/reviews/chatgpt_share_issues_20261026.json')['issues']
    issues = [r for r in rows if r['decision'] == 'needs_review']
    wb = Workbook(); wb.remove(wb.active)
    summary = add_sheet(wb,'阅读说明',['内容','数量／状态','说明'],[
        ['日期','2026-10-30','AI逐条核对后的参考建议，尚非人工金标。疑点数不是错误率。'],
        ['本轮疑点',len(issues),'先看“本轮疑点”，黄色列可填写人工决定；汤面汤底在同一行。'],
        ['历史分享疑点',len(old),'原44项原样带入单独页，不代表本次已解决。'],
        ['新轨迹行动',300,'TS031/035/038 各100；包含22次错误/不完整最终提交，均计入 quota。'],
        ['Active历史参考',109,'检查的是冻结基线中的全部109条用户提供历史问答。'],
        ['Inbox来源',17,'原始问答、非标签回复、控制命令和无回复尾部均保留；未整批激活。'],
        ['来源标记','保留真实来源','对外统称“已审核参考问答”；模型产生的记录不伪称人写。human_confirmed=false。'],
        ['判定原则','汤面＋汤底＋语境','no=错误机制；irrelevant=未定无关细节；yes and no=真正的混合或重要歧义；不能把正确关键词当正确因果。'],
        ['本次状态','不启动新实验','静态审核及回归检查不等于实测Host准确率提升；建议人工确认高优先级后再测。'],
        ['附件链接','未读到','6ae46825 分享链接上次403，不能声称已提取；本表依据仓库已有来源。'],
    ],[25,30,100])
    headers=['审核ID','题目','优先级','原问题／提交','原Host回答','建议标签（空=须拆分）','可疑原因','Active处理','来源','汤面','当前Host完整汤底','人工决定','人工标签','人工备注']
    add_sheet(wb,'本轮疑点',headers,[[r['case_id'],r['puzzle_id'],r['severity'],r['question'],r['observed'],r['proposed_label'],r['reason'],r['active_action'],r['source'],bank[r['puzzle_id']]['opening'],packs[r['puzzle_id']]['solution'],'','',''] for r in issues],[30,10,10,65,18,22,60,20,45,65,80,16,18,40])
    add_sheet(wb,'历史分享疑点',['审核ID','题目','原问题','原回答','原审核理由','原建议','汤面','完整汤底','来源','人工决定','人工标签','人工备注'],[[r['issue_id'],r['puzzle_id'],r['question'],r.get('observed',''),r.get('analysis',''),r.get('recommendation',''),bank.get(r['puzzle_id'],{}).get('opening',''),r.get('reference_answer',''),r.get('source_url',''),'','',''] for r in old],[20,10,65,18,60,60,65,80,45,16,18,40])
    for name, subset in [('三题逐条审核',[r for r in rows if r['origin']=='model_generated']),('Active人工参考',[r for r in rows if r['active_action'] in {'retained','superseded'}]),('Inbox逐条记录',[r for r in rows if r['case_id'].startswith('INBOX_')])]:
        add_sheet(wb,name,['审核ID','题目','类型','原问题／提交','原回答','审核状态','建议标签','理由','Active处理','来源','人工决定','人工标签','人工备注'],[[r['case_id'],r['puzzle_id'],r['action_type'],r['question'],r['observed'],r['decision'],r['proposed_label'],r['reason'],r['active_action'],r['source'],'','',''] for r in subset],[30,10,15,80,22,30,18,65,20,45,16,18,40])
    add_sheet(wb,'题目与汤底',['题目','汤面','数据集汤底','当前Host完整汤底'],[[pid,p['opening'],p['answer'],packs[pid]['solution']] for pid,p in bank.items()],[12,85,100,100])
    add_sheet(wb,'来源与覆盖',['来源路径','SHA256','行动记录数','来源类型','覆盖说明'],[[s[k] for k in ['source','sha256','records','origin','scope']] for s in sources],[95,70,18,30,65])
    active = read(REVIEW/'activation.json') if (REVIEW/'activation.json').exists() else {'changes':[]}
    add_sheet(wb,'Active变更',['题目','案例ID','动作','接入问题','接入标签','来源／审核理由'],[[r['puzzle_id'],r['case_id'],r['action'],r.get('question',''),r.get('answer',''),r.get('reason','')] for r in active['changes']],[12,35,25,90,20,90])
    summary['B3']=f"=COUNTA('本轮疑点'!A2:A{len(issues)+1})"
    summary['B4']=f"=COUNTA('历史分享疑点'!A2:A{len(old)+1})"
    out.parent.mkdir(parents=True,exist_ok=True); wb.save(out)
    cache_formulas(out,{'B3':len(issues),'B4':len(old)})
    checked=load_workbook(out,data_only=True)
    assert checked['本轮疑点'].max_row==len(issues)+1
    assert checked['三题逐条审核'].max_row==301
    assert checked['Active人工参考'].max_row==110
    assert checked['阅读说明']['B3'].value==len(issues)
    # Round-trip every full question and reason; don't silently truncate evidence.
    for n,r in enumerate(issues,2):
        assert checked['本轮疑点'].cell(n,4).value==r['question']
        assert checked['本轮疑点'].cell(n,7).value==r['reason']
    if preview: previews(out,out.parent/'previews',Path('/System/Library/Fonts/PingFang.ttc'))
    print(json.dumps({'workbook':str(out),'rows':len(rows),'issues':len(issues),'historical_issues':len(old),'sources':len(sources)},ensure_ascii=False))


if __name__=='__main__': main()
