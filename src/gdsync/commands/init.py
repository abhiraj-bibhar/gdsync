from pathlib import Path

from gdsync.config.project import (
    is_initialized,
    gdsync_dir,
    write_config,
)
from gdsync.config.state import write_empty_state
from gdsync.constants import IGNORE_FILE


def cmd_init(args):
    if is_initialized():
        print("❌ gdsync is already initialized in this directory")
        return 1

    print("✔ Initializing gdsync in current directory\n")

    print("Select sync scope:")
    print("  1) Specific Google Drive folder")
    print("  2) Entire Google Drive")

    choice = input("> ").strip()

    if choice == "1":
        sync_scope = "folder"
        drive_folder_id = input("Enter Google Drive Folder ID:\n> ").strip()
        if not drive_folder_id:
            print("❌ Folder ID is required")
            return 1
    elif choice == "2":
        sync_scope = "full_drive"
        drive_folder_id = None
    else:
        print("❌ Invalid choice")
        return 1

    # Create .gdsync/
    gdsync_dir().mkdir()

    write_config(sync_scope, drive_folder_id)
    write_empty_state()

    # .gdsyncignore
    ignore_path = gdsync_dir() / IGNORE_FILE
    ignore_path.write_text(
        "# Files to ignore for gdsync\n"
        ".git/\n"
        "node_modules/\n"
        "*.log\n"
    )

    # README
    readme = gdsync_dir() / "README.txt"
    readme.write_text(
        "This directory is managed by gdsync.\n"
        "Do not edit files manually unless you know what you're doing.\n"
    )

    print("\n✅ gdsync initialized successfully")
    print("Run `gdsync run` to start syncing")