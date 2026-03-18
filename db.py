import os
import sqlite3
from sqlite3 import Cursor


def setup() -> Cursor:
    db_file_path = os.getenv("SQL_FILE")
    con = sqlite3.connect(db_file_path)
    cur = con.cursor()
    (cur.execute("CREATE TABLE IF NOT EXISTS user(id text, name text, score integer)")
     .execute('CREATE TABLE IF NOT EXISTS guess(id integer auto_increment PRIMARY KEY, date text, "index" integer, word varchar(5), points integer, correct integer, user_id integer, FOREIGN KEY(user_id) REFERENCES user(id));'))
    return cur
