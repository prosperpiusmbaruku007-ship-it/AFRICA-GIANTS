import subprocess, time, datetime, sys, os
T = [datetime.datetime(2026,11,26,h,m,tzinfo=datetime.timezone.utc) for h,m in ((7,30),(7,50),(8,15),(8,45),(9,15),(9,16))]
env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
for i,t in enumerate(T,1):
    while datetime.datetime.now(datetime.timezone.utc) < t: time.sleep(20)
    subprocess.run([sys.executable,"scratch/read_queue_ro.py",f"scratch/queue_snap_{i}.json"],env=env,timeout=500)
print("monitor done")
