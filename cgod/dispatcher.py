# Module:   dispatcher
# Date:     25th December 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Dispatcher Module

Dispatches request events to registered plugins that have event handlers marked as selectors.
"""


from circuits import handler, BaseComponent


from .plugin import BasePlugin


class Dispatcher(BaseComponent):

    channel = "server"

    def init(self):
        self.selectors = []

    @handler("registered", channel="*")
    def on_registered(self, component, manager):
        if isinstance(component, BasePlugin):
            for method in component.handlers():
                if hasattr(method, "selector"):
                    self.selectors.append(method.selector)

    @handler("unregistered", channel="*")
    def on_unregistered(self, component, manager):
        if isinstance(component, BasePlugin):
            for method in component.handlers():
                if hasattr(method, "selector"):
                    self.selectors.remove(method.selector)

    @handler("request", priority=1)
    def on_request(self, event, req, res):
        if req.selector in self.selectors:
            event.stop()
            self.fire(event.create(req.selector, req, res))
