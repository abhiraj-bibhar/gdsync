from pathlib import Path
import os

HOME = Path(os.environ.get("HOME", str(Path.home())))

GLOBAL_DIR = HOME / ".config" / "gdsync"

OAUTH_FILE = GLOBAL_DIR / "oauth.json"
TOKEN_FILE = GLOBAL_DIR / "token.json"


def ensure_global_dir():
    GLOBAL_DIR.mkdir(parents=True, exist_ok=True)