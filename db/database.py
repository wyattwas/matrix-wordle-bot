import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()
db_file_path = os.getenv("DB_URL")
engine = create_engine(db_file_path)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def setup():
    Base.metadata.create_all(bind=engine)