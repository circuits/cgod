# Module:   core
# Date:     20th December 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Core Module

Crates server component, load plugins and handles process signals.
"""

import os
import pwd
import grp
from logging import getLogger
from signal import SIGINT, SIGHUP, SIGTERM


from circuits import handler, BaseComponent


from .server import Server
from .plugins import Plugins


class DropPrivileges(BaseComponent):

    def init(self, user="nobody", group="nobody"):
        self.user = user
        self.group = group

    def drop_privileges(self):
        if os.getuid() != 0:
            # Running as non-root. Ignore.
            return

        # Get the uid/gid from the name
        uid = pwd.getpwnam(self.user).pw_uid
        gid = grp.getgrnam(self.group).gr_gid

        # Remove group privileges
        os.setgroups([])

        # Try setting the new uid/gid
        os.setgid(gid)
        os.setuid(uid)

        # Ensure a very conservative umask
        os.umask(077)

    @handler("ready", channel="*")
    def on_ready(self, server, bind):
        self.drop_privileges()


class Core(BaseComponent):

    channel = "core"

    def init(self, config):
        self.config = config

        self.logger = getLogger(__name__)

        DropPrivileges(self.config["user"], self.config["group"]).register(self)

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
