# Plugin:   caps
# Date:     26th December 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Caps Plugin

A Caps Plugins providing the caps.txt resource.
"""


__version__ = "0.0.1"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"


from collections import OrderedDict


from circuits import handler, Event
from circuits.net.events import close, write


from ..plugin import BasePlugin
from ..decorators import selector


PREAMBLE = [
    "CAPS",
    "",
    "##",
    "## This is an automatically generated caps file.",
    "##",
    "",
]

VERSION = 1
EXPIRY = 1800


class caps(Event):
    """caps Event"""

    complete = True


class CapsObject(object):

    def __init__(self, version=VERSION, expiry=EXPIRY):
        self.version = version
        self.expiry = expiry

        self.data = OrderedDict()
        self.data["CapsVersion"] = self.version
        self.data["ExpireCapsAfter"] = self.expiry

    def __str__(self):
        return "{}\r\n{}\r\n".format(
            "\r\n".join(PREAMBLE),
            "\r\n".join(("{}={}".format(k, v) for k, v in self.data.iteritems()))
        )

    def add(self, key, value):
        self.data[key] = value


class CapsPlugin(BasePlugin):
    """Caps Plugin"""

    def init(self, server, config):
        super(CapsPlugin, self).init(server, config)

        self.buffer = ""
        self.caps = CapsObject()

    @handler("ready")
    def on_ready(self, server, bind):
        self.fire(caps(self.caps))

    @handler("caps_complete")
    def on_caps_complete(self, evt, val):
        self.buffer = str(self.caps)

    @selector("/caps.txt")
    def on_caps(self, event, req, res):
        res.stream = True
        self.fire(write(req.sock, self.buffer))
        self.fire(close(req.sock))
