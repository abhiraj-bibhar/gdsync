from gdsync.commands.run import _run_sync


def cmd_push(args):
    if args.target != "local":
        raise ValueError("Only `gdsync push local` is supported")

    return _run_sync(
        mode="push",
        conflict_strategy="prefer-local",
        args=args,
    )