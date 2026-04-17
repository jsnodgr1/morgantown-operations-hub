"""CLI entry point for the Morgantown Operations Hub scaffold."""

from __future__ import annotations

import argparse

from morgantown_ops_hub import __version__
from morgantown_ops_hub.logging_utils import configure_logging


def build_parser() -> argparse.ArgumentParser:
    """Create the basic command-line parser."""
    parser = argparse.ArgumentParser(description="Initialize the Morgantown Operations Hub scaffold.")
    parser.add_argument("--log-level", default="INFO", help="Console log level, such as INFO or DEBUG.")
    return parser


def main() -> int:
    """Initialize logging and confirm the pipeline scaffold is wired up."""
    args = build_parser().parse_args()
    logger = configure_logging(args.log_level)
    logger.info("Morgantown Operations Hub scaffold initialized.")
    logger.info("Version: %s", __version__)
    logger.info("Next step: connect source configs, workbook extraction, and snapshot output flow.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
