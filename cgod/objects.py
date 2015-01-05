# Module:   objects
# Date:     20th December 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Objects Module

Implements core objects used to store data
"""


from os import geteuid
from pwd import getpwuid
from textwrap import fill


from .utils import normalize
from . import __name__, __version__


VERSION = "{} {}".format(__name__, __version__)

STATUS_CODES = {
    200: "OK",
    301: "Moved Permanently",
    303: "See Other",
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not Found",
    500: "Internal Server Error",
}


class Request(object):

    def __init__(self, sock, server, selector, query):
        self.sock = sock
        self.server = server
        self.selector = normalize(selector)
        self.query = query

        try:
            self.remote_addr = self.sock.getpeername()
        except:
            self.remote_addr = "169.254.0.1", 0

        self.environ = {
            "USER": getpwuid(geteuid()).pw_name,
            "PEER": self.remote_addr[0],
            "SELECTOR": self.selector,
            "QUERY": self.query,
            "SCRIPT_NAME": self.selector,
            "SERVER_HOST": self.server.host,
            "SERVER_PORT": str(self.server.port),
            "SERVER_VERSION": VERSION,
            "ENCODING": self.server.encoding,
            "WIDTH": str(self.server.width),
            "DOCUMENT_ROOT": str(self.server.rootdir),
        }

    def __repr__(self):
        return "<Request(host={}, port={}, selector={}, query={})>".format(
            self.remote_addr[0], self.remote_addr[1], self.selector, self.query
        )


class Response(object):

    def __init__(self, req):
        self.req = req

        self._lines = []
        self._error = ""
        self._status = 200
        self._stream = False

    def __len__(self):
        return sum(map(len, self._lines))

    def __repr__(self):
        return "<Response(bytes={}, error={}, status={}, stream={})>".format(
            len(self), self.error, self.status, self.stream
        )

    def __unicode__(self):
        return u"{}\r\n.".format(u"\r\n".join(self._lines))

    def __str__(self):
        return unicode(self).encode(self.req.server.encoding)

    @property
    def error(self):
        return self._error

    @error.setter
    def error(self, (status, error)):
        self._status = status
        self._error = error

        self._lines = []
        self.add_error("{} {}: {}".format(status, STATUS_CODES[status], error))

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status):
        self._status = status

    @property
    def stream(self):
        return self._stream

    @stream.setter
    def stream(self, stream):
        self._stream = stream

    def add_text(self, text, width=67):
        """
        Adds a line of text by formatting it as a gopher selector and
        word-wrapping the text to the ``width`` variable.
        """

        string = fill(text, width)
        for line in string.split("\n"):
            self._lines.append(u"i{}\t\tnull.host\t0".format(line))

    def add_para(self, text, width=67):
        """
        Adds a paragraph(s) of text by word-wrapping each paragraph, while
        preserving any newline characters. Word-wraps to the ``width`` variable.
        """

        for para in text.split("\n"):
            self.add_text(para, width)

    def add_error(self, text, width=67):
        """
        Adds a string as an itemtype-3 gopher selector (error), while
        wrapping the text to the ``width`` variable.
        """

        string = fill(text, width)
        for line in string.split("\n"):
            self._lines.append(u"3{}\t\terror.host\t0".format(line))

    def add_link(self, type, text, path, host=None, port=None):
        """
        Adds a gopher selector link using the arguments provided.
        """

        host = host or self.req.server.host
        port = port or self.req.server.port

        self._lines.append(u"{}{}\t{}\t{}\t{}".format(type, text, path, host, port))

    def add_telnet(self, text, host, port=23):
        """
        Adds a telnet link, using the arguments provided.
        """

        self._lines.append(u"8{}\t\t{}\t{}" % (text, host, port))

    def add_url(self, text, url):
        """
        Adds an external link to any url, not just gopher.
        """

        self._lines.append(u"h{}\tURL:{}\tnull.host\t0".format(text, url))

    def add_title(self, text):
        """
        Adds a title.
        """

        self._lines.append(u"i{}\tTITLE\tnull.host\t0".format(text))

    def add_line(self):
        """
        Adds a blank line.
        """

        self._lines.append(u"i\t\tnull.host\t0")
