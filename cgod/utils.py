# Module:   utils
# Date:     20th December 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Utilities Module"""


import stat
from re import sub
from subprocess import check_output


EXEC_MASK = stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH


def execute(req, res, *args):
    try:
        return check_output(*args, env=req.environ, shell=True)
    except Exception as error:
        return "ERROR: {}".format(error)


def is_executable(path):
    return path.stat().st_mode & EXEC_MASK


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

    return root.joinpath(path)
