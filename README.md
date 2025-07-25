# net_prof

net_prof is a network profiler library aimed to profile the HPE Cray Cassini Network Interface Card (NIC) on a compute node to collect, analyze and visualize the network counter events. This tool will help to compare and diagnose a successful workload without any network issues with an unsuccessful workload due to a network issue. net-prof summary reports help to understand, analyze, and optimize current network bandwidth usage for any type of communication — whether it’s ping, point-to-point, send-receive, MPI collectives, or PyTorch CCL collectives — by pinpointing why the current communication API is not achieving its theoretical peak performance.

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

### Pytorch example:
```
import net_prof
import torch.distributed as dist

net_prof.collect("../sys/class/cxi", "/path/to/file/before.json"))
dist.init_process_group(backend="nccl")   # or gloo
x = torch.tensor([1.0], device="cuda")
dist.all_reduce(x, op=dist.ReduceOp.SUM)
net_prof.collect("../sys/class/cxi", "/path/to/file/after.json"))

summary = net_prof.summarize("/path/to/file/before.json", "/path/to/file/after.json")

net_prof.dump(summary)
net_prof.dump_html(summary, "/path/to/file/report.html")
```

### Healthy vs. Faulty Ping Test:
Net-Prof lets you contrast a good and bad run to pinpoint which NIC counters change. 
```
# Simulated "Healthy Node"

import net_prof, os

target = "good-node"

net_prof.collect("/sys/class/cxi", "before_healthy.json")
os.system(f"ping -c 4 {target}")
net_prof.collect("/sys/class/cxi", "after_healthy.json")

net_prof.dump_html(net_prof.summarize("before_healthy.json", "after_healthy.json"),
                   "report_healthy.html")
```
```
# Simulated "Faulty Node"

import net_prof, os

target = "bad-node"          # simulate issue (e.g., firewall drop)

net_prof.collect("/sys/class/cxi", "before_faulty.json")
os.system(f"ping -c 4 {target}")   # expect high loss / timeout
net_prof.collect("/sys/class/cxi", "after_faulty.json")

net_prof.dump_html(net_prof.summarize("before_faulty.json", "after_faulty.json"),
                   "report_faulty.html")
```

### Notes
- We are aware that the Ping issue may not be purely due to cxi or nics, there could be many other reasons like memory, network switches or hardware going down, however this tool is helpful to gain network insights.
- A function such as compare() should be devoloped -- This could allow a user to compare a "idle" test to a "real" test, which visualizes changes between the tests.

It could be implemented as such:
```
# DO NOT FOLLOW THIS CODE. THIS IS A REPRESENTATION OF WHAT CAPABALITIES I WANT net_prof TO HAVE IN THE FUTURE
# psuedocode:

net_prof.collect(before_idle.json)
time.sleep(5) # doing effectively "nothing" or just idling...
net_prof.collect(after_idle.json)

idle_test = net_prof.summarize(before_idle.json, after_idle.json)

net_prof.collect(before_ping.json)
os.system(f"ping -c 4 {target}") 
net_prof.collect(after_ping.json)

ping_test = net_prof.summarize(before_ping.json, after_ping.json)

compare(idle_test, ping_test, report_idle_vs_ping.html)
```


## Profiler Snapshots

![Alt text](docs/image1.png)
![Alt text](docs/image2.png)
![Alt text](docs/non_zero.png)
![Alt text](docs/units.png)
![Alt text](docs/net_prof_sum_html.png)

## References

https://cpe.ext.hpe.com/docs/latest/getting_started/HPE-Cassini-Performance-Counters.html

https://github.com/argonne-lcf/net_prof

https://pypi.org/project/net_prof/

