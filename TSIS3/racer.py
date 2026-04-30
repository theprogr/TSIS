import pygame
import random
import time

WIDTH = 800
HEIGHT = 600

ROAD_X = 180
ROAD_WIDTH = 440
LANE_WIDTH = ROAD_WIDTH // 4
LANES = [ROAD_X + 35, ROAD_X + 135, ROAD_X + 235, ROAD_X + 335]

FINISH_DISTANCE = 3000

WHITE = (245, 245, 245)
BLACK = (20, 20, 20)
GRAY = (90, 90, 90)
DARK_GRAY = (45, 45, 45)
YELLOW = (255, 220, 0)
RED = (220, 40, 40)
GREEN = (40, 180, 70)
BLUE = (50, 120, 255)
PURPLE = (160, 80, 255)
ORANGE = (255, 140, 0)
CYAN = (0, 220, 220)

CAR_COLORS = {
    "blue": BLUE,
    "red": RED,
    "green": GREEN,
    "purple": PURPLE
}


class Player:
    def __init__(self, color):
        self.w = 45
        self.h = 75
        self.x = LANES[1]
        self.y = HEIGHT - 100
        self.color = CAR_COLORS.get(color, BLUE)
        self.shield = False
        self.crashes = 0

    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def move(self, dx):
        self.x += dx

        if self.x < ROAD_X:
            self.x = ROAD_X

        if self.x + self.w > ROAD_X + ROAD_WIDTH:
            self.x = ROAD_X + ROAD_WIDTH - self.w

    def draw(self, screen):
        r = self.rect()

        pygame.draw.rect(screen, self.color, r, border_radius=12)
        pygame.draw.rect(screen, (180, 220, 255), (self.x + 8, self.y + 10, self.w - 16, 18), border_radius=5)
        pygame.draw.rect(screen, BLACK, (self.x + 10, self.y + 35, self.w - 20, 10), border_radius=4)

        pygame.draw.rect(screen, BLACK, (self.x - 6, self.y + 12, 8, 18), border_radius=3)
        pygame.draw.rect(screen, BLACK, (self.x + self.w - 2, self.y + 12, 8, 18), border_radius=3)
        pygame.draw.rect(screen, BLACK, (self.x - 6, self.y + 48, 8, 18), border_radius=3)
        pygame.draw.rect(screen, BLACK, (self.x + self.w - 2, self.y + 48, 8, 18), border_radius=3)

        pygame.draw.circle(screen, (255, 255, 120), (self.x + 10, self.y + 5), 4)
        pygame.draw.circle(screen, (255, 255, 120), (self.x + self.w - 10, self.y + 5), 4)

        pygame.draw.rect(screen, BLACK, r, 2, border_radius=12)

        if self.shield:
            pygame.draw.circle(screen, CYAN, r.center, 52, 3)


class RoadObject:
    def __init__(self, kind, speed):
        self.kind = kind
        self.w = 45
        self.h = 45
        self.x = random.choice(LANES)
        self.y = -80
        self.speed = speed
        self.spawn_time = time.time()

        if kind == "traffic":
            self.h = 75
        elif kind == "moving_barrier":
            self.w = 70
            self.h = 35
            self.direction = random.choice([-1, 1])

    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def update(self):
        self.y += self.speed

        if self.kind == "moving_barrier":
            self.x += self.direction * 2

            if self.x < ROAD_X or self.x + self.w > ROAD_X + ROAD_WIDTH:
                self.direction *= -1

    def expired(self):
        if self.kind in ["nitro", "shield", "repair"]:
            return time.time() - self.spawn_time > 6

        return False

    def draw(self, screen):
        r = self.rect()

        if self.kind.startswith("coin"):
            color = YELLOW if self.kind == "coin1" else ORANGE if self.kind == "coin2" else CYAN
            pygame.draw.circle(screen, color, r.center, 18)
            pygame.draw.circle(screen, BLACK, r.center, 18, 2)

        elif self.kind == "traffic":
            pygame.draw.rect(screen, RED, r, border_radius=12)
            pygame.draw.rect(screen, (180, 220, 255), (self.x + 8, self.y + 45, self.w - 16, 18), border_radius=5)
            pygame.draw.rect(screen, BLACK, (self.x + 10, self.y + 25, self.w - 20, 10), border_radius=4)

            pygame.draw.rect(screen, BLACK, (self.x - 6, self.y + 12, 8, 18), border_radius=3)
            pygame.draw.rect(screen, BLACK, (self.x + self.w - 2, self.y + 12, 8, 18), border_radius=3)
            pygame.draw.rect(screen, BLACK, (self.x - 6, self.y + 48, 8, 18), border_radius=3)
            pygame.draw.rect(screen, BLACK, (self.x + self.w - 2, self.y + 48, 8, 18), border_radius=3)

        elif self.kind == "oil":
            pygame.draw.ellipse(screen, BLACK, r)
            pygame.draw.ellipse(screen, DARK_GRAY, r.inflate(-10, -10))

        elif self.kind == "pothole":
            pygame.draw.ellipse(screen, DARK_GRAY, r)
            pygame.draw.ellipse(screen, BLACK, r, 3)

        elif self.kind == "barrier":
            pygame.draw.rect(screen, ORANGE, r, border_radius=5)
            pygame.draw.line(screen, WHITE, r.topleft, r.bottomright, 4)
            pygame.draw.line(screen, WHITE, r.topright, r.bottomleft, 4)
            pygame.draw.rect(screen, BLACK, r, 2, border_radius=5)

        elif self.kind == "moving_barrier":
            pygame.draw.rect(screen, PURPLE, r, border_radius=5)
            pygame.draw.line(screen, WHITE, r.topleft, r.bottomright, 4)
            pygame.draw.line(screen, WHITE, r.topright, r.bottomleft, 4)
            pygame.draw.rect(screen, BLACK, r, 2, border_radius=5)

        elif self.kind == "speed_bump":
            pygame.draw.rect(screen, YELLOW, r, border_radius=8)
            pygame.draw.rect(screen, BLACK, r, 2, border_radius=8)

        elif self.kind == "boost_strip":
            pygame.draw.rect(screen, CYAN, r, border_radius=8)
            pygame.draw.polygon(screen, WHITE, [(self.x + 12, self.y + 35), (self.x + 22, self.y + 10), (self.x + 32, self.y + 35)])

        elif self.kind in ["nitro", "shield", "repair"]:
            color = CYAN if self.kind == "nitro" else PURPLE if self.kind == "shield" else GREEN
            label = "N" if self.kind == "nitro" else "S" if self.kind == "shield" else "R"

            pygame.draw.rect(screen, color, r, border_radius=10)
            pygame.draw.rect(screen, BLACK, r, 2, border_radius=10)

            font = pygame.font.SysFont("arial", 24, bold=True)
            text = font.render(label, True, WHITE)
            screen.blit(text, text.get_rect(center=r.center))


class RacerGame:
    def __init__(self, screen, clock, username, settings):
        self.screen = screen
        self.clock = clock
        self.username = username
        self.settings = settings

        self.font = pygame.font.SysFont("arial", 22)
        self.big_font = pygame.font.SysFont("arial", 36)

        self.player = Player(settings.get("car_color", "blue"))

        self.objects = []
        self.road_scroll = 0

        self.score = 0
        self.coins = 0
        self.distance = 0

        self.running = True
        self.game_over = False

        self.active_power = None
        self.power_end_time = 0

        self.base_speed = self.get_base_speed()
        self.object_speed = self.base_speed

        self.spawn_timer = 0

    def get_base_speed(self):
        difficulty = self.settings.get("difficulty", "normal")

        if difficulty == "easy":
            return 4
        elif difficulty == "hard":
            return 8
        return 6

    def run(self):
        while self.running and not self.game_over:
            self.clock.tick(60)
            self.handle_events()
            self.update()
            self.draw()

        return {
            "score": self.score,
            "distance": self.distance,
            "coins": self.coins
        }

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.game_over = True

        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            self.player.move(-6)

        if keys[pygame.K_RIGHT]:
            self.player.move(6)

    def spawn_object(self):
        difficulty_bonus = self.distance // 700

        kinds = [
            "traffic",
            "coin1",
            "coin2",
            "coin3",
            "oil",
            "barrier",
            "pothole",
            "nitro",
            "shield",
            "repair",
            "speed_bump",
            "boost_strip",
            "moving_barrier"
        ]

        if difficulty_bonus >= 2:
            kinds += ["traffic", "traffic", "barrier", "oil", "pothole"]

        kind = random.choice(kinds)
        obj = RoadObject(kind, self.object_speed)

        player_rect = self.player.rect()

        if abs(obj.x - player_rect.x) < 90 and self.distance < 400:
            return

        for other in self.objects:
            if obj.rect().colliderect(other.rect().inflate(30, 100)):
                return

        self.objects.append(obj)

    def activate_power(self, power_name, duration):
        if self.active_power is not None:
            return False

        self.active_power = power_name
        self.power_end_time = time.time() + duration

        if power_name == "Nitro":
            self.object_speed += 4

        if power_name == "Shield":
            self.player.shield = True

        return True

    def update_power(self):
        if self.active_power is None:
            return

        if self.active_power == "Shield":
            return

        if time.time() > self.power_end_time:
            if self.active_power == "Nitro":
                self.object_speed = self.base_speed + self.distance // 700

            self.active_power = None

    def update_difficulty(self):
        self.object_speed = self.base_speed + self.distance // 700

        if self.active_power == "Nitro":
            self.object_speed += 4

    def handle_collision(self, obj):
        kind = obj.kind

        if kind.startswith("coin"):
            value = 1 if kind == "coin1" else 3 if kind == "coin2" else 5
            self.coins += value
            self.score += value * 10
            self.objects.remove(obj)
            return

        if kind == "nitro":
            if self.activate_power("Nitro", 4):
                self.score += 30
            self.objects.remove(obj)
            return

        if kind == "shield":
            if self.activate_power("Shield", 9999):
                self.score += 30
            self.objects.remove(obj)
            return

        if kind == "repair":
            if self.active_power is None:
                self.score += 50
                if len(self.objects) > 1:
                    for other in self.objects[:]:
                        if other != obj and other.kind in ["traffic", "oil", "barrier", "pothole", "moving_barrier"]:
                            self.objects.remove(other)
                            break
            self.objects.remove(obj)
            return

        if kind == "boost_strip":
            self.score += 20
            self.distance += 80
            self.objects.remove(obj)
            return

        if kind == "speed_bump":
            self.score -= 10
            self.distance = max(0, self.distance - 30)
            self.objects.remove(obj)
            return

        if kind in ["traffic", "oil", "barrier", "pothole", "moving_barrier"]:
            if self.player.shield:
                self.player.shield = False
                self.active_power = None
                self.objects.remove(obj)
            else:
                self.game_over = True

    def update(self):
        self.distance += 1
        self.score += 1

        self.update_difficulty()
        self.update_power()

        self.spawn_timer += 1
        spawn_rate = max(18, 75 - self.distance // 80)

        if self.spawn_timer >= spawn_rate:
            self.spawn_timer = 0
            self.spawn_object()

        for obj in self.objects[:]:
            obj.speed = self.object_speed
            obj.update()

            if obj.expired():
                self.objects.remove(obj)
                continue

            if obj.y > HEIGHT:
                self.objects.remove(obj)
                continue

            if obj.rect().colliderect(self.player.rect()):
                self.handle_collision(obj)

        if self.distance >= FINISH_DISTANCE:
            self.score += 500
            self.game_over = True

    def draw_road(self):
        self.screen.fill((35, 145, 60))

        pygame.draw.rect(self.screen, GRAY, (ROAD_X, 0, ROAD_WIDTH, HEIGHT))
        pygame.draw.rect(self.screen, WHITE, (ROAD_X - 8, 0, 8, HEIGHT))
        pygame.draw.rect(self.screen, WHITE, (ROAD_X + ROAD_WIDTH, 0, 8, HEIGHT))

        self.road_scroll += self.object_speed

        if self.road_scroll >= 80:
            self.road_scroll = 0

        for lane in range(1, 4):
            x = ROAD_X + lane * LANE_WIDTH
            for y in range(-80, HEIGHT, 120):
                pygame.draw.rect(self.screen, WHITE, (x - 3, y + self.road_scroll, 6, 60))

    def draw_hud(self):
        pygame.draw.rect(self.screen, WHITE, (0, 0, WIDTH, 85))

        remaining_distance = max(0, FINISH_DISTANCE - self.distance)

        self.draw_text(f"Player: {self.username}", 10, 8)
        self.draw_text(f"Score: {self.score}", 10, 35)
        self.draw_text(f"Coins: {self.coins}", 150, 35)
        self.draw_text(f"Distance: {self.distance}", 280, 35)
        self.draw_text(f"Remaining: {remaining_distance}", 450, 35)

        if self.active_power:
            if self.active_power == "Shield":
                power_text = "Shield: ready"
            else:
                remaining = max(0, int(self.power_end_time - time.time()))
                power_text = f"{self.active_power}: {remaining}s"
        else:
            power_text = "Power: None"

        self.draw_text(power_text, 610, 35)

    def draw_text(self, text, x, y):
        surface = self.font.render(text, True, BLACK)
        self.screen.blit(surface, (x, y))

    def draw(self):
        self.draw_road()

        for obj in self.objects:
            obj.draw(self.screen)

        self.player.draw(self.screen)

        self.draw_hud()

        pygame.display.flip()