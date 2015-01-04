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
from ..utils import get_architecture


class ServerInfoPlugin(BasePlugin):
    """Server Info Plugin"""

    def init(self, server, config):
        super(ServerInfoPlugin, self).init(server, config)

        self.info = self.config.get("serverinfo", {})
        self.host = self.config.get("host", "localhost")

        self.architecture = get_architecture()

        self.geolocation = self.info.get("geolocation", None)

        self.admin = self.info.get("admin", "root@{}".format(self.host))
        self.description = self.info.get("description", "{} Gopherspace".format(self.host))

    @handler("caps")
    def on_caps(self, caps):
        caps.add("ServerSoftware", cgod.__name__)
        caps.add("ServerSoftwareVersion", cgod.__version__)
        caps.add("ServerArchitecture", self.architecture)

        caps.add("ServerAdmin", self.admin)
        caps.add("ServerDescription", self.description)

        if self.geolocation is not None:
            caps.add("ServerGeolocationString", self.geolocation)

        caps.add("ServerDefaultEncoding", self.server.encoding)

    @handler("request", priority=2)
    def on_request(self, req, res):
        req.environ["SERVER_DESCRIPTION"] = self.description

    @selector("/version")
    def on_hello(self, event, req, res):
        res.add_text(self.version)
