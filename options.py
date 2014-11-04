#!/usr/bin/python
"""
class to make working out what options are set simpler
"""


class Options(object):
    def __init__(self):
        self._output_to_statsd = None
        self._plot_on_ploty = None
        self._tracking_objects = None

        self.collecting_data = None
        self.display_data = None
        self.filename = None
        self.file_max_size = None
        self.pid = None
        self.plotly_settings = None
        self.sample_interval_sec = None
        self.statsd_host = None
        self.statsd_port = None
        self.statsd_prefix = None
        self.test = None

    def __repr__(self):
        """ print all of the classes properties """
        props = [
            '%s: %s' % (var.title(), getattr(self, var))
            for var in vars(self) if not var.startswith('_')]
        for attr in dir(self.__class__):
            if isinstance(getattr(self.__class__, attr), property):
                props.append('%s: %s' % (attr.title(), getattr(self, attr)))
        return '\n'.join(props)

    @staticmethod
    def from_arguments(arguments):
        required_arguments = {
            'display',
            'collect',
            '--file',
            '--time_interval'}
        assert set(arguments).issuperset(required_arguments), 'missing required arguments'
        options = Options()
        options.collecting_data = arguments['collect']
        options.display_data = arguments['display']
        options.filename = arguments['--file']
        options.file_max_size = float(arguments['--max_file_size'])
        options.output_to_statsd = arguments['--statsd']
        options.pid = int(arguments['<pid>']) if arguments['<pid>'] else None
        options.sample_interval_secs = int(arguments['--time_interval'])
        options.statsd_host = arguments['<statsd_host>']
        options.statsd_port = int(
            arguments['<statsd_port>']) if arguments['<statsd_port>'] else None
        options.statsd_prefix = arguments['<statsd_prefix>']
        options.tracking_objects = arguments['--objects']
        options.plot_on_ploty = arguments['--plotly']
        options.plotly_settings = {
            'username': arguments['--plotly_username'],
            'api_key': arguments['--plotly_api_key'],
            'filename': arguments['--plotly_filename']}
        options.test = arguments['test']
        return options

    @property
    def output_to_statsd(self):
        return self._output_to_statsd

    @output_to_statsd.setter
    def output_to_statsd(self, value):
        # generate error if missing dep for requested feature
        if value:
            import statsd
        self._output_to_statsd = value

    @property
    def plot_on_ploty(self):
        return self._plot_on_ploty

    @plot_on_ploty.setter
    def plot_on_ploty(self, value):
        # generate error if missing dep for requested feature
        if self.display_data:
            if value:
                import plotly
            else:
                import matplotlib.pyplot
        self._plot_on_ploty = value

    @property
    def tracking_objects(self):
        return self._tracking_objects

    @tracking_objects.setter
    def tracking_objects(self, value):
        # generate error if missing dep for requested feature
        if value:
            import pyrasite
        self._tracking_objects = value
