from nio import AsyncClient, RoomMessageText, MatrixRoom

import templates.help


async def help_command(room: MatrixRoom, event: RoomMessageText, client: AsyncClient) -> None:
    if event.body.startswith("!wordle") and "help" in event.body:
        body = ("# What can I do?"
                        "I am the Wordle bot, obviously you can play Wordle with me.\n"
                        "You can use the following commands:\n"
                        "**start:** register for the game\n"
                        "**guess:** get a overview of your guesses of today\n"
                        "**guess** *{word}* **:** take a guess at what today's Wordle might be\n"
                        "**score:** get a overview of the players scores\n"
                        "**date** *{yyyy-mm-dd}* **:** get the Wordle for a specific date\n"
                        "Example: !wordle start")

        await client.room_send(
            room_id=room.room_id,
            message_type="m.room.message",
            content={
                "msgtype": "m.text",
                "body": body,
                "format": "org.matrix.custom.html",
                "formatted_body": templates.help.help_template,
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