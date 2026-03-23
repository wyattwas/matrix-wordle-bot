from sqlalchemy import Column, String
from sqlalchemy.orm import Session

from db.database import Base


class Token(Base):
    __tablename__ = "token"
    id = Column(String, primary_key=True, index=True)

def create(token: str, session: Session) -> Token:
    token = Token(id=token)
    old_token = session.query(Token).scalar()
    if old_token is not None:
        session.delete(old_token)
    session.add(token)
    session.commit()
    session.refresh(token)
    return token