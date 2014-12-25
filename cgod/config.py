# Module:   config
# Date:     20th December 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Configuration Handling

Supports configuration of options via the command-line
and/or a configuration file. Optiona read form
configuration file override those given via command line options.
"""


from warnings import warn
from os.path import exists
from os import environ, getcwd
from ConfigParser import ConfigParser
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, FileType


import reprconf
from . import plugins
from .version import version


class Config(reprconf.Config):

    prefix = "CGOD_"

    def __init__(self, file=None, **kwargs):
        super(Config, self).__init__(file, **kwargs)

        self.parse_environ()
        self.parse_options()

    def parse_environ(self):
        """Check the environment variables for options."""

        config = {}

        for key, value in environ.iteritems():
            if key.startswith(self.prefix):
                name = key[len(self.prefix):].lower()
                config[name] = value

        self.update(config)

    def parse_options(self):
        parser = ArgumentParser(
            formatter_class=ArgumentDefaultsHelpFormatter,
            version=version,
        )

        add = parser.add_argument

        add(
            "-c", "--config", action="store", default=None,
            dest="config", metavar="FILE", type=str,
            help="Read configuration from FILE"
        )

        add(
            "-D", "--debug", action="store_true", default=False,
            dest="debug",
            help="Enable debug mode"
        )

        add(
            "-d", "--daemon", action="store_true", default=False,
            dest="daemon",
            help="Run as a daemon"
        )

        add(
            "-V", "--verbose", action="store_true", default=False,
            dest="verbose",
            help="Enable verbose logging"
        )

        add(
            "-l", "--logfile", action="store", default="-",
            dest="logfile", metavar="FILE", type=FileType(mode="w"),
            help="Write logs to FILE"
        )

        add(
            "-p", "--pidfile", action="store", default="cgod.pid",
            dest="pidfile", metavar="FILE", type=str,
            help="Write pid to FILE"
        )

        add(
            "-P", "--plugin",
            action="append", default=plugins.DEFAULTS, dest="plugins",
            help="Plugins to load (multiple allowed)"
        )

        add(
            "-b", "--bind",
            action="store", type=str,
            default="0.0.0.0:70", metavar="INT", dest="bind",
            help="Bind to interface INT"
        )

        add(
            "-e", "--encoding",
            action="store", type=str,
            default="UTF-8", dest="encoding",
            help="Set default encoding"
        )

        add(
            "-r", "--rootdir",
            action="store", type=str,
            default=getcwd(), dest="rootdir",
            help="Set root directory"
        )

        add(
            "-u", "--user",
            action="store", type=str,
            default="nobody", dest="user",
            help="Set user to drop privileges to"
        )

        add(
            "-g", "--group",
            action="store", type=str,
            default="nobody", dest="group",
            help="Set group to drop privileges to"
        )

        add(
            "-U", "--userdir",
            action="store", type=str,
            default="gopher", dest="userdir",
            help="Set user directory"
        )

        add(
            "-H", "--host",
            action="store", type=str,
            default="localhost", dest="host",
            help="Set hostname"
        )

        namespace = parser.parse_args()

        if namespace.config is not None:
            filename = namespace.config
            if exists(filename):
                config = reprconf.as_dict(str(filename))
                for option, value in config.pop("globals", {}).items():
                    if option in namespace:
                        self[option] = value
                    else:
                        warn("Ignoring unknown option %r" % option)
                self.update(config)

        for option, value in namespace.__dict__.items():
            key = "{}{}".format(self.prefix, option.upper())
            if key in environ and environ[key] != parser.get_default(option):
                continue

            if option not in self and value is not None:
                self[option] = value

    def reload_config(self):
        filename = self.get("config")
        if filename is not None:
            config = reprconf.as_dict(filename)
            config.pop("global", None)
            self.update(config)

    def save_config(self, filename=None):
        if filename is None:
            filename = self.get("config", "cgod.ini")

        parser = ConfigParser()
        parser.add_section("globals")

        for key, value in self.items():
            if isinstance(value, dict):
                parser.add_section(key)
                for k, v in value.items():
                    parser.set(key, k, repr(v))
            else:
                parser.set("globals", key, repr(value))

        with open(filename, "w") as f:
            parser.write(f)
