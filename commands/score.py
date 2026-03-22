from nio import MatrixRoom, RoomMessageText, AsyncClient
from sqlalchemy.orm import Session

from db.database import SessionLocal
from db.user import User


async def score(room: MatrixRoom, event: RoomMessageText, client: AsyncClient, session: Session) -> None:
    if event.body.startswith("!wordle") and "score" in event.body:
        users = session.query(User).order_by(User.score.desc()).all()

        if users is None:
            await client.room_send(
                room_id=room.room_id,
                message_type="m.room.message",
                content={
                    "msgtype": "m.text",
                    "body": "No ones on the scoreboard yet. Type !wordle start to get started",
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

        top_three = users[:3]
        lines = ["🏆 Top 3 Players:"]

        current_user = None
        for u in users:
            if u.id == event.sender:
                current_user = u
                break

        for i, user in enumerate(top_three, start=1):
            lines.append(f"{i}. {user.id} - {user.score} points")

        if current_user and current_user not in top_three:
            lines.append("\nYour position:")
            rank = users.index(current_user) + 1
            lines.append(f"{rank}. {current_user.id} - {current_user.score} points")

        message = "\n".join(lines)

        await client.room_send(
            room_id=room.room_id,
            message_type="m.room.message",
            content={
                "msgtype": "m.text",
                "body": message,
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