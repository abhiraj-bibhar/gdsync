from pathlib import Path
from typing import Dict, List
import os
import hashlib

from gdsync.core.drive import (
    list_drive_files,
    list_all_drive_files,
    build_drive_paths,
)
from gdsync.config.project import load_config


# -------------------------------------------------
# Helpers
# -------------------------------------------------

def _md5(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _scan_local_files(root: Path) -> List[dict]:
    """
    Scan local files under root and return normalized records.
    """
    files = []

    if not root.exists():
        return files

    for dirpath, dirs, filenames in os.walk(root):
        # Never sync project metadata
        if ".gdsync" in dirs:
            dirs.remove(".gdsync")

        for name in filenames:
            full_path = Path(dirpath) / name
            rel_path = full_path.relative_to(root)

            stat = full_path.stat()

            files.append(
                {
                    "path": str(rel_path),
                    "size": stat.st_size,
                    "mtime": stat.st_mtime,
                    "md5": _md5(full_path),
                }
            )

    return files


# -------------------------------------------------
# Planner
# -------------------------------------------------

def plan_sync(
    service,
    project_root: Path,
    download_dir: str | None = None,
) -> Dict[str, List]:
    """
    Plan a sync between local filesystem and Google Drive.

    Returns:
      {
        uploads: [...],
        downloads: [...],
        unchanged: [...],
        conflicts: [...]
      }
    """
    config = load_config()
    sync_scope = config.get("sync_scope")

    # -------------------------------------------------
    # Local root selection
    # -------------------------------------------------
    local_root = project_root
    if sync_scope == "full_drive":
        local_root = project_root / "Drive"
        local_root.mkdir(exist_ok=True)

    local_files = _scan_local_files(local_root)

    # -------------------------------------------------
    # Drive scan
    # -------------------------------------------------
    if sync_scope == "folder":
        drive_files_raw = list_drive_files(
            service,
            config["drive_folder_id"],
        )

        drive_files = [
            {
                "id": f["id"],
                "path": f["name"],  # flat namespace
                "md5": f["md5"],
                "size": f["size"],
                "mtime": f["mtime"],
            }
            for f in drive_files_raw
        ]

    elif sync_scope == "full_drive":
        raw_files = list_all_drive_files(service)
        drive_files = build_drive_paths(raw_files)

        # Optional directory filter (interactive / flag-based)
        if download_dir:
            prefix = download_dir.rstrip("/") + "/"
            drive_files = [
                f for f in drive_files
                if f["path"] == download_dir or f["path"].startswith(prefix)
            ]

    else:
        raise RuntimeError(f"Unknown sync_scope: {sync_scope}")

    # -------------------------------------------------
    # Comparison
    # -------------------------------------------------
    local_map = {f["path"]: f for f in local_files}
    drive_map = {f["path"]: f for f in drive_files}

    uploads: List[dict] = []
    downloads: List[dict] = []
    unchanged: List[dict] = []
    conflicts: List[dict] = []

    # Local → upload / unchanged / conflict
    for path, lf in local_map.items():
        df = drive_map.get(path)

        if not df:
            uploads.append(lf)
            continue

        if lf["md5"] and df["md5"] and lf["md5"] == df["md5"]:
            unchanged.append(lf)
        else:
            conflicts.append(
                {
                    "path": path,
                    "local": lf,
                    "drive": df,
                }
            )

    # Drive-only → download
    for path, df in drive_map.items():
        if path not in local_map:
            downloads.append(df)

    return {
        "uploads": uploads,
        "downloads": downloads,
        "unchanged": unchanged,
        "conflicts": conflicts,
    }