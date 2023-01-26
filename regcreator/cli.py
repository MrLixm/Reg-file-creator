import argparse
import logging
import sys

import regcreator


logger = logging.getLogger(__name__)


def configure_logging(level: int):
    """
    Configure the python logging system for the processing of the given directory.

    Args:
        level: logging level to set the console logger to
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    base_format = "{levelname: <7} | {asctime} [{name}][{funcName}] {message}"

    formatter = logging.Formatter(base_format, style="{")

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    return


def cli():
    """
    Command line argument for processing arg submitted by user.
    """

    parser = argparse.ArgumentParser(
        prog=regcreator.__name__,
        description="Create a Window reg file to edit registery keys.",
    )
    parser.add_argument("--version", action="version", version=regcreator.__version__)
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Toggle logging at debug level.",
    )
    parser.add_argument(
        "target_file",
        help="Path to the reg file to write on disk.",
        type=str,
    )

    parsed = parser.parse_args()

    logging_level = logging.DEBUG if parsed.debug else logging.INFO
    configure_logging(logging_level)
    logger.debug(parsed)

    # TODO finish
    return


if __name__ == "__main__":
    cli()
