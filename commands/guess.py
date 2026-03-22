from datetime import datetime

import requests
from nio import MatrixRoom, RoomMessageText, AsyncClient
from sqlalchemy import func
from sqlalchemy.orm import Session

from db import user
from db.database import SessionLocal
from db.guess import Guess


async def guess(room: MatrixRoom, event: RoomMessageText, client: AsyncClient, session: Session) -> None:
    db = SessionLocal()
    sender = user.get(event.sender, session)
    if not user.is_player_registered(sender.id, session):
        sender = user.create(user_id=event.sender, name=event.sender, session=session)

    date = datetime.today().strftime('%Y-%m-%d')
    wordle_json = requests.get(f"https://www.nytimes.com/svc/wordle/v2/{date}.json").json()
    date = datetime.strptime(date, '%Y-%m-%d').date()
    wordle = wordle_json["solution"]

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

    guess = Guess(
        date=date,
        word=event.body.split(" ")[2],
        correct=event.body.split(" ")[2]==wordle,
        user_id=sender.id
    )

    if len(guess.word) != 5:
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

    guess.index = db.query(func.max(Guess.index)).filter(Guess.user_id == sender.id, Guess.date == date).scalar() or 0
    already_guessed_it = any(guess.correct for guess in sender.get_all_guesses_for_today(session))

    if guess.index == 5 or already_guessed_it:
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

    if guess.index is None:
        guess.index = 0
        guess.points = 50
    elif guess.index == 0:
        guess.index = 1
        guess.points = 40
    elif guess.index == 1:
        guess.index = 2
        guess.points = 30
    elif guess.index == 2:
        guess.index = 3
        guess.points = 20
    elif guess.index == 3:
        guess.index = 4
        guess.points = 15
    elif guess.index == 4:
        guess.index = 5
        guess.points = 10

    if guess.correct:
        chart = build_guesses_chart(sender.get_all_guesses_for_today(session), wordle)

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
        chart = build_guesses_chart(sender.get_all_guesses(session), wordle)

        guess.points = 0

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

    guess.create(session)
    sender.calc_score(session)
    print('End for guess')

def build_guesses_chart(guesses: list[Guess], wordle: str) -> str:
    chart = ""
    guesses.sort(key=lambda guess: guess.index)
    print(f"guesses: {guesses}")

    for guess in guesses:
        for index, letter in enumerate(guess.word):
            if letter == wordle[index]:
                chart += "🟩"
            elif letter in wordle:
                chart += "🟨"
            else:
                chart += "⬛"
        chart += "\n"

    return chart