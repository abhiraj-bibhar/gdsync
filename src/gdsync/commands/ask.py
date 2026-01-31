from gdsync.commands.run import _run_sync


def cmd_ask(args):
    return _run_sync(
        mode="ask",
        conflict_strategy="ask",
        args=args,
    )