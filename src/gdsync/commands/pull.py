from pathlib import Path
from gdsync.commands.run import _run_sync


def cmd_pull(args):
    if args.target != "drive":
        raise ValueError("Only `gdsync pull drive` is supported")

    return _run_sync(
        mode="pull",
        conflict_strategy="prefer-drive",
        args=args,
    )