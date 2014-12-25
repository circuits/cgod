# Module:   decorators
# Date:     25th December 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Decorators Module"""


from inspect import getargspec
from functools import update_wrapper


from circuits import handler


def selector(selector):
    def decorate(f):
        @handler(selector)
        def wrapper(self, event, *args, **kwargs):
            if not getattr(f, "event", False):
                return f(self, *args, **kwargs)
            return f(self, event, *args, **kwargs)

        wrapper.selector = selector

        wrapper.args, wrapper.varargs, wrapper.varkw, wrapper.defaults = getargspec(f)
        if wrapper.args and wrapper.args[0] == "self":
            del wrapper.args[0]

        if wrapper.args and wrapper.args[0] == "event":
            f.event = True
            del wrapper.args[0]
        wrapper.event = True

        return update_wrapper(wrapper, f)

    return decorate
