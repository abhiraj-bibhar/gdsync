import json
from pathlib import Path
from datetime import datetime
from gdsync.constants import GDSYNC_DIR, CONFIG_FILE

from gdsync.constants import (
    GDSYNC_DIR,
    CONFIG_FILE,
    VERSION,
)


def project_root() -> Path:
    return Path.cwd()


def gdsync_dir() -> Path:
    return project_root() / GDSYNC_DIR


def is_initialized() -> bool:
    return gdsync_dir().exists()


def write_config(sync_scope: str, drive_folder_id: str | None):
    cfg = {
        "version": VERSION,
        "project_root": str(project_root()),
        "sync_scope": sync_scope,
        "drive_folder_id": drive_folder_id,
        "created_at": datetime.utcnow().isoformat() + "Z",
    }

    path = gdsync_dir() / CONFIG_FILE
    with open(path, "w") as f:
        json.dump(cfg, f, indent=2)
        

def load_config() -> dict:
    path = Path.cwd() / GDSYNC_DIR / CONFIG_FILE
    with open(path) as f:
        return json.load(f)        