import pygame

def draw_checkbox(renderer, x, y, size, checked):
    rect = pygame.Rect(x, y, size, size)
    pygame.draw.rect(renderer, (255, 255, 255), rect, width = 2)

    if checked:
        pygame.draw.line(renderer, (255, 255, 255), (x + size / 10, y + size / 10), (x + size - size / 10, y + size - size / 10), 2)
        pygame.draw.line(renderer, (255, 255, 255), (x + size - size / 10, y + size / 10), (x + size / 10, y + size - size / 10), 2)


def draw_text_helper(renderer, text, color, x, y):
    text_exp = pygame.font.Font.render(pygame.font.SysFont(pygame.font.get_default_font(), 40), text, True, color)
    pygame.display.get_surface().blit(text_exp, (x, y))

    text_exp_size = text_exp.get_size()
    rect = pygame.Rect(x - 20, y - 10, text_exp_size[0] + 40, text_exp_size[1] + 20)
    pygame.draw.rect(renderer, (255, 255, 255), rect, width = 2)

def draw_gui(renderer, training, limited_tick, draw_matplotlib):
    draw_text_helper(renderer, "limited_tick_time", (255, 255, 255), 20, 50)
    draw_checkbox(renderer, 300, 40, 40, limited_tick)
    draw_text_helper(renderer, "training", (255, 255, 255), 20, 100)
    draw_checkbox(renderer, 300, 90, 40, training)
    draw_text_helper(renderer, "matplot_update", (255, 255, 255), 20, 150)
    draw_checkbox(renderer, 300, 140, 40, draw_matplotlib)