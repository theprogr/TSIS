import pygame
from collections import deque

BLACK = (0, 0, 0)


def draw_preview_shape(surface, tool, start_pos, end_pos, color, width):
    if not start_pos or not end_pos:
        return

    x1, y1 = start_pos
    x2, y2 = end_pos

    left = min(x1, x2)
    top = min(y1, y2)
    rect_w = abs(x2 - x1)
    rect_h = abs(y2 - y1)
    rect = pygame.Rect(left, top, rect_w, rect_h)

    if tool == "line":
        pygame.draw.line(surface, color, start_pos, end_pos, width)

    elif tool == "rectangle":
        pygame.draw.rect(surface, color, rect, width)

    elif tool == "square":
        side = min(rect_w, rect_h)
        pygame.draw.rect(surface, color, pygame.Rect(left, top, side, side), width)

    elif tool == "circle":
        radius = min(rect_w, rect_h) // 2
        center = (left + rect_w // 2, top + rect_h // 2)
        if radius > 0:
            pygame.draw.circle(surface, color, center, radius, width)

    elif tool == "right_triangle":
        points = [(x1, y1), (x1, y2), (x2, y2)]
        pygame.draw.polygon(surface, color, points, width)

    elif tool == "equilateral_triangle":
        side = abs(x2 - x1)
        height = int((3 ** 0.5) / 2 * side)
        direction = 1 if y2 >= y1 else -1
        points = [
            (x1, y1),
            (x1 + side, y1),
            (x1 + side // 2, y1 + direction * height),
        ]
        pygame.draw.polygon(surface, color, points, width)

    elif tool == "rhombus":
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
        points = [(cx, y1), (x2, cy), (cx, y2), (x1, cy)]
        pygame.draw.polygon(surface, color, points, width)


def flood_fill(surface, x, y, fill_color):
    width, height = surface.get_size()

    if not (0 <= x < width and 0 <= y < height):
        return

    target_color = surface.get_at((x, y))
    fill_color_rgba = pygame.Color(*fill_color)

    if target_color == fill_color_rgba:
        return

    queue = deque()
    queue.append((x, y))

    while queue:
        px, py = queue.popleft()

        if px < 0 or px >= width or py < 0 or py >= height:
            continue

        if surface.get_at((px, py)) != target_color:
            continue

        surface.set_at((px, py), fill_color_rgba)

        queue.append((px + 1, py))
        queue.append((px - 1, py))
        queue.append((px, py + 1))
        queue.append((px, py - 1))


def draw_toolbar(screen, font, current_tool, current_color, brush_size, buttons):
    pygame.draw.rect(screen, (235, 235, 235), (0, 0, screen.get_width(), 90))
    pygame.draw.line(screen, (160, 160, 160), (0, 90), (screen.get_width(), 90), 2)

    for button in buttons:
        rect = button["rect"]
        label = button["label"]
        key = button["key"]

        active = key == current_tool or key == f"size_{brush_size}"
        color = (200, 220, 255) if active else (245, 245, 245)

        pygame.draw.rect(screen, color, rect, border_radius=8)
        pygame.draw.rect(screen, (120, 120, 120), rect, 2, border_radius=8)

        text = font.render(label, True, BLACK)
        screen.blit(text, text.get_rect(center=rect.center))

    pygame.draw.rect(screen, (255, 255, 255), (980, 15, 180, 60), border_radius=8)
    pygame.draw.rect(screen, (120, 120, 120), (980, 15, 180, 60), 2, border_radius=8)

    label = font.render("Color", True, BLACK)
    screen.blit(label, (995, 20))

    pygame.draw.rect(screen, current_color, (1070, 23, 70, 36))
    pygame.draw.rect(screen, BLACK, (1070, 23, 70, 36), 2)

    info = font.render(f"Brush: {brush_size}px", True, BLACK)
    screen.blit(info, (995, 52))


def get_color_palette():
    return [
        ((20, 20, 20), pygame.Rect(10, 95, 32, 32)),
        ((255, 255, 255), pygame.Rect(46, 95, 32, 32)),
        ((255, 0, 0), pygame.Rect(82, 95, 32, 32)),
        ((0, 180, 0), pygame.Rect(118, 95, 32, 32)),
        ((0, 0, 255), pygame.Rect(154, 95, 32, 32)),
        ((255, 200, 0), pygame.Rect(190, 95, 32, 32)),
        ((255, 128, 0), pygame.Rect(226, 95, 32, 32)),
        ((128, 0, 255), pygame.Rect(262, 95, 32, 32)),
        ((0, 180, 180), pygame.Rect(298, 95, 32, 32)),
        ((255, 105, 180), pygame.Rect(334, 95, 32, 32)),
    ]