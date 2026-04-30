import pygame
from datetime import datetime
from pathlib import Path

from tools import draw_preview_shape, flood_fill, draw_toolbar, get_color_palette

pygame.init()
pygame.font.init()

WIDTH, HEIGHT = 1200, 800
TOOLBAR_HEIGHT = 135
CANVAS_RECT = pygame.Rect(0, TOOLBAR_HEIGHT, WIDTH, HEIGHT - TOOLBAR_HEIGHT)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TSIS 2 Paint Application")

font = pygame.font.SysFont("arial", 18)
text_font = pygame.font.SysFont("arial", 26)

canvas = pygame.Surface((WIDTH, HEIGHT - TOOLBAR_HEIGHT))
canvas.fill((255, 255, 255))

current_color = (0, 0, 0)
current_tool = "pencil"
brush_size = 2

drawing = False
start_pos = None
last_pos = None
preview_pos = None

text_mode = False
text_position = None
text_buffer = ""

color_palette = get_color_palette()

tool_buttons = [
    {"label": "Pencil", "key": "pencil", "rect": pygame.Rect(10, 10, 92, 34)},
    {"label": "Line", "key": "line", "rect": pygame.Rect(108, 10, 92, 34)},
    {"label": "Rect", "key": "rectangle", "rect": pygame.Rect(206, 10, 92, 34)},
    {"label": "Circle", "key": "circle", "rect": pygame.Rect(304, 10, 92, 34)},
    {"label": "Square", "key": "square", "rect": pygame.Rect(402, 10, 92, 34)},
    {"label": "RightTri", "key": "right_triangle", "rect": pygame.Rect(500, 10, 110, 34)},
    {"label": "EquiTri", "key": "equilateral_triangle", "rect": pygame.Rect(616, 10, 110, 34)},
    {"label": "Rhombus", "key": "rhombus", "rect": pygame.Rect(732, 10, 110, 34)},
    {"label": "Fill", "key": "fill", "rect": pygame.Rect(10, 50, 92, 34)},
    {"label": "Text", "key": "text", "rect": pygame.Rect(108, 50, 92, 34)},
    {"label": "Eraser", "key": "eraser", "rect": pygame.Rect(206, 50, 92, 34)},
    {"label": "2 px", "key": "size_2", "rect": pygame.Rect(304, 50, 78, 34)},
    {"label": "5 px", "key": "size_5", "rect": pygame.Rect(388, 50, 78, 34)},
    {"label": "10 px", "key": "size_10", "rect": pygame.Rect(472, 50, 86, 34)},
]

shape_tools = {
    "line",
    "rectangle",
    "circle",
    "square",
    "right_triangle",
    "equilateral_triangle",
    "rhombus",
}

save_dir = Path("saved_images")
save_dir.mkdir(exist_ok=True)

clock = pygame.time.Clock()
running = True

while running:
    screen.fill((255, 255, 255))

    draw_toolbar(screen, font, current_tool, current_color, brush_size, tool_buttons)

    for color, rect in color_palette:
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, (0, 0, 0), rect, 2)

        if color == current_color:
            pygame.draw.rect(screen, (255, 255, 255), rect, 2)

    screen.blit(canvas, (0, TOOLBAR_HEIGHT))

    if drawing and current_tool in shape_tools and start_pos and preview_pos:
        preview_surface = canvas.copy()
        draw_preview_shape(
            preview_surface,
            current_tool,
            start_pos,
            preview_pos,
            current_color,
            brush_size,
        )
        screen.blit(preview_surface, (0, TOOLBAR_HEIGHT))

    if text_mode and text_position:
        preview_surface = canvas.copy()
        preview_text = text_font.render(text_buffer + "|", True, current_color)
        preview_surface.blit(preview_text, text_position)
        screen.blit(preview_surface, (0, TOOLBAR_HEIGHT))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            ctrl_pressed = pygame.key.get_mods() & pygame.KMOD_CTRL

            if ctrl_pressed and event.key == pygame.K_s:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = save_dir / f"paint_{timestamp}.png"
                pygame.image.save(canvas, str(filename))
                print(f"Saved: {filename}")

            elif text_mode:
                if event.key == pygame.K_RETURN:
                    if text_buffer and text_position:
                        rendered = text_font.render(text_buffer, True, current_color)
                        canvas.blit(rendered, text_position)

                    text_mode = False
                    text_buffer = ""
                    text_position = None

                elif event.key == pygame.K_ESCAPE:
                    text_mode = False
                    text_buffer = ""
                    text_position = None

                elif event.key == pygame.K_BACKSPACE:
                    text_buffer = text_buffer[:-1]

                else:
                    if event.unicode.isprintable():
                        text_buffer += event.unicode

            else:
                if event.key == pygame.K_1:
                    brush_size = 2
                elif event.key == pygame.K_2:
                    brush_size = 5
                elif event.key == pygame.K_3:
                    brush_size = 10
                elif event.key == pygame.K_p:
                    current_tool = "pencil"
                elif event.key == pygame.K_l:
                    current_tool = "line"
                elif event.key == pygame.K_r:
                    current_tool = "rectangle"
                elif event.key == pygame.K_c:
                    current_tool = "circle"
                elif event.key == pygame.K_e:
                    current_tool = "eraser"
                elif event.key == pygame.K_f:
                    current_tool = "fill"
                elif event.key == pygame.K_t:
                    current_tool = "text"
                elif event.key == pygame.K_q:
                    current_tool = "square"
                elif event.key == pygame.K_w:
                    current_tool = "right_triangle"
                elif event.key == pygame.K_a:
                    current_tool = "equilateral_triangle"
                elif event.key == pygame.K_d:
                    current_tool = "rhombus"

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos

            clicked_toolbar = False

            for button in tool_buttons:
                if button["rect"].collidepoint(mouse_pos):
                    clicked_toolbar = True
                    key = button["key"]

                    if key.startswith("size_"):
                        brush_size = int(key.split("_")[1])
                    else:
                        current_tool = key

                    break

            if not clicked_toolbar:
                for color, rect in color_palette:
                    if rect.collidepoint(mouse_pos):
                        current_color = color
                        clicked_toolbar = True
                        break

            if clicked_toolbar:
                continue

            if CANVAS_RECT.collidepoint(mouse_pos):
                canvas_pos = (mouse_pos[0], mouse_pos[1] - TOOLBAR_HEIGHT)

                if current_tool == "fill":
                    flood_fill(canvas, canvas_pos[0], canvas_pos[1], current_color)

                elif current_tool == "text":
                    text_mode = True
                    text_position = canvas_pos
                    text_buffer = ""

                elif current_tool in {"pencil", "eraser"}:
                    drawing = True
                    start_pos = canvas_pos
                    last_pos = canvas_pos

                    draw_color = (255, 255, 255) if current_tool == "eraser" else current_color
                    pygame.draw.circle(canvas, draw_color, canvas_pos, max(1, brush_size // 2))

                elif current_tool in shape_tools:
                    drawing = True
                    start_pos = canvas_pos
                    preview_pos = canvas_pos

        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = event.pos

            if drawing:
                canvas_pos = (mouse_pos[0], mouse_pos[1] - TOOLBAR_HEIGHT)

                if current_tool in {"pencil", "eraser"} and CANVAS_RECT.collidepoint(mouse_pos):
                    draw_color = (255, 255, 255) if current_tool == "eraser" else current_color

                    if last_pos:
                        pygame.draw.line(canvas, draw_color, last_pos, canvas_pos, brush_size)

                    last_pos = canvas_pos

                elif current_tool in shape_tools:
                    preview_pos = canvas_pos

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            mouse_pos = event.pos

            if drawing:
                canvas_pos = (mouse_pos[0], mouse_pos[1] - TOOLBAR_HEIGHT)

                if current_tool in shape_tools and start_pos:
                    draw_preview_shape(
                        canvas,
                        current_tool,
                        start_pos,
                        canvas_pos,
                        current_color,
                        brush_size,
                    )

                drawing = False
                start_pos = None
                last_pos = None
                preview_pos = None

    hint = font.render(
        "Tools: P/L/R/C/E/F/T/Q/W/A/D   Sizes: 1/2/3   Ctrl+S: Save",
        True,
        (40, 40, 40),
    )
    screen.blit(hint, (580, 58))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()