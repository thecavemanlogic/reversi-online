
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
    // fetch("/make-move", {
    //     method: "POST",
    //     headers: {
    //         "Content-Type": "application/json"
    //     },
    //     body: JSON.stringify({
    //         game: game_id,
    //         index: idx
    //     }),
    //     redirect: "follow"
    // }).then(resp => {
    //     console.log('all good!')
    //     location = location.href;
    // }, resp => {
    //     alert("invalid move!");
    // })
}

if (location.pathname === "/play-game") {
    // setTimeout(() => {
    //     location = location.href;
    // }, 1000);
}

let socket = null;

const queryParams = new URLSearchParams(window.location.search);
const GAME_ID = queryParams.get("id");

$(document).ready(function() {

    const NAME = document.getElementById("name-display").innerText;
    console.log("NAME:", NAME)

    socket = io();

    socket.emit("get-state", {
        game: GAME_ID
    });

    $(".square").click(function() {
        const idx = parseInt($(this).attr("class").match(/square-[0-9]+/)[0].split("-")[1]);
        socket.emit("make-move", {
            game: GAME_ID,
            idx: idx
        });
    })

    socket.on("connect", function() {
        socket.emit("join-game", {
            game: GAME_ID
        });
    });

    socket.on("player-error", function(msg) {
        console.log("Error: " + msg.msg);
    });

    socket.on("update-game", function(state) {
        const { game, board, next, winner } = state;
        
        // if the event goes along with the current game in focus
        if (game === GAME_ID) {

            for (let i = 0; i < board.length; ++i) {
                const c = board[i];
                $(`.square-${i}`).html(`<div class="circle ${c == "W" ? "white" : c == "B" ? "black" : ""}"></div>`);
            }
            
            document.getElementById("turn").innerText = (next == NAME);

            if (winner) alert("Game Ended!\nWinner:" + winner);
        }        
    })
});

// const ws = new WebSocket(`ws://${location.hostname}`);
// ws.onerror = err => {
//     console.log(err)
// }