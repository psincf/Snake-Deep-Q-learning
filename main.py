import random
import snake
import sys
import pygame
import time
import draw


game = snake.Game()
game.new_game()

renderer = draw.renderer()

mouse = (0, 0)

running = True
last_time_tick = time.time_ns()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.MOUSEMOTION:
            mouse = event.pos
        elif event.type == pygame.KEYDOWN:

            if game.state == snake.State.Pause: game.state = snake.State.Playing
            if game.state == snake.State.Lose: game.new_game()
            if game.state == snake.State.Win: game.new_game()
            
            if event.scancode == 80: game.add_direction(snake.Direction.Left)
            if event.scancode == 79: game.add_direction(snake.Direction.Right)
            if event.scancode == 82: game.add_direction(snake.Direction.Up)
            if event.scancode == 81: game.add_direction(snake.Direction.Down)

    new_time_tick = time.time_ns()
    if new_time_tick < last_time_tick + 50_000_000: continue
    game.next_tick()

    last_time_tick = new_time_tick

    renderer.fill((0, 0, 0))
    draw.draw_snake(renderer, game)
    pygame.display.flip()