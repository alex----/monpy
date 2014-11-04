#!/usr/bin/python
"""
A process that runs forever. So that we can practice connecting to it
"""
import time
import os
import sys

if __name__ == '__main__':
    l = []
    print('running, pid=%s' % (os.getpid()))
    data = {'key': 'value'}
    while True:
        sys.stdout.write('.')
        l.append(10000*[True])
        sys.stdout.flush()
        time.sleep(1)
