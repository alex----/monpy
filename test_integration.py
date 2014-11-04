#!/usr/bin/python
"""
Test that we can collect data
"""
import json
import mock
import os
import signal
import unittest
import uuid

from monpy import main
from options import Options
from helpers import suppress_stdout


def timeout_handler(signum, frame):
    raise Exception('test exception to force timeout')


class TestDataCollection(unittest.TestCase):
    def test_from_arguments(self):
        options = Options()
        options.collecting_data = True
        options.display_data = False
        options.filename = '/tmp/%s' % (str(uuid.uuid4()))
        options.file_max_size = 0.01
        options.sample_interval_secs = 1
        self.addCleanup(lambda: os.remove(options.filename))
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(3)
        try:
            with suppress_stdout():
                # still get the os system clear call which blanks the screen
                main(options)
        except Exception:
            pass
        data = []
        with open(options.filename, 'r') as data_file:
            for line in data_file:
                data.append(json.loads(line))
        self.assertTrue(len(data) > 0)
        self.assertTrue('cpu_times' in data[0])
        self.assertTrue('utc_time' in data[0])
        self.assertTrue('sample_time' in data[0])
        self.assertTrue('num_threads' in data[0])


if __name__ == '__main__':
    unittest.main()
