# Plugin:   hello
# Date:     25th December 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Hello Plugin

A sample plugin for demonstration purposes.
"""


__version__ = "0.0.1"
__author__ = "James Mills, prologic at shortcircuit dot net dot au"


from ..plugin import BasePlugin
from ..decorators import selector


class HelloPlugin(BasePlugin):
    """HelloCore Plugin"""

    @selector("/hello")
    def on_hello(self, event, req, res):
        res.add_text("Hello World!")
