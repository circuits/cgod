# Module:   protocol
# Date:     20th December 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Protocol Module

Implements the Gopher Protocol and handles the parsing of requests.
"""


from collections import defaultdict


from circuits import Component


from .events import request, response
from .objects import Request, Response


class Gopher(Component):

    channel = "server"

    def init(self, server):
        self.server = server
        self.buffers = defaultdict(str)

    def connect(self, sock, *args):
        self.buffers[sock] = ""

    def disconnect(self, sock):
        if sock in self.buffers:
            del self.buffers[sock]

    def read(self, sock, data):
        if data[-1] != "\n":
            self.buffers[sock] += data
            return

        data = (self.buffers[sock] + data).strip()

        if "?" in data:
            selector, query = data.split("?", 1)
        elif "\t" in data:
            selector, query = data.split("\t", 1)
        else:
            selector, query = (data or "/", "")

        req = Request(sock, self.server, selector, query)
        res = Response(req)

        self.fire(request(req, res))

    def request_complete(self, event, evt, val):
        req, res = evt.args
        self.fire(response(res))
