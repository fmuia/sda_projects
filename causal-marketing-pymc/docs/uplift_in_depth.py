"""Anchor A (deep): uplift/HTE — estimator bake-off, confounding & sensitivity, euro policy."""
import numpy as np, pandas as pd, pymc as pm, pymc_bart as pmb
import matplotlib.pyplot as plt, json, warnings
from sklearn.linear_model import LogisticRegression
warnings.filterwarnings("ignore")
plt.rcParams.update({"figure.dpi":130,"font.size":9.5,"axes.spines.top":False,"axes.spines.right":False})
RNG=np.random.default_rng(7)
n=1400; M=50; DR=160; TU=160; c=8.0

# ---------- DGP ----------
def features():
    recency=RNG.uniform(5,330,n); frequency=RNG.poisson(5,n).astype(float)
    monetary=RNG.uniform(15,180,n); tenure=RNG.uniform(1,60,n); engage=RNG.beta(2,3,n)
    return np.column_stack([recency,frequency,monetary,tenure,engage])
sig=lambda z:1/(1+np.exp(-z))
def truth(X):
    recency,frequency,monetary,tenure,engage=X.T
    mu0=np.clip(20+1.4*frequency+0.25*monetary+12*engage-0.03*recency,0,None)
    persuadable=42*np.exp(-((recency-120)/70)**2)*sig(frequency-3)*sig(9*(engage-0.28))
    sleeping=-24*sig(9*(0.22-engage))*sig(1.2*(frequency-6))
    return mu0, persuadable+sleeping
X=features(); mu0,tau=truth(X)
recency,frequency,monetary,tenure,engage=X.T

# randomized vs observational (targeted selection: marketers historically mailed engaged/recent)
T_rand=RNG.integers(0,2,n).astype(float)
lin=1.8*(engage-0.4)+1.2*((150-recency)/150)+0.15*(frequency-5)
e_obs=sig(lin); T_obs=(RNG.uniform(size=n)<e_obs).astype(float)
def outcome(T): return mu0+tau*T+RNG.normal(0,8,n)
y_rand=outcome(T_rand); y_obs=outcome(T_obs)
print(f"ATE(true)={tau.mean():.2f} | obs treated share={T_obs.mean():.2f} | overlap e in[{e_obs.min():.2f},{e_obs.max():.2f}]")

# ---------- estimators (return CATE posterior samples, shape (S,n)) ----------
def _fit(Xtr,ytr,seed,m=M):
    with pm.Model() as mod:
        Xd=pm.Data("Xd",Xtr); mu=pmb.BART("mu",X=Xd,Y=ytr,m=m)
        sd=pm.HalfNormal("sd",15); pm.Normal("o",mu=mu,sigma=sd,observed=ytr,shape=mu.shape)
        idata=pm.sample(draws=DR,tune=TU,chains=2,cores=2,random_seed=seed,progressbar=False)
    return mod,idata
def _pred(mod,idata,Xnew,seed):
    with mod:
        pm.set_data({"Xd":Xnew})
        pp=pm.sample_posterior_predictive(idata,var_names=["mu"],sample_vars=["mu"],progressbar=False,random_seed=seed)
    return pp.posterior_predictive["mu"].values.reshape(-1,Xnew.shape[0])

def s_learner(X,T,y,s=1):
    Xa=np.column_stack([X,T]); mod,idata=_fit(Xa,y,s)
    X1=Xa.copy();X1[:,-1]=1; X0=Xa.copy();X0[:,-1]=0
    return _pred(mod,idata,X1,s+90)-_pred(mod,idata,X0,s+91)
def t_learner(X,T,y,s=1):
    m1,i1=_fit(X[T==1],y[T==1],s); m0,i0=_fit(X[T==0],y[T==0],s+1)
    return _pred(m1,i1,X,s+90)-_pred(m0,i0,X,s+91)
def bcf(X,T,y,phat,s=1):
    Xp=np.column_stack([X,phat])                      # propensity into prognostic part (RIC fix)
    with pm.Model() as mod:
        Xpd=pm.Data("Xp",Xp); Xtd=pm.Data("Xt",X); z=pm.Data("z",T)
        prog=pmb.BART("prog",X=Xpd,Y=y,m=M)
        tau_b=pmb.BART("tau",X=Xtd,Y=y,m=30)          # fewer trees -> shrink heterogeneity
        mu=pm.Deterministic("mu",prog+tau_b*z)
        sd=pm.HalfNormal("sd",15); pm.Normal("o",mu=mu,sigma=sd,observed=y,shape=mu.shape)
        idata=pm.sample(draws=DR,tune=TU,chains=2,cores=2,random_seed=s,progressbar=False)
    return idata.posterior["tau"].values.reshape(-1,n)

def metrics(cate,tag):
    m=cate.mean(0); lo,hi=np.quantile(cate,[.05,.95],0)
    return {"est":tag,"PEHE":float(np.sqrt(np.mean((m-tau)**2))),"corr":float(np.corrcoef(m,tau)[0,1]),
            "ATE_bias":float(m.mean()-tau.mean()),"cov90":float(np.mean((lo<=tau)&(tau<=hi)))}

# ---------- Part 1+2: bake-off on both regimes ----------
phat_rand=np.full(n,0.5)
lr=LogisticRegression(max_iter=1000).fit(np.column_stack([X,engage*frequency]),T_obs); phat_obs=lr.predict_proba(np.column_stack([X,engage*frequency]))[:,1]
rows=[]
print("randomized..."); 
rows.append({"regime":"randomized",**metrics(s_learner(X,T_rand,y_rand,10),"S-learner")})
rows.append({"regime":"randomized",**metrics(t_learner(X,T_rand,y_rand,20),"T-learner")})
rows.append({"regime":"randomized",**metrics(bcf(X,T_rand,y_rand,phat_rand,30),"BCF")})
print("observational...")
naive=(y_obs[T_obs==1].mean()-y_obs[T_obs==0].mean())
cate_s_o=s_learner(X,T_obs,y_obs,40); cate_t_o=t_learner(X,T_obs,y_obs,50); cate_bcf_o=bcf(X,T_obs,y_obs,phat_obs,60)
rows.append({"regime":"observational",**metrics(cate_s_o,"S-learner")})
rows.append({"regime":"observational",**metrics(cate_t_o,"T-learner")})
rows.append({"regime":"observational",**metrics(cate_bcf_o,"BCF")})
tbl=pd.DataFrame(rows)[["regime","est","PEHE","corr","ATE_bias","cov90"]].round(3)
print(tbl.to_string(index=False)); tbl.to_csv("bakeoff.csv",index=False)
print(f"naive diff-in-means (obs) ATE={naive:.2f} vs true {tau.mean():.2f}  (bias {naive-tau.mean():+.2f})")

# ---------- Fig A: (left) confounding bias in the ATE; (right) estimator failure mode ----------
np.save("arr_tau.npy",tau); np.save("arr_cate_s.npy",cate_s_o); np.save("arr_cate_t.npy",cate_t_o); np.save("arr_cate_bcf.npy",cate_bcf_o)
fig,ax=plt.subplots(1,2,figsize=(9.4,4.0))
# left: ATE estimates — naive (ignore X) is biased; adjusted methods land near truth
names=["naive\n(ignore X)","S-learner","T-learner","BCF"]
vals=[naive,cate_s_o.mean(),cate_t_o.mean(),cate_bcf_o.mean()]
cols=["#d95f0e","#c0c0c0","#2c7fb8","#238b45"]
ax[0].bar(names,vals,color=cols,alpha=.9); ax[0].axhline(tau.mean(),color="k",ls="--")
ax[0].text(3.1,tau.mean()+.2,f"true €{tau.mean():.1f}",fontsize=8,ha="right")
ax[0].set_ylabel("estimated ATE (€)"); ax[0].set_title("Confounding: ignoring X nearly doubles the ATE")
# right: heterogeneity recovery — S-learner (fails) vs BCF (works)
for cate,name,cl in [(cate_s_o,"S-learner",".7"),(cate_bcf_o,"BCF","#238b45")]:
    ax[1].scatter(tau,cate.mean(0),s=7,alpha=.4,label=f"{name} (PEHE {np.sqrt(np.mean((cate.mean(0)-tau)**2)):.1f})",
                  color=("#999999" if name=="S-learner" else cl))
lim=[tau.min()-3,tau.max()+3]; ax[1].plot(lim,lim,"k--",lw=1); ax[1].set_xlim(lim);ax[1].set_ylim(lim)
ax[1].set_xlabel("true τ(x)"); ax[1].set_ylabel("estimated CATE"); ax[1].legend(frameon=False,fontsize=8)
ax[1].set_title("Estimator choice: S-learner flattens heterogeneity")
fig.tight_layout(); fig.savefig("figA_confounding.png",bbox_inches="tight"); plt.close(fig)

# ---------- Fig B: overlap (positivity) ----------
fig,ax=plt.subplots(figsize=(5.4,3.4))
ax.hist(e_obs[T_obs==1],bins=30,alpha=.6,color="#2c7fb8",label="emailed",density=True)
ax.hist(e_obs[T_obs==0],bins=30,alpha=.6,color="#d95f0e",label="not emailed",density=True)
ax.set_xlabel("propensity  e(x)=P(email | x)"); ax.set_ylabel("density")
ax.set_title("Overlap check: do both groups exist everywhere?"); ax.legend(frameon=False)
fig.tight_layout(); fig.savefig("figB_overlap.png"); plt.close(fig)

# ---------- Fig C: calibration by true-effect decile (BCF obs) ----------
lo,hi=np.quantile(cate_bcf_o,[.05,.95],0); inside=(lo<=tau)&(tau<=hi)
dec=pd.qcut(tau,10,labels=False); covd=[inside[dec==k].mean() for k in range(10)]
fig,ax=plt.subplots(figsize=(5.4,3.4)); ax.bar(range(10),covd,color="#2c7fb8",alpha=.85)
ax.axhline(0.90,color="k",ls="--"); ax.set_ylim(0,1); ax.set_xlabel("decile of true effect (low→high)")
ax.set_ylabel("90% CI coverage"); ax.set_title("Is the uncertainty honest across the effect range?")
fig.tight_layout(); fig.savefig("figC_calibration.png"); plt.close(fig)

# ---------- Part 4: sensitivity to an UNOBSERVED confounder (fast linear sweep) ----------
# hidden U drives both emailing and spend with strength s; model adjusts for X only (not U).
def adjusted_ate(Xd,T,y):                 # covariate-adjusted OLS effect of T
    D=np.column_stack([np.ones(n),T,Xd]); beta,*_=np.linalg.lstsq(D,y,rcond=None); return beta[1]
strengths=np.linspace(0,12,25); est=[]
for s in strengths:
    U=RNG.normal(size=n)
    e=sig(lin+0.9*s*U); Tc=(RNG.uniform(size=n)<e).astype(float)
    yc=mu0+tau*Tc+ s*U +RNG.normal(0,8,n)           # U also lifts spend
    est.append(adjusted_ate(X,Tc,yc))
est=np.array(est)
# tipping point: strength at which adjusted ATE first exceeds cost c (would wrongly say "email everyone pays")
tip=strengths[np.argmax(est>c)] if np.any(est>c) else np.nan
fig,ax=plt.subplots(figsize=(5.6,3.6)); ax.plot(strengths,est,color="#2c7fb8",lw=2)
ax.axhline(tau.mean(),color="#238b45",ls="--",label=f"true ATE {tau.mean():.1f}")
ax.axhline(c,color="k",ls=":",label=f"cost €{c:.0f}")
if not np.isnan(tip): ax.axvline(tip,color="#d95f0e",lw=1); ax.text(tip,c+1,f" flips at s≈{tip:.1f}",fontsize=8,color="#d95f0e")
ax.set_xlabel("strength of unobserved confounder  (vs σ=8 noise)"); ax.set_ylabel("estimated ATE (adjusting for X only)")
ax.set_title("Sensitivity: how much hidden confounding overturns the call?"); ax.legend(frameon=False,fontsize=8)
fig.tight_layout(); fig.savefig("figD_sensitivity.png"); plt.close(fig)

# ---------- Part 5: euro policy on BCF(obs) posterior ----------
cate=cate_bcf_o; cm=cate.mean(0)
def profit_by_rank(rank): o=np.argsort(-rank); return np.cumsum(tau[o]-c)
frac=np.arange(1,n+1)/n; pc=profit_by_rank(cm); po=profit_by_rank(tau); k=int(np.argmax(pc))
# cost sensitivity: optimal profit & target-fraction vs c
cs=np.linspace(2,20,19); opt_profit=[]; opt_frac=[]
for cc in cs:
    pr=np.cumsum(tau[np.argsort(-cm)]-cc); kk=int(np.argmax(pr)); opt_profit.append(pr[kk]); opt_frac.append((kk+1)/n)
# confidence-bar sweep: profit from targeting where P(tau>c)>thr (realized on truth)
thrs=np.linspace(0.3,0.95,14); pw=(cate>c).mean(0); conf_profit=[float((tau[pw>t]-c).sum()) for t in thrs]
# value of information (per-customer option value of resolving uncertainty), in euros
voi_i=np.maximum(cate-c,0).mean(0)-np.maximum(cm-c,0); VOI=float(voi_i.sum())
straddle=((np.quantile(cate,.05,0)<c)&(np.quantile(cate,.95,0)>c))
res={"naive_ate":float(naive),"true_ate":float(tau.mean()),
     "profit_everyone":float((tau-c).sum()),"profit_model":float(pc[k]),"profit_oracle":float(po.max()),
     "profit_model_opt":float(pc[k]),"target_frac":float(frac[k]),
     "VOI_total":VOI,"n_straddle":int(straddle.sum()),"VOI_on_straddlers":float(voi_i[straddle].sum()),
     "sens_tip":float(tip) if not np.isnan(tip) else None}
json.dump({"metrics":rows,"policy":res},open("deepA_results.json","w"),indent=2)

fig,ax=plt.subplots(1,3,figsize=(11.4,3.5))
ax[0].plot(frac,pc,color="#2c7fb8",lw=2,label="model"); ax[0].plot(frac,po,color="#238b45",ls="--",lw=1.2,label="oracle")
ax[0].axhline(0,color="k",lw=.6); ax[0].axvline(frac[k],color="#2c7fb8",lw=.7,alpha=.5)
ax[0].plot(frac[k],pc[k],"o",color="#2c7fb8"); ax[0].set_title(f"Profit curve (stop @ {frac[k]*100:.0f}%, €{pc[k]:.0f})")
ax[0].set_xlabel("fraction contacted"); ax[0].set_ylabel("cumulative profit €"); ax[0].legend(frameon=False,fontsize=8)
ax[1].plot(cs,opt_profit,color="#2c7fb8",lw=2); ax1b=ax[1].twinx(); ax1b.plot(cs,np.array(opt_frac)*100,color="#d95f0e",lw=1.4,ls=":")
ax[1].axvline(c,color="k",ls=":",lw=1); ax[1].set_xlabel("discount cost c (€)"); ax[1].set_ylabel("optimal profit €",color="#2c7fb8")
ax1b.set_ylabel("% base contacted",color="#d95f0e"); ax[1].set_title("Policy vs cost assumption")
ax[2].plot(thrs,conf_profit,color="#2c7fb8",lw=2); ax[2].set_xlabel("confidence bar  P(τ>c) >"); ax[2].set_ylabel("realized profit €")
ax[2].set_title("Profit vs how sure we insist on being")
fig.tight_layout(); fig.savefig("figE_policy.png"); plt.close(fig)

print(json.dumps(res,indent=2))
print("saved figs A-E + deepA_results.json + bakeoff.csv")
