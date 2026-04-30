import pygame

from game import (
    load_settings,
    screen_game_over,
    screen_leaderboard,
    screen_main_menu,
    screen_settings,
    run_game,
)

try:
    from db import setup_database
except Exception:
    setup_database = None


def main():
    pygame.init()

    if setup_database:
        try:
            setup_database()
        except Exception as e:
            print("Database setup warning:", e)

    screen = pygame.display.set_mode((800, 700))
    pygame.display.set_caption("TSIS 3 Snake")
    clock = pygame.time.Clock()

    settings = load_settings()
    username = ""

    while True:
        action, maybe_username = screen_main_menu(screen, clock, settings)

        if maybe_username:
            username = maybe_username

        if action == "quit":
            break

        elif action == "leaderboard":
            result = screen_leaderboard(screen, clock)
            if result == "quit":
                break

        elif action == "settings":
            result, settings = screen_settings(screen, clock, settings)
            if result == "quit":
                break

        elif action == "play":
            if not username:
                username = "player"

            game_action, data = run_game(screen, clock, username, settings)

            if game_action == "quit":
                break

            while game_action == "game_over":
                over_action = screen_game_over(screen, clock, data)

                if over_action == "quit":
                    pygame.quit()
                    return

                elif over_action == "retry":
                    game_action, data = run_game(screen, clock, username, settings)

                    if game_action == "quit":
                        pygame.quit()
                        return

                elif over_action == "menu":
                    break

    pygame.quit()


if __name__ == "__main__":
    main()