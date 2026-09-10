"""Static, complete-ranking results; Paul Tol Vibrant palette retained."""
from pathlib import Path
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[2];P=ROOT/'results/paper-experiments-v3';OUT=Path(__file__).parent
DS=['msmarco-passage-trec-dl-2019','msmarco-passage-trec-dl-2020','nfcorpus','scifact','trec-covid'];N=['DL19','DL20','NFCorpus','SciFact','COVID'];COL=['#0077BB','#EE7733','#009988','#EE3377','#33BBEE'];MARK=['o','s','^','D','v'];STYLE=['-','--','-.',':',(0,(5,1,1,1))]
plt.rcParams.update({'font.family':'sans-serif','font.sans-serif':['Arial','DejaVu Sans'],'font.size':8,'axes.spines.top':False,'axes.spines.right':False,'axes.axisbelow':True,'axes.grid':True,'axes.grid.axis':'y','grid.color':'#E5E7EB','grid.linewidth':.5,'legend.frameon':False,'pdf.fonttype':42,'svg.fonttype':'none'})
def save(fig,name):
 for ext in ['png','pdf','svg']:fig.savefig(OUT/f'{name}.{ext}',dpi=300,bbox_inches='tight')
 plt.close(fig)
c=pd.read_csv(P/'fixed-k.csv');g=pd.read_csv(P/'certificate-gaps.csv');a=pd.read_csv(P/'aggregate.csv')
fig,ax=plt.subplots(2,1,figsize=(3.4,3.8),layout='constrained')
for ds,n,col,marker,style in zip(DS,N,COL,MARK,STYLE):
 s=c[(c.dataset==ds)&(c.policy=='dibud')&(c.batch==1)&(c.k==20)];assert s.completed.eq(1).all();v=np.sort(s.cost)
 ax[0].step(np.r_[0,v,1e7],np.r_[0,np.arange(1,len(v)+1)/len(v),1],where='post',color=col,label=n,linestyle=style,lw=1.3)
 s=g[(g.dataset==ds)&(g.policy=='dibud')&(g.batch==1)];assert s.complete20.eq(1).all()
 ax[1].plot([.25,.5,.75,1],[s.k_at25.mean(),s.k_at50.mean(),s.k_at75.mean(),20],color=col,marker=marker,linestyle=style,markersize=3,label=n)
ax[0].set_xscale('symlog',linthresh=100);ax[0].set_xlim(0,1e7);ax[0].set_ylim(0,1.04);ax[0].set_xlabel('Sorted accesses');ax[0].set_ylabel('Fraction with exact Top-20');ax[0].set_title('(a) Full Top-20 completion cost',loc='left');ax[0].legend(fontsize=6.5,loc='lower right',ncol=2)
ax[1].set_xticks([.25,.5,.75,1],['25%','50%','75%','100%']);ax[1].set_ylim(0,21);ax[1].set_ylabel('Mean certified prefix length');ax[1].set_xlabel('Fraction of Top-20 completion cost');ax[1].set_title('(b) Prefix before completion',loc='left');save(fig,'cost')
fig,axes=plt.subplots(1,5,figsize=(7.1,1.9),layout='constrained')
for ax,ds,n in zip(axes,DS,N):
 for pol,col,style in [('balanced','#EE7733','--'),('dibud','#0077BB','-')]:
  s=a[(a.dataset==ds)&(a.policy==pol)&(a.batch==1)].sort_values('budget');assert np.allclose(s.mean_k_lower,s.mean_k_upper);ax.plot(s.budget,s.mean_k_lower,color=col,ls=style,label=pol.title())
 ax.set_xscale('log',base=2);ax.set_xticks([128,1024,10000],['128','1k','10k']);ax.set_ylim(0,102);ax.set_title(n,loc='left');ax.set_xlabel('Budget')
axes[0].set_ylabel('Mean prefix (cap 100)');axes[-1].legend(fontsize=6);save(fig,'yield')
# Keep temporal evidence separate: frozen v2 snapshots, all B=2048 endpoints observed.
fig,axes=plt.subplots(2,3,figsize=(7.1,3.5),layout='constrained')
for ax,ds,n in zip(axes.flat,DS,N):
 for pol,col,style,mark in [('balanced',COL[1],'--','s'),('dibud',COL[0],'-','o')]:
  s=a[(a.dataset==ds)&(a.policy==pol)&(a.batch==1)].sort_values('budget')
  ax.plot(s.budget,s.mean_k_lower,color=col,ls=style,marker=mark,ms=2.5,label=pol.title())
 ax.set_xscale('log',base=2);ax.set_xticks([128,1024,10000],['128','1k','10k']);ax.set_ylim(0,102);ax.set_title(n,loc='left');ax.set_xlabel('Access budget');ax.set_ylabel('Mean prefix (cap 100)')
t=pd.read_csv(ROOT/'results/paper-experiments-v2/aggregate.csv')
ax=axes.flat[5]
for pol,col,style,mark,values in [('balanced',COL[1],'--','s',[17.7,17.2,16.0333333333,15.3,14.8333333333]),('dibud',COL[0],'-','o',[18,17.5666666667,16.4,15.7666666667,15.1])]:
 rows=t[(t.policy==pol)&(t.batch==1)&(t.budget==2048)&t.dataset.str.startswith('trec-covid-chrono-')].sort_values('dataset')
 assert len(rows)==5 and np.allclose(rows.k20_lower,rows.k20_upper)
 values=rows.k20_lower.to_numpy()
 ax.plot(range(1,6),values,color=col,ls=style,marker=mark,ms=3,label=pol.title())
ax.set_title('Corpus snapshots (B=2048)',loc='left');ax.set_xticks(range(1,6));ax.set_xlabel('Round');ax.set_ylabel('Mean prefix (cap 20)');ax.legend(fontsize=7)
save(fig,'yield')
q=pd.read_csv(P/'quality-budget-summary.csv');q=q[q.target==.95].set_index('dataset').loc[DS]
fig,axes=plt.subplots(2,1,figsize=(3.4,3.3),layout='constrained')
for ax,col,title in [(axes[0],'quality_lower','Retained mean nDCG@20 (%)'),(axes[1],'cost_saving_lower','Fewer accesses (%)')]:
 vals=q[col].to_numpy()*100;ax.bar(N,vals,color=COL,width=.65);ax.set_ylim(0,110);ax.set_ylabel(title,fontsize=7)
 for x,v in enumerate(vals):ax.text(x,v+1,f'{v:.2f}',ha='center',fontsize=7)
 ax.tick_params(axis='x',labelsize=7)
axes[0].axhline(95,color='#555555',ls='--',lw=.8)
save(fig,'quality-cost')
