# Module:   events
# Date:     20th December 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Events Module

This module defines events shared by various componetns.
"""


from circuits import Event


class request(Event):
    """request Event"""

    complete = True

class response(Event):
    """response Event"""

    complete = True
