# Module:   server
# Date:     20th December 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Server Module

Main Listening Server Component
"""

import os
import pwd
import grp
from logging import getLogger


from circuits.net.events import close, write
from circuits.net.sockets import TCPServer, TCP6Server
from circuits import handler, BaseComponent, Component

from pathlib import Path
from bidict import bidict


import cgod
from .protocol import Gopher
from .dispatcher import Dispatcher


class DropPrivileges(BaseComponent):

    channel = "server"

    def init(self, user="nobody", group="nobody", channel=channel):
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
        self.unregister()


class Server(Component):

    channel = "server"

    def init(self, config):
        self.config = config

        self.encoding = self.config["encoding"]
        self.width = self.config["width"]
        self.debug = self.config["debug"]

        self.logger = getLogger(__name__)

        self.homedir = Path("/home")
        self.rootdir = Path(self.config["rootdir"])
        self.userdir = self.config["userdir"]

        if ":" in config["bind"]:
            address, port = config["bind"].split(":")
            port = int(port)
        else:
            address, port = config["bind"], 6667

        self.bind = (address, port)
        self.host = config["host"]
        self.port = port

        self.streams = bidict()

        DropPrivileges(self.config["user"], self.config["group"]).register(self)

        if config["ipv6"]:
            self.transport = TCP6Server(
                self.port, channel=self.channel
            ).register(self)
        else:
            self.transport = TCPServer(
                self.bind, channel=self.channel
            ).register(self)

        self.protocol = Gopher(self).register(self)
        self.dispatcher = Dispatcher().register(self)

    def ready(self, server, bind):
        self.logger.info(
            "{} {} ready! Listening on: {}\n".format(
                cgod.__name__, cgod.__version__,
                "{0:s}:{1:d}".format(*bind)
            )
        )

    def read(self, sock, data):
        try:
            host, port = sock.getpeername()
        except:
            return

        self.logger.debug(
            "I: [{0:s}:{1:d}] {2:s}".format(host, port, repr(data))
        )

    def write(self, sock, data):
        try:
            host, port = sock.getpeername()
        except:
            return

        self.logger.debug(
            "O: [{0:s}:{1:d}] {2:s}".format(host, port, repr(data))
        )

    def response_complete(self, event, evt, val):
        res = evt.args[0]

        if not res.stream:
            self.fire(write(res.req.sock, bytes(res)))
            self.fire(close(res.req.sock))

    def response_failure(self, event, evt, val):
        res = evt.args[0]
        self.fire(write(res.req.sock, bytes(res)))
        self.fire(close(res.req.sock))

    def request_failure(self, event, evt, val):
        req, res = evt.args
        self.fire(write(req.sock, bytes(res)))
        self.fire(close(req.sock))

    @handler("read", channel="*")
    def file_read(self, event, *args):
        # Ignore the server read event(s)
        if len(args) > 1:
            return

        data = args[0]
        channel = event.channels[0]
        if channel in self.streams:
            req, file = self.streams[channel]
            self.fire(write(req.sock, data))

    @handler("eof", channel="*")
    def file_eof(self, event):
        channel = event.channels[0]
        if channel in self.streams:
            req, file = self.streams[channel]
            self.fire(close(req.sock))

            file.unregister()

            del self.streams[channel]
