# Plugin:   core
# Date:     20th December 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Core Plugin"""


__version__ = "0.0.1"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"


from uuid import uuid4 as uuid


from pathlib import Path

from circuits.io import File
from circuits import handler


from ..events import response
from ..plugin import BasePlugin
from ..utils import resolvepath
from ..gophertypes import get_type


IGNORE_PATTERNS = ("CSV", "*.bak", "*~", ".*")


class CorePlugin(BasePlugin):
    """Core Plugin"""

    def process_gophermap(self, req, res, gophermap):
        with gophermap.open("r") as f:
            for line in f:
                line = line.strip()

                if not line:
                    res.add_line()
                elif line[0] == "#":
                    # Ignore Comments
                    continue
                elif line[0] == "!":
                    res.add_title(line[1:])
                elif "\t" in line:
                    parts = line.split("\t")
                    if len(parts) < 4:
                        parts += [None] * (4 - len(parts))

                    type_name, selector, host, port = parts
                    type, name = type_name[0], type_name[1:]

                    res.add_link(type, name, selector, host, port)
                else:
                    res.add_text(line)

    def handle_directory(self, req, res, path):
        gophermap = path.joinpath("gophermap")
        if gophermap.exists():
            return self.process_gophermap(req, res, gophermap)

        if path != req.server.rootdir:
            type, name = "1", ".."
            selector = Path().joinpath(*path.parts[:-1]).relative_to(req.server.rootdir)
            res.add_link(type, name, selector)

        for p in path.iterdir():
            if any((p.match(pattern) for pattern in IGNORE_PATTERNS)):
                continue

            type = get_type(p)
            name = p.name
            selector = path.joinpath(p).relative_to(req.server.rootdir)

            res.add_link(type, name, selector)

    def handle_file(self, req, res, path):
        res.stream = True

        channel = uuid()
        filename = str(path)
        self.server.streams[channel] = (req, File(filename, channel=channel).register(self))

    @handler("request")
    def on_request(self, event, req, res):
        path = resolvepath(self.server.rootdir, req.selector)

        if not path.exists():
            res.error = "Resource not found!"
        elif path.resolve().is_dir():
            self.handle_directory(req, res, path)
        else:
            self.handle_file(req, res, path)

        self.fire(response(res))
