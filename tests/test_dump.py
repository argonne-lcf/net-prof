# test_dump

import sys
import os
# import subprocess

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from net_prof import summarize, dump # , dump_report

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))  # go up from tests/

before = os.path.join(project_root, "example", "before.txt")
after = os.path.join(project_root, "example", "after.txt")
metrics = os.path.join(project_root, "src", "net_prof", "data", "metrics.txt")

# If you want to test collect, uncomment below:
# collect("before.txt")
# subprocess.run(["ping", "google.com", "-c", "4"])
# collect("after.txt")
# if using collect make sure to get rid of hard-coded before and after.

summary = summarize(before, after)
dump(summary)

# dump_report stuff
# output_dir = "output"
# os.makedirs(output_dir, exist_ok=True)
# dump_report(summary, output=os.path.join(output_dir, "report.html"))
