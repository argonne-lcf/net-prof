# net-prof

Net-prof is a network profiler aimed to profile the HPE Cray Cassini Network Interface Card (NIC) on a compute node to collect, analyze and visualize the network counter events.

### To Install

```
pip install -r requirements.txt
pip install net-prof
```

### Functions
```
collect(input_directory, "counters.json")
summarize(before, after)
dump(summary)
dump_html(summary, output_html)
```

### To Use

```
import net-prof

script_dir = os.path.dirname(os.path.abspath(__file__))

collect("/cxi/cxi0/device/telemetry/", os.path.join(script_dir, "before.json")) # Collects before interface (1)
dist.all_reduce(x, op=dist.ReduceOp.SUM) # Process that should cause changes to the network runs -- note: can be replaced with something like "os.execute('ping google.com')"
collect("/cxi/cxi0/device/telemetry/", os.path.join(script_dir, "after.json")) # Collects after interface (1)

before = os.path.join(script_dir, "before.json") # assigns before
after = os.path.join(script_dir, "after.json") # assigns after

output_html = os.path.join(script_dir, "report_2.html")
os.makedirs(os.path.join(script_dir, "charts"), exist_ok=True) # make sure charts exists within tests/ or project root

summary = summarize(before, after) # runs summary
dump(summary) # outputs summary to terminal
dump_html(summary, output_html) # outputs summary to html
```

```
# example using dummy example files for interfaces 1-8. (no collect())
import net-prof

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))  # go up from tests/

before = os.path.join(project_root, "example", "before.txt") # takes dummy before.txt
after = os.path.join(project_root, "example", "after.txt") # takes dummy after.txt
metrics = os.path.join(project_root, "src", "net_prof", "data", "metrics.txt") # takes dummy metrics.txt

output_html = os.path.join(script_dir, "report_2.html")
os.makedirs(os.path.join(script_dir, "charts"), exist_ok=True) # make sure charts exists within tests/ or project root

summary = summarize(before, after) # runs summary. Note summary supports an implementation of .txt or .json
dump(summary) # outputs summary to terminal
dump_html(summary, output_html) # outputs summary to html
```

Eventhough we have cxi0 as default, we can loop through and find all available cxi's from [0-8]

### Features in Devolopment:
```
FIX -- Being able to loop through with collect() in the /cxi/ directory -- Right now only one interface can be examined at a time.
FIX -- Feature isn't set up as a package yet so import won't work.
FIX -- report.html & report_2.html share the same charts when they shouldn't... (different data)
Create a single unified test instead of having a bunch of tests.
Adding more charts with mpl.
```

### Profiler Snapshots

![Alt text](docs/image1.png)
![Alt text](docs/image2.png)
![Alt text](docs/net_prof_iface_chart.png)
![Alt text](docs/net_prof_sum_html.png)



### References

https://cpe.ext.hpe.com/docs/latest/getting_started/HPE-Cassini-Performance-Counters.html
