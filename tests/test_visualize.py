# test_visualize

import sys
import os
import matplotlib.pyplot as plt

# Allow importing from net_prof without installing the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from net_prof import summarize
from net_prof.visualize import bar_chart, heat_map, iface1_barchart

# Set paths
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))

before = os.path.join(project_root, "example", "before.txt")
after = os.path.join(project_root, "example", "after.txt")

# Generate summary
summary = summarize(before, after)

# Display visualizations (instead of saving)
bar_chart(summary, output_path=None)  # Modified function will detect None and call plt.show()
heat_map(summary)

iface1_barchart(summary, "iface1_barchart.png")
