# visualize.py

# bar_chart(), heat_map(), iface_heat_map(), pareto_chart() → Graphical views of network counter deltas.

import os
import matplotlib.pyplot as plt
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
    plt.savefig(output_path)
    plt.close()

def heat_map(summary: Dict, output_path: str):
    """Generate a heat map for important metrics diffs per interface."""
    import numpy as np

    metric_ids = sorted(summary['important_metrics'].keys())
    data = []
    for mid in metric_ids:
        row = []
        for iface in range(1, 9):
            row.append(summary['important_metrics'][mid]['diffs'].get(iface, 0))
        data.append(row)

    data = np.array(data)
    fig, ax = plt.subplots(figsize=(12, 8))
    cax = ax.imshow(data, cmap='viridis', aspect='auto')
    ax.set_xticks(range(8))
    ax.set_xticklabels([f"Iface {i}" for i in range(1, 9)])
    ax.set_yticks(range(len(metric_ids)))
    ax.set_yticklabels([summary['important_metrics'][mid]['metric_name'] for mid in metric_ids])
    plt.title('Important Metrics Heat Map')
    plt.xlabel('Interface')
    plt.ylabel('Metric Name')
    fig.colorbar(cax, ax=ax)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
