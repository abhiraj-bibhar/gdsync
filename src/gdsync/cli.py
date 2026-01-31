import argparse
import sys

from gdsync.commands.init import cmd_init
from gdsync.commands.run import cmd_run
from gdsync.commands.status import cmd_status
from gdsync.commands.purge import cmd_purge
from gdsync.commands.auth import (
    cmd_auth,
    cmd_auth_help,
    cmd_auth_status,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gdsync",
        description="Google Drive sync CLI",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    # -----------------
    # gdsync init
    # -----------------
    p_init = subparsers.add_parser(
        "init",
        help="Initialize gdsync in current directory",
    )
    p_init.set_defaults(func=cmd_init)

    # -----------------
    # gdsync run (MAIN ENTRY)
    # -----------------
    p_run = subparsers.add_parser(
        "run",
        help="Run sync (downloads, uploads, conflict resolution)",
    )
    p_run.add_argument(
        "-y", "--yes",
        action="store_true",
        help="Auto confirm all prompts",
    )
    p_run.add_argument(
        "--dry-run",
        action="store_true",
        help="Show sync plan without executing",
    )
    p_run.add_argument(
        "--download-dir",
        metavar="PATH",
        help="Download only this Drive directory (full-drive mode)",
    )
    p_run.add_argument(
        "--conflict-strategy",
        choices=["ask", "prefer-drive", "prefer-local"],
        default="ask",
        help="How to resolve conflicts (default: ask)",
    )
    p_run.set_defaults(func=cmd_run)

    # -----------------
    # gdsync status
    # -----------------
    p_status = subparsers.add_parser(
        "status",
        help="Show sync status",
    )
    p_status.set_defaults(func=cmd_status)

    # -----------------
    # gdsync purge
    # -----------------
    p_purge = subparsers.add_parser(
        "purge",
        help="Remove gdsync from this project",
    )
    p_purge.add_argument(
        "-y", "--yes",
        action="store_true",
        help="Auto confirm purge",
    )
    p_purge.add_argument(
        "--all",
        action="store_true",
        help="Also remove global credentials",
    )
    p_purge.set_defaults(func=cmd_purge)

    # -----------------
    # gdsync auth
    # -----------------
    p_auth = subparsers.add_parser(
        "auth",
        help="Manage Google authentication",
    )

    auth_sub = p_auth.add_subparsers(
        dest="auth_cmd",
        required=False,
    )

    p_auth_help = auth_sub.add_parser(
        "help",
        help="Show authentication setup instructions",
    )
    p_auth_help.set_defaults(func=cmd_auth_help)

    p_auth_status = auth_sub.add_parser(
        "status",
        help="Show authentication status",
    )
    p_auth_status.set_defaults(func=cmd_auth_status)

    # default: gdsync auth
    p_auth.set_defaults(func=cmd_auth)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        return args.func(args) or 0
    except KeyboardInterrupt:
        print("\nAborted.")
        return 130
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1