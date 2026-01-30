import json
from pathlib import Path

from gdsync.constants import GDSYNC_DIR, STATE_FILE


def write_empty_state():
    path = Path.cwd() / GDSYNC_DIR / STATE_FILE
    with open(path, "w") as f:
        json.dump(
            {
                "last_sync": None,
                "files": {},
            },
            f,
            indent=2,
        )