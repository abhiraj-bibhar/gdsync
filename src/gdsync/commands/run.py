from datetime import datetime
from pathlib import Path

from gdsync.config.project import is_initialized, load_config
from gdsync.config.global_cfg import OAUTH_FILE
from gdsync.core.auth import authenticate
from gdsync.core.planner import plan_sync
from gdsync.core.executor import download_files


# -------------------------------------------------
# Helpers
# -------------------------------------------------

def _fmt_time(ts: float) -> str:
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


def _choose_drive_dir(service) -> str | None:
    """
    Interactive Drive directory navigator.
    Allows user to decide whether to download a directory
    or go deeper into it.
    """
    from gdsync.core.drive import (
        list_drive_directories,
        list_drive_subdirectories,
    )

    path_parts: list[str] = []
    id_stack: list[str] = ["root"]

    while True:
        current_id = id_stack[-1]

        if current_id == "root":
            dirs = list_drive_directories(service)
        else:
            dirs = list_drive_subdirectories(service, current_id)

        current_path = "/" + "/".join(path_parts) if path_parts else "/"
        print(f"\nCurrent directory: {current_path}\n")

        if not dirs:
            print("No subdirectories here.")
            print("Downloading this directory.")
            return "/".join(path_parts)

        for i, d in enumerate(dirs, start=1):
            print(f"  {i}) {d['name']}/")

        try:
            choice = int(input("\nSelect a directory: ").strip())
            selected = dirs[choice - 1]
        except Exception:
            print("Invalid selection")
            continue

        print(f"\nSelected: {selected['name']}/\n")
        print("What would you like to do?")
        print("  1) Download THIS directory")
        print("  2) Go inside this directory")

        if path_parts:
            print("  3) Go back")

        action = input("\n> ").strip()

        if action == "1":
            path_parts.append(selected["name"])
            return "/".join(path_parts)

        if action == "2":
            path_parts.append(selected["name"])
            id_stack.append(selected["id"])
            continue

        if action == "3" and path_parts:
            path_parts.pop()
            id_stack.pop()
            continue

        print("Invalid choice")


# -------------------------------------------------
# Command
# -------------------------------------------------

def cmd_run(args):
    # -----------------------------
    # Preconditions
    # -----------------------------
    if not is_initialized():
        print("❌ gdsync is not initialized in this directory")
        print("Run `gdsync init` first")
        return 1

    if not OAUTH_FILE.exists():
        print("❌ Authentication not configured")
        print("Run `gdsync auth`")
        return 1

    service = authenticate()
    print("✅ Authentication OK")

    # -----------------------------
    # Determine download scope
    # -----------------------------
    config = load_config()
    download_dir: str | None = args.download_dir

    if config.get("sync_scope") == "full_drive" and not download_dir:
        print("\nThis project is configured for full Google Drive sync.\n")
        print("What would you like to download?")
        print("  1) Entire Google Drive")
        print("  2) Choose a specific directory")

        choice = input("\n> ").strip()

        if choice == "2":
            download_dir = _choose_drive_dir(service)
            if not download_dir:
                print("Aborted.")
                return 1

    # -----------------------------
    # Plan
    # -----------------------------
    plan = plan_sync(
        service,
        Path.cwd(),
        download_dir=download_dir,
    )

    print("\n🔍 Sync plan\n")

    if plan["downloads"]:
        print("Downloads:")
        for f in plan["downloads"]:
            print(
                f" ↓ {f['path']} | "
                f"{f['size']} bytes | "
                f"{_fmt_time(f['mtime'])}"
            )

    print("\nSummary:")
    print(f"Uploads:   {len(plan['uploads'])}")
    print(f"Downloads: {len(plan['downloads'])}")
    print(f"Unchanged: {len(plan['unchanged'])}")
    print(f"Conflicts: {len(plan['conflicts'])}")

    # -----------------------------
    # Dry-run exit
    # -----------------------------
    if args.dry_run:
        print("\n(no changes were made)")
        return 0

    # -----------------------------
    # Execute downloads
    # -----------------------------
    if plan["downloads"]:
        confirm = input("\nProceed with downloads? (y/N): ").lower()
        if confirm != "y":
            print("Aborted.")
            return 0

        download_files(
            service,
            plan["downloads"],
            Path.cwd(),
            dry_run=False,
        )

        print("\n✅ Download completed")

    return 0