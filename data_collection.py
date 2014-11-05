#!/usr/bin/env python
"""
Class that collects data from process
"""
from datetime import datetime
import json
import os
from functools import partial
import signal
import time

import psutil
import pyrasite

from helpers import process_running, flatten_dict
from display import consol_output_sample, statsd_output_sample

CONNECTION_TIMEOUT = 5  # Seconds


def timeout_handler(pid, signum, frame):
    print('Failed to conenct in %s secs...' % (CONNECTION_TIMEOUT,))
    print('Please ensure that the PID is correct and that you can run "pyrasite-shell %s"' % (pid,))
    exit(1)


def data_file_can_be_overwritten(data_filename):
    while True:
        overwrite_input = raw_input('%s already exists. Overwrite [Y/n]:' % (data_filename,))
        if overwrite_input.lower().strip() in ('n', 'no'):
            return False
        if overwrite_input.lower().strip() in ('y', 'yes'):
            return True
        else:
            print('Bad input "%s"' % (overwrite_input,))


class DataCollection(object):
    def __init__(self, options):
        self.options = options
        self.process_under_examination = None

    def attach_to_process(self):
        """
        ensure that the PID is running,
        that the process can be connected to
        that the process can import objgraph
        will return the command runner
        """
        if not process_running(self.options.pid):
            print('PID (%s) not present' % (self.options.pid,))
            exit(1)
        try:
            signal.signal(signal.SIGALRM, partial(timeout_handler, self.options.pid))
            signal.alarm(CONNECTION_TIMEOUT)
            process_under_examination = pyrasite.PyrasiteIPC(self.options.pid)
            process_under_examination.connect()
            signal.alarm(0)
        except Exception as err:
            print('Failed to connect to process due to Exception: %s' % (err,))
            print(
                'please ensure that the PID is correct and that you can run '
                '"pyrasite-shell %s"' % (self.options.pid,))
            exit(1)
        if 'ImportError' in process_under_examination.cmd('import objgraph'):
            print('Process to monitor can not import objgraph...')
            exit(1)
        return process_under_examination

    def get_process_info_pyrasite_injected(self, attributes):
        """
        I will inject a command that will use psutil to get a dict of the atributes requested
        If the process does not have the ability to import psutil this will fail with a value error
        """
        command = ';'.join((
            'import psutil',
            'import json',
            'print(json.dumps(psutil.Process(%s).as_dict(attrs=%s)))' % (
                self.process_under_examination.pid,
                attributes),))
        return json.loads(self.process_under_examination.cmd(command))

    def get_process_info_directly(self, attributes):
        """
        I will use psutil to return a dict of the attributes requested
        If you do not have permission to look at that process I think this could fail.
        """
        process_info = psutil.Process(self.options.pid).as_dict(attrs=attributes)
        # injected version gets json serialized which turns some named tuples into lists
        # we need to do the same or deal with multiple types of structures
        return json.loads(json.dumps(process_info))

    def restructure_process_info(self, process_info):
        """ some named tuple get turned into list which means we lose some context. """
        process_info['cpu_times'] = {
            'user': process_info['cpu_times'][0],
            'system': process_info['cpu_times'][1]}
        process_info['memory_info'] = {
            'rss': process_info['memory_info'][0],
            'vms': process_info['memory_info'][1]}
        process_info['memory_info_ex'] = {
            'rss': process_info['memory_info_ex'][0],
            'vms': process_info['memory_info_ex'][1],
            'pfaults': process_info['memory_info_ex'][2],
            'pageins': process_info['memory_info_ex'][3]}
        return process_info

    def get_process_info(self):
        """ return a dict with process info - mem usage, threads, fds, cpu usage, etc """
        attributes = (
            'connections',
            'create_time',
            'memory_info_ex',
            'num_fds',
            'cpu_percent',
            'nice',
            'cpu_times',
            'memory_info',
            'open_files',
            'num_threads',
            'memory_percent')
        try:
            process_info = self.get_process_info_directly(attributes)
        except (ValueError, psutil.AccessDenied, psutil.TimeoutExpired):
            if self.process_under_examination:
                try:
                    process_info = self.get_process_info_pyrasite_injected(attributes)
                except (ValueError):
                    return {}  # skip this sample
            else:
                return {}  # skip this sample
        process_info = self.restructure_process_info(process_info)
        process_info['connections'] = len(process_info.get('connections', []))
        process_info['open_files'] = len(process_info.get('open_files', []))
        return process_info

    def get_object_count(self):
        """ return a dict of the most common python objects """
        string_result = self.process_under_examination.cmd(
            'import objgraph;objgraph.show_most_common_types()')
        split_values = string_result.split()
        # we now have a list of strings like [obj1, obj1_count_string, obj2, obj2_count_string]
        info_iterator = iter(split_values)
        # Lets zip the iter - making a list of tuples
        # feed that to map to turn the value into an int and turn that into a dict
        objects_info = dict(map(lambda x: (x[0], int(x[1])), zip(info_iterator, info_iterator)))
        return objects_info

    def sample_process(self):
        """ get a snapshot of state from the process """
        sample = self.get_process_info()
        if self.options.tracking_objects:
            sample['objects'] = self.get_object_count()
        sample['sample_time'] = time.time()
        sample['utc_time'] = str(datetime.utcnow())
        return sample

    def collect_data(self):
        """ start collecting data on the process """
        if self.options.filename:
            if os.path.isfile(self.options.filename):
                if not data_file_can_be_overwritten(self.options.filename):
                    exit(1)
            # reset the file
            open(self.options.filename, 'w').close()

        if self.options.tracking_objects:
            self.process_under_examination = self.attach_to_process()
        while True:
            try:
                sample = self.sample_process()
                consol_output_sample(sample, self.options)
                if self.options.output_to_statsd:
                    statsd_output_sample(sample, self.options)
                if self.options.filename:
                    with open(self.options.filename, 'a') as data_file:
                        data_file.write(json.dumps(sample))
                        data_file.write('\n')
                        if data_file.tell() > 1024*1024*1024*self.options.file_max_size:
                            print('hit max data file size - exiting')
                            exit(1)
                time.sleep(self.options.sample_interval_secs)
            except KeyboardInterrupt:
                exit(1)
