# Module:   server
# Date:     20th December 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Server Module

Main Listening Server Component
"""


from logging import getLogger


from circuits import handler, Component
from circuits.net.sockets import TCPServer
from circuits.net.events import close, write

from pathlib import Path
from bidict import bidict


from .protocol import Gopher
from .version import version


class Server(Component):

    channel = "server"

    def init(self, config):
        self.config = config

        self.encoding = self.config["encoding"]
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

        self.transport = TCPServer(
            self.bind, channel=self.channel
        ).register(self)

        self.protocol = Gopher(self).register(self)

    def ready(self, server, bind):
        self.logger.info(
            "cgod v{0:s} ready! Listening on: {1:s}\n".format(
                version, "{0:s}:{1:d}".format(*bind)
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
