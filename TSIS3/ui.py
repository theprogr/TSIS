import pygame
import sys

WHITE = (245, 245, 245)
BLACK = (20, 20, 20)
DARK = (70, 70, 70)
BLUE = (50, 120, 255)


class Button:
    def __init__(self, text, x, y, w, h):
        self.text = text
        self.rect = pygame.Rect(x, y, w, h)

    def draw(self, screen, font):
        mouse = pygame.mouse.get_pos()
        color = BLUE if self.rect.collidepoint(mouse) else DARK

        pygame.draw.rect(screen, color, self.rect, border_radius=12)

        text = font.render(self.text, True, WHITE)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)

    def clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)


def draw_text(screen, text, font, color, x, y, center=False):
    surface = font.render(text, True, color)
    rect = surface.get_rect()

    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)

    screen.blit(surface, rect)


def username_screen(screen, clock):
    font = pygame.font.SysFont("arial", 28)
    big_font = pygame.font.SysFont("arial", 48)

    name = ""

    while True:
        screen.fill(WHITE)

        draw_text(screen, "Enter Username", big_font, BLACK, 400, 170, True)
        draw_text(screen, name + "|", font, BLACK, 400, 250, True)
        draw_text(screen, "Press ENTER to start", font, DARK, 400, 320, True)

        pygame.display.flip()
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name.strip():
                    return name.strip()

                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]

                elif len(name) < 12 and event.unicode.isprintable():
                    name += event.unicode