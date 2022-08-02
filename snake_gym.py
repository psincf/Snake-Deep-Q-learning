import gym
import numpy as np
import snake;
from typing import Optional
import draw
import math

class SnakeEnv(gym.Env):
    metadata = {"render_modes": ["human"], "render_fps": 4}

    def __init__(self, render_mode: Optional[str] = None, position_x = 0, position_y = 0, renderer = None, size_game = (20, 20), size_obs = 5):
        self.position_x = position_x
        self.position_y = position_y
        self.render_mode = render_mode
        self.size_game = size_game
        self.size_obs = size_obs

        self.observation_space = gym.spaces.Dict(
            {
                "food": gym.spaces.Box(-1, 1, shape=(2, 1), dtype=int),
                "snake_surrounding": gym.spaces.Box(0, 1, shape=(size_obs * 2 + 1, size_obs * 2 + 1), dtype=int)
            }
        )

        self.action_space = gym.spaces.Discrete(4)

        if self.render_mode == "human":
            self.renderer = draw.renderer()
        elif self.render_mode == "cumulate":
            self.renderer = renderer

        self._game = snake.Game(size_game)
        self._game.new_game()


    def _get_obs(self):
        distance_food = self._game.get_vector_head_food()
        distance_food = np.sign(distance_food[0]), np.sign(distance_food[1])

        size_obs = self.size_obs
        size_game = self.size_game

        head = self._game.snake.head()
        surrounding = np.ones((size_obs * 2 + 1, size_obs * 2 + 1), dtype=int)

        for x_obs, x in enumerate(range(head.x - size_obs, head.x + size_obs + 1)):
            for y_obs, y in enumerate(range(head.y - size_obs, head.y + size_obs + 1)):
                if x < 0 or x >= size_game[0] or y < 0 or y >= size_game[1]:
                    continue
                surrounding[x_obs][y_obs] = self._game.matrix[x][y] 

        surrounding = np.delete(surrounding, int((size_obs * 2 + 1) * (size_obs * 2 + 1) / 2)) #delete head of snake

        return {
            "food": distance_food,
            "snake_surrounding": surrounding
        }

    def _get_info(self):
        pass

    def reset(self, seed=None, return_info=False, options=None):
        super().reset(seed=seed)
        self._game.new_game()
        self._game.no_pause()

        self._food = self._game.food
        self._snake = self._game.snake.body
        self._old_distance = self._game.get_distance_head_food()
        self._old_snake_size = len(self._game.snake.body)

        observation = self._get_obs()
        info = self._get_info()

        return observation

    def step(self, action):
        direction = snake.Direction(action)
        done = self._game.state == snake.State.Lose or self._game.state == snake.State.Win

        self._game.next_tich_with_direction(direction)


        observation = self._get_obs()
        info = self._get_info()

        new_distance = self._game.get_distance_head_food()
        new_snake_size = len(self._game.snake.body)

        reward = 0

        if self._game.state == snake.State.Lose: reward = -200
        elif self._game.state == snake.State.Win: reward = 200
        elif new_snake_size > self._old_snake_size: reward = 20
        elif new_distance < self._old_distance: reward = 1
        elif new_distance > self._old_distance: reward = -1

        self._old_distance = new_distance
        self._old_snake_size = len(self._game.snake.body)

        return observation, reward, done, info

    def render(self):
        draw.draw_snake(self.renderer, self._game, self.position_x, self.position_y)
