monpy
===============

We have a so many handy tools for profiling a process but so often I just want to run the process for a day or two and see how its mem usage or CPU looked.
Monpy is a python written process monitor which simply collects data on your process and then lets you either consum a json datafile and/or send the data to a statsd server as it is colelcted or display the data either locally (using matplotlib) or on a webpage (using ploty)

It can collect process information (using psutil) such as memory usage, open file descriptors, CPU.
It can also collect python object counts (using pyrasite and GDB).

Requirements
------------
### Platforms
- *-inx

### Pyrasite
- To collect python object data you must install Pyrasite which in turn requires GDB

Installation
------------
Right now clone the repo :(

Usage
-----
./monpy.py --help
A tool for monitoring python memory use and object allocation.
Mostly glue around pyrosite, objgraph and matplotlib

Usage:
    monpy.py collect <pid> [--file=<file> --time_interval=<interval> --objects --statsd
        (<statsd_host> <statsd_port> <statsd_prefix>) --max_file_size=<max_file_size>]
    monpy.py display [--file=<file> --plotly --plotly_username=
        <plotly_username> --plotly_api_key=<plotly_api_key> --plotly_filename=<plotly_filename>]

Options:
    -h --help                               Show this screen.
    -v --version                            Show version.
    -f --file=<file>                        Data file location [default: /tmp/monpy.data]
    -t --time_interval=<interval>           Time between process sampling (in seconds) [default: 60]
    -o --objects                            Track pythons most common objects 
                                            (requires pyrasite, gdb, etc) [default: False]
    --statsd                                Output process stats to statsd server.
                                            Must provide <statsd_host>, <statsd_port> and <statsd_prefix>
    --plotly                                Display graphs locally [default: False]
    --plotly_username=<plotly_username>     Username to use when access ploty [default: DemoAccount]
    --plotly_api_key=<plotly_api_key>       API key to use when accessing plotly [default: lr1c37zw81]
    --plotly_filename=<plotly_filename>     Filename to use for plotly graph [default: MonpyPlot]
    --max_file_size=<max_file_size>         The max size of the data file in GBs [default: 0.5]


Collect data on process 631 every 30 secs
./monpy.py collect 631 -t 30 --file monpy.data
Collect data on process 631 every 30 secs, including the most common python objects
./monpy.py collect 631 -t 30 --objects --file monpy.data
Display data collected from a monpy collect locally
./monpy.py display --file monpy.data
Display data collected from a monpy collect on a web interface
./monpy.py display --file monpy.data --plotly

