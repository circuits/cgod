# Module:   gophertypes
# Date:     20th December 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Gopher Types Module

Implements support for translating common mimtypes to gophertypes
"""


from fnmatch import fnmatch
from mimetypes import add_type, guess_type


DEFAULT_TYPE = "9"

EXTRA_MIME_TYPES = (
    ("text/x-markdown", ".md"),
    ("text/x-rst", ".rst"),
    ("text/x-yaml", ".yml"),
)

TYPE_MAP = (
    ("text/html", "h",),
    ("image/gif", "g",),
    ("text/*", "0"),
    ("image/*", "I"),
)


for ext, mimetype in EXTRA_MIME_TYPES:
    add_type(ext, mimetype)


def get_type(path):
    if path.is_dir() or path.is_symlink():
        return "1"

    mimetype, encoding = guess_type(path.name)
    if mimetype is None:
        return DEFAULT_TYPE

    for (pattern, gophertype)in TYPE_MAP:
        if fnmatch(mimetype, pattern):
            return gophertype

    return DEFAULT_TYPE
