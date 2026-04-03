from simple_term_menu import TerminalMenu
from telethon import TelegramClient
from telethon.tl.types import User, Chat, Channel


def _chat_type(entity) -> str:
    if isinstance(entity, User):
        return "User"
    if isinstance(entity, Chat):
        return "Group"
    if isinstance(entity, Channel):
        return "Channel" if entity.broadcast else "Group"
    return "Unknown"


async def select_chat(client: TelegramClient):
    dialogs = await client.get_dialogs()

    entries = []
    for d in dialogs:
        kind = _chat_type(d.entity)
        entries.append(f"{d.name}  ({kind})")

    menu = TerminalMenu(
        entries,
        title="\nSelect a chat (↑/↓ to navigate, Enter to select, / to search):",
        menu_cursor="❯ ",
        menu_cursor_style=("fg_cyan", "bold"),
        menu_highlight_style=("fg_cyan", "bold"),
        search_key="/",
        show_search_hint=True,
    )

    index = menu.show()
    if index is None:
        print("No chat selected.")
        raise SystemExit(0)

    print(f'Selected: {dialogs[index].name}')
    return dialogs[index]
