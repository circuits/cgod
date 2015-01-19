# Package:  plugins
# Date:     16th August 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Plugins Package"""


import sys
from logging import getLogger
from traceback import format_exc
from inspect import getmembers, isclass


from pymills.utils import safe__import__


from circuits.tools import kill
from circuits import Event, Component

from cidict import cidict


from ..plugin import BasePlugin


DEFAULTS = ["caps", "core", "hello", "logger", "rewrite", "serverinfo", "sessions", "url"]


def is_plugin(obj):
    return isclass(obj) and issubclass(obj, BasePlugin) and obj is not BasePlugin


class load(Event):
    """load Event"""


class query(Event):
    """query Event"""


class unload(Event):
    """unload Event"""


class Plugins(Component):

    channel = "plugins"

    def init(self, init_args=None, init_kwargs=None):
        self.init_args = init_args or tuple()
        self.init_kwargs = init_kwargs or dict()

        self.logger = getLogger(__name__)

        self.plugins = cidict()

    def query(self, name=None):
        if name is None:
            return self.plugins
        else:
            return self.plugins.get(name, None)

    def load(self, name, package=__package__):
        if name in self.plugins:
            self.logger.warn(
                "Not loading already loaded plugin: {0:s}".format(name)
            )
            return

        try:
            fqplugin = "{0:s}.{1:s}".format(package, name)
            if fqplugin in sys.modules:
                reload(sys.modules[fqplugin])

            m = safe__import__(name, globals(), locals(), package)

            plugins = getmembers(m, is_plugin)

            for name, Plugin in plugins:
                instance = Plugin(*self.init_args, **self.init_kwargs)
                instance.register(self)
                self.logger.debug(
                    "Registered Component: {0:s}".format(instance)
                )
                if name not in self.plugins:
                    self.plugins[name] = set()
                self.plugins[name].add(instance)

            self.logger.info("Loaded plugin: {0:s}".format(name))
        except Exception, e:
            self.logger.error(
                "Could not load plugin: {0:s} Error: {1:s}".format(
                    name, e
                )
            )
            self.logger.error(format_exc())

    def unload(self, name):
        if name in self.plugins:
            instances = self.plugins[name]
            for instance in instances:
                kill(instance)
                self.logger.debug(
                    "Unregistered Component: {0:s}".format(instance)
                )
                if hasattr(instance, "cleanup"):
                    instance.cleanup()
                    self.logger.info(
                        "Cleaned up Component: {0:s}".format(instance)
                    )
            del self.plugins[name]

            self.logger.info("Unloaded plugin: {0:s}".format(name))
        else:
            self.logger.warn(
                "Not unloading unloaded plugin: {0:s}".format(name)
            )
