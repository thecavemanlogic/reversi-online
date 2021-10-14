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
        return user == self.turn
    
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
            self.turn = random.choice(self.players)
            self.mode = Game.ACTIVE
        
        return True

if len(Game.games) == 0:
    Game.load()