# engine.py

# collect(path: str) → Collects raw counter data from the system and saves it to path.
# summarize(before_path: str, after_path: str) → Loads both files and computes a structured summary:
# Diffs by interface
# Top N metrics per interface
# Zero vs non-zero count metrics
#dump(summary: dict) → Neatly prints summary to terminal.

import os
from typing import Dict, List

def load_lines(path: str) -> List[str]:
    """Read a file and return a list of its lines (no trailing newline)."""
    with open(path, 'r') as f:
        return [line.rstrip('\n') for line in f]

def parse_metric_name(raw: str) -> str:
    """Return the metric name (last whitespace-separated token)."""
    return raw.strip().split()[-1]

def parse_counter(raw: str) -> int:
    """Given 'value@timestamp', return the integer counter before the @."""
    return int(raw.split('@')[0])

def collect(output_file: str):
    """Collect a snapshot of counters and write to file (not currently implemented)."""
    raise NotImplementedError("collect() is not currently implemented. Use pre-collected dump files.")

def summarize(before_path: str, after_path: str) -> Dict:
    """Load metrics.txt and two dump files, compute differences, return summary dict."""
    metrics = load_lines(os.path.join(os.path.dirname(__file__), "data/metrics.txt"))
    before = load_lines(before_path)
    after = load_lines(after_path)

    num_metrics = len(metrics)
    num_interfaces = 8

    results = []
    for m_idx, raw_metric in enumerate(metrics):
        metric_id = m_idx + 1
        metric_name = parse_metric_name(raw_metric)
        for iface in range(1, num_interfaces + 1):
            idx = (iface - 1) * num_metrics + m_idx
            cnt_before = parse_counter(before[idx])
            cnt_after = parse_counter(after[idx])
            diff = cnt_after - cnt_before
            results.append({
                'iface': iface,
                'metric_id': metric_id,
                'metric_name': metric_name,
                'diff': diff
            })

    total_non_zero = sum(1 for r in results if r['diff'] != 0)
    non_zero_per_iface = {
        i: sum(1 for r in results if r['iface'] == i and r['diff'] != 0)
        for i in range(1, num_interfaces + 1)
    }

    top20_per_iface = {}
    for i in range(1, num_interfaces + 1):
        iface_rs = [r for r in results if r['iface'] == i]
        iface_rs.sort(key=lambda r: r['diff'], reverse=True)
        top20_per_iface[i] = iface_rs[:20]

    important_ids = [17,18,22,839,835,869,873,
                     564,565,613,614,
                     1600,1599,1598,1597,
                     1724]
    pivot = {}
    for r in results:
        mid = r['metric_id']
        if mid not in important_ids:
            continue
        pivot.setdefault(mid, { 'metric_name': r['metric_name'], 'diffs': {} })
        pivot[mid]['diffs'][r['iface']] = r['diff']

    return {
        'total_non_zero': total_non_zero,
        'non_zero_per_iface': non_zero_per_iface,
        'top20_per_iface': top20_per_iface,
        'important_metrics': pivot
    }

def dump(summary: Dict):
    """Nicely print summary to the console."""
    print(f"\nTotal non-zero diffs: {summary['total_non_zero']}/15120\n")

    print("Non-zero diffs by interface:")
    for iface, count in summary['non_zero_per_iface'].items():
        print(f"  Interface {iface:<2}: {count}/1890")
    print("\n")

    for iface, entries in summary['top20_per_iface'].items():
        print(f"Top 20 diffs for Interface {iface}:")
        print(f"{'Rank':<6}{'Metric ID':<12}{'Metric Name':<30}{'Difference':>12}")
        print('-' * 60)
        for rank, entry in enumerate(entries, start=1):
            print(
                f"{rank:<6}"
                f"{entry['metric_id']:<12}"
                f"{entry['metric_name']:<30}"
                f"{entry['diff']:>12}"
            )
        not_shown = summary['non_zero_per_iface'][iface] - len(entries)
        print(f"Total non-zero diffs not shown in Interface {iface}: {not_shown}\n")

    print("Important Metrics (diffs by interface):")
    id_w, name_w, iface_w = 15, 40, 15
    header = (
        f"{'Metric ID':<{id_w}} {'Metric Name':<{name_w}}"
        + ''.join(f" {'Iface'+str(i):<{iface_w}}" for i in range(1,9))
    )
    print(header)
    print('-' * len(header))
    for mid, data in summary['important_metrics'].items():
        row = f"{mid:<{id_w}} {data['metric_name']:<{name_w}}"
        for i in range(1,9):
            diff = data['diffs'].get(i, 0)
            row += f" {diff:<{iface_w}}"
        print(row)

