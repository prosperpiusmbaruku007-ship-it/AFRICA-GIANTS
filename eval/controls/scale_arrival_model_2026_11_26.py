# Offline arrival / cost model behind docs/decisions/2026-11-26_cpu_split_not_built.md and the 2026-11-26 scale audit.
# ASSUMPTIONS, not measurements of real traffic: 3 questions/participant/day, evening burst (hourly weights below), T4 $0.59/h,
# 600 s scaledown, 90 s cold load, no concurrency per container, 1 reviewer. Run: python eval/controls/scale_arrival_model_2026_11_26.py
# Offline arrival model (assumptions printed). Not a measurement of real traffic.
import random, statistics as st
random.seed(7)
W=[.2,.1,.1,.1,.2,.5,1.5,3,5,6,6,6,6,5,5,5,5,6,8,12,17,13,6,2]   # hourly weights: evening peak 20:00-21:00 ~ 16%
S=sum(W); W=[w/S for w in W]
COLD=90; SCALEDOWN=600; PREFLEN=0.4
def day(n_part, qpp=3, R=1, f=0.0):
    n=int(round(n_part*qpp*(1-f))); ev=[]
    for _ in range(n):
        h=random.choices(range(24),W)[0]; ev.append(h*3600+random.random()*3600)
    ev.sort(); svc=lambda: random.choice([6,25])
    cont=[]   # each: warm_until
    gpu_s=0; cold=0; peak=0; busy_until=[]
    sends=[0]*24; rev=[0]*24; qh=[0]*24
    for t in ev:
        h=int(t//3600); qh[h]+=1
        s=svc(); free=[c for c in cont if c['free']<=t<=c['warm']]
        if free:
            c=free[0]; start=t; acks=1 if s>=12 else 0
        else:
            c={'free':0,'warm':0,'created':t}; cont.append(c); start=t+COLD; cold+=1; gpu_s+=COLD; acks=2
        gpu_s+= s + (SCALEDOWN if True else 0)*0  # accounted below via warm windows
        c['free']=start+s; 
        new_warm=c['free']+SCALEDOWN
        # billed idle tail: extension of warm window beyond previous warm_until
        gpu_s+= max(0,new_warm-max(c['warm'],c['free']))-0 if False else 0
        c['warm']=new_warm
        hold = 1 if random.random()<PREFLEN else 0
        sends[h]+= acks+1+hold + 1.5*R      # participant acks+answer+holding, reviewer push (+renotify avg)
        rev[h]+= 1.5                         # pushes to EACH reviewer
    # billed seconds = union of [start, warm] per container ~ approximate by summing per-container spans
    billed=sum(c['warm']-c['created'] for c in cont)
    pts=sorted([(c['created'],1) for c in cont]+[(c['warm'],-1) for c in cont]); cur=mx=0
    for _,d in pts: cur+=d; mx=max(mx,cur)
    return n, qh, sends, rev, cold, mx, billed
def run(n_part,R=1,days=300,f=0.0):
    cost=[];colds=[];pk_q=[];pk_s=[];pk_rev=[];conts=[]
    for _ in range(days):
        random.seed(random.random())
        n,qh,sends,rev,cold,nc,billed=day(n_part,R=R,f=f)
        # warm-time model: each cold start opens a ~(COLD+svc+SCALEDOWN) period, merges handled by warm reuse
        gpu=billed
        cost.append(gpu*0.000164); colds.append(cold/n if n else 0)
        pk_q.append(max(qh)); pk_s.append(max(sends)); pk_rev.append(max(rev)); conts.append(nc)
    p=lambda a,q: sorted(a)[int(len(a)*q)-1]
    print(f"{n_part:>4} participants R={R}: q/day {n_part*3:>4} | peak-hr q mean {st.mean(pk_q):5.1f} p95 {p(pk_q,.95):4d} | peak-hr SENDS global mean {st.mean(pk_s):6.1f} p95 {p(pk_s,.95):6.1f} | peak-hr pushes/reviewer p95 {p(pk_rev,.95):5.1f} | cold-start share {st.mean(colds)*100:4.0f}% | PEAK CONCURRENT containers mean {st.mean(conts):4.1f} max {max(conts)} | GPU $/day mean {st.mean(cost):5.2f} p95 {p(cost,.95):5.2f}")


for f in (0.0,0.045,0.25):
    print('GPU-skip share f=',f)
    for n in (10,25,50): run(n,R=1,f=f)
