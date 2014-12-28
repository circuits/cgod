# Module:   utils
# Date:     20th December 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Utilities Module"""


import os
import sys
import stat
from re import sub
from operator import itemgetter
from subprocess import check_output
from traceback import format_exception


from funcy import ignore


EXEC_MASK = stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH


def format_error():
    etype, evalue, tb = sys.exc_info()
    traceback = "\r\n".join(
        ("i{}".format(line) for line in format_exception(etype, evalue, tb))
    )
    return "3{}{}\terror.host\t0\r\n{}".format(etype.__name__, evalue, traceback)


def execute(req, res, args, **kwargs):
    kwargs.update(env=req.environ, shell=True)

    try:
        return check_output(args, **kwargs)
    except:
        return format_error()


@ignore(OSError, False)
def exists(path):
    return path.exists()


@ignore(OSError, False)
def is_dir(path):
    return path.is_dir()


@ignore(OSError, False)
def is_executable(path):
    return path.stat().st_mode & EXEC_MASK if path.exists() else False


@ignore(OSError, False)
def is_file(path):
    return path.is_file()


def iterdir(path):
    try:
        tmp = [(not p.is_dir(), p) for p in path.iterdir()]
        tmp.sort()
        return map(itemgetter(1), tmp)
    except OSError:
        return []


def normalize(path):
    # Remove double forward-slashes from the path
    path = sub('\/{2,}', '/', path)
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
    if path.endswith('.'):
        # If the path ends with a period, then it refers to a directory,
        # not a file path
        path = '/'.join(unsplit) + '/'
    else:
        path = '/'.join(unsplit)

    return path


def resolvepath(root, path):
    # Strip leading /
    if path and path[0] == "/":
        path = path[1:]

    try:
        return root.joinpath(path).resolve()
    except OSError:
        return root.joinpath(path)


def which(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None
