from flask import Flask, request, Response, redirect, send_from_directory, abort
from db.game import Game
from db.player import Player
from htmllib import html, head, body, div, h1, div
from db.util import gen_id
from random import random
import json

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

def create_game_square(idx, value):
    x = idx % 8
    y = idx // 8
    color = "light" if (x % 2 == 0) != (y % 2 == 0) else "dark"

    def get_piece(value):
        if value == "X":
            return html.div(cls="circle black")
        elif value == "O":
            return html.div(cls="circle white")

    return html.div(
        "" if value == "." else get_piece(value),
        cls=f"square-{idx} square square-{color}",
        onclick=f"click_square({idx});"
    )

def create_game_board(state: list):

    # squares = [(0 for col in row) for row in state]
    # squares = [create_game_square(i) for i in range(64)]
    flat = [col for row in state for col in row]

    squares = [create_game_square(idx, val) for idx, val in enumerate(flat)]

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
                onclick="join_game();",
                id="join-game-btn"
            )
        )
    )

game_queue = set()

@app.route("/join-game", methods=["POST"])
def join_game():

    resp = Response()

    # register the client if not already a user
    user = Player.get(request.cookies.get("user_id"))
    if user is None:
        user = Player()
        user.save()
        resp.set_cookie("user_id", user.id)

    # get game_id if present
    game_id = request.args.get("id")

    # if given a game id
    if game_id:
        game = Game.get(game_id)

        # if the game exists
        if game:
            
            # if the user successfully joined the game
            if game.join(user.id):
                print("joining game", game_id)
                resp.location = f"/play-game?id={game_id}"
                resp.status_code = 302
                resp.set_data("{}")
            
            # if the user failed to join the game
            else:
                print("user could not join game", game_id)

        # if the game does not exist
        else:
            print(f"game {game_id} does not exist")
            resp.set_data(json.dumps({
                "error": "game does not exist"
            }))
    elif len(game_queue) == 1 and user.id not in game_queue:

        other_user = Player.get(game_queue.pop())
        
        game = Game()
        game.join(user.id)
        game.join(other_user.id)
        game.save()
        

    else:
        game_queue.add(user.id)

    return resp

@app.route("/check-queue")
def queue_status():
    player = Player.get(request.cookies.get("user_id"))
    if not player:
        return abort(401)
    
    game_id = player.get_next_game()
    if not game_id:
        return ""
    
    return redirect(f"/play-game?id={game_id}")
    

@app.route("/play-game")
def play_game():

    # get game
    game = Game.get(request.args.get("id"))
    if not game:
        return abort(404)

    return base(
        h1(f"Game {game.id}"),
        create_game_board(game.state)
    )

@app.route("/make-move", methods=["POST"])
def make_move():

    user = Player.get(request.cookies.get("user_id"))
    if not user:
        abort(401)

    body = request.get_json()

    print("body:", body, type(body))

    idx = body.get("idx")
    game = Game.get(body.get("game"))

    if idx is None:
        print("invalid idx", idx)
        abort(400)
    elif game is None:
        print("game not found!", body.get("game"), Game.games)
        abort(404)

    if not game.is_next(user.id):
        return "Not your turn", 400

    print(1)

    game.make_move(user, idx)

    print(2)

    return ""

# @app.route("/make-move", methods=["POST"])
# def make_move():


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")