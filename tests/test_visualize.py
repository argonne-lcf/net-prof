# test_visualize.py
"""
test_visualize.py calls functions from net_prof.visualize for testing.
"""

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

bar_chart(summary, output_path=None)  # Modified function will detect None for output_path, won't save the .png and just call plt.show()
heat_map(summary) # This function will just display (plt.show()) without adding an argument for output_path.
iface1_barchart(summary, "iface1_barchart.png") # This function will create a barchart named iface1_barchart.png, saving it to dir without. NOTE: I don't use plt.show for this function, thats why it doesn't display as pop-up.
