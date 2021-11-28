import json
import threading

from flask import Flask, request, Response, redirect, send_from_directory, abort
from db.game import Game
from db.player import Player
from htmllib import html, head, body, div, h1
# from db.util import gen_id
# from random import random
from flask_socketio import SocketIO, emit, join_room, leave_room, rooms, send
from threading import Timer

app = Flask(__name__)
socketio = SocketIO(app)

def base(*contents):
    return html.html(
        head(
            html.script(
                src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.5.1/jquery.min.js",
                integrity="sha512-bLT0Qm9VnAYZDflyKcBaQ2gg0hSYNQrJ8RilYldYQ1FxQYoCLtUjuuRuZo+fjqhx/qtq/1itJ0C2ejDxltZVFg==",
                crossorigin="anonymous"
            ),
            html.script(
                src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/3.0.4/socket.io.js",
                integrity="sha512-aMGMvNYu8Ue4G+fHa359jcPb1u+ytAF+P2SCb+PxrjCdO3n3ZTxJ30zuH39rimUggmTwmh2u7wvQsDTHESnmfQ==",
                crossorigin="anonymous"
            ),
            html.title("Reversi Online"),
            html.script(src="/static/script.js"),
            html.link(rel="stylesheet", href="/static/style.css"),

            # Google Fonts
            html.link(rel="stylesheet", href="https://fonts.googleapis.com/css?family=Roboto")
        ),
        body(
            *contents
        )
    ).to_html()

def game_base(*contents):
    user = Player.get(request.cookies.get("user_id"))
    return base(
        div(
            id="banner",
            contents=[
                html.span(
                    "Reversi Online",
                    cls="logo"
                ),
                html.button(
                    "Logout",
                    cls="logout-btn"
                ),
                html.span(
                    user.name,
                    id="name-display"
                )
            ]
        ),
        div(
            *contents,
            id="body-content",
        )
    )

def create_game_square(idx, value):
    x = idx % 8
    y = idx // 8
    color = "light" if (x % 2 == 0) != (y % 2 == 0) else "dark"

    def get_piece(value):
        return html.div()
        # if value == "B":
        #     return html.div(cls="circle black")
        # elif value == "W":
        #     return html.div(cls="circle white")

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
    logged_in = Player.get(request.cookies.get("user_id")) is not None

    if logged_in:
        big_button = html.button(
            "Go to Dashboard",
            onclick="location='/dashboard';"
        )
    else:
        big_button = html.button(
            "Join Game",
            onclick="join_game();",
            id="join-game-btn"
        )

    return base(
        h1("Hello there!"),
        div(
            html.p("how are you doing?"),
            big_button
        )
    )

@app.route("/dashboard")
def dashboard():
    return game_base(
        html.h2("Active Games")
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
    
    user = Player.get(request.cookies.get("user_id"))
    if not user:
        return abort(401)

    return game_base(
        h1(f"Game {game.id}"),
        html.p(f"Your color: {game.get_color(user.id)}"),
        html.p(f"Your turn? <span id=\"turn\">{game.is_next(user.id)}</span>"),
        create_game_board(game.state)
    )

# websocket stuff

@socketio.on("join-game")
def join_game_(msg = {}):
    game = Game.get(msg.get("game"))
    if not game:
        emit("player-error", { "msg": "invalid game" })
        return
    join_room(game.id)

@socketio.on("make-move")
def make_move_(msg = {}):
    game = Game.get(msg.get("game"))
    idx = msg.get("idx")
    user = Player.get(request.cookies.get("user_id"))

    if game.is_done():
        emit("report-error", { "msg": "game is finished" })
        return

    if not game or not idx or not user:
        emit("player-error", { "msg": "invalid move" })
        return

    err, updates = game.make_move(user.id, idx)
    if err != Game.ALL_GOOD:
        emit("player-error", { "msg": Game.get_code(err) })
        return

    emit("update-game", game.get_state(), to=game.id)

    game.save()

    # if game.is_done():
    #     emit("end-game", {
    #         "game": game.id,
    #         "winner": game.get_winner()
    #     }, to=game.id)

@socketio.on("get-state")
def get_state(msg={}):
    game = Game.get(msg.get("game"))
    emit("update-game", game.get_state())


if __name__ == "__main__":
    # from gevent import pywsgi
    # from geventwebsocket.handler import WebSocketHandler
    # server = pywsgi.WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
    # server.serve_forever()
    # app.run(debug=True, host="0.0.0.0")
    socketio.run(app, debug=True, host="0.0.0.0")