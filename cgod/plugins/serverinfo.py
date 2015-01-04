# Plugin:   serverinfo
# Date:     2th January 2015
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Server Info Plugin"""


__version__ = "0.0.1"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"


from circuits import handler


import cgod
from ..plugin import BasePlugin
from ..decorators import selector


class ServerInfoPlugin(BasePlugin):
    """Server Info Plugin"""

    def init(self, server, config):
        super(ServerInfoPlugin, self).init(server, config)

        self.info = self.config.get("serverinfo", {})
        self.host = self.config.get("host", "localhost")

        self.version = "{} {}".format(cgod.__name__, cgod.__version__)
        self.admin = self.info.get("admin", "root@{}".format(self.host))
        self.description = self.info.get("description", "{} Gopherspace".format(self.host))

    @handler("caps")
    def on_caps(self, caps):
        caps.add("ServerAdmin", self.admin)
        caps.add("ServerVersion", self.version)
        caps.add("ServerDescription", self.description)

        caps.add("ServerDefaultEncoding", self.server.encoding)

    @handler("request", priority=2)
    def on_request(self, req, res):
        req.environ["SERVER_DESCRIPTION"] = self.description

    @selector("/version")
    def on_hello(self, event, req, res):
        res.add_text(self.version)
