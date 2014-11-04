#!/usr/bin/python
"""
A bunch of small helpers
"""
import collections
from contextlib import contextmanager
import os
from StringIO import StringIO
import sys


def process_running(pid):
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


@contextmanager
def suppress_stdout():
    original_stdout, sys.stdout = sys.stdout, StringIO()
    yield
    sys.stdout = original_stdout


def flatten_dict(sample, parent_key='', seperator='.'):
    items = []
    for key, value in sample.items():
        new_key = seperator.join([parent_key, key]) if parent_key else key
        if isinstance(value, collections.MutableMapping):
            items.extend(flatten_dict(value, new_key, seperator=seperator).items())
        else:
            items.append((new_key, value))
    return dict(items)
