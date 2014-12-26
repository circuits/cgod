# Plugin:   logger
# Date:     26th December 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Logger Plugin

A plugin to log access to the server.
"""


__version__ = "0.0.1"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"


from circuits import handler


from ..plugin import BasePlugin


class LoggerPlugin(BasePlugin):
    """Logger Plugin"""

    @handler("response_complete")
    def on_response_complete(self, evt, val):
        res = evt.args[0]
        req = res.req

        logline = "{} - {}{}\n".format(
            req.remote_addr[0], req.selector,
            "?{}".format(req.query) if req.query else ""
        )

        self.logger.info(logline)
