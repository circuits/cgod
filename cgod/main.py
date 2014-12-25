# Module:   main
# Date:     20th December 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Main Module

Main entry point responsible for configuring and starting the application.
"""


import sys
import logging
from os import chdir
from os.path import basename
from logging import getLogger


from circuits.app import Daemon
from circuits import Debugger, Manager, Worker

from procname import setprocname


from .core import Core
from .config import Config


def setup_logging(config):
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.DEBUG if config["debug"] else logging.INFO,
        stream=config["logfile"]
    )

    return getLogger(__name__)


def main():
    setprocname(basename(sys.argv[0]))

    config = Config()

    chdir(config["rootdir"])

    logger = setup_logging(config)

    manager = Manager()

    Worker(channel="workers").register(manager)

    if config["debug"]:
        Debugger(
            logger=logger,
            events=config["verbose"],
        ).register(manager)

    if config["daemon"]:
        Daemon(config["pidfile"]).register(manager)

    Core(config).register(manager)

    manager.run()


if __name__ == "__main__":
    main()
