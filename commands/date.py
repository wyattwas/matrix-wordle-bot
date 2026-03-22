import re

import requests
from nio import MatrixRoom, RoomMessageText, AsyncClient


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
            "body": f"The wordle of that day was: || {wordle} ||",
            "format": "org.matrix.custom.html",
            "formatted_body": f'The wordle of that day was: <span data-md="||" data-mx-spoiler>{wordle}</span>',
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