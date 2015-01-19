# Plugin:   rewrite
# Date:     19th January 2015
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Rewrite Plugin

A plugin to transparently rewrite selectors based on regular expressions.
"""


__version__ = "0.0.1"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"


from re import sub


from circuits import handler


from ..plugin import BasePlugin


DEFAULT_RULES = {
    "absuri": ("^([^/].*)", "/\\1")
}


class RewritePlugin(BasePlugin):
    """Rewrite Plugin"""

    def init(self, server, config):
        super(RewritePlugin, self).init(server, config)

        self.rules = self.config.get("rewrite", DEFAULT_RULES)

    @handler("request", priority=2)
    def on_request(self, event, req, res):
        for pattern, replacement in self.rules.values():
            req.selector = sub(pattern, replacement, req.selector)
