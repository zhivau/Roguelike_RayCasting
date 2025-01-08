from domain.base.consts import *
from domain.base.base_objects import TypeCommand, GameStatus
from datalayer import *

import curses
import time


def init_curses():
    screen = curses.initscr()
    curses.noecho()
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(6, curses.COLOR_RED, curses.COLOR_BLUE)
    curses.init_pair(7, curses.COLOR_GREEN, curses.COLOR_BLUE)
    curses.init_pair(8, curses.COLOR_YELLOW, curses.COLOR_BLUE)
    screen.keypad(True)

    return screen


def print_if_game_lost(screen):
    for i in range(MAP_HEIGHT):
        screen.addstr(i, 0, "DEATH^___^" * (MAP_WIDTH // 10))

    screen.refresh()
    time.sleep(3)


def print_if_game_won(screen):
    for i in range(MAP_HEIGHT):
        screen.addstr(i, 0, "NOTDEATH:(" * (MAP_WIDTH // 10))
    screen.refresh()
    time.sleep(3)


def main():
    screen = init_curses()
    game_session, view = load_game(screen)

    while True:
        view.update_area()
        view.update_map()
        view.print_map()
        command, index_item = view.get_signal()
        result = game_session.process_command(command, index_item)
        view.clear_user_interface()

        if (
            command == TypeCommand.EXITGAME
            or result == GameStatus.WON
            or result == GameStatus.LOST
        ):
            break
        elif command == TypeCommand.SAVEGAME:
            save_game(game_session, view)
            break
        elif result == GameStatus.NEXTLEVEL or command == TypeCommand.NEWGAME:
            view.update_level()
            view.clear_map()

    if result == GameStatus.LOST:
        print_if_game_won(screen)
        save_game_stats(view, game_session)
    elif result == GameStatus.WON:
        print_if_game_won(screen)
        save_game_stats(view, game_session)

    curses.endwin()


if __name__ == "__main__":
    main()
