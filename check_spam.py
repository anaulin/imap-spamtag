#!/usr/bin/env python3
"""
Connect to IMAP inbox, run each message through spamc, print spam/not spam.
Requires: IMAP_HOST, IMAP_USER, IMAP_PASS. spamd must be running.
"""

import imaplib
import os
import subprocess

LIMIT = 10


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
            print(raw)
            print("Skipping spamc for now")
            # r = subprocess.run(
            #     ["spamc", "-E"],
            #     input=raw,
            #     capture_output=True,
            #     timeout=30,
            # )
        except (FileNotFoundError, subprocess.TimeoutExpired) as e:
            print(f"UID {uid}: spamc failed: {e}")
            continue
        # result = "spam" if r.returncode == 1 else "not spam"
        # result = "not spam"
        # print(f"UID {uid}: {result}")

    conn.logout()


if __name__ == "__main__":
    main()
