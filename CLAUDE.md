# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Telegram chat backup CLI tool built with Python and Telethon. It connects to a user's Telegram account via the Telegram API, lets them interactively select a chat, and exports messages (with optional media) to JSON and a styled HTML file.

## Running

```bash
pip install -r requirements.txt
python main.py
```

Requires a `.env` file with `API_ID`, `API_HASH`, and optionally `PHONE` (see `.env.example`). Credentials come from https://my.telegram.org.

The tool is interactive (terminal menus via `simple-term-menu`) — it cannot be run non-interactively.

## Architecture

- **`main.py`** — Entry point. Orchestrates auth → chat selection → backup type menu → backup execution.
- **`src/auth.py`** — Creates and authenticates a `TelegramClient` using `.env` credentials. Produces a `tg_backuper.session` file for persistent login.
- **`src/chat_selector.py`** — Fetches all dialogs and presents a searchable terminal menu to pick one.
- **`src/backup.py`** — Core backup logic. Iterates all messages in a chat, resolves senders/forwards, optionally downloads media with retry/flood-wait handling, and writes `messages.json`. Then calls HTML generation.
- **`src/html_export.py`** — Generates a self-contained `chat.html` from the JSON backup data. WhatsApp-style layout with sender colors, reply previews, forwarded message indicators, media embeds, and text formatting (code, spoilers, blockquotes).

### Data flow

`main.py` → `auth.create_client()` → `chat_selector.select_chat()` → `backup.run_backup()` → `html_export.generate_html()`

### Backup output structure

```
backups/<timestamp>/
├── messages.json    # Full message data
├── chat.html        # Standalone HTML viewer
└── media/           # Downloaded media files (if applicable)
```

### Key patterns

- Sender/forward entity resolution uses an in-memory `cache: dict` to avoid redundant Telegram API calls.
- Media downloads use a 3-attempt retry loop with `FloodWaitError` backoff.
- Messages are collected newest-first (Telethon default) then reversed for chronological output.
- HTML export is fully self-contained (inline CSS, no external dependencies).
