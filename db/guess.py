from sqlalchemy import Integer, Column, Date, String, Boolean
from sqlalchemy.orm import Session

from db.database import Base, SessionLocal


class Guess(Base):
    __tablename__ = 'guess'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    date = Column(Date, index=True)
    index = Column(Integer, index=True)
    word = Column(String, index=True)
    points = Column(Integer, index=True)
    correct = Column(Boolean, index=True)
    user_id = Column(String, index=True)

    def create(self, session: Session) -> None:
        session.add(self)
        session.commit()
        session.refresh(self)