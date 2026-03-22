from nio import AsyncClient, RoomMessageText, MatrixRoom


async def help_command(room: MatrixRoom, event: RoomMessageText, client: AsyncClient) -> None:
    if event.body.startswith("!wordle") and "help" in event.body:
        formatted_body = (f"<h1 data-md=\"#\">What can I do?</h1>"
                        f"I am the Wordle bot, obviously you can play Wordle with me.<br>"
                        f"You can use the following commands:<br>"
                        f"<strong data-md=\"**\">start:</strong> register for the game<br>"
                        f"<strong data-md=\"**\">guess:</strong> take a guess at what today's Wordle might be<br>"
                        f"<strong data-md=\"**\">score:</strong> get a overview of the players scores<br>"
                        f"<strong data-md=\"**\">date:</strong> get the Wordle for a specific date<br>"
                        f"Example: !wordle start")

        await client.room_send(
            room_id=room.room_id,
            message_type="m.room.message",
            content={
                "msgtype": "m.text",
                "body": formatted_body
                .replace("<strong data-md=\"**\">", "**")
                .replace("</strong>", "**")
                .replace("<h1 data-md=\"#\">", "# ")
                .replace("</h1>", "")
                .replace("<br>", "\n"),
                "format": "org.matrix.custom.html",
                "formatted_body": formatted_body,
                "m.relates_to": {
                    "rel_type": "m.reply",
                    "event_id": event.event_id,
                    "is_falling_back": True,
                    "m.in_reply_to": {
                        "event_id": event.event_id
                    }
                }
            }
        )