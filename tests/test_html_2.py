# test_html_2.py
"""
This test builds upon test_html.py, and instead of using a predetermined before/after.txt test_html_2.py uses collect() to store before and after as .json files, storing the results to report_2.html.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
# lets you use: "from net_prof import summarize, dump" even though net_prof isn't installed as a package.
# remove after: pip install -e .

from net_prof import summarize, dump, dump_html, collect # , dump_report

# Define where this script lives so we can anchor output paths
script_dir = os.path.dirname(os.path.abspath(__file__))

collect("/home/kvelusamy/Downloads/dummy/sys/class/cxi/cxi0/device/telemetry", os.path.join(script_dir, "before.json"))
# Inbetween these two functions call something like os.execute('ping google.com')
collect("/home/kvelusamy/Downloads/dummy/sys/class/cxi/cxi0/device/telemetry", os.path.join(script_dir, "after.json"))

before = os.path.join(script_dir, "before.json")
after = os.path.join(script_dir, "after.json")

summary = summarize(before, after)

# Ensure output directory for charts exists within tests/ or project root
output_html = os.path.join(script_dir, "report_2.html")  # e.g., tests/report.html
os.makedirs(os.path.join(script_dir, "charts"), exist_ok=True)

dump_html(summary, output_html)

print(f"HTML report created at {output_html}")
