import os

from dotenv import load_dotenv
from telethon import TelegramClient


async def create_client() -> TelegramClient:
    load_dotenv()

    try:
        api_id = int(os.environ["API_ID"])
        api_hash = os.environ["API_HASH"]
    except KeyError:
        print("Error: API_ID and API_HASH must be set in .env file.")
        print("Get them from https://my.telegram.org")
        raise SystemExit(1)

    phone = os.environ.get("PHONE")

    client = TelegramClient("tg_backuper", api_id, api_hash)
    await client.start(phone=phone)

    me = await client.get_me()
    print(f"Logged in as {me.first_name} {me.last_name or ''}".strip())

    return client
