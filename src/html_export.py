import html
from datetime import datetime
from pathlib import Path

SENDER_COLORS = [
    "#e3f2fd", "#f3e5f5", "#e8f5e9", "#fff3e0",
    "#fce4ec", "#e0f7fa", "#f1f8e9", "#ede7f6",
    "#fff8e1", "#e1f5fe", "#f9fbe7", "#fbe9e7",
]

CSS = """
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: #e5ddd5;
    padding: 20px;
    max-width: 800px;
    margin: 0 auto;
}
.header {
    background: #075e54;
    color: white;
    padding: 16px 20px;
    border-radius: 8px 8px 0 0;
    margin-bottom: 0;
    position: sticky;
    top: 0;
    z-index: 10;
}
.header h1 { font-size: 18px; font-weight: 600; }
.header .meta { font-size: 12px; opacity: 0.8; margin-top: 4px; }
.chat {
    background: #e5ddd5;
    padding: 12px 16px;
    display: flex;
    flex-direction: column;
    gap: 4px;
}
.date-sep {
    text-align: center;
    margin: 12px 0;
}
.date-sep span {
    background: #d4eaf5;
    color: #3a6d8c;
    font-size: 12px;
    padding: 4px 12px;
    border-radius: 8px;
    font-weight: 500;
}
.msg {
    max-width: 75%;
    padding: 6px 10px 6px 10px;
    border-radius: 8px;
    position: relative;
    word-wrap: break-word;
    line-height: 1.4;
    font-size: 14px;
}
.msg-left { align-self: flex-start; }
.msg-right { align-self: flex-end; }
.sender {
    font-size: 12px;
    font-weight: 600;
    margin-bottom: 2px;
}
.time {
    font-size: 11px;
    color: #667781;
    float: right;
    margin-left: 8px;
    margin-top: 4px;
}
a.reply {
    display: block;
    background: rgba(0,0,0,0.05);
    border-left: 3px solid #075e54;
    padding: 4px 8px;
    margin-bottom: 4px;
    border-radius: 4px;
    font-size: 12px;
    color: #555;
    max-height: 50px;
    overflow: hidden;
    text-decoration: none;
    cursor: pointer;
}
a.reply:hover { background: rgba(0,0,0,0.1); }
.msg.highlight { animation: highlight 1.5s ease; }
@keyframes highlight {
    0% { box-shadow: 0 0 0 3px rgba(7,94,84,0.5); }
    100% { box-shadow: none; }
}
.text { white-space: pre-wrap; }
.text code {
    background: rgba(0,0,0,0.06);
    padding: 1px 4px;
    border-radius: 3px;
    font-family: "SF Mono", "Fira Code", "Consolas", monospace;
    font-size: 13px;
}
.text pre {
    background: rgba(0,0,0,0.06);
    padding: 8px 10px;
    border-radius: 6px;
    font-family: "SF Mono", "Fira Code", "Consolas", monospace;
    font-size: 13px;
    overflow-x: auto;
    margin: 4px 0;
}
.text a { color: #075e54; }
.text blockquote {
    border-left: 3px solid #075e54;
    padding-left: 8px;
    margin: 4px 0;
    color: #555;
}
.text .tg-spoiler {
    background: #333;
    color: #333;
    border-radius: 3px;
    padding: 0 2px;
    cursor: pointer;
    transition: color 0.2s;
}
.text .tg-spoiler:hover { color: #fff; }
.media { margin: 4px 0; }
.media img {
    max-width: 100%;
    border-radius: 6px;
    display: block;
}
.media video {
    max-width: 100%;
    border-radius: 6px;
    display: block;
}
.media audio { width: 100%; margin: 4px 0; }
.media .sticker { max-width: 200px; }
.media .video-note {
    width: 240px;
    height: 240px;
    border-radius: 50%;
    object-fit: cover;
}
.media a {
    display: inline-block;
    padding: 6px 10px;
    background: rgba(0,0,0,0.05);
    border-radius: 6px;
    color: #075e54;
    text-decoration: none;
    font-size: 13px;
}
.media a:hover { text-decoration: underline; }
.media-placeholder {
    display: inline-block;
    padding: 4px 8px;
    background: rgba(0,0,0,0.06);
    border-radius: 4px;
    color: #888;
    font-size: 12px;
    font-style: italic;
}
.forwarded {
    background: rgba(0,0,0,0.04);
    border-left: 3px solid #5ca7d8;
    padding: 4px 8px;
    margin-bottom: 4px;
    border-radius: 4px;
    font-size: 12px;
    color: #5ca7d8;
    font-weight: 500;
}
"""


def _sender_color(sender_id: int | None) -> str:
    if sender_id is None:
        return SENDER_COLORS[0]
    return SENDER_COLORS[sender_id % len(SENDER_COLORS)]


def _render_media(msg: dict) -> str:
    media_type = msg.get("media_type")
    media_file = msg.get("media_file")

    if not media_type:
        return ""

    if not media_file:
        return f'<div class="media-placeholder">[{html.escape(media_type)}]</div>'

    escaped = html.escape(media_file)

    if media_type == "photo":
        return f'<div class="media"><img src="{escaped}" loading="lazy" alt="photo"></div>'
    if media_type == "video":
        return f'<div class="media"><video controls preload="none"><source src="{escaped}"></video></div>'
    if media_type == "video_note":
        return f'<div class="media"><video class="video-note" controls preload="none"><source src="{escaped}"></video></div>'
    if media_type in ("voice", "audio"):
        return f'<div class="media"><audio controls preload="none" src="{escaped}"></audio></div>'
    if media_type == "sticker":
        return f'<div class="media"><img class="sticker" src="{escaped}" loading="lazy" alt="sticker"></div>'
    # document, animation, other
    filename = Path(media_file).name
    return f'<div class="media"><a href="{escaped}">\U0001f4ce {html.escape(filename)}</a></div>'


def _render_message(msg: dict, reply_map: dict, my_id: int | None) -> str:
    sender_id = msg.get("from_id")
    sender_name = html.escape(msg.get("from_name", "Unknown"))
    color = _sender_color(sender_id)
    side = "msg-right" if sender_id == my_id else "msg-left"

    time_str = ""
    if msg.get("date"):
        try:
            dt = datetime.fromisoformat(msg["date"])
            time_str = dt.strftime("%H:%M")
        except (ValueError, TypeError):
            pass

    parts = []
    msg_id = msg.get("id", "")
    parts.append(f'<div class="msg {side}" id="msg-{msg_id}" style="background:{color}">')
    parts.append(f'<div class="sender" style="color:{_sender_name_color(sender_id)}">{sender_name}</div>')

    fwd = msg.get("forwarded_from")
    if fwd:
        fwd_name = html.escape(fwd.get("from_name", "Unknown"))
        fwd_date = ""
        if fwd.get("date"):
            try:
                fwd_dt = datetime.fromisoformat(fwd["date"])
                fwd_date = f' &middot; {fwd_dt.strftime("%b %d, %Y")}'
            except (ValueError, TypeError):
                pass
        parts.append(f'<div class="forwarded">Forwarded from <b>{fwd_name}</b>{fwd_date}</div>')

    reply_id = msg.get("reply_to_msg_id")
    if reply_id and reply_id in reply_map:
        replied = reply_map[reply_id]
        reply_text = html.escape(replied.get("text", "")[:100])
        reply_sender = html.escape(replied.get("from_name", ""))
        parts.append(f'<a href="#msg-{reply_id}" class="reply"><b>{reply_sender}</b><br>{reply_text}</a>')

    media_html = _render_media(msg)
    if media_html:
        parts.append(media_html)

    text_html = msg.get("text_html", "")
    if text_html:
        parts.append(f'<span class="text">{text_html}</span>')
    elif msg.get("text"):
        parts.append(f'<span class="text">{html.escape(msg["text"])}</span>')

    parts.append(f'<span class="time">{time_str}</span>')
    parts.append('</div>')

    return "\n".join(parts)


SENDER_NAME_COLORS = [
    "#075e54", "#7b1fa2", "#c62828", "#1565c0",
    "#2e7d32", "#e65100", "#4527a0", "#00838f",
    "#ad1457", "#558b2f", "#6a1b9a", "#d84315",
]


def _sender_name_color(sender_id: int | None) -> str:
    if sender_id is None:
        return SENDER_NAME_COLORS[0]
    return SENDER_NAME_COLORS[sender_id % len(SENDER_NAME_COLORS)]


def generate_html(backup_data: dict, backup_dir: Path, my_id: int | None = None):
    chat_info = backup_data["chat"]
    messages = backup_data["messages"]

    reply_map = {m["id"]: m for m in messages}

    parts = []
    parts.append("<!DOCTYPE html>")
    parts.append('<html lang="en"><head>')
    parts.append('<meta charset="utf-8">')
    parts.append('<meta name="viewport" content="width=device-width, initial-scale=1">')
    parts.append(f'<title>{html.escape(chat_info["title"])} — Backup</title>')
    parts.append(f"<style>{CSS}</style>")
    parts.append("</head><body>")

    parts.append('<div class="header">')
    parts.append(f'<h1>{html.escape(chat_info["title"])}</h1>')
    parts.append(f'<div class="meta">{chat_info["type"]} &middot; {backup_data["message_count"]} messages &middot; backed up {html.escape(backup_data["backed_up_at"][:10])}</div>')
    parts.append("</div>")
    parts.append('<div class="chat">')

    last_date = None
    for msg in messages:
        if msg.get("date"):
            try:
                dt = datetime.fromisoformat(msg["date"])
                msg_date = dt.strftime("%B %d, %Y")
                if msg_date != last_date:
                    parts.append(f'<div class="date-sep"><span>{msg_date}</span></div>')
                    last_date = msg_date
            except (ValueError, TypeError):
                pass

        parts.append(_render_message(msg, reply_map, my_id))

    parts.append("</div>")
    parts.append("""<script>
document.querySelectorAll('a.reply').forEach(a => {
    a.addEventListener('click', e => {
        e.preventDefault();
        const target = document.querySelector(a.getAttribute('href'));
        if (!target) return;
        target.scrollIntoView({behavior: 'smooth', block: 'center'});
        target.classList.remove('highlight');
        void target.offsetWidth;
        target.classList.add('highlight');
    });
});
</script>""")
    parts.append("</body></html>")

    html_path = backup_dir / "chat.html"
    html_path.write_text("\n".join(parts), encoding="utf-8")
    return html_path
