import asyncio
import os
from multiprocessing.spawn import old_main_modules

from dotenv import load_dotenv
from nio import AsyncClient, MatrixRoom, RoomMessageText, InviteEvent, AsyncClientConfig

import db.database as db
from commands.help import help_command

from commands.invite_event import invites
from commands.score import score
from db import token
from db.database import SessionLocal
from db.token import Token
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
    client.config = AsyncClientConfig(store_sync_tokens=True)
    old_token = session.query(Token).scalar()
    await client.sync_forever(since=old_token.id if old_token else None)

load_dotenv()
password = os.getenv("PASSWORD") or ""
home_server = os.getenv("HOME_SERVER") or "https://matrix.org"
user_name = os.getenv("USER_NAME") or ""

client = AsyncClient(homeserver=home_server, user=user_name, config=AsyncClientConfig(store_sync_tokens=True))
client.add_event_callback(message_callback, RoomMessageText)
with SessionLocal() as session:
    client.add_event_callback(
        lambda room, event: wordle_command(room, event, client, session),
        RoomMessageText
    )
    client.add_event_callback(
        lambda room, event: invites(room, event, client),
        InviteEvent
    )
    client.add_event_callback(
        lambda room, event: score(room, event, client, session),
        RoomMessageText
    )
    client.add_event_callback(
        lambda room, event: help_command(room, event, client),
        RoomMessageText
    )
db.setup()

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Shutting down")
finally:
    if client.next_batch:
        print(f"Saving token: {client.next_batch}")
        with SessionLocal() as session:
            token.create(client.next_batch, session)
    else:
        print("Could not save token")
    asyncio.run(client.close())
