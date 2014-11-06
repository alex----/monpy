#!/usr/bin/env python
from setuptools import setup
from setuptools.command.install import install

setup(name='monpy',
      version='0.1',
      description='Python written process monitor',
      author='Alex Sanchez',
      url='https://github.com/alex----/monpy',
      packages=['monpy'],
      install_requires=[
        'docopt==0.6.1',
        'pyrasite==2.0',
        'objgraph==1.8.1',
        'psutil==2.1.3',
        'tabulate==0.7.3',
        'matplotlib==1.4.2',
        'mock==1.0.1',
        'statsd==3.0.1',
        'plotly==1.3.1']
     )