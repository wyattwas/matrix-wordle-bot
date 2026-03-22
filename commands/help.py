from nio import AsyncClient, RoomMessageText, MatrixRoom


async def help_command(room: MatrixRoom, event: RoomMessageText, client: AsyncClient) -> None:
    if event.body.startswith("!wordle") and "help" in event.body:
        formatted_body = ("<h1 data-md=\"#\">What can I do?</h1>"
                        "I am the Wordle bot, obviously you can play Wordle with me.<br>"
                        "You can use the following commands:<br>"
                        "<strong data-md=\"**\">start:</strong> register for the game<br>"
                        "<strong data-md=\"**\">guess:</strong> get a overview of your guesses of today<br>"
                        "<strong data-md=\"**\">guess</strong> <i data-md=\"*\">{word}</i><strong data-md=\"**\">:</strong> take a guess at what today's Wordle might be<br>"
                        "<strong data-md=\"**\">score:</strong> get a overview of the players scores<br>"
                        "<strong data-md=\"**\">date</strong> <i data-md=\"*\">{yyyy-mm-dd}</i><strong data-md=\"**\">:</strong> get the Wordle for a specific date<br>"
                        "Example: !wordle start")

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
                .replace("<br>", "\n")
                .replace("<i data-md=\"*\">", "*")
                .replace("</i>", "*"),
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