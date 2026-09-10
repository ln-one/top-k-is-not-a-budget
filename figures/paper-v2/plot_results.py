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
t=pd.read_csv(P/'transfer-summary.csv');a=pd.read_csv(P/'aggregate.csv');c=pd.read_csv(P/'fixed-k.csv',dtype={'query_id':str});g=pd.read_csv(P/'certificate-gaps.csv',dtype={'query_id':str});q=pd.read_csv(P/'quality-budget-summary.csv')
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
fig,ax=plt.subplots(2,1,figsize=(3.4,3.6),layout='constrained')
for ds,n,col,marker,style in zip(DS,N,colors,markers,styles):
 s=c[(c.dataset==ds)&(c.policy=='dibud')&(c.batch==1)&(c.k==20)];cost=np.sort(s[s.completed==1].cost);xx=np.r_[0,cost,10000];yy=np.r_[0,np.arange(1,len(cost)+1)/len(s),len(cost)/len(s)];ax[0].step(xx,yy,where='post',label=n,color=col,lw=1.3,linestyle=style)
 s=g[(g.dataset==ds)&(g.policy=='dibud')&(g.batch==1)&(g.complete20==1)];ax[1].plot([.25,.5,.75,1],[s.k_at25.mean(),s.k_at50.mean(),s.k_at75.mean(),20],color=col,label=n,markersize=3,marker=marker,linestyle=style)
ax[0].set_xscale('symlog',linthresh=100);ax[0].set_xlim(0,10000);ax[0].set_ylim(0,1.04);ax[0].set_xlabel('Sorted accesses');ax[0].set_ylabel('Fraction with observed\nexact Top-20');ax[0].set_title('(a) Completion cost',loc='left');ax[0].legend(fontsize=7)
ax[1].set_xticks([.25,.5,.75,1],['25%','50%','75%','100%']);ax[1].set_xlabel('Fraction of observed Top-20 cost');ax[1].set_ylabel('Mean certified prefix length');ax[1].set_ylim(0,21);ax[1].set_title('(b) Prefix before completion',loc='left');save(fig,'cost')
fig,axes=plt.subplots(2,3,figsize=(7.1,4.05),layout='constrained')
for ax,ds,n in zip(axes.flat,DS,N):
 for pol,(col,label) in methods.items():
  s=a[(a.dataset==ds)&(a.policy==pol)&(a.batch==1)].sort_values('budget');ax.plot(s.budget,s.mean_k_lower,label=label,color=col,lw=1.5,**method_styles[pol]);ax.fill_between(s.budget,s.mean_k_lower,s.mean_k_upper,color=col,alpha=.12)
 ax.set_xscale('log',base=2);ax.set_xticks([128,1024,10000],['128','1024','10000']);ax.set_ylim(0,102);ax.set_title(n,loc='left');ax.set_ylabel('Mean prefix (cap 100)');ax.set_xlabel('Access budget')
ax=axes.flat[-1]
for pol,(col,label) in methods.items():
 s=a[(a.dataset.str.contains('chrono'))&(a.policy==pol)&(a.batch==1)&(a.budget==2048)].sort_values('dataset');ax.plot(range(1,6),s.k20_lower,color=col,label=label,lw=1.5,**method_styles[pol])
ax.set_ylim(0,21);ax.set_xticks(range(1,6));ax.set_title('Snapshots, B=2048',loc='left');ax.set_ylabel('Mean prefix (cap 20)');ax.set_xlabel('Corpus snapshot');ax.legend(fontsize=7);save(fig,'yield')
fig,ax=plt.subplots(2,1,figsize=(3.4,3.6),layout='constrained')
s=q[q.target==.95].set_index('dataset').loc[DS];x=np.arange(5)
ax[0].bar(x,100*s.quality_lower,color=colors,width=.6);ax[0].errorbar(x,100*s.quality_lower,yerr=[np.zeros(5),100*(s.quality_upper-s.quality_lower)],fmt='none',color='black',capsize=3);ax[0].axhline(95,color='#555555',ls='--',lw=.8);ax[0].set_ylim(0,102);ax[0].set_xticks(x,N);ax[0].set_ylabel('Held-out nDCG@20\nretained (%)');ax[0].set_title('(a) 95% calibration target',loc='left')
ax[1].bar(x,100*s.cost_saving_lower,color=colors,width=.6);ax[1].set_xticks(x,N);ax[1].set_ylim(0,100);ax[1].set_ylabel('Access reduction (%)');ax[1].set_title('(b) Access reduction',loc='left')
for i,v in enumerate(s.cost_saving_lower):ax[1].text(i,100*v+2,('≥' if s.baseline20_completion.iloc[i]<1 else '')+f'{100*v:.1f}',ha='center',fontsize=7)
save(fig,'quality-cost')
# Distribution and granularity retained as standalone supporting figure.
fig,ax=plt.subplots(2,1,figsize=(3.4,3.6),layout='constrained')
for pol,(col,label) in methods.items():
 s=a[(a.dataset.isin(DS))&(a.policy==pol)&(a.batch==1)].groupby('budget').agg({'at20_lower':'mean','at20_upper':'mean','empty_lower':'mean','empty_upper':'mean'})
 ax[0].plot(s.index,s.at20_lower,color=col,label=label,lw=1.5,**method_styles[pol]);ax[0].fill_between(s.index,s.at20_lower,s.at20_upper,color=col,alpha=.12);ax[1].plot(s.index,s.empty_upper,color=col,label=label,lw=1.5,**method_styles[pol]);ax[1].fill_between(s.index,s.empty_lower,s.empty_upper,color=col,alpha=.12)
for v in ax:v.set_xscale('log',base=2);v.set_xlabel('Access budget');v.set_ylim(0,1.02);v.legend(fontsize=7)
ax[0].set_ylabel('Fraction returning at least 20');ax[1].set_ylabel('Fraction returning no results');save(fig,'delivery')
