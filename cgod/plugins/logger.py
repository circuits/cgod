# Plugin:   logger
# Date:     26th December 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Logger Plugin

A plugin to log access to the server.
"""


__version__ = "0.0.1"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"


import datetime
from urllib import quote
from email._parseaddr import _monthnames


from circuits import handler


from ..plugin import BasePlugin


def formattime():
    now = datetime.datetime.now()
    month = _monthnames[now.month - 1].capitalize()
    return ("[%02d/%s/%04d:%02d:%02d:%02d]" %
            (now.day, month, now.year, now.hour, now.minute, now.second))


class LoggerPlugin(BasePlugin):
    """Logger Plugin"""

    format = "%(h)s %(l)s %(u)s %(t)s \"%(r)s\" %(s)s %(b)s \"%(f)s\" \"%(a)s\""

    def init(self, server, config):
        super(LoggerPlugin, self).init(server, config)

        self.logfile = self.config.get(__name__, {}).get("logfile", "access.log")
        self.log = open(self.logfile, "a")

    @handler("response_complete")
    def on_response_complete(self, evt, val):
        res = evt.args[0]
        req = res.req

        atoms = {"h": req.remote_addr[0],
                 "l": "-",
                 "u": getattr(req, "login", None) or "-",
                 "t": formattime(),
                 "r": quote("%s%s" % (req.selector, (req.query and "?%s" % req.query) or "")),
                 "s": int(res.status),
                 "b": len(res),
                 "f": "-",
                 "a": "-",
                 }
        for k, v in list(atoms.items()):
            if isinstance(v, str):
                v = v.encode("utf8")
            elif not isinstance(v, str):
                v = str(v)
            # Fortunately, repr(str) escapes unprintable chars, \n, \t, etc
            # and backslash for us. All we have to do is strip the quotes.
            v = repr(v)[1:-1]
            # Escape double-quote.
            atoms[k] = v.replace("\"", "\\\"")

        self.log.write(self.format % atoms)
        self.log.write("\n")
        self.log.flush()
