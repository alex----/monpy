#!/usr/bin/python
"""
Test the functions provided by the helpers module
"""
import os
from multiprocessing import Process
import sys
import unittest
import mock
import helpers


class TestHelpers(unittest.TestCase):

    def test_process_running(self):
        self.assertTrue(helpers.process_running(os.getpid()))
        no_op_process = Process(target=lambda: None)
        no_op_process.start()
        self.assertTrue(helpers.process_running(no_op_process.pid))
        no_op_process.join()
        self.assertFalse(helpers.process_running(no_op_process.pid))

    def test_suppress_stdout(self):
        with mock.patch.object(sys, 'stdout') as mock_stdout:
            with helpers.suppress_stdout():
                sys.stdout.write('.')
                self.assertFalse(mock_stdout.write.called)

    def test_flatten_dict(self):
        self.assertEqual(helpers.flatten_dict({}), {})
        dict_to_flatten = {'a': 1, 'b': 2, 'c': 3}
        self.assertEqual(helpers.flatten_dict(dict_to_flatten), dict_to_flatten)
        dict_to_flatten = {'a': {'b': 1}, 'c': 2}
        flat_dict = helpers.flatten_dict(dict_to_flatten)
        self.assertEqual(flat_dict, {'a.b': 1, 'c': 2})
        flat_dict = helpers.flatten_dict(dict_to_flatten, seperator='-')
        self.assertEqual(flat_dict, {'a-b': 1, 'c': 2})

if __name__ == '__main__':
    unittest.main()
