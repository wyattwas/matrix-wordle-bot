from nio import MatrixRoom, RoomMessageText, AsyncClient
from sqlalchemy.orm import Session

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
        lines_body = ["🏆 Top 3 Players:"]
        lines_formatted_body = ["🏆 Top 3 Players:"]

        current_user = next((u for u in users if u.id == event.sender), None)

        for i, user in enumerate(top_three, start=1):
            lines_body.append(f"{i}. {user.id} - {user.score} points")
            lines_formatted_body.append(
                f'{i}. <a href="https://matrix.to/#/{user.id}">{user.name}</a> - {user.score} points')

        if current_user and current_user not in top_three:
            lines_body.append("\nYour position:")
            lines_formatted_body.append("<br>Your position:")
            rank = users.index(current_user) + 1
            lines_body.append(f"{rank}. {current_user.id} - {current_user.score} points")
            lines_formatted_body.append(
                f'{rank}. <a href="https://matrix.to/#/{current_user.id}">{current_user.name}</a> - {current_user.score} points')

        body = "\n".join(lines_body)
        formatted_body = "<br>".join(lines_formatted_body)

        await client.room_send(
            room_id=room.room_id,
            message_type="m.room.message",
            content={
                "msgtype": "m.text",
                "body": body,
                "format": "org.matrix.custom.html",
                "formatted_body": formatted_body,
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