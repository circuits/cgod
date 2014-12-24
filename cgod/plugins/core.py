# Plugin:   core
# Date:     20th December 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Core Plugin"""


__version__ = "0.0.1"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"


from uuid import uuid4 as uuid


from pathlib import Path

from circuits.io import File
from circuits import handler, task
from circuits.net.events import close, write


from ..events import response
from ..plugin import BasePlugin
from ..gophertypes import get_type
from ..utils import execute, is_executable, resolvepath


IGNORE_PATTERNS = ("CSV", "*.bak", "*~", ".*")


class CorePlugin(BasePlugin):
    """Core Plugin"""

    def handle_gophermap(self, req, res, gophermap):  # noqa
        # XXX: C901 McCabe complexity 11

        with gophermap.open("r") as f:
            for line in f:
                line = line.strip()

                if not line:
                    res.add_line()
                elif line == ".":
                    # Stop Processing
                    break
                elif line[0] == "#":
                    # Ignore Comments
                    continue
                elif line[0] == "!":
                    res.add_title(line[1:])
                elif line[0] == "=":
                    res.add_text(execute(req, res, line[1:]))
                elif "\t" in line:
                    parts = line.split("\t")
                    if len(parts) < 4:
                        parts += [None] * (4 - len(parts))

                    type_name, selector, host, port = parts
                    type, name = type_name[0], type_name[1:]

                    if host is None or host == req.server.host:
                        slash = "" if req.selector[-1] == "/" else "/"
                        selector = "{}{}{}".format(req.selector, slash, selector)

                    res.add_link(type, name, selector, host, port)
                else:
                    res.add_text(line)

    def handle_directory(self, req, res, path, root):
        if path != root:
            type, name = "1", ".."
            selector = Path().joinpath(*path.parts[:-1]).relative_to(root)
            slash = "" if req.selector[-1] == "/" else "/"
            selector = "{}{}{}".format(req.selector, slash, selector)
            res.add_link(type, name, selector)

        for p in path.iterdir():
            if any((p.match(pattern) for pattern in IGNORE_PATTERNS)):
                continue

            type = get_type(p)
            name = p.name
            selector = path.joinpath(p).relative_to(root)
            slash = "" if req.selector[-1] == "/" else "/"
            selector = "{}{}{}".format(req.selector, slash, selector)

            res.add_link(type, name, selector)

    def handle_file(self, req, res, path):
        res.stream = True

        channel = uuid()
        filename = str(path)
        self.server.streams[channel] = (req, File(filename, channel=channel).register(self))

    def handle_executable(self, req, res, path):
        res.stream = True
        self.fire(task(execute, req, res, str(path)), "workers")

    @handler("task_success", channel="workers")
    def on_task_success(self, evt, val):
        fn, req, res, path = evt.args
        self.fire(write(req.sock, val))
        self.fire(close(req.sock))

    @handler("request")
    def on_request(self, event, req, res):
        parts = req.selector.split("/")

        if len(parts) > 1 and parts[1] and parts[1][0] == "~":
            root = Path(self.server.homedir.joinpath(parts[1][1:], self.server.userdir))
            path = resolvepath(root, "/".join(parts[2:]))
        else:
            root = self.server.rootdir
            path = resolvepath(root, req.selector)

        if not path.exists():
            res.error = "Resource not found!"
        elif path.is_dir():
            gophermap = path.joinpath("gophermap")

            if is_executable(gophermap):
                self.handle_executable(req, res, gophermap)
            elif gophermap.exists():
                self.handle_gophermap(req, res, gophermap)
            else:
                self.handle_directory(req, res, path, root)
        elif is_executable(path):
            self.handle_executable(req, res, path)
        else:
            self.handle_file(req, res, path)

    @handler("request_complete")
    def on_request_complete(self, event, evt, val):
        req, res = evt.args
        self.fire(response(res))
