
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
        resp.redirected
    }, resp => {
        alert("invalid move!");
    })
}