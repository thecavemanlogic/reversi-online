from flask import Flask, request, Response, redirect, send_from_directory
from htmllib import html, head, body, div, h1, div
from db.util import gen_id
from random import random

app = Flask(__name__)

def base(*contents):
    return html.html(
        head(
            html.script(src="/static/script.js"),
            html.link(rel="stylesheet", href="/static/style.css")
        ),
        body(
            *contents
        )
    ).to_html()

def create_game_square(idx):
    x = idx % 8
    y = idx // 8
    color = "light" if (x % 2 == 0) != (y % 2 == 0) else "dark"
    return html.div(
        "" if random() > 0.8 else html.div(cls="circle"),
        cls=f"square-{idx} square square-{color}",
        onclick=f"click_square({idx});"
    )

def create_game_board():

    squares = [create_game_square(i) for i in range(64)]

    return html.div(
        *squares,
        cls="grid"
    )

@app.route("/static/<path:path>")
def send_static(path):
    return send_from_directory(path)

@app.route("/")
def index():
    return base(
        h1("Hello there!"),
        div(
            html.p("how are you doing?"),
            html.button(
                "Join Game",
                onclick="join_game();"
            )
        )
    )

game_queue = set()

@app.route("/join-game", methods=["POST"])
def join_game():

    resp = Response()

    # if not a registered user
    if request.cookies.get("user_id") is None:
        resp.set_cookie("user_id", gen_id())

    game_id = request.args.get("id")
    if game_id is None:
        game_id = gen_id()

    resp.location = f"/play-game?id={game_id}"
    resp.status_code = 302

    # return redirect("/play-game?id=", resp)
    return resp

@app.route("/play-game")
def play_game():
    game_id = request.args.get("id")
    return base(
        h1(f"Game {game_id}"),
        create_game_board()
    )

# @app.route("/make-move", methods=["POST"])
# def make_move():


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")