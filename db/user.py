from datetime import datetime
from typing import List

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session

from db.database import Base
from db.guess import Guess


class User(Base):
    __tablename__ = 'user'

    id = Column(String, primary_key=True, unique=True, index=True)
    name = Column(String, index=True)
    score = Column(Integer, index=True)

    def calc_score(self, session: Session) -> float:
        guesses = session.query(Guess).filter(Guess.user_id == self.id).all()
        print(f'calc_score: {guesses}')

        self.score = sum(g.points for g in guesses)

        print(f'calc_score: {self.score}')
        session.commit()

        return self.score

    def get_all_guesses(self, session: Session) -> List[Guess]:
        return session.query(Guess).filter(Guess.user_id == self.id).all()

    def get_all_guesses_for_today(self, session: Session) -> List[Guess]:
        return session.query(Guess).filter(Guess.user_id == self.id, Guess.date == datetime.today().strftime('%Y-%m-%d')).all()


def get(user_id: str, session: Session) -> User or None:
    return session.query(User).filter_by(id=user_id).scalar()

def create(user_id: str, name: str, session: Session, score=0) -> User:
    user = User(id=user_id, name=name, score=score)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def is_player_registered(user_id: str, session: Session) -> bool:
    return session.query(User.id).filter(User.id == user_id).scalar() is not None