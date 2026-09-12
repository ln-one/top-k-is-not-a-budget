"""Measured replay figures; no synthetic data. All intervals preserve observation limits."""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[2];P=ROOT/'results/paper-experiments-v2';OUT=Path(__file__).parent
DS=['msmarco-passage-trec-dl-2019','msmarco-passage-trec-dl-2020','nfcorpus','scifact','trec-covid'];N=['DL19','DL20','NFCorpus','SciFact','COVID']
# Paul Tol Vibrant: https://sronpersonalpages.nl/~pault/ (Fig. 3).
colors=['#0077BB','#EE7733','#009988','#EE3377','#33BBEE']
markers=['o','s','^','D','v'];styles=['-','--','-.',':',(0,(5,1,1,1))]
methods={'balanced':('#EE7733','Balanced'),'dibud':('#0077BB','DiBud')}
method_styles={'balanced':dict(linestyle='--',marker='s',markersize=3,markerfacecolor='white'), 'dibud':dict(linestyle='-',marker='o',markersize=3)}
plt.rcParams.update({'font.family':'sans-serif','font.sans-serif':['Arial','DejaVu Sans'],'font.size':8,'axes.spines.top':False,'axes.spines.right':False,'axes.linewidth':.7,'axes.edgecolor':'#555555','axes.axisbelow':True,'grid.color':'#E5E7EB','grid.linewidth':.5,'axes.grid':True,'axes.grid.axis':'y','legend.frameon':False,'pdf.fonttype':42,'svg.fonttype':'none'})
def save(fig,name):
 for ext in ('pdf','svg','png'):fig.savefig(OUT/f'{name}.{ext}',bbox_inches='tight',dpi=300)
 plt.close(fig)
t=pd.read_csv(P/'transfer-summary.csv')
# Transfer: query dependence, snapshot dependence, then held-out transfer.
grid=pd.read_csv(P/'transfer-grid.csv')
curves=grid.groupby(['dataset','snapshot','L'],as_index=False).ndcg10.mean()
curves.to_csv(P/'transfer-depth-means.csv',index=False)
fig,ax=plt.subplots(1,3,figsize=(7.1,2.65),layout='constrained')
for ds,n,col,marker,style in zip(DS[:2],['DL 2019','DL 2020'],colors,markers,styles):
 s=curves[curves.dataset==ds].sort_values('L')
 ax[0].plot(s.L,s.ndcg10,label=n,color=col,marker=marker,linestyle=style,markersize=3,lw=1.3)
 best=s.loc[s.ndcg10.idxmax()]
 ax[0].scatter([best.L],[best.ndcg10],s=55,facecolors='none',edgecolors=col,zorder=4)
for i,(col,marker,style) in enumerate(zip(colors,markers,styles),1):
 s=curves[curves.snapshot==i].sort_values('L')
 ax[1].plot(s.L,s.ndcg10,label=f'R{i}',color=col,marker=marker,linestyle=style,markersize=2.5,lw=1.1)
 best=s.loc[s.ndcg10.idxmax()]
 ax[1].scatter([best.L],[best.ndcg10],s=55,facecolors='none',edgecolors=col,zorder=4)
for v in ax[:2]:
 v.set_xscale('log');v.set_xticks([10,100,1000,5000],['10','100','1k','5k']);v.set_xlabel('Truncation depth L');v.set_ylabel('Mean nDCG@10')
ax[0].set_title('(a) Same corpus, different queries',loc='left',fontsize=8)
ax[0].legend(fontsize=7,loc='lower right');ax[0].set_ylim(.61,.69)
ax[1].set_title('(b) Same queries, changing corpus',loc='left',fontsize=8)
ax[1].legend(fontsize=6.5,ncol=3,loc='lower right',columnspacing=.6,handlelength=1.5)
s=t[t.dataset.str.contains('chrono')].sort_values('dataset');x=np.arange(1,6)
ax[2].errorbar(x,s.delta,yerr=np.array([s.delta-s.ci_lower,s.ci_upper-s.delta]),color='#009988',marker='o',lw=1.2,markersize=3,capsize=2)
ax[2].axhline(0,color='#555555',lw=.7,ls='--');ax[2].set_xticks(x)
ax[2].set_xlabel('Corpus snapshot');ax[2].set_ylabel('Frozen L − full RRF\n(mean nDCG@10)')
ax[2].set_title('(c) Transfer of Round-1 selection',loc='left',fontsize=8)
save(fig,'transfer')
