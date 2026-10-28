#!/usr/bin/env python3
"""Rebuild the 2026-10-26 audit workbook from versioned JSON; no model/network calls.
Requires openpyxl. Optional previews require Pillow and a local CJK font.
"""
import argparse
import json
import math
import unicodedata
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import CellIsRule
from openpyxl.utils import get_column_letter
from openpyxl.workbook.properties import CalcProperties
ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'data/host_reference/sources/chatgpt_shares_20261026'
A=ROOT/'data/host_reference/reviews'
NAVY='16324F';TEAL='006D77';WHITE='FFFFFF';INK='243746';PALE='EEF4F8';EDIT='FFF2CC'


def read(p):return json.loads(p.read_text())
def text(v):
    if v is None:return ''
    if isinstance(v,(dict,list)):return json.dumps(v,ensure_ascii=False)
    return v

def display_width(s):return sum(2 if unicodedata.east_asian_width(c) in 'WF' else 1 for c in str(s))

def add_sheet(wb,name,headers,rows,widths):
    ws=wb.create_sheet(name);ws.sheet_view.showGridLines=False;ws.sheet_view.zoomScale=85
    ws.append(headers)
    for r in rows:ws.append([text(v) for v in r])
    ws.freeze_panes='D2' if len(headers)>6 else 'B2'
    ws.auto_filter.ref=ws.dimensions;ws.row_dimensions[1].height=32
    ws.print_title_rows='1:1';ws.sheet_properties.pageSetUpPr.fitToPage=True
    ws.page_setup.orientation='landscape';ws.page_setup.paperSize=ws.PAPERSIZE_A3;ws.page_setup.fitToWidth=1;ws.page_setup.fitToHeight=0
    ws.print_options.horizontalCentered=True
    for col,(h,width) in enumerate(zip(headers,widths),1):
        ws.column_dimensions[get_column_letter(col)].width=width
        for row in range(1,ws.max_row+1):
            c=ws.cell(row,col)
            if isinstance(c.value,str):c.data_type='s'  # imported =,+,-,@ stay literal; only explicit summary formulas execute
            c.font=Font(name='Microsoft YaHei',size=11,color=WHITE if row==1 else ('0070C0' if h.startswith('人工') else INK),bold=row==1)
            c.fill=PatternFill('solid',fgColor=NAVY if row==1 else (EDIT if h.startswith('人工') else (WHITE if row%2 else PALE)))
            c.alignment=Alignment(vertical='top',wrap_text=True)
            if row>1 and isinstance(c.value,str) and c.value.startswith('https://'):
                c.hyperlink=c.value;c.font=Font(name='Microsoft YaHei',size=11,color=TEAL,underline='single')
        if h in ('人工决定','人工标签'):
            options='待审核,接受,改写,修改标签,暂缓,非问题' if h=='人工决定' else 'yes,no,yes and no,irrelevant'
            dv=DataValidation(type='list',formula1='"'+options+'"',allow_blank=True);dv.error='请使用下拉选项';dv.showErrorMessage=True;ws.add_data_validation(dv);dv.add(f'{get_column_letter(col)}2:{get_column_letter(col)}{max(ws.max_row,2)}')
    for row in range(2,ws.max_row+1):
        lines=max(sum(max(1,math.ceil(display_width(part)/max(8,width-2))) for part in str(ws.cell(row,c).value or '').split('\n')) for c,width in enumerate(widths,1))
        ws.row_dimensions[row].height=min(409,max(42,lines*15+12))
    return ws


def cache_formulas(path,values):
    # openpyxl does not calculate formulas. Store independently verified count caches;
    # keep actual formulas, with fullCalcOnLoad so human edits recalculate in Excel.
    ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    with zipfile.ZipFile(path) as z:entries={n:z.read(n) for n in z.namelist()}
    root=ET.fromstring(entries['xl/worksheets/sheet1.xml'])
    for cell in root.findall('.//s:c',ns):
        if cell.attrib['r'] in values:
            val=cell.find('s:v',ns)
            if val is None:val=ET.SubElement(cell,'{'+ns['s']+'}v')
            val.text=str(values[cell.attrib['r']])
    entries['xl/worksheets/sheet1.xml']=ET.tostring(root,encoding='utf-8',xml_declaration=True)
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
        for name,content in entries.items():z.writestr(name,content)


def previews(path,out,font_path):
    from PIL import Image,ImageDraw,ImageFont
    out.mkdir(parents=True,exist_ok=True);wb=load_workbook(path,data_only=True)
    font=ImageFont.truetype(str(font_path),17);bold=ImageFont.truetype(str(font_path),19)
    def wrap(s,width,draw):
        lines=[]
        for part in str(s).split('\n'):
            line=''
            for char in part:
                if draw.textlength(line+char,font=font)>width and line:lines.append(line);line=''
                line+=char
            lines.append(line)
        return lines
    for idx,ws in enumerate(wb.worksheets):
        # Detail sheets have many columns: preview the source and core judgment together.
        selected={'新分享疑点':[1,2,3,4,8,9,10], '混合细节案例':[1,2,3,4,7], '原始行动记录':[1,2,3,5,6,7]}.get(ws.title,list(range(1,min(ws.max_column,5)+1)))
        widths=[min(450,max(130,ws.column_dimensions[get_column_letter(c)].width*7)) for c in selected]
        scale=min(1,1900/sum(widths));widths=[int(w*scale) for w in widths]
        im=Image.new('RGB',(sum(widths)+40,1500),'white');dr=ImageDraw.Draw(im);dr.text((20,10),ws.title+' · preview（所选列，完整内容见Excel）',font=bold,fill='#16324F');y=50
        for r in range(1,min(ws.max_row,5)+1):
            wrapped=[wrap(ws.cell(r,c).value if ws.cell(r,c).value is not None else '',w-16,dr) for c,w in zip(selected,widths)]
            height=max(len(lines) for lines in wrapped)*25+18
            if y+height>1450:break
            x=20
            for c,w,lines in zip(selected,widths,wrapped):
                fill='#16324F' if r==1 else ('#EEF4F8' if r%2==0 else '#FFFFFF')
                dr.rectangle((x,y,x+w,y+height),fill=fill,outline='#D5E0E8')
                for li,line in enumerate(lines):dr.text((x+8,y+8+li*25),line,font=font,fill='white' if r==1 else '#243746')
                x+=w
            y+=height
        im.crop((0,0,im.width,y+20)).save(out/f'{idx+1:02d}.png')


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out',type=Path,default=ROOT/'outputs/20261026_host_review/host_review_20261026.xlsx',help='Output XLSX; rebuilding replaces this generated artifact')
    ap.add_argument('--preview-dir',type=Path,help='Optional directory for representative PNG previews, one per sheet')
    ap.add_argument('--font',type=Path,default=Path('/System/Library/Fonts/PingFang.ttc'),help='CJK font for optional previews only')
    args=ap.parse_args()
    issues=read(A/'chatgpt_share_issues_20261026.json')['issues'];old=read(A/'experiment_findings_snapshot_20261026.json')['findings'];mixed=read(A/'mixed_detail_cases_20261026.json')['cases'];infra=read(A/'infra_review_20261026.json')['issues'];sessions=read(D/'sessions.json');pairs=read(D/'qa_pairs.json');merge=read(A/'chatgpt_share_merge_20261026.json');history=read(A/'history_qa_merge_20261026.json')
    wb=Workbook();wb.remove(wb.active);wb.calculation=CalcProperties(calcId=191029,fullCalcOnLoad=True)
    summary=add_sheet(wb,'概览',['指标 / 阅读顺序','数量 / 状态','解释'],[
        ['审核日期','2026-10-26','AI审核建议，未获人工确认；疑点数量不是Host错误率。'],
        ['新分享疑点',len(issues),'先查此页：身份、错误因果、未说明细节被确认、人工回改。'],
        ['历史合并需处理',15,'14条改写 + 1条暂缓；历史页同时提供全部89条。'],
        ['旧实验审核发现',len(old),'来自8个已完成的v6审核；有正确判分观察与边界争议，非全部错误。'],
        ['混合细节案例',len(mixed),'真实原句；按主问/关系判断，不能按真词比例投票。'],
        ['共享聊天片段',len(sessions),'题库内5题，TS034两次尝试；另有题库外火车题。'],
        ['行动记录',len(pairs),'包含提问、完整提交、回改未答及尾题未答。不是311个标准Q&A。'],
        ['具有规范标签的行动',sum(p['label_observed'] is not None for p in pairs),'标签能解析不代表标签正确。'],
        ['无规范标签的行动',sum(p['label_observed'] is None for p in pairs),'2处拼写待定、1次纠正非当前反馈、2个未答尾题。'],
        ['此次绑定Host示例',merge['added_examples'],'保留原题/原标签，AI核对，仍待人工；其他原句不自动进入Host。'],
        ['系统/设计检查',len(infra),'部分v7已修，部分仍是研究限制；不在本轮恢复实验。'],
        ['人工已填决定',0,'只统计新分享疑点的人工决定栏；蓝字黄色底可编辑。'],
        ['用途','审核资料，不是训练完成或准确率报告','原始反馈与建议分栏；复盘、自评、用户纠正、最终提交分别记录。'],
        ['数据隐私','只收录这两个公开分享','不发布原始HTML或页面启动数据，不导入账户其他聊天。'],
    ],[34,25,95])
    add_sheet(wb,'新分享疑点',['问题ID','题目ID','案例ID','类别','原始player消息','原始Host反馈','确定性','分析','处理建议','优先级','标准答案','来源','人工决定','人工标签','人工备注'],[[i['issue_id'],i['puzzle_id'],i['case_id'],i['category'],i['question'],i['observed'],i['certainty'],i['analysis'],i['recommendation'],i['priority'],i['reference_answer'],i['source_url'],'','',''] for i in issues],[13,12,29,24,110,75,24,65,65,10,105,50,16,18,50])
    hist=[]
    for g in history['puzzles']:
        for e in g['decisions']:
            m=e.get('merged') or {};hist.append([g['puzzle_id'],e['source_case_id'],e['decision'],e['original']['question'],e['original']['answer'],m.get('question',''),m.get('answer',''),e['review_note'],e.get('evidence'),g['source_pack'],'','',''])
    add_sheet(wb,'历史合并审核',['题目ID','案例ID','决定','原始问题','原始答案','入库问题','入库答案','理由','来源证据','来源文件','人工决定','人工标签','人工备注'],hist,[12,29,16,90,18,90,18,80,90,55,16,18,50])
    add_sheet(wb,'旧实验审核发现',['运行','轮次','类别','原审核确定性','证据','原审核分析','原建议','审核状态','来源','人工决定','人工备注'],[[i['run'],i.get('turns'),i.get('category'),i.get('certainty'),i.get('evidence'),i.get('explanation'),i.get('suggested_correction'),i['status'],i['source'],'',''] for i in old],[35,22,42,50,130,130,100,35,60,16,50])
    add_sheet(wb,'混合细节案例',['案例ID','题目ID','原始问题','原Host反馈','正确/已知主干','未知或错误部分','建议整句处理','建议拆问（AI改写）','类型','来源','人工决定','人工备注'],[[i[k] for k in ['case_id','puzzle_id','question','observed','main','detail','recommendation','atomic_rewrite','type','source_url']]+['',''] for i in mixed],[29,12,105,18,55,55,75,100,28,50,16,50])
    add_sheet(wb,'原始行动记录',['案例ID','题目ID','会话ID','消息序号','完整player原文','完整Host原文','规范标签','动作类型','规范化状态','后续人工纠正','绑定Host','审核状态','player消息ID','Host消息ID','来源','人工决定','人工标签','人工备注'],[[p['case_id'],p['puzzle_id'],p['session_id'],p['message_index'],p['player_text'],p['host_feedback_raw'],p['label_observed'],p['action_type'],p['label_normalization'],p.get('later_correction'), '是' if p['eligible_for_host_pack'] else '否',p['review_status'],p['message_id'],p['feedback_message_id'],p['source_url'],'','',''] for p in pairs],[29,12,40,13,130,140,18,22,35,65,12,48,40,40,50,16,18,50])
    add_sheet(wb,'会话索引',['会话ID','题目ID','动作数','标准标签数','纠正未答','拼写待定','尾题未答','final数','绑定数','起始消息','结束消息','来源','汤面'],[[s['session_id'],s['puzzle_id'],s['recorded_actions'],s['standard_label_rows'],s['unanswered_correction_rows'],s['unresolved_typo_rows'],s['unanswered_at_segment_end'],s['final_submission_rows'],s['bound_examples'],s['first_message'],s['last_message'],s['source_url'],s['opening_message']] for s in sessions],[40,24,12,14,12,12,12,12,12,12,12,50,120])
    add_sheet(wb,'系统与设计',['ID','事项','当前状态','证据/限制','来源','人工检查内容','人工决定','人工备注'],[[i[k] for k in ['issue_id','topic','status','evidence','source','human_check']]+['',''] for i in infra],[12,35,65,90,65,80,16,50])
    bound=[]
    for group in merge['puzzles']:
        for e in group['added_examples']:bound.append([group['puzzle_id'],e['case_id'],e['question'],e['answer'],e['rationale'],e['review_status'],group['merged_pack'],e['provenance']['source_url'],'','',''])
    add_sheet(wb,'已绑定示例',['题目ID','案例ID','问题','标签','私有理由','审核状态','绑定文件','来源','人工决定','人工标签','人工备注'],bound,[12,29,105,18,100,48,70,50,16,18,50])
    sources=[['分享1','https://chatgpt.com/share/6adf3775-b4dc-83ea-83d0-ef0cf69dbc45','495条可见消息；用户提供；本地可见文本抽取，保留消息ID。'],['分享2','https://chatgpt.com/share/6adf37d6-5080-83e9-abbc-2ced03b615d6','138条可见消息；包含人工回改、未答末题。'],['导出官方说明','https://help.openai.com/en/articles/7260999-exporting-your-chatgpt-history-and-data','登录网页→头像→Settings→Data controls→Export data→Export/Confirm export。'],['导出下载提醒','https://help.openai.com/en/articles/7260999-exporting-your-chatgpt-history-and-data','邮件/短信通知；最多可能7天；下载链接24小时过期。ZIP含聊天及其他账户数据。'],['只提供相关题目','data/host_reference/sources/chatgpt_shares_20261026/README.md','完整账户导出可能包含其他隐私；可只整理相关会话文本/JSON，不必提供整个账户归档。'],['当前评判来源','data/annotations/turtle50_v4/private.json','标准答案、rubric及completion_requirements优先；不为配合历史回答改写汤底。'],['当前四标签prompt','prompts/loop_host_v1.txt','旧prompts/archive/host_system_v0.5.1.txt不是当前loop四标签prompt。'],['来源文件范围','data/host_reference/reviews/experiment_findings_snapshot_20261026.json','41条旧审核发现是完整快照；旧run文件本地仍在但不是新生成结果。'],['人工确认范围','data/host_reference/reviews/chatgpt_share_merge_20261026.json','新绑定21条为人工原答+AI核对，human_confirmed=false。'],['表格生成','scripts/export_host_review.py','需要openpyxl；可选Pillow预览。黄色底蓝字是人工可填写栏。长原文保留完整，可在编辑栏展开。'],['运行状态','docs/host_repair_v7.md','正式实验暂停；本轮只做离线测试与资料审核，没有新准确率。']]
    add_sheet(wb,'来源与导出',['项目','链接/路径','说明'],sources,[30,95,110])
    formulas={
        'B3':("COUNTA('新分享疑点'!A2:A10000)",len(issues)),
        'B4':("COUNTIF('历史合并审核'!C2:C10000,\"rewritten\")+COUNTIF('历史合并审核'!C2:C10000,\"withheld\")",15),
        'B5':("COUNTA('旧实验审核发现'!A2:A10000)",len(old)),
        'B6':("COUNTA('混合细节案例'!A2:A10000)",len(mixed)),
        'B7':("COUNTA('会话索引'!A2:A10000)",len(sessions)),
        'B8':("COUNTA('原始行动记录'!A2:A10000)",len(pairs)),
        'B9':("COUNTIF('原始行动记录'!G2:G10000,\"yes\")+COUNTIF('原始行动记录'!G2:G10000,\"no\")+COUNTIF('原始行动记录'!G2:G10000,\"yes and no\")+COUNTIF('原始行动记录'!G2:G10000,\"irrelevant\")",sum(p['label_observed'] is not None for p in pairs)),
        'B10':('B8-B9',sum(p['label_observed'] is None for p in pairs)),
        'B11':("COUNTA('已绑定示例'!A2:A10000)",len(bound)),
        'B12':("COUNTA('系统与设计'!A2:A10000)",len(infra)),
        'B13':("COUNTA('新分享疑点'!M2:M10000)",0),
    }
    for cell,(formula,_) in formulas.items():summary[cell]='='+formula;summary[cell].font=Font(name='Microsoft YaHei',size=12,bold=True,color=TEAL)
    args.out.parent.mkdir(parents=True,exist_ok=True);wb.save(args.out);cache_formulas(args.out,{k:v[1] for k,v in formulas.items()})
    actual=load_workbook(args.out,data_only=True);raw=load_workbook(args.out,data_only=False)
    for cell,(formula,value) in formulas.items():assert actual['概览'][cell].value==value and raw['概览'][cell].value=='='+formula
    assert actual['原始行动记录'].max_row==312 and actual['已绑定示例'].max_row==22
    for ws in raw:
        for row in ws:
            for cell in row:
                assert cell.data_type!='e',(ws.title,cell.coordinate,cell.value)
                assert cell.data_type!='f' or ws.title=='概览',(ws.title,cell.coordinate)
    if args.preview_dir:previews(args.out,args.preview_dir,args.font)
    print(json.dumps({'output':str(args.out),'sheets':len(wb.worksheets),'issues':len(issues),'actions':len(pairs),'bound_examples':len(bound),'validated':True},ensure_ascii=False))

if __name__=='__main__':main()
