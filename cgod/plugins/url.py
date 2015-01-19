# Plugin:   url
# Date:     1st January 2015
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""URL Plugin

A plugin to handle non-compliant Gopher clients requesting resources of the form:

h<text>\tURL:<url>\t<host>\t<port>
"""


__version__ = "0.0.1"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"


from circuits import handler
from circuits.net.events import close, write


from ..plugin import BasePlugin


TEMPLATE = (
    "<html>"
    " <head>"
    "  <meta http-equiv=\"refresh\" content=\"{timeout:d};URL={url:s}\">"
    " </head>"
    " <body>"
    "  <p>"
    "   You are following an external link to a Web site.  You will be"
    "   automatically taken to the site shortly.  If you do not get sent"
    "   there, please click"
    "   <a href=\"{url:s}\">here</a> to go to the web site."
    "  </p>"
    "  <p>"
    "   The URL linked is: {url:s}"
    "  </p>"
    "  <p>"
    "   <a href=\"{url:s}\">{url:s}</A>"
    "  </p>"
    "  <p>"
    "   Thanks for using Gopher!"
    "  </p>"
    " </body>"
    "</html>"
)


class URLPlugin(BasePlugin):
    """URL Plugin"""

    def init(self, server, config):
        super(URLPlugin, self).init(server, config)

        self.timeout = self.config.get("url", {}).get("redirect-timeout", 5)

    @handler("request", priority=1)
    def on_request(self, event, req, res):
        if req.selector and req.selector.startswith("URL:"):
            event.stop()
            _, url = req.selector.split(":", 1)
            req.stream = True
            self.fire(write(req.sock, TEMPLATE.format(timeout=self.timeout, url=url)))
            self.fire(close(req.sock))
