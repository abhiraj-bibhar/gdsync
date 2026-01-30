from pathlib import Path
from googleapiclient.http import MediaIoBaseDownload
import io
import sys


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
    percent = int(ratio * 100)

    return f"[{bar}] {percent:3d}%"


# -------------------------------------------------
# Executor
# -------------------------------------------------

def download_files(service, downloads, project_root: Path, dry_run=False):
    """
    Download Drive files to local filesystem, preserving directory structure,
    with progress bar.
    """
    if not downloads:
        print("Nothing to download.")
        return

    base_dir = project_root / "Drive"

    for f in downloads:
        target = base_dir / f["path"]

        # Safety: never overwrite existing files
        if target.exists():
            print(f"⚠ Skipping existing file: {f['path']}")
            continue

        # Ensure parent directories exist
        target.parent.mkdir(parents=True, exist_ok=True)

        print(f"\n↓ {f['path']}")

        if dry_run:
            print("  (dry-run)")
            continue

        request = service.files().get_media(fileId=f["id"])
        fh = io.FileIO(target, "wb")
        downloader = MediaIoBaseDownload(fh, request)

        total_size = f.get("size", 0)
        downloaded = 0
        done = False

        while not done:
            status, done = downloader.next_chunk()
            if status:
                downloaded = int(status.progress() * total_size)
                bar = _progress_bar(downloaded, total_size)
                size_info = (
                    f"{_format_size(downloaded)} / "
                    f"{_format_size(total_size)}"
                )

                sys.stdout.write(f"\r{bar} {size_info}")
                sys.stdout.flush()

        sys.stdout.write("\n")
        print("  ✔ Downloaded")