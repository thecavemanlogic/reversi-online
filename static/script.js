
const urlQuery = new URLSearchParams(location.search);
const game_id = urlQuery.get("id");

function callApiPost(path, body = null) {
    return fetch(path, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: body === null ? null : JSON.stringify(body)
    })
}

function join_game() {
    document.getElementById("join-game-btn").disabled = true;
    fetch("/join-game", {
        method: "POST"
    }).then(resp => {
        console.log(resp)
        if (resp.redirected) {
            location = resp.url;
        }
        else {
            checkQueueStatus();
        }
    });
}

function checkQueueStatus() {
    fetch("/check-queue")
        .then(resp => {
            if (resp.redirected) {
                location = resp.url;
            }
            else {
                setTimeout(checkQueueStatus, 1000);
            } 
        });
}

function click_square(idx) {
    fetch("/make-move", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            game: game_id,
            index: idx
        }),
        redirect: "follow"
    }).then(resp => {
        console.log('all good!')
        location = location.href;
    }, resp => {
        alert("invalid move!");
    })
}

if (location.pathname === "/play-game") {
    // setTimeout(() => {
    //     location = location.href;
    // }, 1000);
}

let socket = null;

$(document).ready(function() {

    console.log("Document initialized");

    socket = io();

    socket.on("connect", function() {
        console.log("Connected to WS server");
        socket.send("some data");
    });

    socket.on("message", function(msg) {
        console.log("received:", msg);
    });
});

// const ws = new WebSocket(`ws://${location.hostname}`);
// ws.onerror = err => {
//     console.log(err)
// }