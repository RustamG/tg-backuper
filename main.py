import asyncio

from simple_term_menu import TerminalMenu

from src.auth import create_client
from src.chat_selector import select_chat
from src.backup import run_backup

BACKUP_TYPES = [
    ("Text only", "text"),
    ("Media only", "media"),
    ("Both (text + media)", "both"),
]


async def main():
    client = await create_client()

    async with client:
        dialog = await select_chat(client)

        output_dir = input("\nOutput directory [./backups]: ").strip() or "./backups"

        menu = TerminalMenu(
            [label for label, _ in BACKUP_TYPES],
            title="\nWhat to backup:",
            menu_cursor="❯ ",
            menu_cursor_style=("fg_cyan", "bold"),
            menu_highlight_style=("fg_cyan", "bold"),
        )
        index = menu.show()
        if index is None:
            print("No backup type selected.")
            raise SystemExit(0)

        backup_type = BACKUP_TYPES[index][1]
        await run_backup(client, dialog, output_dir, backup_type)


if __name__ == "__main__":
    asyncio.run(main())
