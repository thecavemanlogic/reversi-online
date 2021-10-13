
const urlQuery = new URLSearchParams(location.search);
const game_id = urlQuery.get("id");

function join_game() {
    fetch("/join-game", {
        method: "POST"
    }).then(resp => {
        if (resp.status == 200) {
            location = resp.url;
        }
        else {
            alert("Error!");
        }
    });
}

function click_square(idx) {
    fetch("/make-move", {
        method: "POST",
        body: JSON.stringify({
            game_id: game_id,
            index: idx
        })
    }).then(resp => {
        console.log('all good!')
    }, resp => {
        alert("invalid move!");
    })
}