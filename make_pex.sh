#!/bin/sh
echo "Installing PEX..."
sudo pip install pex
echo "Building pex file..."
sudo pex --python=python2.7 -s /Users/alex/Documents/code/tmp/monpy -r plotly==1.3.1 -r docopt==0.6.1 -r pyrasite==2.0 -r objgraph==1.8.1 -r psutil==2.1.3 -r tabulate==0.7.3 -r matplotlib==1.4.2 -r mock==1.0.1 -r statsd==3.0.1 -e monpy.monpy -o monpy.pex --