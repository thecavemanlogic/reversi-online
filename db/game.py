import re
import db
import os
import json
import random
from db.player import Player

from db.util import gen_id
from db.database import get_game, create_game, update_game, get_game_participants

os.makedirs(".db", exist_ok=True)

initial_state = """
........
........
........
...XO...
...OX...
........
........
........
""".replace('\n', '')

class Game:

    games = dict()

    # various game modes
    OPEN = 0
    ACTIVE = 1
    FINISHED = 2

    BAD_MOVE = 3
    NOT_YOUR_TURN = 4
    NOT_IN_GAME = 5
    ALL_GOOD = 6

    @staticmethod
    def get_code(code: int) -> str:
        strings = ["OPEN", "ACTIVE", "FINISHED", "BAD_MOVE", "NOT_YOUR_TURN", "Not in game", "All good"]
        return strings[code]

    @staticmethod
    def get(id):
        return Game.games.get(id)
    
    @staticmethod
    def store():
        with open(".db/games.json", "w") as f:
            json.dump(list(map(
                lambda x: Game.games[x].to_json(),
                Game.games
            )), f)
    
    @staticmethod
    def load():
        if os.path.isfile(".db/games.json"):
            with open(".db/games.json") as f:
                for game in json.load(f):
                    game = Game(data=game)
                    Game.games[game.id] = game
    
    @staticmethod
    def state_to_string(state: list) -> str:
        return "".join(map(
            lambda x: "".join(x),
            state
        ))

    @staticmethod
    def state_to_list(state: str) -> list:
        rows = re.findall(".{8}", state)
        rows = list(map(
            lambda x: re.findall(".", x),
            rows
        ))
        return rows

    def __init__(self, data=None):

        if data:
            self.id = data["id"]
            self.state = Game.state_to_list(data["state"])
            self.mode = data["mode"]
            self.turn = data["turn"]
            self.players = data["players"]
        else:
            self.id = gen_id(resource=Game.games)
            self.state = Game.state_to_list(initial_state)
            self.mode = Game.OPEN
            self.turn = None
            self.players = []
    
    def save(self):
        Game.games[self.id] = self
        Game.store()
    
    def to_json(self):
        return {
            "id": self.id,
            "state": Game.state_to_string(self.state),
            "mode": self.mode,
            "turn": self.turn,
            "players": self.players
        }
    
    def is_next(self, user):
        return user == self.players[self.turn]
    
    def join(self, name):
        if self.mode != Game.OPEN:
            return False
        
        player = Player.get(name)
        if player:
            player.game_queue.append(self.id)
        else:
            return False
        
        self.players.append(name)

        if len(self.players) == 2:
            self.turn = random.choice([0, 1])
            self.mode = Game.ACTIVE
        
        return True
    
    def make_ray(self, x: int, y: int, dx: int, dy: int, max_steps=2, goal_chr="") -> bool:

        if dx == 0 and dy == 0:
            return False

        steps = 0

        print("dx and dy:", dx, dy)

        while (x >= 0 and x < 8) and (y >= 0 and y < 8) and steps < max_steps:

            print(f"x: {x} y: {y}")

            if self.state[y][x] == goal_chr:
                return True

            x += dx
            y += dy
            steps += 1
        
        return False
    
    def make_rays(self, x: int, y: int, max_steps=2, goal_chr="") -> bool:
        for i in range(9):
            dx = (i // 3) - 1
            dy = (i % 3) - 1
            if self.make_ray(x, y, dx, dy, max_steps=max_steps, goal_chr=goal_chr):
                return True
        return False
    
    def make_move(self, user: str, idx: int) -> int:
        
        # handle errors
        if user not in self.players:
            return Game.NOT_IN_GAME
        elif not self.is_next(user):
            return Game.NOT_YOUR_TURN
        elif idx < 0 or idx > 63:
            return Game.BAD_MOVE
        
        x = idx % 8
        y = idx // 8

        piece = "O" if self.players.index(user) == 0 else "X"
        o_piece = "O" if piece == "X" else "X"

        if self.state[y][x] != ".":
            return Game.BAD_MOVE
        elif not self.make_rays(x, y, goal_chr=o_piece):
            return Game.BAD_MOVE
        
        
        
        self.turn = (self.turn + 1) % 2

        return Game.ALL_GOOD
        


if len(Game.games) == 0:
    Game.load()