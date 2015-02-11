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
from os.path import abspath, isabs, expanduser
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
        self.check_options()

    def check_options(self):
        path_options = ("config", "logfile", "rootdir", "userdir",)
        file_options = (
            ("logfile", "w",),
        )

        for path_option in path_options:
            value = self.get(path_options, None)
            if value and not isabs(value):
                self[path_options] = abspath(expanduser(value))

        for file_option, file_mode in file_options:
            value = self.get(file_option, None)
            if value and not isinstance(value, file):
                self[file_option] = open(value, file_mode)

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
            "-6" "--ipv6",
            action="store_true",
            default=False, dest="ipv6",
            help="Enable IPv6 support"
        )

        add(
            "-e", "--encoding",
            action="store", type=str,
            default="UTF-8", dest="encoding",
            help="Set default encoding"
        )

        add(
            "-w", "--width",
            action="store", type=int,
            default=70, dest="width",
            help="Sel default page width"
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

    def reload(self):
        filename = self.get("config")
        if filename is not None:
            config = reprconf.as_dict(filename)
            config.pop("global", None)
            self.update(config)

    def save(self, filename=None):
        if filename is None:
            return

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
