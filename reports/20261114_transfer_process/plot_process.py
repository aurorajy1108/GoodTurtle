"""Descriptive fixed-A case figure; dots are B repeats, not independent A's."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
rows = json.loads((ROOT/'set1_game_metrics.json').read_text())
summary = json.loads((ROOT/'set1_condition_metrics.json').read_text())
conditions = ['direct', 'answer_only', 'session']
labels = ['Direct', 'Answer only', 'Session']
colors = ['#516777', '#267a74', '#aa583c']
fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.4), layout='constrained')
for j,c in enumerate(conditions):
    group = sorted([r for r in rows if r['fixed_A']=='TS015' and r['condition']==c], key=lambda r:r['repeat'])
    s = next(r for r in summary if r['fixed_A']=='TS015' and r['condition']==c)
    assert len(group)==4 and all(r['first_supported_food_sense'] is not None for r in group)
    offsets = [-.12,-.04,.04,.12]
    for i,r in enumerate(group):
        for ax, y in zip(axes,[r['first_supported_food_sense'],100*r['final_score']]):
            ax.scatter(j+offsets[i],y,s=42,color=colors[j],zorder=3)
            ax.annotate(str(r['repeat']),(j+offsets[i],y),xytext=(3,5),textcoords='offset points',fontsize=8)
    axes[0].plot([j-.23,j+.23],[s['observed_only_median']]*2,color=colors[j],lw=2)
    axes[1].errorbar(j,100*s['final_score_mean'],yerr=100*s['final_score_sample_sd'],color=colors[j],capsize=7,lw=1.2,fmt='_',markersize=18)
for ax in axes:
    ax.set_xticks(range(3),labels);ax.set_xlim(-.5,2.5)
    ax.spines[['top','right']].set_visible(False);ax.grid(axis='y',alpha=.18)
axes[0].set(ylabel='Submission of supported meal-course interpretation',ylim=(0,70),title='Earlier entry into the relevant interpretation\nHorizontal bars: medians')
axes[1].set(ylabel='Original final reconstruction score (%)',ylim=(0,100),title='Earlier entry is not sufficient for completion\nBars: mean ± sample SD')
fig.suptitle('TS015 → TS013: one fixed A, four B repeats per condition',fontsize=12)
fig.savefig(ROOT/'semantic_entry_vs_final.png',dpi=200)
fig.savefig(ROOT/'semantic_entry_vs_final.svg')
plt.close(fig)
