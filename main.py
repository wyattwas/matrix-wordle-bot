import asyncio
import os

from dotenv import load_dotenv
from nio import AsyncClient, MatrixRoom, RoomMessageText, InviteEvent, AsyncClientConfig

import db
from invite_event import invites
from wordle import wordle_command

async def message_callback(room: MatrixRoom, event: RoomMessageText) -> None:
    print(
        f"Message received in room {room.display_name}\n"
        f"{room.user_name(event.sender)} | {event.body}"
    )

async def main() -> None:
    print(await client.login(password))
    await client.join("!siypcvZvJjaxckwixG:matrix.opencodespace.org")
    await client.set_presence("online", "Wanna try guessing today's wordle?")
    await client.sync_forever()

load_dotenv()
password = os.getenv("PASSWORD") or ""
home_server = os.getenv("HOME_SERVER") or "https://matrix.org"
user_name = os.getenv("USER_NAME") or ""

client = AsyncClient(homeserver=home_server, user=user_name, config=AsyncClientConfig(store_sync_tokens=True))
client.add_event_callback(message_callback, RoomMessageText)
client.add_event_callback(
    lambda room, event: wordle_command(room, event, client, sql_cursor),
    RoomMessageText
)
client.add_event_callback(
    lambda room, event: invites(client, room, event),
    InviteEvent
)
sql_cursor = db.setup()

asyncio.run(main())
