# test_collect.py

# Not fully implemented!

import sys
import os
import json
# import subprocess

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
# lets you use: "from net_prof import summarize, dump" even though net_prof isn't installed as a package.
# remove after: pip install -e .


from net_prof import collect

collect("/home/kvelusamy/Downloads/dummy/sys/class/cxi/cxi0/device/telemetry/", "before.json")

if os.path.exists("before.json"):
    print("Success! before.json successfully created.")
else:
    print("Failure! before.json was not created.")

# load the JSON you just created
with open("before.json") as f:
    data = json.load(f)

print("\nCounters with a real group assignment:")
for idx, entry in enumerate(data, start=1):
    if entry["group"] != "UNGROUPED":
        print(f"{idx:4d}: {entry['counter_name']} → {entry['group']} ({entry['description']})")
        
print("Counters with non-zero values:")
for entry in data:
    if entry["value"] != 0:
        print(
            f'ID {entry["id"]}: '
            f'{entry["counter_name"]} = {entry["value"]} '
            f'(group: {entry["group"]})'
        )


