from flask import Flask, request, Response, redirect
from htmllib import html, head, body, div, h1, div
from util import gen_id

app = Flask(__name__)

@app.route("/")
def index():
    return html.html(
        head(),
        body(
            h1("Hello there!"),
            div(
                html.p("how are you doing?")
            )
        )
    ).to_html()

game_queue = set()

@app.route("/join-game", methods=["POST"])
def join_game():

    resp = Response()

    # if not a registered user
    if request.cookies.get("user_id") is None:
        resp.set_cookie("user_id", gen_id())

    game_id = request.args.get("id")
    if game_id is None:
        pass
    request.cookies.get()
    Response().set_cookie()
    return redirect("/play-game?id=")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")