import pygame

def renderer():
    pygame.init()
    return pygame.display.set_mode((1000, 600))

def draw_snake(screen, game, x = 0, y = 0):

    for position in game.snake.body:
        rect = pygame.Rect(position.x * 10 + x, position.y * 10 + y, 10, 10)
        pygame.draw.rect(screen, (0, 120, 0), rect)
        pygame.draw.rect(screen, (255, 255, 255), rect, width = 1)
    

    rect = pygame.Rect(game.snake.head().x * 10 + x, game.snake.head().y * 10 + y, 10, 10)
    pygame.draw.rect(screen, (255, 120, 120), rect)
    pygame.draw.rect(screen, (255, 255, 255), rect, width = 1)

    rect = pygame.Rect(game.food.x * 10 + x, game.food.y * 10 + y, 10, 10)
    pygame.draw.rect(screen, (255, 120, 120), rect)
    pygame.draw.rect(screen, (255, 0, 0), rect, width = 1)

    rect = pygame.Rect(0 + x, 0 + y, game.size[0] * 10, game.size[1] * 10)
    pygame.draw.rect(screen, (255, 255, 0), rect, width = 1)