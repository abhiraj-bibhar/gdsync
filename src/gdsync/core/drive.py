from datetime import datetime, timezone
from functools import lru_cache


# -----------------------------
# Helpers
# -----------------------------

def _parse_mtime(ts: str | None):
    if not ts:
        return None
    return (
        datetime.fromisoformat(ts.replace("Z", "+00:00"))
        .astimezone(timezone.utc)
        .timestamp()
    )


# -----------------------------
# Folder-based listing
# -----------------------------

def list_drive_files(service, parent_id: str):
    """
    List files inside a specific Google Drive folder.
    """
    files = []
    page_token = None

    while True:
        resp = service.files().list(
            q=f"'{parent_id}' in parents and trashed=false",
            fields=(
                "nextPageToken, "
                "files(id,name,md5Checksum,modifiedTime,size)"
            ),
            pageToken=page_token,
        ).execute()

        for f in resp.get("files", []):
            files.append(
                {
                    "id": f["id"],
                    "name": f["name"],
                    "md5": f.get("md5Checksum"),
                    "size": int(f.get("size", 0)),
                    "mtime": _parse_mtime(f.get("modifiedTime")),
                }
            )

        page_token = resp.get("nextPageToken")
        if not page_token:
            break

    return files


# -----------------------------
# Full-drive listing
# -----------------------------

def list_all_drive_files(service):
    """
    List all files in 'My Drive'.
    """
    files = []
    page_token = None

    while True:
        resp = service.files().list(
            q="trashed=false",
            fields=(
                "nextPageToken, "
                "files(id,name,parents,md5Checksum,modifiedTime,size,mimeType)"
            ),
            pageToken=page_token,
        ).execute()

        files.extend(resp.get("files", []))

        page_token = resp.get("nextPageToken")
        if not page_token:
            break

    return files


def build_drive_paths(files):
    """
    Build full paths for Drive files using parent relationships.
    """
    by_id = {f["id"]: f for f in files}

    @lru_cache(None)
    def resolve_path(file_id):
        f = by_id[file_id]
        parents = f.get("parents")

        if not parents:
            return f["name"]

        parent_id = parents[0]
        parent = by_id.get(parent_id)

        if not parent:
            return f["name"]

        return f"{resolve_path(parent_id)}/{f['name']}"

    results = []

    for f in files:
        if f.get("mimeType") == "application/vnd.google-apps.folder":
            continue

        results.append(
            {
                "id": f["id"],
                "path": resolve_path(f["id"]),
                "md5": f.get("md5Checksum"),
                "size": int(f.get("size", 0)),
                "mtime": _parse_mtime(f.get("modifiedTime")),
            }
        )

    return results
    
def list_drive_directories(service):
    """
    List top-level directories in 'My Drive'.
    """
    dirs = []
    page_token = None

    while True:
        resp = service.files().list(
            q=(
                "mimeType='application/vnd.google-apps.folder' "
                "and 'root' in parents "
                "and trashed=false"
            ),
            fields="nextPageToken, files(id,name)",
            pageToken=page_token,
        ).execute()

        dirs.extend(resp.get("files", []))

        page_token = resp.get("nextPageToken")
        if not page_token:
            break

    return dirs    
def list_drive_subdirectories(service, parent_id: str):
    """
    List subdirectories of a given Google Drive folder.
    """
    dirs = []
    page_token = None

    while True:
        resp = service.files().list(
            q=(
                "mimeType='application/vnd.google-apps.folder' "
                f"and '{parent_id}' in parents "
                "and trashed=false"
            ),
            fields="nextPageToken, files(id,name)",
            pageToken=page_token,
        ).execute()

        dirs.extend(resp.get("files", []))

        page_token = resp.get("nextPageToken")
        if not page_token:
            break

    return dirs