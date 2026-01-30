import json

from gdsync.config.global_cfg import (
    ensure_global_dir,
    OAUTH_FILE,
    TOKEN_FILE,
)
from gdsync.core.auth import authenticate


def cmd_auth(args):
    ensure_global_dir()

    print("🔐 gdsync authentication setup\n")

    if OAUTH_FILE.exists():
        confirm = input(
            "Authentication is already configured.\n"
            "Reconfigure authentication? (y/N): "
        ).strip().lower()
        if confirm != "y":
            print("Aborted.")
            return 0

        OAUTH_FILE.unlink(missing_ok=True)
        TOKEN_FILE.unlink(missing_ok=True)

    print("\nYou need Google OAuth credentials (Desktop App).")
    print("Create them here:")
    print("👉 https://console.cloud.google.com/apis/credentials\n")

    client_id = input("Enter CLIENT ID:\n> ").strip()
    client_secret = input("Enter CLIENT SECRET:\n> ").strip()

    if not client_id or not client_secret:
        print("❌ Client ID and secret are required")
        return 1

    oauth_config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost"],
        }
    }

    with open(OAUTH_FILE, "w") as f:
        json.dump(oauth_config, f, indent=2)

    print("\n✔ OAuth configuration saved")
    authenticate()
    print("\n✅ Authentication successful")


def cmd_auth_status(args):
    ensure_global_dir()

    print("Authentication status:\n")

    if OAUTH_FILE.exists():
        print("✔ OAuth configuration: present")
    else:
        print("❌ OAuth configuration: missing")

    if TOKEN_FILE.exists():
        print("✔ Token: present")
    else:
        print("❌ Token: missing")

    if OAUTH_FILE.exists() and TOKEN_FILE.exists():
        try:
            authenticate()
            print("✔ Google Drive access: OK")
        except Exception as e:
            print(f"❌ Google Drive access failed: {e}")


def cmd_auth_help(args):
    print(
        """
gdsync authentication (interactive)

Run:
  gdsync auth

You will be asked for:
- Google OAuth Client ID
- Google OAuth Client Secret

How to get them:
1. Go to https://console.cloud.google.com/
2. Create/select a project
3. Enable "Google Drive API"
4. Create OAuth Client ID
   - Application type: Desktop App

No files to copy. No JSON to manage.
"""
    )