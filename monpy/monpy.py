#!/usr/bin/env python
"""
A tool for monitoring python memory use and object allocation.
Mostly glue around pyrasite, objgraph and matplotlib

Usage:
    monpy.py collect <pid> (--file=<file> | (--statsd <statsd_host> <statsd_port> <statsd_prefix>))
        [--time_interval=<interval> --objects --max_file_size=<max_file_size>]
    monpy.py collect <pid> (--file=<file> (--statsd <statsd_host> <statsd_port> <statsd_prefix>))
        [--time_interval=<interval> --objects --max_file_size=<max_file_size>]
    monpy.py display [--file=<file> --plotly --plotly_username=
        <plotly_username> --plotly_api_key=<plotly_api_key> --plotly_filename=<plotly_filename>]
    monpy.py test

Options:
    -h --help                               Show this screen.
    -v --version                            Show version.
    -f --file=<file>                        Data file location
    -t --time_interval=<interval>           Time between process sampling (in seconds) [default: 60]
    -o --objects                            Track pythons most common objects
                                            (requires pyrasite, gdb, etc) [default: False]
    --statsd                                Output process stats to statsd server.
                                            Must provide <statsd_host>, <statsd_port> and
                                            <statsd_prefix>
    --plotly                                Display graphs locally [default: False]
    --plotly_username=<plotly_username>     Username to use when access ploty [default: DemoAccount]
    --plotly_api_key=<plotly_api_key>       API key to use when accessing plotly
                                            [default: lr1c37zw81]
    --plotly_filename=<plotly_filename>     Filename to use for plotly graph [default: MonpyPlot]
    --max_file_size=<max_file_size>         The max size of the data file in GBs [default: 0.5]

examples:
    Collecting data (sampling every 30 seconds):
    ./monpy.py collect 1977 --file monpy.data -t 30
    ./monpy.py collect 1977 --statsd localhost 8125 'monpystats' -t 30
    ./monpy.py collect 1977 --statsd localhost 8125 '' --file monpy.data -t 30
    Displaying data:
    ./monpy.py display --file tmp.data
    ./monpy.py display --file tmp.data --plotly
"""
import glob
import os
import unittest

from docopt import docopt

from options import Options
from data_collection import DataCollection
from helpers import flatten_dict
from display import display


def main(options):
    # print('__main__')
    options = Options.from_arguments(arguments)
    if options.collecting_data:
        data_collection = DataCollection(options)
        data_collection.collect_data()

    elif options.display_data:
        display(options)

    elif options.test:
        print('running tests...')
        suite = unittest.TestSuite()
        for t in [test.split('.')[0] for test in glob.glob('test_*.py')]:
            try:
                # If the module defines a suite() function, call it to get the suite.
                mod = __import__(t, globals(), locals(), ['suite'])
                suitefn = getattr(mod, 'suite')
                suite.addTest(suitefn())
            except (ImportError, AttributeError):
                # else, just load all the test cases from the module.
                suite.addTest(unittest.defaultTestLoader.loadTestsFromName(t))
        unittest.TextTestRunner().run(suite)


if __name__ == '__main__':
    # print('__name__')
    try:
        # print(docopt)
        arguments = docopt(__doc__, version='pymemtracker version 0.1')
    except BaseException as err:
        print('Bas usage:')
        print(__doc__)
        exit(1)
        # print(dir(err))
        # print(err.message)
        # print('ffs')
    # print(arguments)
    main(arguments)

