#!/usr/bin/env python
"""
Test the functions provided by the options module
"""
import os
import uuid
from multiprocessing import Process
import sys
import unittest
import mock
from monpy.options import Options
import random


def get_random_string():
    return str(uuid.uuid4())


def get_random_int():
    return random.randrange(1000, 2000)


class TestOptions(unittest.TestCase):

    def test_from_arguments(self):
        arguments = {'--file': get_random_string(),
                     '--max_file_size': str(get_random_int()),
                     '--objects': get_random_string(),
                     '--plotly': get_random_string(),
                     '--plotly_api_key': get_random_string(),
                     '--plotly_filename': get_random_string(),
                     '--plotly_username': get_random_string(),
                     '--statsd': get_random_string(),
                     '--time_interval': str(get_random_int()),
                     '<pid>': str(get_random_int()),
                     '<statsd_host>': get_random_string(),
                     '<statsd_port>': str(get_random_int()),
                     '<statsd_prefix>': get_random_string(),
                     'collect': get_random_string(),
                     'display': get_random_string(),
                     'test': get_random_string()}

        options = Options.from_arguments(arguments)
        self.assertEqual(options.collecting_data, arguments['collect'])
        self.assertEqual(options.display_data, arguments['display'])
        self.assertEqual(options.filename, arguments['--file'])
        self.assertEqual(options.file_max_size, float(arguments['--max_file_size']))
        self.assertEqual(options.output_to_statsd, arguments['--statsd'])
        self.assertEqual(options.pid, int(arguments['<pid>']))
        self.assertEqual(options.plotly_settings['username'], arguments['--plotly_username'])
        self.assertEqual(options.plotly_settings['api_key'], arguments['--plotly_api_key'])
        self.assertEqual(options.plotly_settings['filename'], arguments['--plotly_filename'])
        self.assertEqual(options.plot_on_ploty, arguments['--plotly'])
        self.assertEqual(options.sample_interval_secs, int(arguments['--time_interval']))
        self.assertEqual(options.statsd_host, arguments['<statsd_host>'])
        self.assertEqual(options.statsd_port, int(arguments['<statsd_port>']))
        self.assertEqual(options.statsd_prefix, arguments['<statsd_prefix>'])
        self.assertEqual(options.tracking_objects, arguments['--objects'])
        self.assertEqual(options.test, arguments['test'])


if __name__ == '__main__':
    unittest.main()
