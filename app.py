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
    user_id = request.cookies.get("user_id")
    if user_id is None:
        new_player = Player()
        user_id = gen_id()
        resp.set_cookie("user_id", new_player.id)

    # get game_id if present
    game_id = request.args.get("id")

    # if given a game id
    if game_id:
        game = Game.get(game_id)

        # if the game exists
        if game:
            
            # if the user successfully joined the game
            if game.join(user_id):
                print("joining game", game_id)
                resp.location = f"/play-game?id={game_id}"
                resp.status_code = 302
                resp.set_data("{}")
            
            # if the user failed to join the game
            else:
                print("user could not join game", game_id)
                resp.set_data("{}")

        # if the game does not exist
        else:
            print(f"game {game_id} does not exist")
            resp.set_data(json.dumps({
                "error": "game does not exist" 
            }))
    
    # if there is another player in the queue
    elif len(game_queue) > 0 and user_id not in game_queue:

        print("creating a new game")
        
        # create a new game
        game = Game()
        game.join(user_id)
        game.join(game_queue.pop())

        resp.location = f"/play-game?id={game.id}"
        resp.status_code = 302
        resp.set_data("{}")

    else:
        print("adding player to queue", len(game_queue))
        game_queue.add(user_id)
        resp.set_data("{}")

    # return redirect("/play-game?id=", resp)
    return resp

@app.route("/queue-status")
def queue_status():
    player = Player.get(request.cookies.get("user_id"))
    if not player:
        return abort(401)
    
    game_id = player.get_next_game()
    if not game_id:
        return {}
    
    return redirect(f"/player-game?id={game_id}")
    

@app.route("/play-game")
def play_game():

    # get game
    game = Game.get(request.args.get("id"))
    if not game:
        return abort(404)

    return base(
        h1(f"Game {game.id}"),
        create_game_board()
    )

# @app.route("/make-move", methods=["POST"])
# def make_move():


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")