# visualize.py — Graphical views of network counter deltas

import matplotlib.pyplot as plt
import numpy as np
from collections import Counter
from itertools import islice
from typing import Dict


# -----------------------------------------------------------------------------
# Bar charts for counter *group* and *unit* frequencies
# -----------------------------------------------------------------------------

def group_barchart(summary: Dict,
                   output_path: str,
                   top_n: int = 15,
                   *,
                   exclude: set[str] = {"UNGROUPED"}):
    """Top-N groups by # counters, skipping 'UNGROUPED' by default."""
    col = summary.get("collected", [])
    c = Counter(
        g
        for e in col
        for g in e.get("groups", [])
        if g not in exclude
    )
    if not c:            # nothing left to plot
        print("No grouped counters to plot"); return

    labels, counts = zip(*islice(c.most_common(top_n), 0, top_n))
    plt.figure(figsize=(12, 6))
    plt.barh(labels, counts)
    plt.title(f"Top {top_n} Counter Groups")
    plt.xlabel("# Counters")
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig(output_path); plt.close()


def unit_barchart(summary: Dict,
                  output_path: str,
                  *,
                  exclude: set[str] = {"No Units"}):
    """Bars for counter *units* (e.g. packets, flits), skipping 'No Units'."""
    col = summary.get("collected", [])
    c = Counter(
        (e.get("units") or ["No Units"])[0]
        for e in col
        if (e.get("units") or ["No Units"])[0] not in exclude
    )
    if not c:
        print("No unit-tagged counters to plot"); return

    labels, counts = zip(*sorted(c.items(), key=lambda kv: kv[1], reverse=True))
    plt.figure(figsize=(10, 5))
    plt.bar(labels, counts)
    plt.title("Counters by Unit")
    plt.ylabel("# Counters")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(output_path); plt.close()


# -----------------------------------------------------------------------------
# Non‑zero diff counts per interface
# -----------------------------------------------------------------------------

def non_zero_bar_chart(
    summary: Dict,
    output_path: str | None = None,
    *,
    title: str = "Non‑zero Metrics per Interface",
    facecolor: str | None = None,
) -> None:
    """Bar chart of **total non‑zero counter diffs** for each interface."""
    iface_diffs = summary.get("non_zero_per_iface", {})
    if not iface_diffs:
        print("[non_zero_bar_chart] No diff data found – chart skipped.")
        return

    interfaces = sorted(iface_diffs)
    counts = [iface_diffs[i] for i in interfaces]

    plt.figure(figsize=(10, 6))
    plt.bar(interfaces, counts, color=facecolor)
    plt.title(title)
    plt.xlabel("Interface")
    plt.ylabel("Non‑zero counter diffs")
    plt.xticks(interfaces)
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()

    if output_path:
        plt.savefig(output_path)
        plt.close()
    else:
        plt.show()


# -----------------------------------------------------------------------------
# Heat‑map of per‑interface diffs for chosen metrics
# -----------------------------------------------------------------------------

def heat_map(
    summary: Dict,
    metric_ids: list[int] | None = None,
    output_path: str | None = None,
    *,
    cmap: str = "viridis",
):
    """Heat‑map showing the diff value of *metric_ids* across interfaces.

    If *metric_ids* is ``None`` the 20 metrics with the highest diff on
    **Interface 1** are plotted (old behaviour).
    """
    # Determine which metrics to plot
    top20_iface1 = summary.get("top20_per_iface", {}).get(1, [])
    if metric_ids is None:
        metric_ids = [entry["metric_id"] for entry in top20_iface1]

    if not metric_ids:
        print("[heat_map] No metrics to plot – chart skipped.")
        return None

    metric_names: list[str] = []
    data_rows: list[list[int]] = []

    for mid in metric_ids:
        # Try to grab a human‑readable name
        name_entry = next((e for e in top20_iface1 if e["metric_id"] == mid), None)
        metric_names.append(name_entry["metric_name"] if name_entry else f"Metric {mid}")

        row = []
        for iface in range(1, 9):
            metric = next(
                (r for r in summary.get("top20_per_iface", {}).get(iface, []) if r["metric_id"] == mid),
                None,
            )
            row.append(metric["diff"] if metric else 0)
        data_rows.append(row)

    data = np.array(data_rows)

    fig, ax = plt.subplots(figsize=(12, 0.45 * len(metric_ids) + 2))
    cax = ax.imshow(data, cmap=cmap, aspect="auto")

    ax.set_xticks(range(8))
    ax.set_xticklabels([f"Iface {i}" for i in range(1, 9)], rotation=45)
    ax.set_yticks(range(len(metric_ids)))
    ax.set_yticklabels(metric_names)

    ax.set_title("Interface‑wise Counter Diffs")
    ax.set_xlabel("Interface")
    ax.set_ylabel("Metric")
    fig.colorbar(cax, ax=ax, label="Difference")
    plt.tight_layout()

    if output_path:
        fig.savefig(output_path)
        plt.close()
    else:
        plt.show()

    return fig


# -----------------------------------------------------------------------------
# Per‑interface top‑20 diff bar chart
# -----------------------------------------------------------------------------

def generate_iface_barchart(
    summary: Dict,
    iface: int,
    output_path: str,
    *,
    color: str | None = None,
) -> None:
    """Generate a bar chart for the **top‑20 diffs** on a single interface."""
    entries = summary.get("top20_per_iface", {}).get(iface, [])
    if not entries:
        print(f"[generate_iface_barchart] No data for iface {iface} – chart skipped.")
        return

    names = [e["metric_name"] for e in entries]
    diffs = [e["diff"] for e in entries]

    plt.figure(figsize=(12, 6))
    plt.barh(names, diffs, color=color)
    plt.title(f"Top 20 Diffs – Interface {iface}")
    plt.xlabel("Difference")
    plt.ylabel("Metric Name")
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
