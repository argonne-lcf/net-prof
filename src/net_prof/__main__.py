# __main__

# Used for internal testing or dev commands, not exposed to users.
#dump_report(summary: dict, output="report.html")→ Generates HTML summary using internal visualizations.

import os
from net_prof.engine import summarize, dump
from net_prof.visualize import bar_chart, heat_map
import importlib.resources as pkg_resources
import net_prof.data  # this is your data/ directory as a package

def main():
    # Hardcoded user input files
    before_path = "example/before.txt"
    after_path = "example/after.txt"

    # Locate the internal metrics.txt using importlib
    with pkg_resources.path(net_prof.data, "metrics.txt") as metrics_path:
        # Generate summary
        summary = summarize(before_path, after_path, str(metrics_path))
        dump(summary)

    # Create output directory
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    # Visualize
    bar_chart_path = os.path.join(output_dir, "bar_chart.png")
    heat_map_path = os.path.join(output_dir, "heat_map.png")

    bar_chart(summary, bar_chart_path)
    heat_map(summary, heat_map_path)

    print(f"\nCharts saved to {output_dir}/")

if __name__ == "__main__":
    main()

