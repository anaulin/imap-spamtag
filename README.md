# imap-spamtag

Connects to an IMAP inbox, runs each message through spamc (SpamAssassin), categorizes as spam/not spam.

## Requirements

- [mise](https://mise.jdx.dev/) (manages Python via uv)
- Docker (for spamd)

## Setup

```zsh
mise install
cp .env.example .env   # edit with IMAP_HOST, IMAP_USER, IMAP_PASS
```

## Run

1. Start spamd: `docker compose up`
2. Run the checker: `python check_spam.py`
