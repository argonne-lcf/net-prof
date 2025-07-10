# engine.py

import glob
import os
import json
import re
import csv
from typing import Dict, List, Tuple, Any, Optional
from .visualize import (
    iface1_barchart, iface2_barchart, iface3_barchart, iface4_barchart,
    iface5_barchart, iface6_barchart, iface7_barchart, iface8_barchart
)
from datetime import datetime, timezone

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

def load_grouping_rules(rules_path: str) -> List[Dict]:
    """Load grouping rules from a CSV into compiled regex patterns."""
    rules: List[Dict] = []
    with open(rules_path, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)  # comma-delimited
        for row in reader:
            pattern = row.get('Regex')
            if not pattern:
                continue
            rules.append({
                'regex': re.compile(pattern, re.IGNORECASE),
                'group': row.get('Counter_Group', 'UNGROUPED'),
                'description': row.get('Counter_Description', 'No description'),
                'unit': row.get('Unit', 'No Units')
            })
    return rules

def match_all_groups(counter_name: str, rules: List[Dict]) -> Tuple[List[str], List[str]]:
    """
    Return three parallel lists:
      - all groups whose regex matches counter_name
      - all corresponding descriptions
    If none match, returns (["UNGROUPED"], ["No description"], ["No Units"]).
    """
    groups, descs, units = [], [], []
    for rule in rules:
        if rule['regex'].match(counter_name):
            groups.append(rule['group'])
            descs.append(rule['description'])
            units.append(rule['unit'])
    if not groups:
        return ["UNGROUPED"], ["No description"], ["No Units"]
    return groups, descs, units

def _collect_one_interface(telemetry_dir: str, interface_id: int) -> List[Dict[str, Any]]:
    """
    Read a single /…/cxiX/device/telemetry directory and return a list
    of counter dicts for that one interface.
    """
    rules_path = os.path.join(os.path.dirname(__file__), 'data', 'grouping_rules.csv')
    rules = load_grouping_rules(rules_path)

    collected: List[Dict[str, Any]] = []
    files = sorted(f for f in os.listdir(telemetry_dir)
                   if os.path.isfile(os.path.join(telemetry_dir, f)))
    print(f"  [iface {interface_id}] Found {len(files)} files")

    for idx, filename in enumerate(files, start=1):
        filepath = os.path.join(telemetry_dir, filename)
        raw = open(filepath, 'r').read().strip()
        if '@' not in raw:
            continue
        value_str, timestamp_str = raw.split('@', 1)
        try:
            value = int(value_str)
        except ValueError:
            continue
        try:
            timestamp = float(timestamp_str)
        except ValueError:
            timestamp = None
            
        human_ts = (
        datetime.fromtimestamp(timestamp, timezone.utc)
        .isoformat()
        if timestamp is not None else None
        )

        groups, descriptions, units = match_all_groups(filename, rules)
        collected.append({
            'id':            idx,
            'interface':     interface_id,
            'counter_name':  filename,
            'value':         value,
            'timestamp':     timestamp,
            'timestamp_ISO_8601': human_ts,
            'groups':         groups,
            'descriptions':   descriptions,
            'units': units
        })

    return collected

def collect(input_path: str, output_file: str):
    """
    Collect counters from either a single telemetry dir or the entire /sys/class/cxi/ tree.
    Writes a merged JSON list into output_file.
    Raises ValueError on invalid input.
    """
    # Normalize and verify the base path exists
    input_path = os.path.normpath(input_path)
    if not os.path.isdir(input_path):
        raise ValueError(f"Path {input_path!r} does not exist or is not a directory.")
    
    # Collect start_time
    start_time = datetime.now(timezone.utc)
    
    all_entries: List[Dict[str, Any]] = []

    basename      = os.path.basename(input_path)
    parent        = os.path.basename(os.path.dirname(input_path))
    grandparent   = os.path.basename(os.path.dirname(os.path.dirname(input_path)))

    # Single-interface mode: basename is “telemetry” and grandparent is “cxi<digit>”
    if basename == "telemetry" and re.match(r"cxi\d+", grandparent):
        # sanity check: directory not empty
        files = [f for f in os.listdir(input_path)
                 if os.path.isfile(os.path.join(input_path, f))]
        if not files:
            raise ValueError(f"Telemetry directory {input_path!r} contains no files.")
        
        iface_num = int(grandparent.replace("cxi", "")) + 1
        print(f"Collecting interface {iface_num} from {input_path}")
        all_entries = _collect_one_interface(input_path, iface_num)

    # Multi-interface mode: parent of cxi* subdirs
    elif os.path.isdir(input_path) and any(re.fullmatch(r"cxi\d+", d) for d in os.listdir(input_path)):
        print(f"Scanning for telemetry under {input_path}")
        found_any = False
        for entry in sorted(os.listdir(input_path)):
            if re.fullmatch(r"cxi\d+", entry):
                telemetry_dir = os.path.join(input_path, entry, "device", "telemetry")
                if os.path.isdir(telemetry_dir):
                    # sanity check each telemetry dir
                    files = [f for f in os.listdir(telemetry_dir)
                             if os.path.isfile(os.path.join(telemetry_dir, f))]
                    if not files:
                        print(f"  Warning: {telemetry_dir!r} is empty, skipping.")
                        continue
                    iface_num = int(entry.replace("cxi", "")) + 1
                    print(f"Collecting interface {iface_num} from {telemetry_dir}")
                    all_entries.extend(_collect_one_interface(telemetry_dir, iface_num))
                    found_any = True
        if not found_any:
            raise ValueError(f"No valid cxi*/device/telemetry subfolders found under {input_path!r}")

    else:
        # Neither telemetry nor parent-of-cxi*, bail out
        raise ValueError(
            f"Path {input_path!r} is neither a telemetry directory "
            "nor a parent of cxi* interfaces."
        )
    
    # Collect end_time, calculate duration
    end_time = datetime.now(timezone.utc)
    duration = (end_time - start_time).total_seconds()
    
    meta = {
        "input_path":  input_path,
        "started_at":  start_time.isoformat(),
        "finished_at": end_time.isoformat(),
        "duration_s":  (end_time - start_time).total_seconds()
    }

    out = {
        "meta":     meta,
        "counters": all_entries
    }

    with open(output_file, "w") as out_f:
        json.dump(out, out_f, indent=2)
    print(f"Collected {len(all_entries)} counters in {meta['duration_s']:.2f}s → {output_file}")

def summarize(before_path: str,
              after_path: str,
              metrics_path: Optional[str] = None
             ) -> Dict[str, Any]:
    """
    Load metrics definitions and two counter dumps (txt or json), compute differences,
    and return a structured summary including collected json data and metadata if provided.
    """
    # locate metrics.txt
    if metrics_path is None:
        metrics_path = os.path.join(
            os.path.dirname(__file__),
            'data',
            'metrics.txt'
        )
    metrics = load_lines(metrics_path)

    # detect JSON vs. plain-text dumps
    is_json = before_path.lower().endswith('.json') and after_path.lower().endswith('.json')
    if is_json:
        before_json = json.load(open(before_path))
        after_json  = json.load(open(after_path))

        # pull out metadata blocks (if collect() wrote them)
        before_meta = before_json.get('meta', {})
        after_meta  = after_json .get('meta', {})

        # pull out the actual counter lists
        before_list = before_json.get('counters', before_json)
        after_list  = after_json .get('counters',  after_json)
    else:
        before_meta = {}
        after_meta  = {}
        before_list = None  # not used in non-JSON mode
        after_list  = None
        before = load_lines(before_path)
        after  = load_lines(after_path)

    num_metrics    = len(metrics)
    num_interfaces = 8

    # build diff results
    results: List[Dict[str, Any]] = []
    for m_idx, raw_metric in enumerate(metrics):
        metric_id   = m_idx + 1
        metric_name = parse_metric_name(raw_metric)
        for iface in range(1, num_interfaces + 1):
            if is_json:
                cnt_before = next(
                    (e['value'] for e in before_list
                     if e['counter_name'].endswith(metric_name) and e['interface'] == iface),
                    0
                )
                cnt_after = next(
                    (e['value'] for e in after_list
                     if e['counter_name'].endswith(metric_name) and e['interface'] == iface),
                    0
                )
            else:
                idx = (iface - 1) * num_metrics + m_idx
                cnt_before = parse_counter(before[idx])
                cnt_after  = parse_counter(after[idx])

            diff = cnt_after - cnt_before
            results.append({
                'iface':        iface,
                'metric_id':    metric_id,
                'metric_name':  metric_name,
                'diff':         diff
            })

    # summary stats
    total_non_zero = sum(1 for r in results if r['diff'] != 0)
    non_zero_per_iface = {
        i: sum(1 for r in results if r['iface'] == i and r['diff'] != 0)
        for i in range(1, num_interfaces + 1)
    }

    # top-20 per interface, sorted by absolute diff
    top20_per_iface: Dict[int, List[Dict[str, Any]]] = {}
    for i in range(1, num_interfaces + 1):
        iface_rs = [r for r in results if r['iface'] == i]
        iface_rs.sort(key=lambda r: abs(r['diff']), reverse=True)
        top20_per_iface[i] = iface_rs[:20]

    # pivot out the “important” metrics
    important_ids = [
        17, 18, 22, 839, 835, 869, 873,
        564, 565, 613, 614,
        1600, 1599, 1598, 1597,
        1724
    ]
    pivot: Dict[int, Dict[str, Any]] = {}
    for r in results:
        mid = r['metric_id']
        if mid not in important_ids:
            continue
        pivot.setdefault(mid, {
            'metric_name': r['metric_name'],
            'diffs': {}
        })
        pivot[mid]['diffs'][r['iface']] = r['diff']

    # assemble and return the summary
    return {
        'before_meta':       before_meta,
        'after_meta':        after_meta,
        'total_non_zero':    total_non_zero,
        'non_zero_per_iface': non_zero_per_iface,
        'top20_per_iface':   top20_per_iface,
        'important_metrics': pivot,
        'collected':         before_list if is_json else []
    }


def dump(summary: Dict[str, Any]):
    """Nicely print summary to the console."""
    print(f"\nTotal non-zero diffs: {summary['total_non_zero']}\n")
    print("Non-zero diffs by interface:")
    for iface, count in summary['non_zero_per_iface'].items():
        print(f"  Interface {iface:<2}: {count}\n")
    for iface, entries in summary['top20_per_iface'].items():
        print(f"Top 20 diffs for Interface {iface}:")
        print(f"{'Rank':<6}{'Metric ID':<12}{'Metric Name':<30}{'Difference':>12}")
        print('-'*60)
        for rank, entry in enumerate(entries, start=1):
            print(f"{rank:<6}{entry['metric_id']:<12}{entry['metric_name']:<30}{entry['diff']:>12}")
        not_shown = summary['non_zero_per_iface'][iface] - len(entries)
        print(f"Total non-zero diffs not shown in Interface {iface}: {not_shown}\n")
    print("Important Metrics (diffs by interface):")
    id_w, name_w, iface_w = 15, 40, 15
    header = f"{'Metric ID':<{id_w}} {'Metric Name':<{name_w}}" + ''.join(f" {'Iface'+str(i):<{iface_w}}" for i in range(1,9))
    print(header)
    print('-'*len(header))
    for mid, data in summary['important_metrics'].items():
        row = f"{mid:<{id_w}} {data['metric_name']:<{name_w}}"
        for i in range(1,9):
            diff = data['diffs'].get(i, 0)
            row += f" {diff:<{iface_w}}"
        print(row)
        
        
def dump_html(summary: dict, output_file: str):
    """
    Write the summary as a self-contained HTML report with charts.
    """

    # ------------------------------------------------------------------ #
    # 1.  Make /charts dir & render 8 bar-charts                         #
    # ------------------------------------------------------------------ #
    charts_dir = os.path.join(os.path.dirname(output_file), "charts")
    existed = os.path.isdir(charts_dir)
    os.makedirs(charts_dir, exist_ok=True)
    if existed:
        print(f"Charts directory already exists at: {charts_dir}")
    else:
        print(f"Created charts directory at:      {charts_dir}")

    iface1_barchart(summary, os.path.join(charts_dir, "iface1.png"))
    iface2_barchart(summary, os.path.join(charts_dir, "iface2.png"))
    iface3_barchart(summary, os.path.join(charts_dir, "iface3.png"))
    iface4_barchart(summary, os.path.join(charts_dir, "iface4.png"))
    iface5_barchart(summary, os.path.join(charts_dir, "iface5.png"))
    iface6_barchart(summary, os.path.join(charts_dir, "iface6.png"))
    iface7_barchart(summary, os.path.join(charts_dir, "iface7.png"))
    iface8_barchart(summary, os.path.join(charts_dir, "iface8.png"))
    print(f"Generated 8 chart images in:       {charts_dir}")

    now = datetime.now(timezone.utc)

    # ------------------------------------------------------------------ #
    # 2.  Start HTML / CSS                                               #
    # ------------------------------------------------------------------ #
    html: list[str] = []
    html.append(f"<html><head><title>Net-Prof Report — {now}</title>")
    html.append(r"""
<style>
 body  { font-family: system-ui, sans-serif; margin:0; padding:2rem; background:#fafafa; }
 main  { max-width:1200px; margin:auto; }
 h1,h2 { margin-top:0 }
 table { border-collapse:collapse; width:100%; margin:1.5rem 0; font-size:0.9rem;
         background:#fff; box-shadow:0 1px 3px rgba(0,0,0,.05); }
 th,td { border:1px solid #e0e0e0; padding:0.45rem 0.65rem; text-align:left; }
 th    { background:#f5f5f5 }
 tr:nth-child(even) { background:#fafafa }
 tr:hover { background:#f0f7ff }
 summary { cursor:pointer; font-weight:600 }
 details>summary { padding:0.35rem; border-radius:4px }
 details[open]>summary { background:#e8f0fe }
 img   { border:1px solid #ddd; border-radius:4px; margin-bottom:1rem; max-width:100% }
</style></head><body><main>
""")

    # ------------------------------------------------------------------ #
    # 3.  Header & meta                                                  #
    # ------------------------------------------------------------------ #
    html.append(f"<h1>Net-Prof Summary <small style='font-size:0.6em'>(created {now})</small></h1>")
    html.append(f"<h2>Total Non-zero Diffs: {summary['total_non_zero']} / 15120</h2>")

    bm = summary.get("before_meta", {})
    am = summary.get("after_meta",  {})

    if bm:
        html.append(f"<p><strong>Before snapshot</strong> collected from "
                    f"{bm['input_path']}<br>"
                    f"Started at:  {bm['started_at']}<br>"
                    f"Finished at: {bm['finished_at']} "
                    f"(took {bm['duration_s']:.2f}s)</p>")

    if bm and am and 'finished_at' in bm and 'started_at' in am:
        gap = (datetime.fromisoformat(am['started_at']) -
               datetime.fromisoformat(bm['finished_at'])).total_seconds()
        html.append(f"<p><strong>Operation between collection</strong>: (took {gap:.2f}s)</p>")

    if am:
        html.append(f"<p><strong>After snapshot</strong> collected from "
                    f"{am['input_path']}<br>"
                    f"Started at:  {am['started_at']}<br>"
                    f"Finished at: {am['finished_at']} "
                    f"(took {am['duration_s']:.2f}s)</p>")

    # ------------------------------------------------------------------ #
    # 4.  Non-zero per-iface table                                       #
    # ------------------------------------------------------------------ #
    html.append("<h3>Non-zero Diffs by Interface</h3>")
    html.append("<table><tr><th>Interface</th><th>Non-zero Count</th></tr>")
    for iface, count in summary['non_zero_per_iface'].items():
        html.append(f"<tr><td>Interface {iface}</td><td>{count} / 1890</td></tr>")
    html.append("</table>")

    # ------------------------------------------------------------------ #
    # 5.  NEW  — Counters-per-group table                                #
    # ------------------------------------------------------------------ #
    collected = summary.get("collected", [])
    group_counts: dict[str, int] = {}
    for entry in collected:
        for g in entry.get("groups", []):
            group_counts[g] = group_counts.get(g, 0) + 1

    if group_counts:
        html.append("<h3>Counters per Group</h3>")
        html.append("<table><tr><th>Group</th><th># Counters</th></tr>")
        # sort by descending count
        for g, n in sorted(group_counts.items(), key=lambda kv: kv[1], reverse=True):
            html.append(f"<tr><td>{g}</td><td>{n}</td></tr>")
        html.append("</table>")

    # ------------------------------------------------------------------ #
    # 6.  Charts section (collapsed)                                     #
    # ------------------------------------------------------------------ #
    html.append("<details>")
    html.append("<summary><h2>Top 20 Diffs by Interface — Charts</h2></summary>")
    for i in range(1, 9):
        html.append(f"<h4>Interface {i}</h4>")
        html.append(f"<img src='charts/iface{i}.png' alt='Interface {i} bar chart'>")
    html.append("</details>")

    # ------------------------------------------------------------------ #
    # 7.  Top-20 raw tables (collapsed)                                  #
    # ------------------------------------------------------------------ #
    html.append("<details>")
    html.append("<summary><h2>Top 20 Diffs by Interface — Raw Tables</h2></summary>")
    for iface, entries in summary['top20_per_iface'].items():
        html.append(f"<h4>Interface {iface}</h4>")
        html.append("<table><tr><th>Rank</th><th>Metric ID</th><th>Metric Name</th><th>Diff</th></tr>")
        for rank, entry in enumerate(entries, start=1):
            html.append(f"<tr><td>{rank}</td><td>{entry['metric_id']}</td>"
                        f"<td>{entry['metric_name']}</td><td>{entry['diff']}</td></tr>")
        html.append("</table>")
    html.append("</details>")

    # ------------------------------------------------------------------ #
    # 8.  Important metrics (collapsible)                                #
    # ------------------------------------------------------------------ #
    html.append("<details>")
    html.append("<summary><h2>Important Metrics</h2></summary>")
    html.append("<table><tr><th>Metric ID</th><th>Metric Name</th>" +
                "".join(f"<th>Iface {i}</th>" for i in range(1, 9)) + "</tr>")
    for mid, data in summary['important_metrics'].items():
        html.append(f"<tr><td>{mid}</td><td>{data['metric_name']}</td>")
        for i in range(1, 9):
            html.append(f"<td>{data['diffs'].get(i, 0)}</td>")
        html.append("</tr>")
    html.append("</table></details>")

    # ------------------------------------------------------------------ #
    # 9.  Counter-groups detail (one row per counter, 8 iface columns)   #
    # ------------------------------------------------------------------ #
    html.append("<h2>Counter Groups Detail</h2>")

    cxi_groups = [
        ("CxiPerfStats",            "Traffic Congestion Counter Group"),
        ("CxiErrStats",             "Network Error Counter Group"),
        ("CxiOpCommands",           "Operation (Command) Counter Group"),
        ("CxiOpPackets",            "Operation (Packet) Counter Group"),
        ("CxiDmaEngine",            "DMA Engine Counter Group"),
        ("CxiWritesToHost",         "Writes-to-Host Counter Group"),
        ("CxiMessageMatchingPooled","Message Matching of Pooled Counters"),
        ("CxiTranslationUnit",      "Translation Unit Counter Group"),
        ("CxiLatencyHist",          "Latency Histogram Counter Group"),
        ("CxiPctReqRespTracking",   "PCT Request & Response Tracking Counter Group"),
        ("CxiLinkReliability",      "Link Reliability Counter Group"),
        ("CxiCongestion",           "Congestion Counter Group"),
    ]

    collected = summary.get("collected", [])

    # build a fast index:  {(group, counter_name): {"desc":…, "unit":…, "iface_vals":{i:v}}}
    index: dict[tuple[str, str], dict] = {}
    for entry in collected:
        for g, desc in zip(entry.get("groups", []), entry.get("descriptions", [])):
            key = (g, entry["counter_name"])
            rec = index.setdefault(key, {
                "description": desc,
                "unit": (entry.get("units") or [""])[0],
                "iface_vals": {i: 0 for i in range(1, 9)}
            })
            rec["iface_vals"][entry["interface"]] = entry["value"]

    # render one <details> per group
    for g_key, g_desc in cxi_groups:
        html.append(f"<details><summary><strong>{g_key}</strong> — {g_desc}</summary>")
        html.append(
            "<table><tr>"
            "<th>Counter Name</th><th>Description</th><th>Unit</th>" +
            "".join(f"<th>Iface&nbsp;{i}</th>" for i in range(1, 9)) +
            "</tr>"
        )

        # pull rows for this group, sorted by counter_name
        rows = [(k, itm) for k, itm in index.items() if k[0] == g_key]
        for (grp, counter_name), item in sorted(rows, key=lambda t: t[0][1]):  # sort by counter_name
            html.append("<tr>")
            html.append(f"<td>{counter_name}</td>")
            html.append(f"<td title='{item['description']}'>{item['description']}</td>")
            html.append(f"<td>{item['unit']}</td>")
            for i in range(1, 9):
                html.append(f"<td>{item['iface_vals'].get(i, 0)}</td>")
            html.append("</tr>")


        html.append("</table></details>")


    # ------------------------------------------------------------------ #
    # 10.  Finish & write file                                           #
    # ------------------------------------------------------------------ #
    html.append("</main></body></html>")
    with open(output_file, "w") as f:
        f.write("\n".join(html))

    print(f"HTML report saved to: {output_file}")


