from domain.domain import GameSession
from presentation import View

import json
import os.path


def save_game(game, view):
    game_session_json = json.dumps(game, default=lambda o: o.to_dict())
    view_json = json.dumps(view.to_dict())

    with open("save.json", "w") as save_file:
        save_file.write(game_session_json)
        save_file.write("\n")
        save_file.write(view_json)


def load_game(screen):
    game_session_result = GameSession()

    path = "save.json"
    if os.path.isfile(path):
        with open(path, "r") as save_file:
            game_session_line = save_file.readline()
            view_line = save_file.readline()

            game_session_json = json.loads(game_session_line)
            view_json = json.loads(view_line)

            game_session_result.load_data(**game_session_json)

            view_result = View(screen, game_session_result)
            view_result.update_level()
            view_result.load_data(**view_json)
    else:
        view_result = View(screen, game_session_result)
    return game_session_result, view_result


def save_game_stats(view, game_session):
    view.all_game_stats.append(game_session.game_stats)
    view.all_game_stats.sort(key=lambda gs: gs["sum_treasures"], reverse=True)

    if len(view.all_game_stats) >= 8:
        view.all_game_stats.pop(-1)

    for room in view.sequence:
        room[1] = False

    for corridor in view.corridors:
        corridor[1] = False

    new_game_session = GameSession()
    save_game(new_game_session, view)
