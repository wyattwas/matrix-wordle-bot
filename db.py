import os
import sqlite3
from datetime import datetime
from sqlite3 import Cursor


def setup() -> Cursor:
    db_file_path = os.getenv("SQL_FILE")
    con = sqlite3.connect(db_file_path)
    cur = con.cursor()
    (cur.execute("CREATE TABLE IF NOT EXISTS user(id text, name text, score integer)")
     .execute('CREATE TABLE IF NOT EXISTS guess(id integer auto_increment PRIMARY KEY, date text, "index" integer, word varchar(5), points integer, correct integer, user_id integer, FOREIGN KEY(user_id) REFERENCES user(id));'))
    return cur

def is_player_registered(user_id: str, sql_cursor: Cursor) -> bool:
    sql_cursor.execute('SELECT id FROM user WHERE id=?', (user_id,))
    user = sql_cursor.fetchone()
    return user is not None

def register_player(user_id: str, sql_cursor: Cursor) -> None:
    execute_and_commit(
        sql_cursor,
        'INSERT INTO user VALUES(?, ?, ?)',
        (user_id, user_id, 0)
    )

def register_player_if_not_already(user_id: str, sql_cursor: Cursor) -> None:
    if not is_player_registered(user_id, sql_cursor):
        register_player(user_id, sql_cursor)

def get_all_guesses_for_user(user_id: str, sql_cursor: Cursor) -> list:
    return get_all_guesses_for_user_for_date(user_id, datetime.today(), sql_cursor)

def get_all_guesses_for_user_for_date(user_id: str, date: datetime, sql_cursor: Cursor) -> list:
    sql_cursor.execute('SELECT * FROM guess WHERE date=? AND user_id=?', (date, user_id))
    return sql_cursor.fetchall()

def execute_and_commit(sql_cursor, *args, **kwargs) -> Cursor:
    sql_cursor.execute(*args, **kwargs)
    sql_cursor.connection.commit()
    return sql_cursor