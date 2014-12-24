# Module:   objects
# Date:     20th December 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Objects Module

Implements core objects used to store data
"""


from textwrap import fill


from .utils import normalize


class Request(object):

    def __init__(self, sock, server, selector, query):
        self.sock = sock
        self.server = server
        self.selector = normalize(selector)
        self.query = query

        try:
            self.local_addr = self.sock.getlocalname()
        except:
            self.local_addr = self.server.bind

        try:
            self.remote_addr = self.sock.getpeername()
        except:
            self.remote_addr = None, 0

    def __repr__(self):
        return "<Request(host={}, port={}, selector={}, query={})>".format(
            self.remote_addr[0], self.remote_addr[1], self.selector, self.query
        )

    @property
    def environ(self):
        return {
            "REMOTE_ADDR": self.remote_addr[0],
            "LOCAL_ADDR": self.local_addr[0],
            "SCRIPT_NAME": self.selector,
            "SERVER_HOST": self.server.host,
            "SERVER_PORT": str(self.server.port),
            "QUERY_STRING": self.query,
            "CHARSET": self.server.encoding,
            "DOCUMENT_ROOT": str(self.server.rootdir),

        }


class Response(object):

    def __init__(self, req):
        self.req = req

        self._error = ""
        self._lines = []
        self._stream = False

    def __len__(self):
        return sum(map(len, self._lines))

    def __repr__(self):
        return "<Response(bytes={}, error={}, stream={})>".format(
            len(self), repr(self.error), self.stream
        )

    def __str__(self):
        return "{}\r\n.".format("\r\n".join(self._lines)) if not self.error else self.error

    def __bytes__(self):
        return str(self).encode(self.req.server.encoding)

    @property
    def error(self):
        return self._error

    @error.setter
    def error(self, error):
        self._error = error

    @property
    def stream(self):
        return self._stream

    @stream.setter
    def stream(self, stream):
        self._stream = stream

    def add(self, line):
        """
        Adds a line (RAW).
        """

        self._lines.append(line)

    def add_text(self, text, width=67):
        """
        Adds a line of text by formatting it as a gopher selector and
        word-wrapping the text to the ``width`` variable.
        """

        string = fill(text, width)
        for line in string.split("\n"):
            self._lines.append("i{}\t\tnull.host\t0".format(line))

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
            self._lines.append("3{}\t\tnull.host\t0".format(line))

    def add_link(self, type, text, path, host=None, port=None):
        """
        Adds a gopher selector link using the arguments provided.
        """

        host = host or self.req.server.host
        port = port or self.req.server.port

        self._lines.append("{}{}\t{}\t{}\t{}".format(type, text, path, host, port))

    def add_telnet(self, text, host, port=23):
        """
        Adds a telnet link, using the arguments provided.
        """

        self._lines.append("8{}\t\t{}\t{}" % (text, host, port))

    def add_url(self, text, url):
        """
        Adds an external link to any url, not just gopher.
        """

        self._lines.append("h{}\tURL:{}\tnull.host\t0".format(text, url))

    def add_title(self, text):
        """
        Adds a title.
        """

        self._lines.append("i{}\tTITLE\tnull.host\t0".format(text))

    def add_line(self):
        """
        Adds a blank line.
        """

        self._lines.append("i\t\tnull.host\t0")
