# Module:   plugin
# Date:     20th December 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Plugin Module

This module provides the basic infastructure plugins. All plugins
should subclass BasePlugin to be properly registered as plugins.
"""


from logging import getLogger


from circuits import BaseComponent


class BasePlugin(BaseComponent):

    channel = "server"

    def init(self, server, config):
        self.server = server
        self.config = config
        self.logger = getLogger(
            "{}.{}".format(
                self.__class__.__module__,
                self.__class__.__name__
            )
        )
