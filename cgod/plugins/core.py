# Plugin:   core
# Date:     20th December 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Core Plugin"""


__version__ = "0.0.1"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"


from uuid import uuid4 as uuid
from subprocess import check_output


from pathlib import Path

from circuits.io import File
from circuits import handler


from ..events import response
from ..plugin import BasePlugin
from ..utils import resolvepath
from ..gophertypes import get_type


IGNORE_PATTERNS = ("CSV", "*.bak", "*~", ".*")


def execute(req, *args):
    try:
        return check_output(*args, env=req.environ, shell=True)
    except Exception as error:
        return "ERROR: {}".format(error)


class CorePlugin(BasePlugin):
    """Core Plugin"""

    def process_gophermap(self, req, res, gophermap):  # noqa
        # XXX: C901 McCabe complexity 11

        with gophermap.open("r") as f:
            for line in f:
                line = line.strip()

                if not line:
                    res.add_line()
                elif line == ".":
                    break
                elif line[0] == "#":
                    # Ignore Comments
                    continue
                elif line[0] == "!":
                    res.add_title(line[1:])
                elif line[0] == "=":
                    res.add_text(execute(req, line[1:]))
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
        gophermap = path.joinpath("gophermap")
        if gophermap.exists():
            return self.process_gophermap(req, res, gophermap)

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
        elif path.resolve().is_dir():
            self.handle_directory(req, res, path, root)
        else:
            self.handle_file(req, res, path)

        self.fire(response(res))
