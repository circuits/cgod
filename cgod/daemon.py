# Module:   daemon
# Date:     20th June 2009
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Daemon Component

Component to daemonize a system into the background and detach it from its
controlling PTY. Supports PID file writing, logging stdin, stdout and stderr
and changing the current working directory.
"""


from __future__ import print_function

import os
import sys
import fcntl
from logging import getLogger


from circuits import handler, BaseComponent


UMASK = 0
WORKDIR = "/"
DEVNULL = getattr(os, "devnull", "/dev/null")


class Daemon(BaseComponent):
    """Daemon Component

    :param pidfile: .pid filename
    :type  pidfile: str or unicode

    :param path: path to change directory to
    :type path: str
    """

    def init(self, pidfile, path=WORKDIR):
        self.pidfile = os.path.abspath(pidfile)
        self.path = os.path.abspath(path)

        self.logger = getLogger(__name__)

        self.logger.debug("pidfile: {}".format(self.pidfile))
        self.logger.debug("path: {}".format(self.path))

    def create_lockfile(self):
        # If pidfile already exists, we should read pid from there; to overwrite it, if locking
        # will fail, because locking attempt somehow purges the file contents.
        if os.path.isfile(self.pidfile):
            with open(self.pidfile, "r") as old_pidfile:
                old_pid = old_pidfile.read()

        # Create a lockfile so that only one instance of this daemon is running at any time.
        try:
            lockfile = open(self.pidfile, "w")
        except IOError:
            print("Unable to create the pidfile.", file=sys.stderr)
            raise SystemExit(1)

        try:
            # Try to get an exclusive lock on the file.
            # This will fail if another process has the file locked.
            fcntl.flock(lockfile, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError:
            print("Unable to lock on the pidfile.", file=sys.stderr)

            # We need to overwrite the pidfile if we got here.
            with open(self.pidfile, "w") as pidfile:
                pidfile.write(old_pid)

            raise SystemExit(1)

        return lockfile

    def daemonize(self):
        lockfile = self.create_lockfile()

        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                os._exit(0)
        except OSError as e:
            print("fork #1 failed: {0:d} ({0:s})".format(e.errno, str(e)), file=sys.stderr)
            raise SystemExit(1)

        # decouple from parent environment
        os.chdir(self.path)
        os.setsid()
        os.umask(UMASK)

        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # exit from second parent
                os._exit(0)
        except OSError as e:
            sys.stderr.write(
                "fork #2 failed: {0:d} ({0:s})\n".format(
                    e.errno, str(e)
                )
            )

            raise SystemExit(1)

        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()

        for fd in (0, 1, 2):
            try:
                os.close(fd)
            except OSError:
                pass

        os.open(DEVNULL, os.O_RDWR)  # standard input (0)

        # Duplicate stdin to stdout and stderr.
        os.dup2(0, 1)  # stdout (1)
        os.dup2(0, 2)  # stderr (2)

        try:
            lockfile.write("%s" % (os.getpid()))
            lockfile.flush()
        except IOError:
            print("Unable to write pid to the pidfile.", file=sys.stderr)
            raise SystemExit(1)

    @handler("ready", channel="*")
    def on_ready(self, server, bind):
        self.logger.debug("daemonizing ...")
        self.daemonize()
        self.unregister()
