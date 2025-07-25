# compare.py

import sys
import os
import time
from net_prof import summarize, dump, dump_html, collect, compare # remove after: pip install -e .

# lets you use: "from net_prof import summarize, dump" even though net_prof isn't installed as a package.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
# Define where this script lives so we can anchor output paths
script_dir = os.path.dirname(os.path.abspath(__file__))

collect("/home/kvelusamy/Downloads/dummy/sys/class/cxi", os.path.join(script_dir, "beforeIdle.json"))
print(f"Waiting 3 seconds before moving onto after.json...")
time.sleep(3)
collect("/home/kvelusamy/Downloads/dummy/sys/class/cxi", os.path.join(script_dir, "afterIdle.json"))

beforeIdle = os.path.join(script_dir, "beforeIdle.json")
afterIdle = os.path.join(script_dir, "afterIdle.json")

collect("/home/kvelusamy/Downloads/dummy/sys/class/cxi", os.path.join(script_dir, "beforePing.json"))
print(f"Pinging google...")
os.system(f"ping -c 4 {"google.com"}") 
collect("/home/kvelusamy/Downloads/dummy/sys/class/cxi", os.path.join(script_dir, "afterPing.json"))

beforePing = os.path.join(script_dir, "beforePing.json")
afterPing = os.path.join(script_dir, "afterPing.json")

idletest = summarize(beforeIdle, afterIdle)
pingtest = summarize(beforePing, afterPing)

compare(idletest,
    pingtest,
    "report_idle_vs_ping.html",
    label_a="Idle baseline",
    label_b="Ping workload"
)
