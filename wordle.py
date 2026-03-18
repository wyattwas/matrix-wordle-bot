from sqlite3 import Cursor

import requests
import re

from datetime import datetime
from nio import MatrixRoom, RoomMessageText, AsyncClient

from db import register_player_if_not_already


async def wordle_command(room: MatrixRoom, event: RoomMessageText, client: AsyncClient, sql_cursor: Cursor) -> None:
    if event.body.startswith("!wordle"):
        if "start" in event.body:
            await start(room, event, client, sql_cursor)

        if "guess" in event.body:
            await guess(room, event, client, sql_cursor)

        if "date" in event.body:
            await date(room, event, client)


async def start(room: MatrixRoom, event: RoomMessageText, client: AsyncClient, sql_cursor: Cursor) -> None:
    register_player_if_not_already(event.sender, sql_cursor)

    await client.room_send(
        room_id=room.room_id,
        message_type="m.room.message",
        content={
            "msgtype": "m.text",
            "body": "Please do: !wordle guess <your_guess>",
            "m.relates_to": {
                "rel_type": "m.thread",
                "event_id": event.event_id,
                "is_falling_back": True,
                "m.in_reply_to": {
                    "event_id": event.event_id
                }
            }
        }
    )

async def guess(room: MatrixRoom, event: RoomMessageText, client: AsyncClient, sql_cursor: Cursor) -> None:
    register_player_if_not_already(event.sender, sql_cursor)

    user_id = event.sender
    date = datetime.today().strftime('%Y-%m-%d')
    wordle_json = requests.get(f"https://www.nytimes.com/svc/wordle/v2/{date}.json").json()
    wordle = wordle_json["solution"]
    chart = ""

    if len(event.body.split(" ")) < 3:
        await client.room_send(
            room_id=room.room_id,
            message_type="m.room.message",
            content={
                "msgtype": "m.text",
                "body": "You didn't guess anything silly",
                "m.relates_to": {
                    "rel_type": "m.thread",
                    "event_id": event.event_id,
                    "is_falling_back": True,
                    "m.in_reply_to": {
                        "event_id": event.event_id
                    }
                }
            }
        )
        return

    guess = event.body.split(" ")[2]

    if len(guess) != 5:
        await client.room_send(
            room_id=room.room_id,
            message_type="m.room.message",
            content={
                "msgtype": "m.text",
                "body": "The word has to be at least five letters long.",
                "m.relates_to": {
                    "rel_type": "m.thread",
                    "event_id": event.event_id,
                    "is_falling_back": True,
                    "m.in_reply_to": {
                        "event_id": event.event_id
                    }
                }
            }
        )
        return

    for index, letter in enumerate(guess):
        if letter == wordle[index]:
            chart += "🟩"
        elif letter in wordle:
            chart += "🟨"
        else:
            chart += "⬛"

    sql_cursor.execute('SELECT max("index") FROM guess WHERE date=? AND user_id=?', (date, user_id))
    current_index = sql_cursor.fetchone()
    current_index = current_index[0]

    if current_index == 5:
        await client.room_send(
            room_id=room.room_id,
            message_type="m.room.message",
            content={
                "msgtype": "m.text",
                "body": f"You already finished your wordle for today",
                "m.relates_to": {
                    "rel_type": "m.thread",
                    "event_id": event.event_id,
                    "is_falling_back": True,
                    "m.in_reply_to": {
                        "event_id": event.event_id
                    }
                }
            }
        )
        return

    points = 0
    if current_index is None:
        current_index = 0
        points = 50
    elif current_index == 0:
        current_index = 1
        points = 40
    elif current_index == 1:
        current_index = 2
        points = 30
    elif current_index == 2:
        current_index = 3
        points = 20
    elif current_index == 3:
        current_index = 4
        points = 15
    elif current_index == 4:
        current_index = 5
        points = 10

    if wordle == guess:
        sql_cursor.execute(
            'INSERT INTO guess (date, "index", word, points, correct, user_id) VALUES(?, ?, ?, ?, ?, ?)',
            (date, current_index, guess, points, 1, user_id)
        )

        await client.room_send(
            room_id=room.room_id,
            message_type="m.room.message",
            content={
                "msgtype": "m.text",
                "body": f"{chart}\nYou got it: {wordle}",
                "m.relates_to": {
                    "rel_type": "m.thread",
                    "event_id": event.event_id,
                    "is_falling_back": True,
                    "m.in_reply_to": {
                        "event_id": event.event_id
                    }
                }
            }
        )
    else:
        sql_cursor.execute(
            'INSERT INTO guess (date, "index", word, points, correct, user_id) VALUES(?, ?, ?, ?, ?, ?)',
            (date, current_index, guess, points, 0, user_id)
        )

        await client.room_send(
            room_id=room.room_id,
            message_type="m.room.message",
            content={
                "msgtype": "m.text",
                "body": chart,
                "m.relates_to": {
                    "rel_type": "m.thread",
                    "event_id": event.event_id,
                    "is_falling_back": True,
                    "m.in_reply_to": {
                        "event_id": event.event_id
                    }
                }
            }
        )

async def date(room: MatrixRoom, event: RoomMessageText, client: AsyncClient) -> None:
    date = event.body.split(" ")[2]
    r = re.compile('\\d{4}-\\d{2}-\\d{2}')

    if r.match(date) is None:
        await client.room_send(
            room_id=room.room_id,
            message_type="m.room.message",
            content={
                "msgtype": "m.text",
                "body": "That's not a proper date (YYYY-MM-DD).",
                "m.relates_to": {
                    "rel_type": "m.thread",
                    "event_id": event.event_id,
                    "is_falling_back": True,
                    "m.in_reply_to": {
                        "event_id": event.event_id
                    }
                }
            }
        )
        return

    wordle_json = requests.get(
        f"https://www.nytimes.com/svc/wordle/v2/{date}.json").json()
    wordle = wordle_json.get("solution")

    if date == "2001-09-11":
        await client.room_send(
            room_id=room.room_id,
            message_type="m.room.message",
            content={
                "msgtype": "m.image",
                "body": "Twin-towers.jpg",
                "url": "mxc://matrix.opencodespace.org/zvPltjaGoFcgpNLsydFSfKLP",
                "m.relates_to": {
                    "rel_type": "m.thread",
                    "event_id": event.event_id,
                    "is_falling_back": True,
                    "m.in_reply_to": {
                        "event_id": event.event_id
                    }
                }
            }
        )
        return

    if wordle is None:
        await client.room_send(
            room_id=room.room_id,
            message_type="m.room.message",
            content={
                "msgtype": "m.text",
                "body": f"Sorry! I couldn't find the wordle for that date ({date}).",
                "m.relates_to": {
                    "rel_type": "m.thread",
                    "event_id": event.event_id,
                    "is_falling_back": True,
                    "m.in_reply_to": {
                        "event_id": event.event_id
                    }
                }
            }
        )
        return

    await client.room_send(
        room_id=room.room_id,
        message_type="m.room.message",
        content={
            "msgtype": "m.text",
            "body": f"The wordle of that day was: ||{wordle}||",
            "m.relates_to": {
                "rel_type": "m.thread",
                "event_id": event.event_id,
                "is_falling_back": True,
                "m.in_reply_to": {
                    "event_id": event.event_id
                }
            }
        }
    )