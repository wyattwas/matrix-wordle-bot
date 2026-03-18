from sqlite3 import Cursor

from nio import MatrixRoom, RoomMessageText, AsyncClient


async def score(room: MatrixRoom, event: RoomMessageText, client: AsyncClient, sql_cursor: Cursor) -> None:
    if event.body.startswith("!wordle") and "score" in event.body:
        sql_cursor.execute('SELECT id, score FROM user ORDER BY score DESC')
        score_board = sql_cursor.fetchall()

        if not score_board:
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

        top_three = score_board[:3]
        lines = ["🏆 Top 3 Players:"]

        current_user = None
        for u in score_board:
            if u[0] == event.sender:
                current_user = u
                break

        for i, user in enumerate(top_three, start=1):
            lines.append(f"{i}. {user[0]} - {user[1]} points")

        if current_user and current_user not in top_three:
            lines.append("\nYour position:")
            rank = score_board.index(current_user) + 1
            lines.append(f"{rank}. {event.sender[0]} - {event.sender[1]} points")

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