# Module:   main
# Date:     20th December 2014
# Author:   James Mills, prologic at shortcircuit dot net dot au


"""Main Module

Main entry point responsible for configuring and starting the application.
"""


import logging
from logging import getLogger


from circuits.app import Daemon
from circuits import Debugger, Manager, Worker


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
    config = Config()

    logger = setup_logging(config)

    manager = Manager()

    Worker(channel="threadpool").register(manager)
    Worker(channel="processpool").register(manager)

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
