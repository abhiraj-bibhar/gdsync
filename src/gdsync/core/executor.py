from pathlib import Path
from datetime import datetime
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
import io
import sys
import json

# -------------------------------------------------
# Helpers
# -------------------------------------------------

def _format_size(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def _progress_bar(done: int, total: int, width: int = 30) -> str:
    if total <= 0:
        return "[?]"
    ratio = min(done / total, 1.0)
    filled = int(ratio * width)
    bar = "#" * filled + "-" * (width - filled)
    return f"[{bar}] {int(ratio * 100):3d}%"


def _fmt_time(ts: float) -> str:
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


def _with_suffix(path: str, suffix: str) -> str:
    p = Path(path)
    return str(p.with_name(f"{p.stem} {suffix}{p.suffix}"))


# -------------------------------------------------
# Conflict report
# -------------------------------------------------

def report_conflicts(conflicts: list[dict]):
    print(f"\n⚠ Conflicts detected ({len(conflicts)})\n")

    for i, c in enumerate(conflicts, start=1):
        local = c["local"]
        drive = c["drive"]
        path = c["path"]

        ext = Path(path).suffix.lower() or "unknown"

        print(f"{i}) {path}")
        print(f"   Type: {ext[1:] if ext.startswith('.') else ext}")
        print(
            f"   Local:  {_format_size(local['size'])} | "
            f"modified {_fmt_time(local['mtime'])}"
        )
        print(
            f"   Drive:  {_format_size(drive['size'])} | "
            f"modified {_fmt_time(drive['mtime'])}"
        )

        if ext == ".pdf":
            print("   Note: PDF annotations cannot be merged safely")

        print()


# -------------------------------------------------
# Download
# -------------------------------------------------

def download_files(
    service,
    downloads,
    project_root: Path,
    *,
    dry_run: bool = False,
    overwrite: bool = False,
):
    if not downloads:
        return

    base_dir = project_root / "Drive"

    for f in downloads:
        target = base_dir / f["path"]

        if target.exists() and not overwrite:
            print(f"⚠ Skipping existing file: {f['path']}")
            continue

        target.parent.mkdir(parents=True, exist_ok=True)

        print(f"\n↓ {f['path']}")

        if dry_run:
            print("  (dry-run)")
            continue

        request = service.files().get_media(fileId=f["id"])
        fh = io.FileIO(target, "wb")
        downloader = MediaIoBaseDownload(fh, request)

        total = int(f.get("size", 0))
        done = False

        while not done:
            status, done = downloader.next_chunk()
            if status:
                downloaded = int(status.progress() * total)
                sys.stdout.write(
                    f"\r{_progress_bar(downloaded, total)} "
                    f"{_format_size(downloaded)} / {_format_size(total)}"
                )
                sys.stdout.flush()

        sys.stdout.write("\n  ✔ Downloaded\n")


# -------------------------------------------------
# Upload
# -------------------------------------------------

def upload_files(
    service,
    uploads,
    project_root: Path,
    *,
    dry_run: bool = False,
    overwrite: bool = False,
):
    if not uploads:
        return

    from gdsync.core.drive import ensure_drive_folder

    local_root = (
        project_root / "Drive"
        if (project_root / "Drive").exists()
        else project_root
    )

    drive_root_id = "root"
    folder_cache = {"": drive_root_id}

    for f in uploads:
        rel = Path(f["path"])
        dirs, filename = rel.parts[:-1], rel.parts[-1]

        parent_id = drive_root_id
        current = ""

        for d in dirs:
            current = f"{current}/{d}" if current else d
            if current not in folder_cache:
                folder_cache[current] = (
                    "dry-run"
                    if dry_run
                    else ensure_drive_folder(service, d, parent_id)
                )
            parent_id = folder_cache[current]

        print(f"\n↑ {f['path']}")

        if dry_run:
            print("  (dry-run)")
            continue

        media = MediaFileUpload(
            local_root / f["path"],
            resumable=True,
        )

        request = service.files().create(
            body={"name": filename, "parents": [parent_id]},
            media_body=media,
        )

        total = f["size"]
        response = None

        while response is None:
            status, response = request.next_chunk()
            if status:
                uploaded = int(status.progress() * total)
                sys.stdout.write(
                    f"\r{_progress_bar(uploaded, total)} "
                    f"{_format_size(uploaded)} / {_format_size(total)}"
                )
                sys.stdout.flush()

        sys.stdout.write("\n  ✔ Uploaded\n")


# -------------------------------------------------
# Conflict resolution
# -------------------------------------------------

def resolve_conflicts(
    service,
    conflicts: list[dict],
    strategy: str,
    project_root: Path,
    *,
    yes: bool = False,
    dry_run: bool = False,
):
    if not conflicts:
        return

    print("\n⚠ Resolving conflicts\n")

    for c in conflicts:
        path = c["path"]
        local = c["local"]
        drive = c["drive"]

        print(f"Conflict: {path}")

        # -----------------------------
        # ASK MODE
        # -----------------------------
        if strategy == "ask" and not yes:
            print("Choose resolution:")
            print("  1) Prefer Drive (overwrite local)")
            print("  2) Prefer Local (overwrite Drive)")
            print("  3) Keep both")
            print("  4) Skip")

            choice = input("> ").strip()

            if choice == "1":
                action = "prefer-drive"
            elif choice == "2":
                action = "prefer-local"
            elif choice == "3":
                action = "keep-both"
            else:
                print("  Skipped")
                continue
        else:
            action = strategy

        # -----------------------------
        # PREFER DRIVE
        # -----------------------------
        if action == "prefer-drive":
            print("  ↓ Overwriting local with Drive")

            download_files(
                service,
                [drive],
                project_root,
                dry_run=dry_run,
                overwrite=True,
            )

        # -----------------------------
        # PREFER LOCAL
        # -----------------------------
        elif action == "prefer-local":
            print("  ↑ Overwriting Drive with local")

            upload_files(
                service,
                [local],
                project_root,
                dry_run=dry_run,
                overwrite=True,
            )

        # -----------------------------
        # KEEP BOTH
        # -----------------------------
        elif action == "keep-both":
            print("  ↔ Keeping both copies")

            local_copy = local.copy()
            drive_copy = drive.copy()

            local_copy["path"] = _with_suffix(path, "(local copy)")
            drive_copy["path"] = _with_suffix(path, "(drive copy)")

            if dry_run:
                print(f"    Local → {local_copy['path']}")
                print(f"    Drive → {drive_copy['path']}")
                continue

            download_files(
                service,
                [drive_copy],
                project_root,
                overwrite=False,
            )

            upload_files(
                service,
                [local_copy],
                project_root,
                overwrite=False,
            )

        else:
            print("  Skipped")

def _conflict_log_path(project_root: Path) -> Path:
    return project_root / ".gdsync" / "conflicts.json"


def log_conflict(
    project_root: Path,
    *,
    path: str,
    local: dict,
    drive: dict,
    strategy: str,
    result: str,
):
    log_file = _conflict_log_path(project_root)
    log_file.parent.mkdir(exist_ok=True)

    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "path": path,
        "local": {
            "size": local.get("size"),
            "mtime": local.get("mtime"),
        },
        "drive": {
            "size": drive.get("size"),
            "mtime": drive.get("mtime"),
        },
        "strategy": strategy,
        "result": result,
    }

    if log_file.exists():
        with open(log_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = []

    data.append(entry)

    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)            