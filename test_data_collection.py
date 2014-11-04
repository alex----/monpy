#!/usr/bin/python
"""
Test the functions provided by the helpers module
"""
import os
from multiprocessing import Process
import sys
import unittest
import mock
from data_collection import DataCollection
from copy import copy
import random


EXAMPLE_PROCESS_INFO = {
    'num_threads': 1,
    'cpu_times': [0.01855797, 0.016009821],
    'cpu_percent': 0.0,
    'connections': [],
    'memory_percent': 0.09002685546875,
    'memory_info': [7733248, 2522398720],
    'create_time': 1414972109.239619,
    'memory_info_ex': [7733248, 2522398720, 10117120, 0],
    'open_files': [],
    'num_fds': 3,
    'nice': 0}


class TestDataCollection(unittest.TestCase):
    def test_restructure_process_info(self):
        data_collection = DataCollection(None)
        restructured_process_info = data_collection.restructure_process_info(
            copy(EXAMPLE_PROCESS_INFO))
        self.assertEqual(
            restructured_process_info['cpu_times']['user'],
            EXAMPLE_PROCESS_INFO['cpu_times'][0])
        self.assertEqual(
            restructured_process_info['cpu_times']['system'],
            EXAMPLE_PROCESS_INFO['cpu_times'][1])
        self.assertEqual(
            restructured_process_info['memory_info']['rss'],
            EXAMPLE_PROCESS_INFO['memory_info'][0])
        self.assertEqual(
            restructured_process_info['memory_info']['vms'],
            EXAMPLE_PROCESS_INFO['memory_info'][1])
        self.assertEqual(
            restructured_process_info['memory_info_ex']['rss'],
            EXAMPLE_PROCESS_INFO['memory_info_ex'][0])
        self.assertEqual(
            restructured_process_info['memory_info_ex']['vms'],
            EXAMPLE_PROCESS_INFO['memory_info_ex'][1])
        self.assertEqual(
            restructured_process_info['memory_info_ex']['pfaults'],
            EXAMPLE_PROCESS_INFO['memory_info_ex'][2])
        self.assertEqual(
            restructured_process_info['memory_info_ex']['pageins'],
            EXAMPLE_PROCESS_INFO['memory_info_ex'][3])

    def test_get_object_count(self):
        expected_object_count = {
            'function': random.randrange(0, 999),
            'wrapper_descriptor': random.randrange(0, 999),
            'dict': random.randrange(0, 999),
            'tuple': random.randrange(0, 999)}
        objgraph_result = '\n'.join(
            '%s  %s' % (obj, count) for obj, count
            in expected_object_count.items())

        data_collection = DataCollection(None)
        with mock.patch.object(
                data_collection, 'process_under_examination') as mock_process_injector:
            mock_process_injector.cmd.return_value = objgraph_result
            object_count = data_collection.get_object_count()
            self.assertEqual(object_count, expected_object_count)

    def test_get_process_info_directly(self):
        mock_options = mock.MagicMock()
        mock_options.pid = os.getpid()
        data_collection = DataCollection(mock_options)
        process_info = data_collection.get_process_info_directly(('cpu_percent',))
        self.assertTrue('cpu_percent' in process_info)

    def test_get_process_info_using_directly_method(self):
        data_collection = DataCollection(None)
        with mock.patch.object(data_collection, 'get_process_info_directly') as mock_get_directly:
            mock_get_directly.return_value = copy(EXAMPLE_PROCESS_INFO)
            process_info = data_collection.get_process_info()
            self.assertTrue('num_threads' in process_info)
            self.assertTrue(type(process_info['connections']), int)
            self.assertTrue(type(process_info['open_files']), int)

    def test_get_process_info_failing_directly_method(self):
        data_collection = DataCollection(None)
        with mock.patch.object(data_collection, 'get_process_info_directly') as mock_get_directly:
            mock_get_directly.side_effect = ValueError('mock value error')
            mock_get_directly.return_value = copy(EXAMPLE_PROCESS_INFO)
            with mock.patch.object(
                    data_collection, 'get_process_info_pyrasite_injected') as mock_get_injected:
                process_info = data_collection.get_process_info()
                self.assertFalse(mock_get_injected.called)
                self.assertFalse('num_threads' in process_info)

    def test_get_process_info_failing_to_injection_method(self):
        data_collection = DataCollection(None)
        data_collection.process_under_examination = True
        with mock.patch.object(data_collection, 'get_process_info_directly') as mock_get_directly:
            mock_get_directly.side_effect = ValueError('mock value error')
            with mock.patch.object(
                    data_collection, 'get_process_info_pyrasite_injected') as mock_get_injected:
                mock_get_injected.return_value = copy(EXAMPLE_PROCESS_INFO)
                process_info = data_collection.get_process_info()
                self.assertTrue(mock_get_injected.called)
                self.assertTrue('num_threads' in process_info)
                self.assertTrue(type(process_info['connections']), int)
                self.assertTrue(type(process_info['open_files']), int)

    def test_sample_process_not_tracking_objects(self):
        mock_options = mock.MagicMock()
        mock_options.tracking_objects = False
        data_collection = DataCollection(mock_options)
        with mock.patch.object(data_collection, 'get_process_info') as mock_get_process_info:
            mock_get_process_info.return_value = {'mock_process_attr': 100}
            process_sample = data_collection.sample_process()
            self.assertEqual(process_sample['mock_process_attr'], 100)
            self.assertTrue('sample_time' in process_sample)
            self.assertTrue('utc_time' in process_sample)

    def test_sample_process_tracking_objects(self):
        mock_options = mock.MagicMock()
        mock_options.tracking_objects = True
        data_collection = DataCollection(mock_options)
        with mock.patch.object(data_collection, 'get_process_info') as mock_get_process_info:
            mock_get_process_info.return_value = {'mock_process_attr': 100}
            with mock.patch.object(data_collection, 'get_object_count') as mock_get_object_count:
                mock_get_object_count.return_value = {'list': 200}
                process_sample = data_collection.sample_process()
                self.assertEqual(process_sample['mock_process_attr'], 100)
                self.assertEqual(process_sample['objects']['list'], 200)
                self.assertTrue('sample_time' in process_sample)
                self.assertTrue('utc_time' in process_sample)

if __name__ == '__main__':
    unittest.main()
