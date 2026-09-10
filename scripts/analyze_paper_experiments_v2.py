"""Analysis of preregistered access-budget experiments; retain censored bounds."""
import hashlib,json,math
from pathlib import Path
import numpy as np
import pandas as pd
from pilot_simple_schedulers import DATASETS
from run_paper_experiments_v2 import BUDGETS,KS,LS
OUT=Path('results/paper-experiments-v2');rng=np.random.default_rng(20260910);R=2000

def save(name,rows):pd.DataFrame(rows).to_csv(OUT/name,index=False)
def ci(x):return np.quantile(x,[.025,.975]).tolist()
def folds(ds,qids,temporal=False):
    if temporal:return {q:(int(q)-1)%5 for q in qids}
    return {q:i%5 for i,q in enumerate(sorted(qids,key=lambda q:hashlib.sha256((ds+'/'+q).encode()).hexdigest()))}
def bootmean(x):
    x=np.asarray(x,float);return ci(x[rng.integers(len(x),size=(R,len(x)))].mean(axis=1))
def main():
 b=pd.read_csv(OUT/'budget-yield.csv',dtype={'query_id':str});c=pd.read_csv(OUT/'fixed-k.csv',dtype={'query_id':str});t=pd.read_csv(OUT/'transfer-grid.csv',dtype={'query_id':str})
 summaries=[];paired=[];auc=[];cost=[];gaps=[]
 for (ds,pol,batch,B),g in b.groupby(['dataset','policy','batch','budget']):
    q=g.k.to_numpy();known=g.known.to_numpy().astype(bool)
    summaries.append(dict(dataset=ds,policy=pol,batch=batch,budget=B,n=len(g),coverage=known.mean(),mean_k_lower=q.mean(),mean_k_upper=g.k_upper.mean(),k20_lower=np.minimum(q,20).mean(),k20_upper=np.minimum(g.k_upper,20).mean(),median_k_lower=np.median(q),p10_k_lower=np.quantile(q,.1),empty_lower=((q==0)&known).mean(),empty_upper=(q==0).mean(),at10_lower=(q>=10).mean(),at10_upper=((q>=10)|~known).mean(),at20_lower=(q>=20).mean(),at20_upper=((q>=20)|~known).mean()))
 for (ds,batch,B),g in b.groupby(['dataset','batch','budget']):
    d=g[g.policy=='dibud'].set_index('query_id');bal=g[g.policy=='balanced'].set_index('query_id').loc[d.index]
    for cap in (20,100):
      lo=np.minimum(d.k,cap).to_numpy()-np.minimum(bal.k_upper,cap).to_numpy();hi=np.minimum(d.k_upper,cap).to_numpy()-np.minimum(bal.k,cap).to_numpy()
      lci=bootmean(lo);uci=bootmean(hi)
      paired.append(dict(dataset=ds,batch=batch,budget=B,cap=cap,n=len(d),both_known=((d.known==1)&(bal.known==1)).mean(),delta_lower=lo.mean(),delta_upper=hi.mean(),ci_lower=lci[0],ci_upper=uci[1]))
 for (ds,q,pol,batch),g in b.groupby(['dataset','query_id','policy','batch']):
    g=g.sort_values('budget');x=np.log(g.budget.to_numpy());den=x[-1]-x[0]
    auc.append(dict(dataset=ds,query_id=q,policy=pol,batch=batch,lower=np.trapezoid(g.k.to_numpy()/100,x)/den,upper=np.trapezoid(g.k_upper.to_numpy()/100,x)/den,complete=int(g.known.all())))
 a=pd.DataFrame(auc);save('auc-per-query.csv',auc);aa=[]
 for (ds,batch),g in a.groupby(['dataset','batch']):
    d=g[g.policy=='dibud'].set_index('query_id');z=g[g.policy=='balanced'].set_index('query_id').loc[d.index]
    lo=d.lower-z.upper;hi=d.upper-z.lower
    aa.append(dict(dataset=ds,batch=batch,n=len(d),dibud_lower=d.lower.mean(),dibud_upper=d.upper.mean(),balanced_lower=z.lower.mean(),balanced_upper=z.upper.mean(),delta_lower=lo.mean(),delta_upper=hi.mean(),ci_lower=bootmean(lo)[0],ci_upper=bootmean(hi)[1],wins=(lo>1e-12).sum(),losses=(hi< -1e-12).sum(),ties=((abs(lo)<1e-12)&(abs(hi)<1e-12)).sum(),ambiguous=((lo<=1e-12)&(hi>=-1e-12)&~((abs(lo)<1e-12)&(abs(hi)<1e-12))).sum()))
 for (ds,pol,batch,k),g in c[c.k.isin(KS)].groupby(['dataset','policy','batch','k']):
    n=len(g);lower=np.sort(g.lower_bound.to_numpy());upper=np.sort(np.where(g.completed,g.cost,np.inf));qs={}
    for label,p in [('median',.5),('p90',.9),('p95',.95)]:
        ix=math.ceil(p*n)-1;qs[label+'_lower']=lower[ix];qs[label+'_upper']=upper[ix]
    cost.append(dict(dataset=ds,policy=pol,batch=batch,k=k,n=n,completion=g.completed.mean(),mean_cost_lower=g.lower_bound.mean(),**qs))
 for (ds,q,pol,batch),g in c[(c.k<=20)].groupby(['dataset','query_id','policy','batch']):
    g=g.sort_values('k');done=g[g.completed==1];C=done.cost.to_numpy();inc=np.diff(np.r_[0,C]);complete=len(done)==20
    gaps.append(dict(dataset=ds,query_id=q,policy=pol,batch=batch,complete20=int(complete),last_k=len(done),last_cost=C[-1] if len(C) else 0,terminal_accesses=g.terminal_accesses.iloc[0],unresolved_accesses=g.terminal_accesses.iloc[0]-(C[-1] if len(C) else 0),max_gap=inc.max() if len(inc) else 0,max_gap_rank=int(inc.argmax()+1) if len(inc) else 0,max_share=inc.max()/C[-1] if complete else np.nan,k_at25=(C<=.25*C[-1]).sum() if complete else np.nan,k_at50=(C<=.5*C[-1]).sum() if complete else np.nan,k_at75=(C<=.75*C[-1]).sum() if complete else np.nan))
 save('aggregate.csv',summaries);save('paired.csv',paired);save('auc-aggregate.csv',aa);save('cost-summary.csv',cost);save('certificate-gaps.csv',gaps)
 # Full-L cross-fitting: select by calibration nDCG10, independent held-out IDs.
 tr=[];cal=[];foldrows=[];ts=[]
 groups=[([ds],False) for ds in DATASETS]+[([f'trec-covid-chrono-r{i}' for i in range(1,6)],True)]
 for dslist,temporal in groups:
    first=t[t.dataset==dslist[0]];ids=sorted(first.query_id.unique());fd=folds(dslist[0],ids,temporal);n=len(ids)
    calib=first.pivot(index='query_id',columns='L',values='ndcg10').loc[ids,list(LS)].to_numpy()
    for q in ids:foldrows.append(dict(group=dslist[0],query_id=q,fold=fd[q]))
    bootstrap={ds:np.zeros((R,2)) for ds in dslist}
    for f in range(5):
      train=np.array([i for i,q in enumerate(ids) if fd[q]!=f]);test=np.array([i for i,q in enumerate(ids) if fd[q]==f])
      means=calib[train].mean(axis=0);choice=int(np.argmax(means));L=LS[choice]
      cal.append(dict(group=dslist[0],fold=f,L=L,calibration_n=len(train),heldout_n=len(test),calibration_ndcg10=means[choice]))
      train_draw=rng.choice(train,size=(R,len(train)));test_draw=rng.choice(test,size=(R,len(test)));selected=calib[train_draw].mean(axis=1).argmax(axis=1)
      for ds in dslist:
        dg=t[t.dataset==ds];mat=dg.pivot(index='query_id',columns='L',values='ndcg10').loc[ids,list(LS)].to_numpy();ref=dg.groupby('query_id').full_ndcg10.first().loc[ids].to_numpy()
        chosen=dg[dg.L==L].set_index('query_id')
        for ix in test:
          row=chosen.loc[ids[ix]];tr.append(dict(dataset=ds,query_id=ids[ix],fold=f,L=L,ndcg10=row.ndcg10,full_ndcg10=row.full_ndcg10,ordered20=row.ordered20,overlap20=row.overlap20,accesses=row.accesses))
        bootstrap[ds][:,0]+=mat[test_draw,selected[:,None]].sum(axis=1)/n;bootstrap[ds][:,1]+=ref[test_draw].sum(axis=1)/n
    for ds in dslist:
      rows=pd.DataFrame([r for r in tr if r['dataset']==ds]);interval=ci(bootstrap[ds][:,0]-bootstrap[ds][:,1])
      ts.append(dict(dataset=ds,n=n,L_choices=','.join(str(x['L']) for x in cal[-5:]),ndcg10=rows.ndcg10.mean(),full_ndcg10=rows.full_ndcg10.mean(),delta=rows.ndcg10.mean()-rows.full_ndcg10.mean(),ci_lower=interval[0],ci_upper=interval[1],ordered20=rows.ordered20.mean(),overlap20=rows.overlap20.mean(),accesses=rows.accesses.mean()))
 save('transfer-folds.csv',foldrows);save('transfer-calibration.csv',cal);save('transfer-test.csv',tr);save('transfer-summary.csv',ts)
 # Top20 quality vs same-policy completion cost. All-query savings use an upper
 # bound on budget cost / lower bound on exact completion cost when censored.
 qb=b[(b.batch==1)&(b.policy=='dibud')].copy();cc=c[(c.batch==1)&(c.policy=='dibud')&(c.k==20)].set_index(['dataset','query_id'])
 for i,row in qb.iterrows():
    x=cc.loc[(row.dataset,row.query_id)];qb.loc[i,'baseline_cost_lower']=x.lower_bound
    qb.loc[i,'capped_cost_upper']=min(row.budget,x.cost) if x.completed else row.budget
    qb.loc[i,'ndcg20_upper']=row.ndcg20 if row.known or row.k>=20 else row.full_ndcg20
 qs=[]
 def quality_summary(ds,g,**extra):
    ref=g.full_ndcg20.sum();comp=g[g.baseline20_complete==1]
    return dict(dataset=ds,n=len(g),**extra,quality_lower=g.ndcg20.sum()/ref if ref else np.nan,quality_upper=g.ndcg20_upper.sum()/ref if ref else np.nan,cost_saving_lower=max(0.,1-g.capped_cost_upper.sum()/g.baseline_cost_lower.sum()),baseline20_completion=g.baseline20_complete.mean(),completed_subset_n=len(comp),completed_subset_saving=1-comp.capped_cost_upper.sum()/comp.cost20.sum() if len(comp) else np.nan,at20=(g.k>=20).mean(),zero_upper=(g.k==0).mean())
 for (ds,B),g in qb.groupby(['dataset','budget']):qs.append(quality_summary(ds,g,budget=B))
 save('quality-cost-grid.csv',qs);selectedrows=[];qcal=[];qsummary=[]
 for ds in DATASETS:
    dg=qb[qb.dataset==ds];ids=sorted(dg.query_id.unique());fd=folds(ds,ids);arr=dg.pivot(index='query_id',columns='budget',values='ndcg20').loc[ids,list(BUDGETS)].to_numpy();ref=dg.groupby('query_id').full_ndcg20.first().loc[ids].to_numpy()
    lookup=dg.set_index(['query_id','budget'])
    for target in (.9,.95,.99):
      rows=[]
      for f in range(5):
        train=[i for i,q in enumerate(ids) if fd[q]!=f];test=[q for q in ids if fd[q]==f];den=ref[train].sum();rat=arr[train].sum(axis=0)/den if den else np.zeros(len(BUDGETS));eligible=np.flatnonzero(rat>=target);idx=int(eligible[0]) if len(eligible) else len(BUDGETS)-1;B=BUDGETS[idx]
        qcal.append(dict(dataset=ds,target=target,fold=f,budget=B,calibration_retention=rat[idx],calibration_success=int(len(eligible)>0)))
        for q in test:
          r=lookup.loc[(q,B)].to_dict();r.update(query_id=q,budget=B,target=target,fold=f);rows.append(r);selectedrows.append(r)
      summary=quality_summary(ds,pd.DataFrame(rows),target=target);summary['budget_choices']=','.join(str(x['budget']) for x in qcal[-5:]);summary['successful_folds']=sum(x['calibration_success'] for x in qcal[-5:]);qsummary.append(summary)
 save('quality-cost-per-query.csv',qb.to_dict('records'));save('quality-budget-calibration.csv',qcal);save('quality-budget-heldout.csv',selectedrows);save('quality-budget-summary.csv',qsummary)
 (OUT/'bootstrap-config.json').write_text(json.dumps(dict(replicates=R,seed=20260910,transfer='nested calibration reselection and disjoint heldout resampling; same heldout identity across snapshots',paired='query-level',quality_budget='heldout point estimates, no significance claim'),indent=2))
 print(pd.DataFrame(aa).to_string(index=False));print(pd.DataFrame(qsummary).to_string(index=False));print(pd.DataFrame(ts).to_string(index=False))
if __name__=='__main__':main()
