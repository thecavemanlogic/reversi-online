import os
import sqlite3
import util

conn: sqlite3.Connection = None
cur: sqlite3.Cursor = None

initial_state = """
........
........
........
...XO...
...OX...
........
........
........
""".replace('\n', '')

def init():
    global conn, cur

    if not os.path.isfile('reversi.db'):
        conn = sqlite3.connect('reversi.db')
        cur = conn.cursor()
        cur.executescript('''
        create table user (
            username text not null,
            password text not null,

            primary key(username)
        );

        create table game (
            id text not null,
            state text not null,
            turn integer not null,
            winner text,

            primary key(id),
            foreign key(winner) references user(username)
        );

        create table participation (
            game text,
            user text,

            primary key(game, user),
            foreign key(game) references game(id)
        );
        ''')
    else:
        conn = sqlite3.connect('reversi.db')
        cur = conn.cursor()

# admin functions

def list_all_users():
    cur.execute("select * from user")
    return cur.fetchall()

def list_active_games() -> (int, str):
    cur.execute("select * from game where winner is NULL")
    return cur.fetchall()

def delete_user(username: str):
    cur.execute("delete from user where username = ?", (username,))

# user functions

def create_user(username, password):
    try:
        cur.execute("insert into user values (?, ?)", (username, password))
        return True
    except:
        return False

def login(username, password):
    cur.execute("select * from user where username = ? and password = ?", (username, password))
    return len(cur.fetchall()) > 0

# games

def create_game():
    id = util.gen_id(k=6)
    cur.execute("insert into game (id, state, turn) values (?, ?, 0)", (id, initial_state))
    return id
