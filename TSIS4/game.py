import json
import random
from pathlib import Path

import pygame

try:
    from db import save_result, get_top_scores, get_personal_best, setup_database
except Exception:
    save_result = None
    get_top_scores = None
    get_personal_best = None
    setup_database = None


WIDTH, HEIGHT = 800, 700
TOP_BAR = 80
GRID_SIZE = 20
PLAY_WIDTH = WIDTH
PLAY_HEIGHT = HEIGHT - TOP_BAR
FPS = 60

WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
GRAY = (180, 180, 180)
LIGHT_GRAY = (230, 230, 230)
RED = (220, 50, 50)
DARK_RED = (120, 0, 0)
BLUE = (60, 110, 255)
YELLOW = (245, 200, 40)
PURPLE = (170, 80, 255)
ORANGE = (255, 140, 0)
SHIELD_COLOR = (0, 180, 180)

SETTINGS_FILE = Path(__file__).resolve().parent / "settings.json"


def load_settings():
    if SETTINGS_FILE.exists():
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    return {
        "snake_color": [0, 200, 0],
        "grid_overlay": True,
        "sound": False,
    }


def save_settings(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4)


def random_free_cell(snake, obstacles, foods, powerup):
    blocked = set(snake) | set(obstacles)

    for food in foods:
        blocked.add(food["pos"])

    if powerup:
        blocked.add(powerup["pos"])

    cols = PLAY_WIDTH // GRID_SIZE
    rows = PLAY_HEIGHT // GRID_SIZE

    choices = []

    for x in range(cols):
        for y in range(rows):
            pos = (x, y)
            if pos not in blocked:
                choices.append(pos)

    return random.choice(choices) if choices else None


def generate_food(snake, obstacles, foods, powerup):
    pos = random_free_cell(snake, obstacles, foods, powerup)

    if pos is None:
        return None

    weight = random.choice([1, 2, 3])
    colors = {
        1: RED,
        2: ORANGE,
        3: YELLOW,
    }

    lifetime = random.randint(5000, 9000)

    return {
        "kind": "normal",
        "pos": pos,
        "weight": weight,
        "color": colors[weight],
        "spawn_time": pygame.time.get_ticks(),
        "lifetime": lifetime,
    }


def generate_poison(snake, obstacles, foods, powerup):
    pos = random_free_cell(snake, obstacles, foods, powerup)

    if pos is None:
        return None

    return {
        "kind": "poison",
        "pos": pos,
        "color": DARK_RED,
        "spawn_time": pygame.time.get_ticks(),
        "lifetime": 8000,
    }


def generate_powerup(snake, obstacles, foods):
    pos = random_free_cell(snake, obstacles, foods, None)

    if pos is None:
        return None

    kind = random.choice(["speed", "slow", "shield"])

    color_map = {
        "speed": BLUE,
        "slow": PURPLE,
        "shield": SHIELD_COLOR,
    }

    return {
        "kind": kind,
        "pos": pos,
        "color": color_map[kind],
        "spawn_time": pygame.time.get_ticks(),
        "lifetime": 8000,
    }


def generate_obstacles(level, snake):
    obstacles = set()

    if level < 3:
        return obstacles

    cols = PLAY_WIDTH // GRID_SIZE
    rows = PLAY_HEIGHT // GRID_SIZE

    head_x, head_y = snake[0]

    safe_zone = {
        (head_x + dx, head_y + dy)
        for dx in range(-2, 3)
        for dy in range(-2, 3)
    }

    needed = min(5 + (level - 3) * 2, 18)
    attempts = 0

    while len(obstacles) < needed and attempts < 500:
        attempts += 1
        pos = (
            random.randint(1, cols - 2),
            random.randint(1, rows - 2),
        )

        if pos in snake or pos in safe_zone:
            continue

        obstacles.add(pos)

    return obstacles


def draw_grid(screen):
    for x in range(0, PLAY_WIDTH, GRID_SIZE):
        pygame.draw.line(screen, LIGHT_GRAY, (x, TOP_BAR), (x, HEIGHT))

    for y in range(TOP_BAR, HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, LIGHT_GRAY, (0, y), (WIDTH, y))


def draw_text(screen, text, font, color, x, y, center=False):
    img = font.render(text, True, color)
    rect = img.get_rect()

    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)

    screen.blit(img, rect)
    return rect


def button(screen, rect, text, font, mouse_pos):
    color = (200, 220, 255) if rect.collidepoint(mouse_pos) else (240, 240, 240)

    pygame.draw.rect(screen, color, rect, border_radius=10)
    pygame.draw.rect(screen, BLACK, rect, 2, border_radius=10)

    draw_text(screen, text, font, BLACK, rect.centerx, rect.centery, center=True)

    return rect


def run_game(screen, clock, username, settings):
    snake = [(10, 10), (9, 10), (8, 10)]
    direction = (1, 0)
    next_direction = direction

    score = 0
    level = 1
    food_eaten_for_level = 0

    foods = []
    powerup = None

    active_effect = None
    effect_end_time = 0
    shield_available = False

    obstacles = set()

    if setup_database:
        try:
            personal_best = get_personal_best(username)
        except Exception:
            personal_best = 0
    else:
        personal_best = 0

    base_speed = 8
    move_delay = 1000 // base_speed
    last_move_time = pygame.time.get_ticks()

    foods.append(generate_food(snake, obstacles, foods, powerup))
    foods.append(generate_poison(snake, obstacles, foods, powerup))

    ui_font = pygame.font.SysFont("arial", 22)

    running = True

    while running:
        now = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit", None

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and direction != (0, 1):
                    next_direction = (0, -1)
                elif event.key == pygame.K_DOWN and direction != (0, -1):
                    next_direction = (0, 1)
                elif event.key == pygame.K_LEFT and direction != (1, 0):
                    next_direction = (-1, 0)
                elif event.key == pygame.K_RIGHT and direction != (-1, 0):
                    next_direction = (1, 0)

        foods = [
            f for f in foods
            if now - f["spawn_time"] <= f["lifetime"]
        ]

        while len([f for f in foods if f["kind"] == "normal"]) < 1:
            new_food = generate_food(snake, obstacles, foods, powerup)
            if new_food:
                foods.append(new_food)

        while len([f for f in foods if f["kind"] == "poison"]) < 1:
            new_poison = generate_poison(snake, obstacles, foods, powerup)
            if new_poison:
                foods.append(new_poison)

        if powerup is None and random.random() < 0.003:
            powerup = generate_powerup(snake, obstacles, foods)

        if powerup and now - powerup["spawn_time"] > powerup["lifetime"]:
            powerup = None

        current_speed = base_speed + (level - 1) * 2

        if active_effect and now > effect_end_time:
            active_effect = None

        if active_effect == "speed":
            current_speed += 4
        elif active_effect == "slow":
            current_speed = max(4, current_speed - 3)

        move_delay = max(60, 1000 // current_speed)

        if now - last_move_time >= move_delay:
            last_move_time = now
            direction = next_direction

            head_x, head_y = snake[0]
            new_head = (
                head_x + direction[0],
                head_y + direction[1],
            )

            hit_wall = (
                new_head[0] < 0
                or new_head[0] >= PLAY_WIDTH // GRID_SIZE
                or new_head[1] < 0
                or new_head[1] >= PLAY_HEIGHT // GRID_SIZE
            )

            hit_self = new_head in snake
            hit_obstacle = new_head in obstacles

            if hit_wall or hit_self or hit_obstacle:
                if shield_available:
                    shield_available = False
                else:
                    running = False
            else:
                snake.insert(0, new_head)
                ate_something = False

                for food in foods[:]:
                    if food["pos"] == new_head:
                        ate_something = True
                        foods.remove(food)

                        if food["kind"] == "normal":
                            score += food["weight"]
                            food_eaten_for_level += 1

                            growth = food["weight"]

                            for _ in range(growth - 1):
                                snake.append(snake[-1])

                            if food_eaten_for_level >= 4:
                                food_eaten_for_level = 0
                                level += 1
                                obstacles = generate_obstacles(level, snake)

                        elif food["kind"] == "poison":
                            score = max(0, score - 1)

                            for _ in range(2):
                                if len(snake) > 1:
                                    snake.pop()

                            if len(snake) <= 1:
                                running = False

                if powerup and powerup["pos"] == new_head:
                    if powerup["kind"] == "shield":
                        shield_available = True
                    else:
                        active_effect = powerup["kind"]
                        effect_end_time = now + 5000

                    powerup = None
                    ate_something = True

                if not ate_something and running:
                    snake.pop()

        screen.fill(WHITE)

        pygame.draw.rect(screen, (245, 245, 245), (0, 0, WIDTH, TOP_BAR))
        pygame.draw.line(screen, GRAY, (0, TOP_BAR), (WIDTH, TOP_BAR), 2)

        draw_text(screen, f"Player: {username}", ui_font, BLACK, 15, 10)
        draw_text(screen, f"Score: {score}", ui_font, BLACK, 15, 40)
        draw_text(screen, f"Level: {level}", ui_font, BLACK, 160, 40)
        draw_text(screen, f"Best: {personal_best}", ui_font, BLACK, 270, 40)
        draw_text(screen, f"Shield: {'Yes' if shield_available else 'No'}", ui_font, BLACK, 390, 40)

        effect_text = active_effect if active_effect else "none"
        draw_text(screen, f"Effect: {effect_text}", ui_font, BLACK, 560, 40)

        if settings.get("grid_overlay", True):
            draw_grid(screen)

        for ox, oy in obstacles:
            rect = pygame.Rect(
                ox * GRID_SIZE,
                TOP_BAR + oy * GRID_SIZE,
                GRID_SIZE,
                GRID_SIZE,
            )
            pygame.draw.rect(screen, BLACK, rect)

        for food in foods:
            fx, fy = food["pos"]
            rect = pygame.Rect(
                fx * GRID_SIZE,
                TOP_BAR + fy * GRID_SIZE,
                GRID_SIZE,
                GRID_SIZE,
            )
            pygame.draw.rect(screen, food["color"], rect)

        if powerup:
            px, py = powerup["pos"]
            rect = pygame.Rect(
                px * GRID_SIZE,
                TOP_BAR + py * GRID_SIZE,
                GRID_SIZE,
                GRID_SIZE,
            )
            pygame.draw.rect(screen, powerup["color"], rect)
            draw_text(screen, powerup["kind"][0].upper(), ui_font, WHITE, rect.x + 5, rect.y + 1)

        snake_color = tuple(settings.get("snake_color", [0, 200, 0]))

        for i, (sx, sy) in enumerate(snake):
            rect = pygame.Rect(
                sx * GRID_SIZE,
                TOP_BAR + sy * GRID_SIZE,
                GRID_SIZE,
                GRID_SIZE,
            )

            color = snake_color if i else (0, 120, 0)
            pygame.draw.rect(screen, color, rect)

        pygame.display.flip()
        clock.tick(FPS)

    if save_result:
        try:
            save_result(username, score, level)
            personal_best = max(personal_best, score)
        except Exception:
            personal_best = max(personal_best, score)
    else:
        personal_best = max(personal_best, score)

    return "game_over", {
        "score": score,
        "level": level,
        "best": personal_best,
    }


def screen_main_menu(screen, clock, settings):
    font = pygame.font.SysFont("arial", 28)
    big_font = pygame.font.SysFont("arial", 42, bold=True)
    username = ""

    while True:
        mouse_pos = pygame.mouse.get_pos()
        screen.fill(WHITE)

        draw_text(screen, "TSIS 3 Snake Game", big_font, BLACK, WIDTH // 2, 90, center=True)
        draw_text(screen, "Enter username:", font, BLACK, WIDTH // 2, 170, center=True)

        input_rect = pygame.Rect(WIDTH // 2 - 160, 200, 320, 45)

        pygame.draw.rect(screen, (250, 250, 250), input_rect, border_radius=8)
        pygame.draw.rect(screen, BLACK, input_rect, 2, border_radius=8)

        draw_text(
            screen,
            username or "Type here...",
            font,
            BLACK if username else GRAY,
            input_rect.x + 10,
            input_rect.y + 8,
        )

        play_rect = pygame.Rect(WIDTH // 2 - 120, 290, 240, 50)
        leaderboard_rect = pygame.Rect(WIDTH // 2 - 120, 355, 240, 50)
        settings_rect = pygame.Rect(WIDTH // 2 - 120, 420, 240, 50)
        quit_rect = pygame.Rect(WIDTH // 2 - 120, 485, 240, 50)

        button(screen, play_rect, "Play", font, mouse_pos)
        button(screen, leaderboard_rect, "Leaderboard", font, mouse_pos)
        button(screen, settings_rect, "Settings", font, mouse_pos)
        button(screen, quit_rect, "Quit", font, mouse_pos)

        pygame.display.flip()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit", username

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                elif event.key == pygame.K_RETURN:
                    if username.strip():
                        return "play", username.strip()
                else:
                    if event.unicode.isprintable() and len(username) < 18:
                        username += event.unicode

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if play_rect.collidepoint(event.pos):
                    if username.strip():
                        return "play", username.strip()
                elif leaderboard_rect.collidepoint(event.pos):
                    return "leaderboard", username.strip()
                elif settings_rect.collidepoint(event.pos):
                    return "settings", username.strip()
                elif quit_rect.collidepoint(event.pos):
                    return "quit", username.strip()


def screen_game_over(screen, clock, data):
    font = pygame.font.SysFont("arial", 28)
    big_font = pygame.font.SysFont("arial", 42, bold=True)

    while True:
        mouse_pos = pygame.mouse.get_pos()
        screen.fill(WHITE)

        draw_text(screen, "Game Over", big_font, RED, WIDTH // 2, 120, center=True)
        draw_text(screen, f"Final Score: {data['score']}", font, BLACK, WIDTH // 2, 220, center=True)
        draw_text(screen, f"Level Reached: {data['level']}", font, BLACK, WIDTH // 2, 265, center=True)
        draw_text(screen, f"Personal Best: {data['best']}", font, BLACK, WIDTH // 2, 310, center=True)

        retry_rect = pygame.Rect(WIDTH // 2 - 120, 400, 240, 50)
        menu_rect = pygame.Rect(WIDTH // 2 - 120, 465, 240, 50)

        button(screen, retry_rect, "Retry", font, mouse_pos)
        button(screen, menu_rect, "Main Menu", font, mouse_pos)

        pygame.display.flip()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if retry_rect.collidepoint(event.pos):
                    return "retry"
                elif menu_rect.collidepoint(event.pos):
                    return "menu"


def screen_leaderboard(screen, clock):
    font = pygame.font.SysFont("arial", 22)
    big_font = pygame.font.SysFont("arial", 38, bold=True)

    try:
        rows = get_top_scores(10) if get_top_scores else []
    except Exception:
        rows = []

    while True:
        mouse_pos = pygame.mouse.get_pos()
        screen.fill(WHITE)

        draw_text(screen, "Leaderboard - Top 10", big_font, BLACK, WIDTH // 2, 60, center=True)

        headers = ["Rank", "Username", "Score", "Level", "Date"]
        xs = [70, 160, 390, 500, 620]

        for x, h in zip(xs, headers):
            draw_text(screen, h, font, BLACK, x, 130)

        pygame.draw.line(screen, BLACK, (50, 160), (750, 160), 2)

        y = 180

        for i, row in enumerate(rows, start=1):
            username, score, level, played_at = row

            if hasattr(played_at, "strftime"):
                date_str = played_at.strftime("%Y-%m-%d")
            else:
                date_str = str(played_at)[:10]

            values = [str(i), username, str(score), str(level), date_str]

            for x, value in zip(xs, values):
                draw_text(screen, value, font, BLACK, x, y)

            y += 38

        if not rows:
            draw_text(screen, "No database results yet.", font, GRAY, WIDTH // 2, 240, center=True)

        back_rect = pygame.Rect(WIDTH // 2 - 100, 610, 200, 48)
        button(screen, back_rect, "Back", font, mouse_pos)

        pygame.display.flip()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_rect.collidepoint(event.pos):
                    return "back"


def screen_settings(screen, clock, settings):
    font = pygame.font.SysFont("arial", 26)
    big_font = pygame.font.SysFont("arial", 38, bold=True)

    colors = [
        [0, 200, 0],
        [0, 120, 255],
        [255, 140, 0],
        [180, 50, 180],
        [30, 30, 30],
    ]

    color_rects = [
        pygame.Rect(230 + i * 90, 320, 50, 50)
        for i in range(len(colors))
    ]

    while True:
        mouse_pos = pygame.mouse.get_pos()
        screen.fill(WHITE)

        draw_text(screen, "Settings", big_font, BLACK, WIDTH // 2, 70, center=True)

        grid_rect = pygame.Rect(230, 160, 330, 48)
        sound_rect = pygame.Rect(230, 230, 330, 48)
        save_rect = pygame.Rect(WIDTH // 2 - 120, 520, 240, 50)

        button(screen, grid_rect, f"Grid: {'On' if settings['grid_overlay'] else 'Off'}", font, mouse_pos)
        button(screen, sound_rect, f"Sound: {'On' if settings['sound'] else 'Off'}", font, mouse_pos)

        draw_text(screen, "Snake Color:", font, BLACK, 230, 285)

        for rect, color in zip(color_rects, colors):
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, BLACK, rect, 2)

            if list(color) == settings["snake_color"]:
                pygame.draw.rect(screen, YELLOW, rect, 3)

        button(screen, save_rect, "Save & Back", font, mouse_pos)

        pygame.display.flip()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit", settings

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if grid_rect.collidepoint(event.pos):
                    settings["grid_overlay"] = not settings["grid_overlay"]

                elif sound_rect.collidepoint(event.pos):
                    settings["sound"] = not settings["sound"]

                elif save_rect.collidepoint(event.pos):
                    save_settings(settings)
                    return "back", settings

                else:
                    for rect, color in zip(color_rects, colors):
                        if rect.collidepoint(event.pos):
                            settings["snake_color"] = color


































                        