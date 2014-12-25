# Module:   core
# Date:     20th December 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Core Module

Crates server component, load plugins and handles process signals.
"""

from logging import getLogger
from signal import SIGINT, SIGHUP, SIGTERM


from circuits import handler, BaseComponent


from .server import Server
from .plugins import Plugins


class Core(BaseComponent):

    channel = "core"

    def init(self, config):
        self.config = config

        self.logger = getLogger(__name__)

        self.server = Server(self.config).register(self)

        self.plugins = Plugins(
            init_args=(self.server, self.config)
        ).register(self)

        self.logger.info("Loading plugins...")
        for plugin in self.config["plugins"]:
            self.plugins.load(plugin)

    @handler("signal", channel="*")
    def signal(self, signo, stack):
        if signo == SIGHUP:
            self.config.reload_config()
        elif signo in (SIGINT, SIGTERM):
            raise SystemExit(0)
        return True
