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
...BW...
...WB...
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
            self.end_state = data["end_state"]
        else:
            self.id = gen_id(resource=Game.games)
            self.state = Game.state_to_list(initial_state)
            self.mode = Game.OPEN
            self.turn = None
            self.players = []
            self.end_state = None
    
    def save(self):
        Game.games[self.id] = self
        Game.store()
    
    def to_json(self):
        return {
            "id": self.id,
            "state": Game.state_to_string(self.state),
            "mode": self.mode,
            "turn": self.turn,
            "players": self.players,
            "end_state": self.end_state
        }
    
    def is_next(self, user: str) -> bool:
        return user == self.players[self.turn]
    
    def get_next(self):
        return Player.get(self.players[self.turn]).name
    
    def get_color(self, user: str) -> str:
        return ["black", "white"][self.players.index(user)]
    
    def get_state(self):
        return {
            "game": self.id,
            "board": Game.state_to_string(self.state),
            "turn": Player.get(self.players[self.turn]).name,
            "winner": self.get_winner()
        }
    
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
            raise Exception("Don't do that!")

        steps = 0

        while (x >= 0 and x < 8) and (y >= 0 and y < 8) and steps < max_steps:

            if self.state[y][x] == goal_chr:
                return True

            x += dx
            y += dy
            steps += 1
        
        return False
    
    def make_rays(self, x: int, y: int, max_steps=2, goal_chr="") -> bool:
        arr = []
        for i in range(9):
            if i == 4:
                continue
            dx = (i // 3) - 1
            dy = (i % 3) - 1
            if self.make_ray(x, y, dx, dy, max_steps=max_steps, goal_chr=goal_chr):
                arr.append((dx, dy))
        return arr
    
    def perform_ray_move(self, x: int, y: int, dx: int, dy: int, color: str, side_effect=True):

        if dx == 0 and dy == 0:
            return []
        
        other_color = "W" if color == "B" else "B"

        original_x = x
        original_y = y
        
        x += dx
        y += dy

        while True:
            if x < 0 or x >= 8 or y < 0 or y >= 8:
                return []
            elif self.state[y][x] == ".":
                return []
            elif self.state[y][x] == color:
                break
            x += dx
            y += dy
        
        if abs(x - original_x) == 1 or abs(y - original_y) == 1:
            return []

        if not side_effect:
            return True

        changes = []
        while x != original_x or y != original_y:
            self.state[y][x] = color
            changes.append((x + y * 8, color))
            x -= dx
            y -= dy
        
        self.state[y][x] = color
        changes.append((x + y * 8, color))

        return changes
    
    def perform_move(self, x: int, y: int, color: str, side_effect=True):
        if self.state[y][x] != ".":
            return []
        if side_effect:
            return [item for dx in range(-1, 2) for dy in range(-1, 2) for item in self.perform_ray_move(x, y, dx, dy, color, side_effect)]
        else:
            return any([self.perform_ray_move(x, y, dx, dy, color, side_effect) for dx in range(-1, 2) for dy in range(-1, 2)])
        
    def get_user_color(self, user: str):
        return "B" if self.players.index(user) == 0 else "W"

    def has_move(self, user: str) -> bool:
        color = self.get_user_color(user)
        for y in range(8):
            for x in range(8):
                if self.perform_move(x, y, color, side_effect=False) == True:
                    return True
        return False


    def make_move(self, user: str, idx: int) -> int:
        
        # handle errors
        if user not in self.players:
            return Game.NOT_IN_GAME, None
        elif not self.is_next(user):
            return Game.NOT_YOUR_TURN, None
        elif idx < 0 or idx > 63:
            return Game.BAD_MOVE, None
        
        x = idx % 8
        y = idx // 8

        piece = "B" if self.players.index(user) == 0 else "W"
        o_piece = "W" if piece == "B" else "B"

        changes = self.perform_move(x, y, piece)
        if len(changes) == 0:
            return Game.BAD_MOVE, None

        self.turn = (self.turn + 1) % 2

        if not self.has_move(self.players[self.turn]):
            self.end()

        return Game.ALL_GOOD, changes
        
    def end(self):
        self.mode = Game.FINISHED

        b_score = 0
        w_score = 0

        for row in self.state:
            for square in row:
                if square == "B":
                    b_score += 1
                elif square == "W":
                    w_score += 1
        
        self.end_state = {
            "scores": {
                "white": w_score,
                "black": b_score
            } 
        }
    
    def is_done(self):
        return self.mode == Game.FINISHED
    
    def get_winner(self):
        if self.end_state:
            w = self.end_state["scores"]["white"]
            b = self.end_state["scores"]["black"]
            if w > b:
                return self.players[1]
            elif w < b:
                return self.players[0]
        return None


if len(Game.games) == 0:
    Game.load()