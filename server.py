#!/usr/bin/env python


from __future__ import print_function

import re
from fnmatch import fnmatch
from uuid import uuid4 as uuid
from mimetypes import guess_type


from pathlib import Path
from bidict import bidict


from circuits.io import File
from circuits import handler, Event, Component
from circuits.net.sockets import TCPServer
from circuits.net.events import close, write


DEFAULT_BIND = ("0.0.0.0", 7000)

IGNORE_PATTERNS = ("CSV", "*.bak", "*~", ".*")

DEFAULT_TYPE = "9"

TYPE_MAP = (
    ("text/html", "h",),
    ("image/gif", "g",),
    ("text/*", "0"),
    ("image/*", "I"),
)


def get_type(p):
    if p.is_dir() or p.is_symlink():
        return "1"

    mimetype, encoding = guess_type(p.name)
    if mimetype is None:
        return DEFAULT_TYPE

    for (pattern, gophertype)in TYPE_MAP:
        if fnmatch(mimetype, pattern):
            return gophertype

    return DEFAULT_TYPE


def gophermap(req, docroot):
    lines = []

    host = req.local_addr[0]
    port = req.local_addr[1]

    if docroot != req.server.docroot:
        type, name = "1", ".."
        selector = Path().joinpath(*docroot.parts[:-1]).relative_to(req.server.docroot)
        lines.append("{}{}\t{}\t{}\t{}".format(type, name, selector, host, port))

    for p in docroot.iterdir():
        if any((p.match(pattern) for pattern in IGNORE_PATTERNS)):
            continue

        type = get_type(p)
        name = p.name
        selector = docroot.joinpath(p).relative_to(req.server.docroot)

        lines.append("{}{}\t/{}\t{}\t{}".format(type, name, selector, host, port))

    return "\r\n".join(lines)


def normalize(selector):
    # Remove double forward-slashes from the path
    path = re.sub('\/{2,}', '/', selector)
    # With that done, go through and remove all the relative references
    unsplit = []
    for part in path.split('/'):
        # If we encounter the parent directory, and there's
        # a segment to pop off, then we should pop it off.
        if part == '..' and (not unsplit or unsplit.pop() is not None):
            pass
        elif part != '.':
            unsplit.append(part)

    # With all these pieces, assemble!
    if selector.endswith('.'):
        # If the path ends with a period, then it refers to a directory,
        # not a file path
        selector = '/'.join(unsplit) + '/'
    else:
        selector = '/'.join(unsplit)

    return selector


def resolvepath(docroot, selector):
    # Strip type
    if selector:
        selector = selector[1:]

    # Strip leading /
    if selector and selector[0] == "/":
        selector = selector[1:]

    return docroot.joinpath(selector)


class request(Event):
    """request Event"""


class Request(object):

    def __init__(self, sock, server, selector):
        self.sock = sock
        self.server = server
        self.selector = normalize(selector)

        try:
            self.local_addr = self.sock.getlocalname()
        except:
            self.local_addr = self.server.bind

        try:
            self.remote_addr = self.sock.getpeername()
        except:
            self.remote_addr = None, 0

    def __repr__(self):
        return "<Request(host={}, port={}, selector={})>".format(
            self.remote_addr[0], self.remote_addr[1], self.selector
        )


class Transport(Component):

    def init(self, bind, **kwargs):
        TCPServer(bind).register(self)


class Protocol(Component):

    def init(self, server, **kwargs):
        self.server = server

    def read(self, sock, data):
        selector = data.strip()
        self.fire(request(Request(sock, self.server, selector)))


class Server(Component):

    channel = "server"

    def init(self, bind=None):
        self.bind = bind or DEFAULT_BIND

        self.transport = Transport(self.bind, channel=self.channel).register(self)
        self.protocol = Protocol(self, channel=self.channel).register(self)

        self.docroot = Path.cwd()

        self.streams = bidict()

        # from circuits import Debugger
        # Debugger().register(self)

    @handler("read", channel="*")
    def read(self, event, *args):
        # Ignore the server read event(s)
        if len(args) > 1:
            return

        data = args[0]
        channel = event.channels[0]
        if channel in self.streams:
            req, file = self.streams[channel]
            self.fire(write(req.sock, data))

    @handler("eof", channel="*")
    def eof(self, event):
        channel = event.channels[0]
        if channel in self.streams:
            req, file = self.streams[channel]
            self.fire(close(req.sock))

            file.unregister()

            del self.streams[channel]

    def request(self, req):
        filepath = resolvepath(self.docroot, req.selector)

        if filepath.is_dir() or filepath.is_symlink():
            response = "{}\r\n.".format(gophermap(req, filepath))
        else:
            if filepath.exists():
                channel = uuid()
                filename = str(filepath)
                self.streams[channel] = (req, File(filename, channel=channel).register(self))
                return

            response = "3File not found!\t\terror.host\t0"

        self.fire(write(req.sock, response))
        self.fire(close(req.sock))


def main():
    Server().run()


if __name__ == "__main__":
    main()
