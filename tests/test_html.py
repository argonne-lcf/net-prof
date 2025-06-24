# test_html.py
"""
This test outputs a html file named report.html using a predefined before.txt, after.txt, and metrics.txt.
"""


import sys
import os
# import subprocess

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
# lets you use: "from net_prof import summarize, dump" even though net_prof isn't installed as a package.
# remove after: pip install -e .

from net_prof import summarize, dump, dump_html # , dump_report

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))  # go up from tests/

before = os.path.join(project_root, "example", "before.txt")
after = os.path.join(project_root, "example", "after.txt")
metrics = os.path.join(project_root, "src", "net_prof", "data", "metrics.txt")

summary = summarize(before, after)

# Ensure output directory for charts exists within tests/ or project root
output_html = os.path.join(script_dir, "report.html")  # e.g., tests/report.html
os.makedirs(os.path.join(script_dir, "charts"), exist_ok=True)

dump_html(summary, output_html)

print(f"HTML report created at {output_html}")
