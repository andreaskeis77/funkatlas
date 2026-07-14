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
    probe = sub.add_parser("probe", help="run the measurement supervisor")
    probe.add_argument("--max-runtime", type=float, default=None)
    probe.add_argument("--once", action="store_true")
    heartbeat = sub.add_parser("heartbeat", help="show heartbeat gaps (night-run check)")
    heartbeat.add_argument("--hours", type=int, default=24)
    args = parser.parse_args(argv)

    if args.command == "version":
        from funkatlas import __version__

        print(__version__)
        return 0
    if args.command == "gate":
        from funkatlas.gate import main as gate_main

        return gate_main()
    if args.command == "probe":
        from funkatlas.supervisor import main as probe_main

        forwarded = []
        if args.max_runtime is not None:
            forwarded += ["--max-runtime", str(args.max_runtime)]
        if args.once:
            forwarded.append("--once")
        return probe_main(forwarded)
    if args.command == "heartbeat":
        from funkatlas import schema
        from funkatlas.status import heartbeat_report

        conn = schema.connect()
        try:
            schema.ensure_schema(conn)
            print(heartbeat_report(conn, hours=args.hours))
        finally:
            conn.close()
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
