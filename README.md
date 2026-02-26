# imap-spamtag

Connects to an IMAP inbox, runs each message through rspamd (HTTP API), categorizes as spam/not spam.

## Requirements

- [mise](https://mise.jdx.dev/) (manages Python via uv)
- Docker (for rspamd)

## Setup

```zsh
mise install
cp .env.example .env   # edit with IMAP_HOST, IMAP_USER, IMAP_PASS
```

## Run

1. Start rspamd: `docker compose up`
2. Run the checker: `python check_spam.py`

The script talks to rspamd at `http://localhost:11333`; set `RSPAMD_URL` to use a different host/port.
