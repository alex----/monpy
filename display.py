#!/usr/bin/python
"""
Displaying module
Really want to be able to output to consol when matplotlib is not installed
So doing some ugly imports on method calls. Should improve this.
"""
from itertools import chain
import os
import json

from helpers import suppress_stdout, flatten_dict
from tabulate import tabulate


def display(options):
    if not os.path.isfile(options.filename):
        print('File "%s" not found' % (options.filename,))
        exit(1)

    flat_sample_list = []
    with open(options.filename, 'r') as data_file:
        for sample_string in data_file:
            sample = json.loads(sample_string)
            flat_sample_list.append(flatten_dict(sample))
    if options.plot_on_ploty:
        url = plotly_plot_sample_list(flat_sample_list, options)
        print('data plotted at: %s' % (url,))
    else:
        local_plot_sample_list(flat_sample_list)


def consol_output_sample(sample, options):
    """ display sample on consol """
    os.system('clear')
    print(options)
    flattened_sample = flatten_dict(sample)
    tabled_sample = tabulate((key, value) for key, value in sorted(flattened_sample.items()))
    print(tabled_sample)


def statsd_output_sample(sample, options):
    """ output a sample to statsd for display in graphite """
    import statsd
    uninteresting_keys = ('sample_time', 'utc_time', 'create_time')
    statsd_client = statsd.StatsClient(options.statsd_host, options.statsd_port)
    for stat, value in flatten_dict(sample).items():
        if stat not in uninteresting_keys:
            statsd_client.gauge(options.statsd_prefix + stat, value, delta=False)


class _Cursor:
    def __init__(self, axis):
        self.axis = axis
        self.x_line = axis.axhline(color='k', alpha=0.1)  # the horiz line
        self.y_line = axis.axvline(color='k', alpha=0.1)  # the vert line

    def mouse_move(self, event):
        from pylab import draw
        if not event.inaxes:
            return

        x, y = event.xdata, event.ydata
        # update the line positions
        self.x_line.set_ydata(y)
        self.y_line.set_xdata(x)
        draw()


def local_plot_sample_list(flat_sample_list):
    """ display list of samples localling using matplotlib """
    import matplotlib.pyplot as plt
    from matplotlib.widgets import CheckButtons
    from pylab import connect
    # grab the time axis
    start_time = flat_sample_list[0]['sample_time']
    time_x_axis = [t['sample_time'] - start_time for t in flat_sample_list]
    # find all keys
    all_sample_keys = (set(chain(*flat_sample_list)))
    # omit the really dull stuff
    plotable_keys = all_sample_keys.difference({'sample_time', 'utc_time', 'create_time'})
    plots = {}
    _figure, axis = plt.subplots()

    # create plot for every key
    for plotable_key in plotable_keys:
        # a None is just ignored by matplotlib
        y_axis = [sample.get(plotable_key) for sample in flat_sample_list]
        # store the plot by name
        plots[plotable_key], = axis.plot(time_x_axis, y_axis, visible=False, lw=2)
    # make space for the clickable legend
    plt.subplots_adjust(left=0.45, right=0.98, bottom=0.05, top=0.98)
    # make a legend to select the plot you want to see
    rax = plt.axes([0.02, 0.05, 0.35, 0.93])
    plot_selector = CheckButtons(rax, plotable_keys, (len(plotable_keys)*[False]))
    # set all the labels in the plot selector to the same color as the plot
    for lable in plot_selector.labels:
        lable.set_color(plots[lable.get_text()].get_color())
    # overlay lines
    cursor = _Cursor(axis)
    connect('motion_notify_event', cursor.mouse_move)

    def plot_selection_update(label):
        """ Called with the checkbox lable which we can use to find the plot"""
        # toggle plot visibility
        plots[label].set_visible(not plots[label].get_visible())
        # if something visible
        if any(plot.get_visible() for plot in plots.values()):
            # rescale the plot based on actual visible data rather than the default auto scale
            ymax = max([max(p.get_ydata()) for p in plots.values() if p.get_visible()])
            ymin = min([min(p.get_ydata()) for p in plots.values() if p.get_visible()])
            axis.set_ylim(ymin, ymax, auto=True)
        plt.draw()

    plot_selector.on_clicked(plot_selection_update)
    plt.show()


def plotly_plot_sample_list(flat_sample_list, options):
    """ display list of samples localling using plotly """
    import plotly
    import plotly.plotly as py
    from plotly.graph_objs import Data, Scatter
    # grab the time axis
    start_time = flat_sample_list[0]['sample_time']
    time_x_axis = [t['sample_time'] - start_time for t in flat_sample_list]
    # find all keys
    all_sample_keys = (set(chain(*flat_sample_list)))
    # omit the really dull stuff
    plotable_keys = all_sample_keys.difference({'sample_time', 'utc_time', 'create_time'})
    data = []
    # create plot for every key
    for plotable_key in plotable_keys:
        # a None is just ignored by matplotlib
        y_axis = [sample.get(plotable_key) for sample in flat_sample_list]
        data.append(Scatter(x=time_x_axis, y=y_axis, name=plotable_key))
    plotly.tools.set_credentials_file(
        username=options.plotly_settings['username'],
        api_key=options.plotly_settings['api_key'])
    with suppress_stdout():
        unique_url = py.plot(
            data,
            filename=options.plotly_settings['filename'],
            auto_open=False,
            world_readable=True)
    return unique_url
