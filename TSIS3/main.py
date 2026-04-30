import pygame
import sys

from ui import Button, draw_text, username_screen
from racer import RacerGame, WIDTH, HEIGHT
from persistence import load_settings, save_settings, load_leaderboard, add_score

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TSIS 3 Racer Game")

clock = pygame.time.Clock()

font = pygame.font.SysFont("arial", 26)
big_font = pygame.font.SysFont("arial", 48)

WHITE = (245, 245, 245)
BLACK = (20, 20, 20)
DARK_GRAY = (80, 80, 80)


def main_menu():
    play_button = Button("Play", 300, 180, 200, 50)
    leaderboard_button = Button("Leaderboard", 300, 250, 200, 50)
    settings_button = Button("Settings", 300, 320, 200, 50)
    quit_button = Button("Quit", 300, 390, 200, 50)

    while True:
        screen.fill(WHITE)

        draw_text(screen, "TSIS 3 RACER", big_font, BLACK, WIDTH // 2, 90, True)

        play_button.draw(screen, font)
        leaderboard_button.draw(screen, font)
        settings_button.draw(screen, font)
        quit_button.draw(screen, font)

        pygame.display.flip()
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if play_button.clicked(event):
                play_game()

            elif leaderboard_button.clicked(event):
                leaderboard_screen()

            elif settings_button.clicked(event):
                settings_screen()

            elif quit_button.clicked(event):
                pygame.quit()
                sys.exit()


def play_game():
    settings = load_settings()
    username = username_screen(screen, clock)

    game = RacerGame(screen, clock, username, settings)
    result = game.run()

    add_score(username, result["score"], result["distance"])
    game_over_screen(result)


def leaderboard_screen():
    back_button = Button("Back", 300, 500, 200, 50)

    while True:
        screen.fill(WHITE)

        draw_text(screen, "LEADERBOARD", big_font, BLACK, WIDTH // 2, 60, True)

        leaderboard = load_leaderboard()

        if not leaderboard:
            draw_text(screen, "No scores yet", font, DARK_GRAY, WIDTH // 2, 250, True)
        else:
            y = 130
            for index, entry in enumerate(leaderboard, start=1):
                text = f"{index}. {entry['name']} | Score: {entry['score']} | Distance: {entry['distance']}"
                draw_text(screen, text, font, BLACK, 100, y)
                y += 35

        back_button.draw(screen, font)

        pygame.display.flip()
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if back_button.clicked(event):
                return


def settings_screen():
    settings = load_settings()

    sound_button = Button("", 300, 170, 220, 50)
    color_button = Button("", 300, 240, 220, 50)
    difficulty_button = Button("", 300, 310, 220, 50)
    back_button = Button("Back", 300, 420, 220, 50)

    colors = ["blue", "red", "green", "purple"]
    difficulties = ["easy", "normal", "hard"]

    while True:
        screen.fill(WHITE)

        sound_button.text = "Sound: ON" if settings["sound"] else "Sound: OFF"
        color_button.text = f"Car: {settings['car_color']}"
        difficulty_button.text = f"Difficulty: {settings['difficulty']}"

        draw_text(screen, "SETTINGS", big_font, BLACK, WIDTH // 2, 80, True)

        sound_button.draw(screen, font)
        color_button.draw(screen, font)
        difficulty_button.draw(screen, font)
        back_button.draw(screen, font)

        pygame.display.flip()
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_settings(settings)
                pygame.quit()
                sys.exit()

            if sound_button.clicked(event):
                settings["sound"] = not settings["sound"]
                save_settings(settings)

            elif color_button.clicked(event):
                current = colors.index(settings["car_color"])
                settings["car_color"] = colors[(current + 1) % len(colors)]
                save_settings(settings)

            elif difficulty_button.clicked(event):
                current = difficulties.index(settings["difficulty"])
                settings["difficulty"] = difficulties[(current + 1) % len(difficulties)]
                save_settings(settings)

            elif back_button.clicked(event):
                save_settings(settings)
                return


def game_over_screen(result):
    retry_button = Button("Retry", 220, 420, 160, 50)
    menu_button = Button("Main Menu", 420, 420, 160, 50)

    while True:
        screen.fill(WHITE)

        draw_text(screen, "GAME OVER", big_font, BLACK, WIDTH // 2, 120, True)
        draw_text(screen, f"Score: {result['score']}", font, BLACK, WIDTH // 2, 210, True)
        draw_text(screen, f"Distance: {result['distance']}", font, BLACK, WIDTH // 2, 250, True)
        draw_text(screen, f"Coins: {result['coins']}", font, BLACK, WIDTH // 2, 290, True)

        retry_button.draw(screen, font)
        menu_button.draw(screen, font)

        pygame.display.flip()
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if retry_button.clicked(event):
                play_game()
                return

            elif menu_button.clicked(event):
                return


if __name__ == "__main__":
    main_menu()