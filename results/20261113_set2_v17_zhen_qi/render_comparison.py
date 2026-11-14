"""Plot immutable local records, with cohorts separated by scoring/Host version."""
import csv,hashlib,json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.lines import Line2D
import numpy as np
DATA=Path(__file__).resolve().parent
OUT=DATA/'figures'
rows=json.loads((DATA/'comparison_53_records.json').read_text())
import os
font=Path(os.environ.get('GOODTURTLE_CHINESE_FONT','/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'))
if not font.is_file():raise SystemExit('Set GOODTURTLE_CHINESE_FONT to an installed Chinese TTF/TTC font')
font_manager.fontManager.addfont(font)
plt.rcParams.update({'font.family':font_manager.FontProperties(fname=font).get_name(),'axes.unicode_minus':False,
 'pdf.fonttype':42,'ps.fonttype':42,'svg.fonttype':'none','font.size':11})
cohorts=['teammate_round1','teammate_round2','your_v17_r1_r5']
labels={'teammate_round1':'组友第1轮｜Host v12 / 评分v5',
 'teammate_round2':'组友第2轮｜Host v13 / 评分v5',
 'your_v17_r1_r5':'你的本轮｜Host v17 / 评分v6'}
keys=[('none','direct'),('TS033','answer_only'),('TS033','session'),('TS035','answer_only'),('TS035','session'),('TS012','answer_only'),('TS012','session')]
xticks=['direct\n无前题经验','TS033\nanswer-only','TS033\ncontext','TS035\nanswer-only','TS035\ncontext','TS012\nanswer-only','TS012\ncontext']
colors=['#353535','#447D9D','#B1C3CC','#447D9D','#B1C3CC','#447D9D','#B1C3CC']
def group(cohort,key):
 src,cond=key
 return [r for r in rows if r['cohort']==cohort and r['condition']==cond and (cond=='direct' or r['source']==src)]
stats=[]
for cohort in cohorts:
 for key in keys:
  rr=group(cohort,key);assert rr
  stats.append({'cohort':cohort,'source':key[0],'condition':key[1],'n':len(rr),
  'mean_percent':float(np.mean([r['score']*100 for r in rr])),
  'sample_sd_percent':float(np.std([r['score']*100 for r in rr],ddof=1)) if len(rr)>1 else None,
  'scores_percent':[r['score']*100 for r in rr],'solved':sum(r['solved'] for r in rr)})
assert len(rows)==53 and not any(r['solved'] for r in rows)
assert sum(s['n'] for s in stats)==53
# One consistent reading direction: source panels -> three plain-language conditions.
# Direct controls are repeated as references in each panel; summaries count each game once.
from matplotlib.patches import Patch
palette={'your_v17_r1_r5':'#245B9B','teammate_round1':'#CC7933','teammate_round2':'#649681'}
short={'your_v17_r1_r5':'你（每组5局）','teammate_round1':'组友 · 第1轮','teammate_round2':'组友 · 第2轮'}
def draw_comparison(selected, basename, title):
 fig,axes=plt.subplots(1,3,figsize=(17,7.6),sharey=True,facecolor='white')
 fig.subplots_adjust(left=.06,right=.985,bottom=.275,top=.72,wspace=.12)
 fig.text(.06,.94,title,fontsize=25,weight='bold',color='#151515')
 fig.text(.06,.877,'每个面板是一道前题；从左到右看：不带经验 → 只看答案 → 看完整过程。',fontsize=13,color='#555555')
 fig.legend(handles=[Patch(facecolor=palette[c],label=short[c]) for c in selected],
  loc='upper left',bbox_to_anchor=(.053,.84),frameon=False,ncol=len(selected),fontsize=13,
  handlelength=1.2,columnspacing=2.5)
 width=.25 if len(selected)==3 else .30
 shifts=np.linspace(-width*(len(selected)-1)/2,width*(len(selected)-1)/2,len(selected))
 for ax,src in zip(axes,['TS033','TS035','TS012']):
  ax.set_title('前题 '+src,fontsize=17,weight='bold',loc='left',pad=14)
  ax.set_ylim(-3,112);ax.set_xlim(-.6,2.6)
  ax.set_yticks([0,20,40,60,80,100],[f'{v}%' for v in [0,20,40,60,80,100]])
  ax.set_axisbelow(True);ax.yaxis.grid(True,color='#E5E5E5',linewidth=.8)
  for side in ('top','right','left'):ax.spines[side].set_visible(False)
  ax.spines['bottom'].set_color('#BDBDBD');ax.tick_params(length=0,pad=10)
  ax.set_xticks([0,1,2],['不带前题经验','只看前题答案','看完整前题过程'],fontsize=12)
  for ci,c in enumerate(selected):
   for xi,cond in enumerate(['direct','answer_only','session']):
    rr=group(c,('none' if cond=='direct' else src,cond))
    mean=float(np.mean([r['score']*100 for r in rr]));x=xi+shifts[ci]
    ax.bar(x,mean,width=width*.90,color=palette[c],zorder=2)
    ax.text(x,mean+5,f'{mean:g}%',ha='center',va='bottom',fontsize=11,weight='bold',color=palette[c])
    offsets=np.linspace(-width*.28,width*.28,len(rr)) if len(rr)>1 else [0]
    for offset,r in zip(offsets,rr):
     intervened=bool(r.get('protocol_interventions',0))
     ax.scatter(x+offset,r['score']*100,s=24 if len(rr)>1 else 31,marker='D' if intervened else 'o',
      facecolor='white',edgecolor=palette[c],linewidth=1.1,zorder=4,clip_on=False)
 axes[0].set_ylabel('最终交卷得分',labelpad=12,fontsize=13)
 if len(selected)==3:
  fig.text(.06,.165,'柱＝均值，点＝每局分数。你的每组5局；组友每轮的迁移条件各1局、无经验对照3局。',fontsize=11.5,color='#444444')
  fig.text(.06,.108,'同一批“无经验对照”在三个面板重复显示，方便比较；总样本仍为53局，没有重复计数。',fontsize=11.5,color='#444444')
  fig.text(.06,.052,'版本不同：你 Host v17 / 评分v6；组友第1轮 v12/v5、第2轮 v13/v5。保留原分，不能据柱高判断可靠优劣。',fontsize=10.5,color='#666666')
 else:
  fig.text(.06,.165,'柱＝本轮均值，点＝每局分数。每轮“只看答案”和“看完整过程”各来源只有1局，无经验对照3局。',fontsize=11.5,color='#444444')
  fig.text(.06,.108,'无经验对照在三个面板重复显示，实际共18局目标题。两轮重新生成前题，Host也从v12改为v13。',fontsize=11.5,color='#444444')
  fig.text(.06,.052,'均保留旧评分v5原分；其中两局100%仍未达到完整解答标准。完整协议与辅助调用记录见配套报告。',fontsize=10.5,color='#666666')
 for ext in ('png','pdf','svg'):fig.savefig(OUT/f'{basename}.{ext}',dpi=200,facecolor='white')
 plt.close(fig)
draw_comparison(['teammate_round1','teammate_round2'],'teammate_results','组友的结果：三种经验形式怎么比？')
draw_comparison(['your_v17_r1_r5','teammate_round1','teammate_round2'],'comparison_53','双方结果：前题经验有没有帮助？')
(OUT/'stratified_summary.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2)+'\n')
with (OUT/'stratified_summary.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(stats[0]));w.writeheader();w.writerows(stats)
provenance={'data_sha256':hashlib.sha256((DATA/'comparison_53_records.json').read_bytes()).hexdigest(),
 'source_main_commit':'25f4cc4561680445d1932226b53a2eb32e215c2d','unique_targets':53,
 'figures':['teammate_results','comparison_53'],'pooled_across_versions':False,'direct_repeated_for_reference_only':True,'layout':'source_panels_grouped_bars','model_calls':0}
(OUT/'comparison_provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
print('Generated teammate18 and stratified combined53 PNG/PDF/SVG; yours35 preserved separately.')
