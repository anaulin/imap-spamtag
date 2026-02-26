#!/usr/bin/env python3
"""
Connect to IMAP inbox, run each message through rspamd, print spam/not spam.
Requires: IMAP_HOST, IMAP_USER, IMAP_PASS. rspamd must be running (docker compose up).
Optional: RSPAMD_URL (default http://localhost:11333).
"""

import imaplib
import json
import os
import urllib.error
import urllib.request
from email import policy
from email.parser import BytesParser

LIMIT = 10
RSPAMD_TIMEOUT = 30


def check_rspamd(raw: bytes) -> str:
    base = os.environ.get("RSPAMD_URL", "http://localhost:11333").rstrip("/")
    url = f"{base}/checkv2"
    req = urllib.request.Request(url, data=raw, method="POST")
    req.add_header("Content-Length", str(len(raw)))
    try:
        with urllib.request.urlopen(req, timeout=RSPAMD_TIMEOUT) as resp:
            data = json.loads(resp.read().decode())
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError) as e:
        raise RuntimeError(e) from e
    action = data.get("action", "no action")
    return "spam" if action != "no action" else "not spam"


def main():
    host = os.environ.get("IMAP_HOST")
    user = os.environ.get("IMAP_USER")
    password = os.environ.get("IMAP_PASS")
    if not all((host, user, password)):
        print("Set IMAP_HOST, IMAP_USER, IMAP_PASS")
        raise SystemExit(1)

    try:
        conn = imaplib.IMAP4_SSL(host)
        conn.login(user, password)
        conn.select("INBOX", readonly=True)
    except imaplib.IMAP4.error as e:
        print(f"IMAP error: {e}")
        raise SystemExit(1)

    try:
        _, data = conn.uid("search", None, "ALL")
        uids = data[0].split()
        uids = uids[-LIMIT:] if len(uids) >= LIMIT else uids
    except imaplib.IMAP4.error as e:
        print(f"IMAP search error: {e}")
        conn.logout()
        raise SystemExit(1)

    for uid in uids:
        uid = uid.decode() if isinstance(uid, bytes) else uid
        try:
            _, data = conn.uid("fetch", uid, "(BODY.PEEK[])")
        except imaplib.IMAP4.error as e:
            print(f"UID {uid}: fetch failed: {e}")
            continue
        if not data or data[0] is None:
            print(f"UID {uid}: no data")
            continue
        part = data[0]
        raw = part[1] if isinstance(part, tuple) and len(part) > 1 else part
        if raw is None:
            raw = b""
        try:
            result = check_rspamd(raw)
        except RuntimeError as e:
            print(f"UID {uid}: rspamd failed: {e}")
            continue
        msg = BytesParser(policy=policy.default).parsebytes(raw)
        subject = msg.get("Subject", "(no subject)")
        print(f"UID {uid}: {result} — {subject}")

    conn.logout()


if __name__ == "__main__":
    main()
