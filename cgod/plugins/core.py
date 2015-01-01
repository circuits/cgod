# Plugin:   core
# Date:     20th December 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Core Plugin"""


__version__ = "0.0.1"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"


from uuid import uuid4 as uuid
from tempfile import NamedTemporaryFile


from pathlib import Path

from circuits.io import File
from circuits import handler, task
from circuits.net.events import close, write


from ..plugin import BasePlugin
from ..gophertypes import get_type
from ..utils import execute, exists, is_dir, is_executable, is_file, iterdir, resolvepath, which


IGNORE_PATTERNS = ["CSV", "gophermap", "*.bak", "*~", ".*"]


class CorePlugin(BasePlugin):
    """Core Plugin"""

    def init(self, server, config):
        super(CorePlugin, self).init(server, config)

        self.rootdir = self.config.get("rootdir", Path.cwd())

    def handle_gophermap(self, req, res, gophermap):  # noqa
        # XXX: C901 McCabe complexity 11

        ignore = []

        with gophermap.open("r", encoding=self.server.encoding) as f:
            for line in f:
                line = line.strip("\r\n")

                if not line:
                    res.add_line()
                elif line == ".":
                    # Stop Processing
                    return
                elif line[0] == "#":
                    # Ignore Comments
                    continue
                elif line[0] == "!":
                    res.add_title(line[1:])
                elif line[0] == "=":
                    arg = line[1:].split(" ", 1)[0]

                    if arg and arg[0] == "/":
                        path = resolvepath(self.rootdir, arg)
                    else:
                        path = resolvepath(gophermap.parent, arg)

                    prog = which(arg)

                    if prog is not None or is_executable(path):
                        with NamedTemporaryFile() as f:
                            f.write(execute(req, res, line[1:], cwd=str(gophermap.parent)))
                            f.seek(0)
                            self.handle_gophermap(req, res, Path(f.name))
                    elif is_file(path):
                        self.handle_gophermap(req, res, path)
                    else:
                        res.error = (404, "Resource not found!")
                elif line[0] == "-":
                    ignore.append(line[1:])
                elif line == "*":
                    path = gophermap.parent
                    self.handle_directory(req, res, path, ignore=ignore)
                    return
                elif line[0] == "3":
                    parts = line.split("\t")
                    res.add_error(parts[0][1:])
                elif "\t" in line:
                    parts = line.split("\t")
                    if len(parts) < 4:
                        parts += [None] * (4 - len(parts))

                    type_name, selector, host, port = parts
                    type, name = type_name[0], type_name[1:]

                    selector = selector or name

                    if type != "h" and host in (None, req.server.host) and selector[0] != "/":
                        slash = "" if req.selector[-1] == "/" else "/"
                        selector = "{}{}{}".format(req.selector, slash, selector or name)

                    res.add_link(type, name, selector, host, port)
                else:
                    res.add_text(line)

    def handle_directory(self, req, res, path, ignore=None):
        ignore_patterns = IGNORE_PATTERNS[:]
        if ignore is not None:
            ignore_patterns += ignore

        gopherignore = path.joinpath(".gopherignore")
        if is_file(gopherignore):
            with gopherignore.open("r") as f:
                for line in f:
                    ignore_patterns.append(line.strip())

        if path != self.rootdir:
            type, name = "1", ".."
            selector = "/".join(req.selector.rstrip("/").split("/")[:-1]) or "/"
            res.add_link(type, name, selector)

        for p in iterdir(path):
            if any((p.match(pattern) for pattern in ignore_patterns)):
                continue

            type = get_type(p)
            name = p.name
            selector = p.name
            slash = "" if req.selector[-1] == "/" else "/"
            selector = "{}{}{}".format(req.selector, slash, selector)

            res.add_link(type, name, selector)

    def handle_file(self, req, res, path):
        res.stream = True

        channel = uuid()
        filename = str(path)
        self.server.streams[channel] = (req, File(filename, channel=channel).register(self))

    def handle_executable(self, req, res, script, *args):
        if args:
            req.environ["SCRIPT_NAME"] = "/".join(req.selector.split("/")[:-(len(args))])
        res.stream = True
        args = " ".join((str(script),) + args)
        self.fire(task(execute, req, res, args, cwd=str(script.parent)), "workers")

    @handler("caps")
    def on_caps(self, caps):
        # XXX: Make this depend on the environment

        caps.add("PathDelimeter", "/")
        caps.add("PathIdentity", ".")
        caps.add("PathParent", "..")
        caps.add("PathParentDouble", "FALSE")
        caps.add("PathKeepPreDelimeter", "FALSE")

    @handler("task_success", channel="workers")
    def on_task_success(self, evt, val):
        req = evt.args[1]

        self.fire(write(req.sock, val))
        self.fire(close(req.sock))

    @handler("request")  # noqa
    def on_request(self, event, req, res):
        # XXX: C901 McCabe complexity 10

        parts = req.selector.split("/")

        if len(parts) > 1 and parts[1] and parts[1][0] == "~":
            root = Path(self.server.homedir.joinpath(parts[1][1:], self.server.userdir))
            path = resolvepath(root, "/".join(parts[2:]))
        else:
            root = self.server.rootdir
            path = resolvepath(root, req.selector)

        if not exists(path):
            parent = path.parent
            gophermap = parent.joinpath("gophermap")

            if is_executable(gophermap):
                self.handle_executable(req, res, gophermap, path.name)
            elif is_executable(parent) and not is_dir(parent):
                self.handle_executable(req, res, parent, path.name)
            else:
                res.error = (404, "Resource not found!")
        elif is_dir(path):
            gophermap = path.joinpath("gophermap")

            if is_executable(gophermap):
                self.handle_executable(req, res, gophermap)
            elif is_file(gophermap):
                self.handle_gophermap(req, res, gophermap)
            else:
                self.handle_directory(req, res, path)
        elif is_executable(path):
            self.handle_executable(req, res, path)
        else:
            gophermap = path.with_suffix(".gophermap")

            if is_file(gophermap):
                self.handle_gophermap(req, res, gophermap)
            else:
                self.handle_file(req, res, path)
