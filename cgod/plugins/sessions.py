# Plugin:   sessions
# Date:     28th December 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Sessions Plugin

A plugin to manage user sessions and session data.
"""


__version__ = "0.0.1"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"


from pwd import getpwnam
from grp import getgrnam
from os import chmod, chown
from collections import defaultdict


from circuits.net.events import write
from circuits import handler, BaseComponent
from circuits.net.sockets import UNIXServer

from shortuuid import uuid


from ..plugin import BasePlugin
from ..decorators import selector


class Dict(BaseComponent):

    channel = "sessions"

    def init(self, data, channel=channel):
        self.data = data

    def KEYS(self, sid):
        return " ".join(self.data[sid].keys())

    def HAS(self, sid, key):
        return "1" if key in self.data[sid] else "0"

    def GET(self, sid, key):
        return self.data[sid].get(key, "")

    def DEL(self, sid, key):
        if key in self.data[sid]:
            del self.data[sid][key]
        return "OK"

    def SET(self, sid, key, value):
        self.data[sid][key] = value
        return "OK"

    @handler("read")
    def read(self, sock, data):
        data = data.strip().split(" ", 3)

        try:
            if len(data) < 2:
                raise ValueError("At least 2 parameters required {} given".format(len(data)))

            cmd, sid, args = data[0], data[1], data[2:]
            cmd = cmd.upper()

            self.fire(write(sock, "{}\n".format(getattr(self, cmd)(sid, *args))))
        except Exception as e:
            self.fire(write(sock, "ERR {}\n".format(e)))


class Sessions(BaseComponent):

    channel = "sessions"

    def init(self, path="/tmp/cgod.sock", user="nobody", group="nobody", channel=channel):
        self.path = path
        self.user = user
        self.group = group

        self.uid = getpwnam(self.user).pw_uid
        self.gid = getgrnam(self.group).gr_gid

        self.data = defaultdict(dict)

        # Dict Server (Key/Value Database)
        self.transport = UNIXServer(self.path, channel=self.channel).register(self)
        self.protocol = Dict(self.data, channel=self.channel).register(self)

        chown(self.path, self.uid, self.gid)
        chmod(self.path, 0666)

    def new(self):
        for k, v in self.data.iteritems():
            if not v:
                return k
        return uuid()

    def get(self, sid):
        return self.data[sid]

    def keys(self):
        return self.data.keys()


class SessionsPlugin(BasePlugin):
    """Sessions Plugin"""

    def init(self, server, config):
        super(SessionsPlugin, self).init(server, config)

        self.sessions = Sessions(user=config["user"], group=config["group"]).register(self)

    @handler("request", priority=2)
    def on_request(self, event, req, res):
        if "+" in req.selector:
            req.selector, req.sid = req.selector.split("+", 1)
        else:
            req.sid = self.sessions.new()

        req.environ["SID"] = req.sid

        req.session = self.sessions.get(req.sid)

    @selector("/session")
    def on_session(self, event, req, res):
        res.add_text("Session ID: {}".format(req.sid))
        res.add_line()
        res.add_text("Session Data:")
        for k, v in req.session.iteritems():
            res.add_text(" {}: {}".format(k, v))
        res.add_text("-" * 66)
        res.add_link("1", "List all Sessions", "/sessions")

    @selector("/sessions")
    def on_sessions(self, event, req, res):
        res.add_text("Active Sessions:")
        sessions = self.sessions.keys()
        for sid in sessions:
            res.add_link("1", sid, "/session+{}".format(sid))
        res.add_line()
        res.add_text("Total: {}".format(len(sessions)))
