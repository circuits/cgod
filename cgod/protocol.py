# Module:   protocol
# Date:     20th December 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Protocol Module

Implements the Gopher Protocol and handles the parsing of requests.
"""


from circuits import Component


from .events import request
from .objects import Request, Response


class Gopher(Component):

    channel = "server"

    def init(self, server):
        self.server = server

    def read(self, sock, data):
        selector, query = data.strip().split("\t", 1) or ("/", "")

        req = Request(sock, self.server, selector, query)
        res = Response(req)

        self.fire(request(req, res))
