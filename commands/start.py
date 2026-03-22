from nio import MatrixRoom, RoomMessageText, AsyncClient
from sqlalchemy.orm import Session

from db import user


async def start(room: MatrixRoom, event: RoomMessageText, client: AsyncClient, session: Session) -> None:
    if not user.is_player_registered(event.sender, session):
        user.create(user_id=event.sender, name=event.sender, session=session)

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