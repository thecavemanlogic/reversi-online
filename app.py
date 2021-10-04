from flask import Flask
from htmllib import html, head, body, div, h1, div

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