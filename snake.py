from ast import Raise
from enum import Enum
import random
import copy
import math
import numpy as np

class Position:
    def __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y

    def __eq__(self, other):
        if self.x == other.x and self.y == other.y: return True
        return False

    def __str__(self):
        return "x = " + str(self.x) + ", y = " + str(self.y)

class Direction(Enum):
    Up = 0
    Left = 1
    Down = 2
    Right = 3

    def is_modified_by(self, direction):
        if self == direction:
            return False
        
        if self == Direction.Up and direction == Direction.Down: return False
        if self == Direction.Down and direction == Direction.Up: return False
        if self == Direction.Left and direction == Direction.Right: return False
        if self == Direction.Right and direction == Direction.Left: return False

        return True
    
class State(Enum):
    Pause = 0
    Playing = 1
    Lose = 2
    Win = 3

class Snake:
    body = []

    def is_in(self, position):
        for part in self.body:
            if position == part:
                return True
        return False

    def append_body_part(self, position):
        self.body.append(position)

    def move_to(self, position):
        self.body.append(position)
        self.body.pop(0)

    def head(self):
        return self.body[len(self.body) - 1]

    def tail(self):
        return self.body[0]

    def reset(self, size_map):
        max_x = size_map[0] - 5
        max_y = size_map[1] - 5

        x = random.randint(2, max_x)
        y = random.randint(2, max_y)

        self.body = [Position(x, y), Position(x + 1, y), Position(x + 2, y)]

    def clear(self):
        self.body = []


class Game:


    def __init__(self, size = (20, 20)):
        self.matrix = np.zeros(size, dtype=int)
        self.free_position = []
        self.state = State.Pause
        self.food = False
        self.size = size
        self.snake = Snake()
        self.last_direction = Direction.Right
        self.directions = []

    def new_food(self):
        i = random.randint(0, len(self.free_position) - 1)
        new_food = self.free_position.pop(i)
        self.food = new_food
    
    def new_game(self):
        self.matrix = np.zeros(self.size, dtype=int)
        self.free_position.clear()
        for x in range(0, self.size[0]):
            for y in range(0, self.size[1]):
                self.free_position.append(Position(x, y))


        self.last_direction = Direction.Right
        self.state = State.Pause
        self.snake.reset(self.size)

        for position in self.snake.body:
            self.free_position.remove(copy.copy(position))
            self.matrix[position.x][position.y] = 1

        self.new_food()

    def add_direction(self, direction):
        self.directions.append(direction)

    def no_pause(self):
        if self.state == State.Pause: self.state = State.Playing

    def next_tick(self):
        if self.state == State.Lose or self.state == State.Win or self.state == State.Pause: return
        new_direction = False
        while len(self.directions) > 0:
            new_direction = self.directions.pop(0)
            if self.last_direction.is_modified_by(new_direction):
                break
            else:
                new_direction = False
        
        if new_direction == False: new_direction = self.last_direction

        self.next_tich_with_direction(new_direction)

    def next_tich_with_direction(self, direction):
        if self.state == State.Lose or self.state == State.Win or self.state == State.Pause: return
        if not self.last_direction.is_modified_by(direction):
            direction = self.last_direction
        
        new_x = 0
        new_y = 0

        if direction == Direction.Left: new_x = -1
        if direction == Direction.Right: new_x = 1
        if direction == Direction.Up: new_y = -1
        if direction == Direction.Down: new_y = 1

        new_head = copy.copy(self.snake.head())
        new_head.x += new_x
        new_head.y += new_y


        if new_head.x < 0 or new_head.x >= self.size[0] or new_head.y < 0 or new_head.y >= self.size[1]:
            self.state = State.Lose
            return
        
        if self.snake.is_in(new_head):
            self.state = State.Lose
            return

        self.matrix[new_head.x][new_head.y] = 1
        if new_head == self.food:
            self.snake.append_body_part(new_head)
            if len(self.free_position) == 0:
                self.state = State.Win
                return
            else:
                self.new_food()
        else:
            old_tail = self.snake.tail()
            self.free_position.append(old_tail)
            self.matrix[old_tail.x][old_tail.y] = 0
            self.snake.move_to(new_head)
            self.free_position.remove(copy.copy(new_head))
        
        self.last_direction = direction

    def get_vector_head_food(self):
        head = self.snake.head()
        food = self.food

        return (head.x - food.x, head.y - food.y)

    def get_distance_head_food(self):
        head = self.snake.head()
        food = self.food
        
        distance_x = abs(head.x - food.x)
        distance_y = abs(head.y - food.y)

        distance = math.sqrt(distance_x * distance_x + distance_y * distance_y)
        return distance

    #def ai(self):
    #    if self.state != self.state.Playing: return
    #    if self.snake.head().x == self.size[0] - 1:
    #        if self.snake.head().y != self.size[1] - 1:
    #            self.add_direction(Direction.Down)

    #    if self.snake.head().y == 1:
    #        if self.snake.head().x == 0:
    #            pass
    #        else:
    #            if self.last_direction == Direction.Up:
    #                self.add_direction(Direction.Left)
    #                self.add_direction(Direction.Down)


    #    if self.snake.head().y == 0:
    #        if self.snake.head().x == 0:
    #            self.add_direction(Direction.Right)

    #    if self.snake.head().y == self.size[1] - 1:
    #        if self.last_direction == Direction.Down:
    #            self.add_direction(Direction.Left)
    #            self.add_direction(Direction.Up)