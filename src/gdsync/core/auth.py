import json

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

from gdsync.config.global_cfg import (
    ensure_global_dir,
    OAUTH_FILE,
    TOKEN_FILE,
)

SCOPES = ["https://www.googleapis.com/auth/drive"]


def authenticate():
    ensure_global_dir()

    if not OAUTH_FILE.exists():
        raise RuntimeError(
            "OAuth configuration not found.\n"
            "Run `gdsync auth` to configure authentication."
        )

    with open(OAUTH_FILE) as f:
        client_config = json.load(f)

    creds = None

    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(
            TOKEN_FILE, SCOPES
        )

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_config(
            client_config,
            SCOPES,
            redirect_uri="http://localhost",
        )

        auth_url, _ = flow.authorization_url(prompt="consent")
        print("\n🔐 Google authentication required\n")
        print(auth_url)

        code = input("\nPaste authorization code:\n> ").strip()
        flow.fetch_token(code=code)
        creds = flow.credentials

        TOKEN_FILE.write_text(creds.to_json())

    return build("drive", "v3", credentials=creds)