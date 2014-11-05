#!/bin/sh
# This will take a fairly clean ubutu to a point it can build this PEX.
# We are assuming that you have pip
echo "Installing PEX..."
sudo pip install pex==0.7.0
echo "Installing wheel..."
sudo pip install wheel==0.24.0
echo "Installing distribute..."
sudo pip install distribute==0.7.3
echo "install Matplotlib deps..."
python -mplatform | grep Ubuntu && sudo apt-get update && sudo apt-get install python-dev libpng-dev libfreetype6-dev || echo "Not Ubuntu skipping matplotlib deps"
echo "Building pex file..."
sudo pex --python=python2.7 -s . -r plotly==1.3.1 -r docopt==0.6.1 -r pyrasite==2.0 -r objgraph==1.8.1 -r psutil==2.1.3 -r tabulate==0.7.3 -r matplotlib==1.4.2 -r mock==1.0.1 -r statsd==3.0.1 -e monpy.monpy -o monpy.pex --