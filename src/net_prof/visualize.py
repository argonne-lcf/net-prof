# visualize.py

# bar_chart(), heat_map(), iface_heat_map(), pareto_chart() → Graphical views of network counter deltas.

import os
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict

def bar_chart(summary: Dict, output_path: str):
    """Plot bar charts of total non-zero metrics per interface."""
    interfaces = list(summary['non_zero_per_iface'].keys())
    counts = list(summary['non_zero_per_iface'].values())

    plt.figure(figsize=(10, 6))
    plt.bar(interfaces, counts, color='skyblue')
    plt.title('Non-zero Metrics per Interface')
    plt.xlabel('Interface')
    plt.ylabel('Count')
    plt.xticks(interfaces)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path)
        plt.close()
    else:
        plt.show()

def heat_map(summary: Dict):
    """Heatmap: Top 20 highest diffs from iface1 across all interfaces."""
    top20_iface1 = summary['top20_per_iface'][1]
    metric_names = [entry['metric_name'] for entry in top20_iface1]
    metric_ids   = [entry['metric_id']   for entry in top20_iface1]

    # Construct data matrix: 20 rows (metrics), 8 columns (iface1–8)
    data = []
    for mid in metric_ids:
        row = []
        for iface in range(1, 9):
            # Get the diff for this metric on this iface
            metric = next(
                (r for r in summary['top20_per_iface'].get(iface, []) if r['metric_id'] == mid),
                None
            )
            row.append(metric['diff'] if metric else 0)
        data.append(row)

    data = np.array(data)

    fig, ax = plt.subplots(figsize=(12, 10))
    cax = ax.imshow(data, cmap='viridis', aspect='auto')
    
    ax.set_xticks(range(8))
    ax.set_xticklabels([f"Iface {i}" for i in range(1, 9)], rotation=45)
    
    ax.set_yticks(range(20))
    ax.set_yticklabels(metric_names)

    plt.title("Top 20 Diffs from Interface 1 Across All Interfaces")
    plt.xlabel("Interface")
    plt.ylabel("Metric")
    fig.colorbar(cax, ax=ax, label='Difference')
    plt.tight_layout()
    plt.show()
    
    
def generate_iface_barchart(summary: Dict, iface: int, output_path: str):
    """Generate a bar chart for the top 20 diffs for a given interface."""
    entries = summary['top20_per_iface'].get(iface, [])
    names = [e['metric_name'] for e in entries]
    diffs = [e['diff'] for e in entries]

    plt.figure(figsize=(12, 6))
    plt.barh(names, diffs, color='teal')
    plt.title(f'Top 20 Diffs - Interface {iface}')
    plt.xlabel('Difference')
    plt.ylabel('Metric Name')
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def iface1_barchart(summary: Dict, output_path: str):
    generate_iface_barchart(summary, 1, output_path)

def iface2_barchart(summary: Dict, output_path: str):
    generate_iface_barchart(summary, 2, output_path)

def iface3_barchart(summary: Dict, output_path: str):
    generate_iface_barchart(summary, 3, output_path)

def iface4_barchart(summary: Dict, output_path: str):
    generate_iface_barchart(summary, 4, output_path)

def iface5_barchart(summary: Dict, output_path: str):
    generate_iface_barchart(summary, 5, output_path)

def iface6_barchart(summary: Dict, output_path: str):
    generate_iface_barchart(summary, 6, output_path)

def iface7_barchart(summary: Dict, output_path: str):
    generate_iface_barchart(summary, 7, output_path)

def iface8_barchart(summary: Dict, output_path: str):
    generate_iface_barchart(summary, 8, output_path)
