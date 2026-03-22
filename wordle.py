from nio import MatrixRoom, RoomMessageText, AsyncClient
from sqlalchemy.orm import Session

from commands.date import date
from commands.guess import guess
from commands.start import start


async def wordle_command(room: MatrixRoom, event: RoomMessageText, client: AsyncClient, session: Session) -> None:
    if event.body.startswith("!wordle"):
        if "start" in event.body:
            await start(room, event, client, session)

        if "guess" in event.body:
            await guess(room, event, client, session)

        if "date" in event.body:
            await date(room, event, client)
