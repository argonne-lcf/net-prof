# net_prof

net_prof is a network profiler library aimed to profile the HPE Cray Cassini Network Interface Card (NIC) on a compute node to collect, analyze and visualize the network counter events. This tool will help to compare and diagnose a successful workload without any network issues with an unsuccessful workload due to a network issue.

## To Install

```
pip install net_prof
```

## Functions
```
collect(input_directory, output.json)
summarize(before, after)
dump(summary)
dump_html(summary, output.html)
```

### Example Utilizing multi-NIC
```
import net_prof

net_prof.collect("../sys/class/cxi", "/path/to/file/before.json"))
# Perform some sort of action between before and after.
net_prof.collect("../sys/class/cxi", "/path/to/file/after.json"))

summary = net_prof.summarize("/path/to/file/before.json", "/path/to/file/after.json")

net_prof.dump(summary)
net_prof.dump_html(summary, "/path/to/file/report.html")
```

### Instructions for single-NIC collection
If you want to collect a single-NIC, pass in the /telemetry/ directory, otherwise, provide a /cxi/ directory.
For example:
Instead of giving a ../sys/class/cxi/ directory:
```
net_prof.collect("../sys/class/cxi", os.path.join(script_dir, "before.json"))
```
pass in the whole directory up to /telemetry of specific NIC:
```
net_prof.collect("../sys/class/cxi/cxi0/device/telemetry", os.path.join(script_dir, "before.json"))
```

### Test used by Aurora:
```
import os
import net_prof

target_host = "x4306c7s2b0n0.hostmgmt2306.cm.aurora.alcf.anl.gov"

net_prof.collect("/sys/class/cxi/","/lus/flare/projects/datascience/kaushik/network/net-prof-tests/ping-test/before.json")
os.system(f"ping -c 4 {target_host}") 
net_prof.collect("/sys/class/cxi/","/lus/flare/projects/datascience/kaushik/network/net-prof-tests/ping-test/after.json")

summary = net_prof.summarize("/lus/flare/projects/datascience/kaushik/network/net-prof-tests/ping-test/before.json", "/lus/flare/projects/datascience/kaushik/network/net-prof-tests/ping-test/after.json")

net_prof.dump(summary)
net_prof.dump_html(summary, "/lus/flare/projects/datascience/kaushik/network/net-prof-tests/ping-test/net_prof_report.html")
```

## Profiler Snapshots

![Alt text](docs/image1.png)
![Alt text](docs/image2.png)
![Alt text](docs/net_prof_iface_chart.png)
![Alt text](docs/net_prof_sum_html.png)

## References

https://cpe.ext.hpe.com/docs/latest/getting_started/HPE-Cassini-Performance-Counters.html

https://github.com/argonne-lcf/net_prof

https://pypi.org/project/net_prof/

