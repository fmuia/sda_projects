"""Anchor B (deep): synthetic control geo-lift — estimator comparison, placebo inference, euro decision."""
import numpy as np, pandas as pd, pymc as pm
import matplotlib.pyplot as plt, json, warnings
from scipy.optimize import minimize
warnings.filterwarnings("ignore")
plt.rcParams.update({"figure.dpi":130,"font.size":9.5,"axes.spines.top":False,"axes.spines.right":False})
RNG=np.random.default_rng(3)

# ---------- DGP: weekly sales panel, factor structure so controls can reconstruct treated ----------
W=60; LAUNCH=40; nD=30                      # 60 weeks, launch wk40, 30 DMAs (1 treated + 29 controls)
t=np.arange(W)
trend=0.4*t
season=8*np.sin(2*np.pi*t/26)+4*np.sin(2*np.pi*t/13)
macro=np.cumsum(RNG.normal(0,1.2,W))       # common shock (AR-ish) — this is what breaks naive pre/post
F=np.column_stack([trend,season,macro])    # common factors
levels=RNG.uniform(80,140,nD)
loads=RNG.uniform(0.6,1.4,(nD,3))
sales=levels[:,None]+loads@F.T+RNG.normal(0,3,(nD,W))   # (nD, W)
treated_idx=0
LIFT_PCT=0.12                              # true campaign lift: +12% of treated baseline, post-launch
base_treated=sales[treated_idx,LAUNCH:].mean()
sales_obs=sales.copy()
true_effect=LIFT_PCT*(levels[treated_idx]+loads[treated_idx]@F.T)   # per-week true lift (only applied post)
sales_obs[treated_idx,LAUNCH:]+=true_effect[LAUNCH:]
y_tr=sales_obs[treated_idx]; Ctrl=np.delete(sales_obs,treated_idx,axis=0)   # (29, W)
pre=slice(0,LAUNCH); post=slice(LAUNCH,W)
true_total=float(true_effect[post].sum()); true_avg=float(true_effect[post].mean())
print(f"true avg weekly lift €{true_avg:.1f} | true total post lift €{true_total:.0f}")

# ---------- fast simplex synthetic control (for placebos) ----------
def sc_weights(target_pre, donors_pre):
    J=donors_pre.shape[0]
    def loss(w): r=target_pre-w@donors_pre; return r@r
    cons=[{"type":"eq","fun":lambda w:w.sum()-1}]; bnds=[(0,1)]*J
    w0=np.full(J,1/J)
    res=minimize(loss,w0,bounds=bnds,constraints=cons,method="SLSQP")
    return res.x
def sc_effect(target, donors, pre, post):
    w=sc_weights(target[pre],donors[:,pre]); cf=w@donors
    return target-cf, w                      # gap over all weeks, weights

# ---------- Bayesian synthetic control (main estimate, with uncertainty) ----------
with pm.Model() as m:
    w=pm.Dirichlet("w",a=np.ones(Ctrl.shape[0]))
    sd=pm.HalfNormal("sd",5)
    mu=pm.math.dot(w,Ctrl[:,pre])
    pm.Normal("obs",mu=mu,sigma=sd,observed=y_tr[pre])
    idata=pm.sample(1000,tune=1000,chains=4,cores=4,random_seed=1,progressbar=False,target_accept=0.95)
Wp=idata.posterior["w"].values.reshape(-1,Ctrl.shape[0])          # (S, 29)
cf_post=Wp@Ctrl                                                    # (S, W) counterfactual draws
effect_post=y_tr[None,:]-cf_post                                  # (S, W)
eff_mean=effect_post.mean(0); eff_lo,eff_hi=np.quantile(effect_post,[.05,.95],0)
total_post=effect_post[:,post].sum(1)                            # posterior of total lift
pre_rmse=np.sqrt(np.mean((eff_mean[pre])**2))

# ---------- Depth 1: naive estimators (biased) vs SC ----------
naive_prepost=y_tr[post].mean()-y_tr[pre].mean()                 # ignores trend/season/macro
naive_vs_avg=(y_tr[post]-Ctrl[:,post].mean(0)).mean()           # treated minus average control
sc_avg=eff_mean[post].mean()
bakeB={"true_avg":true_avg,"naive_prepost":float(naive_prepost),
       "naive_vs_avgctrl":float(naive_vs_avg),"synthetic_control":float(sc_avg)}
print("estimator (avg weekly lift €):",json.dumps(bakeB,indent=2))

# ---------- Depth 2: placebo-in-space (permutation inference) ----------
placebo_gaps=[]; donors_all=sales_obs.copy()
for j in range(nD):
    if j==treated_idx: continue
    others=np.delete(np.arange(nD),[treated_idx,j])              # exclude real treated + this placebo
    gap,_=sc_effect(sales_obs[j],sales_obs[others],pre,post)
    # only keep placebos with a decent pre-fit (Abadie discards bad fits)
    if np.sqrt(np.mean(gap[pre]**2))<3*pre_rmse: placebo_gaps.append(gap)
placebo_gaps=np.array(placebo_gaps)
real_gap,w_main=sc_effect(y_tr,Ctrl,pre,post)
real_post=real_gap[post].mean()
placebo_post=placebo_gaps[:,post].mean(1)
p_space=float((np.sum(np.abs(placebo_post)>=abs(real_post))+1)/(len(placebo_post)+1))
print(f"placebo-in-space: real avg gap €{real_post:.1f}; {len(placebo_gaps)} placebos; permutation p={p_space:.3f}")

# ---------- Depth 2b: placebo-in-time (fake launch, expect ~0) ----------
FAKE=30
gap_fake,_=sc_effect(y_tr[:LAUNCH],Ctrl[:,:LAUNCH],slice(0,FAKE),slice(FAKE,LAUNCH))
fake_effect=float(gap_fake[FAKE:LAUNCH].mean())
print(f"placebo-in-time (fake launch wk{FAKE}, pre-real-launch): avg gap €{fake_effect:.1f} (should be ~0)")

# ---------- Depth 3: euro decision ----------
CAMPAIGN_COST=300.0   # EUR 300k campaign cost (sales in EUR000)
p_beats=float((total_post>CAMPAIGN_COST).mean())
roi_draws=total_post-CAMPAIGN_COST
res={"true_total":true_total,"total_mean":float(total_post.mean()),
     "total_lo":float(np.quantile(total_post,.05)),"total_hi":float(np.quantile(total_post,.95)),
     "pre_rmse":float(pre_rmse),"p_space":p_space,"fake_time_effect":fake_effect,
     "campaign_cost":CAMPAIGN_COST,"P_lift_gt_cost":p_beats,
     "roi_mean":float(roi_draws.mean()),"bakeoff":bakeB}
json.dump(res,open("deepB_results.json","w"),indent=2); print(json.dumps(res,indent=2))

# ---------- FIGURES ----------
# B1: treated vs synthetic counterfactual
fig,ax=plt.subplots(figsize=(7.4,3.8))
ax.plot(t,y_tr,color="#111",lw=1.8,label="treated DMA (observed)")
ax.plot(t,cf_post.mean(0),color="#2c7fb8",lw=1.6,ls="--",label="synthetic counterfactual")
ax.fill_between(t,np.quantile(cf_post,.05,0),np.quantile(cf_post,.95,0),color="#2c7fb8",alpha=.2)
ax.axvline(LAUNCH,color="#d95f0e",lw=1); ax.text(LAUNCH+.4,ax.get_ylim()[0]+3,"launch",color="#d95f0e",fontsize=8)
ax.fill_between(t[post],y_tr[post],cf_post.mean(0)[post],color="#238b45",alpha=.25)
ax.set_xlabel("week"); ax.set_ylabel("weekly sales (€000)"); ax.set_title("Treated DMA vs its synthetic control")
ax.legend(frameon=False,fontsize=8); fig.tight_layout(); fig.savefig("figB1_sc.png"); plt.close(fig)

# B2: placebo-in-space spaghetti
fig,ax=plt.subplots(figsize=(7.4,3.8))
for g in placebo_gaps: ax.plot(t,g,color="#bbbbbb",lw=.7,alpha=.7)
ax.plot(t,real_gap,color="#238b45",lw=2,label="treated DMA")
ax.axvline(LAUNCH,color="#d95f0e",lw=1); ax.axhline(0,color="k",lw=.6)
ax.set_xlabel("week"); ax.set_ylabel("gap vs synthetic (€000)")
ax.set_title(f"Placebo test: is the treated gap an outlier?  (permutation p={p_space:.3f})")
ax.legend(frameon=False,fontsize=8); fig.tight_layout(); fig.savefig("figB2_placebo.png"); plt.close(fig)

# B3: euro decision — estimator bar + total lift posterior
fig,ax=plt.subplots(1,2,figsize=(9.6,3.6))
nm=["naive\npre/post","treated −\navg control","synthetic\ncontrol","TRUE"]
vv=[naive_prepost,naive_vs_avg,sc_avg,true_avg]; cl=["#d95f0e","#e6ab02","#2c7fb8","#238b45"]
ax[0].bar(nm,vv,color=cl,alpha=.9); ax[0].axhline(true_avg,color="k",ls="--",lw=.8)
ax[0].set_ylabel("avg weekly lift (€000)"); ax[0].set_title("Naive estimators are confounded by trend/season")
ax[1].hist(total_post,bins=40,color="#2c7fb8",alpha=.85)
ax[1].axvline(CAMPAIGN_COST,color="#d95f0e",lw=1.4); ax[1].text(CAMPAIGN_COST,ax[1].get_ylim()[1]*.9,f" cost €{CAMPAIGN_COST:.0f}",fontsize=8)
ax[1].axvline(true_total,color="k",ls="--",lw=.8); ax[1].text(true_total,ax[1].get_ylim()[1]*.75,f" true",fontsize=8)
ax[1].set_xlabel("total incremental sales, post period (€000)")
ax[1].set_title(f"Rollout decision:  P(lift > cost) = {p_beats:.2f}")
fig.tight_layout(); fig.savefig("figB3_decision.png"); plt.close(fig)
print("saved figB1-B3 + deepB_results.json")
