# test_html.py

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
dump_html(summary, "report.html")
