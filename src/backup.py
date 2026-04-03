import asyncio
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from telethon import TelegramClient
from telethon.errors import FloodWaitError
from telethon.tl.types import (
    MessageMediaPhoto,
    MessageMediaDocument,
    User,
    Chat,
    Channel,
)


def _chat_type(entity) -> str:
    if isinstance(entity, User):
        return "User"
    if isinstance(entity, Chat):
        return "Group"
    if isinstance(entity, Channel):
        return "Channel" if entity.broadcast else "Group"
    return "Unknown"


def _classify_media(media) -> str:
    if isinstance(media, MessageMediaPhoto):
        return "photo"
    if isinstance(media, MessageMediaDocument):
        doc = media.document
        if doc is None:
            return "document"
        for attr in doc.attributes:
            cls_name = type(attr).__name__
            if cls_name == "DocumentAttributeAudio":
                return "voice" if getattr(attr, "voice", False) else "audio"
            if cls_name == "DocumentAttributeVideo":
                return "video_note" if getattr(attr, "round_message", False) else "video"
            if cls_name == "DocumentAttributeSticker":
                return "sticker"
            if cls_name == "DocumentAttributeAnimated":
                return "animation"
        return "document"
    return "other"


async def _resolve_sender(client, msg, cache: dict) -> tuple[int | None, str]:
    sender = msg.sender
    if sender is None:
        try:
            sender = await msg.get_sender()
        except Exception:
            return None, "Unknown"

    if sender is None:
        return None, "Unknown"

    sender_id = sender.id
    if sender_id in cache:
        return sender_id, cache[sender_id]

    if isinstance(sender, User):
        name = f"{sender.first_name or ''} {sender.last_name or ''}".strip()
    else:
        name = getattr(sender, "title", None) or str(sender_id)

    cache[sender_id] = name or str(sender_id)
    return sender_id, cache[sender_id]


def _status(text: str):
    cols = shutil.get_terminal_size().columns
    sys.stdout.write(f"\r{text[:cols]:<{cols}}")
    sys.stdout.flush()


async def _download_with_retry(client, msg, media_dir: Path, msg_id: int, media_type: str, msg_date: datetime | None) -> str | None:
    date_prefix = msg_date.strftime("%Y-%m-%dT%H-%M-%S") if msg_date else "unknown"
    filename = f"{date_prefix}_{media_type}_{msg_id}"
    for attempt in range(3):
        try:
            path = await client.download_media(msg, file=str(media_dir / filename))
            if path:
                return f"media/{Path(path).name}"
            return None
        except FloodWaitError as e:
            _status(f"  Rate limited, waiting {e.seconds}s...")
            await asyncio.sleep(e.seconds)
        except Exception as e:
            _status(f"  Warning: failed to download media for msg {msg_id}: {e}")
            return None
    return None


async def run_backup(client: TelegramClient, dialog, output_dir: str, backup_type: str):
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    backup_dir = Path(output_dir) / timestamp
    backup_dir.mkdir(parents=True, exist_ok=True)

    media_dir = backup_dir / "media"
    if backup_type in ("media", "both"):
        media_dir.mkdir(exist_ok=True)

    total = (await client.get_messages(dialog.entity, limit=0)).total
    print(f'\nBacking up "{dialog.name}" ({total} messages)...')

    messages = []
    sender_cache = {}
    count = 0
    media_count = 0

    async for msg in client.iter_messages(dialog.entity, limit=None):
        count += 1
        has_media = msg.media is not None
        media_type = _classify_media(msg.media) if has_media else None

        if backup_type == "media" and not has_media:
            _status(f"  [{count}/{total}] Skipping text-only message #{msg.id}")
            continue

        sender_id, sender_name = await _resolve_sender(client, msg, sender_cache)

        media_file = None
        if has_media and backup_type in ("media", "both"):
            _status(f"  [{count}/{total}] Downloading {media_type} from message #{msg.id}")
            media_file = await _download_with_retry(client, msg, media_dir, msg.id, media_type, msg.date)
            if media_file:
                media_count += 1
        else:
            _status(f"  [{count}/{total}] Message #{msg.id}")

        message_data = {
            "id": msg.id,
            "date": msg.date.isoformat() if msg.date else None,
            "from_id": sender_id,
            "from_name": sender_name,
            "text": msg.text or "",
            "reply_to_msg_id": msg.reply_to.reply_to_msg_id if msg.reply_to else None,
            "media_type": media_type,
            "media_file": media_file,
        }
        messages.append(message_data)

    messages.reverse()

    output = {
        "chat": {
            "id": dialog.id,
            "title": dialog.name,
            "type": _chat_type(dialog.entity),
        },
        "backup_type": backup_type,
        "backed_up_at": datetime.now(timezone.utc).isoformat(),
        "message_count": len(messages),
        "messages": messages,
    }

    _status("")
    print()

    json_path = backup_dir / "messages.json"
    json_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"  Done! {len(messages)} messages backed up.")
    if backup_type in ("media", "both"):
        print(f"  Media files: {media_count}")
    print(f"  Output: {backup_dir}/")
