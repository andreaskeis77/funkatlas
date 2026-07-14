"""CLI dispatcher: ``python -m funkatlas <command>``.

Imports are lazy inside branches so startup stays fast and any subcommand
works without the others' dependencies.
"""

from __future__ import annotations

import argparse
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="funkatlas")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("version", help="print version")
    sub.add_parser("gate", help="run the quality gate")
    args = parser.parse_args(argv)

    if args.command == "version":
        from funkatlas import __version__

        print(__version__)
        return 0
    if args.command == "gate":
        from funkatlas.gate import main as gate_main

        return gate_main()
    return 2


if __name__ == "__main__":
    sys.exit(main())
