# Module:   gophertypes
# Date:     20th December 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Gopher Types Module

Implements support for translating common mimtypes to gophertypes
"""


from fnmatch import fnmatch


import magic


DEFAULT_TYPE = "9"

TYPE_MAP = (
    ("text/html", "h"),
    ("text/*", "0"),

    ("image/gif", "g"),
    ("image/*", "I"),

    ("audio/*", "s"),

    ("application/x-tar", "5"),
    ("application/x-gtar", "5"),

    ("application/x-xz", "5"),
    ("application/x-zip", "5"),
    ("application/x-gzip", "5"),
    ("application/x-bzip2", "5"),
)


def get_type(path):
    if path.is_dir() or path.is_symlink():
        return "1"

    mimetype = magic.from_file(str(path), mime=True)

    if mimetype is None:
        return DEFAULT_TYPE

    for (pattern, gophertype)in TYPE_MAP:
        if fnmatch(mimetype, pattern):
            return gophertype

    return DEFAULT_TYPE
