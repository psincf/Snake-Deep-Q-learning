import random
import io
import snake
import snake_gym
import sys
import pygame
import time
import tensorflow as tf
from tensorflow import keras
import numpy as np
import draw
import draw_gui
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.backends.backend_agg as agg

fig, ax = plt.subplots()
plt.grid(True)
fig.set_size_inches(8.0, 4.0)
ax.set_xlabel("game")
ax.set_ylabel("score")
fig.set_dpi(80)
canvas_plot = agg.FigureCanvasAgg(fig)

size_game = 20
size_obs = 5
matplotlib_image = []
renderer = draw.renderer()
snake_games = []
last_observations = []

for i in range(4):
    if i == 0:
        snake_game = snake_gym.SnakeEnv("human", 400, 0, renderer, (size_game, size_game), size_obs)
        last_observations.append(snake_game.reset())
        snake_games.append(snake_game)
    else:
        snake_game = snake_gym.SnakeEnv("cumulate", 800, (i - 1) * 200, renderer, (size_game, size_game), size_obs)
        last_observations.append(snake_game.reset())
        snake_games.append(snake_game)

running = True
limited_tick_time = False
draw_matplotlib = True

score_per_game = []
training = True
input_size = ((size_obs * 2 + 1) * (size_obs * 2 + 1) - 1) + 2 #snake surronding + food direction
exploration = 1.0
discount_factor = 0.0
learning_rate = 0.1

def best_action(action_list):
    action_temp, action_temp_q = 0, -1_000_000
    for i, action_result in enumerate(action_list[0]):
        if action_result > action_temp_q:
            action_temp = i
            action_temp_q = action_result
    action = action_temp

    return action, action_temp_q

def observation_to_array(observation):
    food = np.asarray(observation["food"])
    snake_surrounding = np.asarray(observation["snake_surrounding"])
    state = np.append(food, snake_surrounding)
    state = np.reshape(state, (1, input_size))
    return state

def create_model():
    model = keras.Sequential()
    model.add(keras.Input(shape=(input_size,)))
    model.add(keras.layers.Dense(256, activation = "relu"))
    model.add(keras.layers.Dense(64, activation = "relu"))
    model.add(keras.layers.Dense(4))

    initial_input = np.zeros(input_size)
    initial_input = tf.convert_to_tensor(initial_input)
    initial_input = tf.expand_dims(initial_input, 0)
    model(initial_input)
    model.compile(loss=keras.losses.Huber(), optimizer=keras.optimizers.Adam(learning_rate = 0.001), metrics=["accuracy"])
    return model

def mean_value_list(list_game, mean_count):
    new_list = []
    last_values = []
    for game_result in list_game:
        last_values.append(game_result)
        if len(last_values) > mean_count:
            last_values.pop(0)
        new_list.append(np.mean(last_values))
    
    return new_list

def evaluate_q_values(model, model_target, batch_size, observation_history, reward_history, action_history, new_observation_history, done_history):
    indices = np.random.choice(len(observation_history), batch_size)

    X = []
    Y = []

    for i_range in range(batch_size):
        indice = indices[i_range]

        observation_temp = observation_history[indice]
        reward_temp = reward_history[indice]
        action_temp = action_history[indice]
        new_observation_temp = new_observation_history[indice]
        done_temp = done_history[indice]

        state = observation_to_array(observation_temp)
        all_q_actions = model(state).numpy()[0]

        q_value = all_q_actions[action_temp]

        new_state = observation_to_array(new_observation_temp)
        q_value_t_plus_one = model_target(new_state).numpy()
        best_next_action, best_next_action_q = best_action(q_value_t_plus_one)

        new_q = 0
        if done_temp:
            new_q = reward_temp
        else:
            new_q = reward_temp + discount_factor * best_next_action_q

        all_q_actions[action_temp] = (1 - learning_rate) * q_value + learning_rate * new_q

        state = observation_to_array(observation_temp)[0]
        X.append(state)
        Y.append(all_q_actions)

        
    X = np.array(X)
    Y = np.array(Y)

    return X, Y


model = create_model()
model_target = create_model()
model_target.set_weights(model.get_weights())

frame = 0
frame_since_eat = 0

observation_history = []
reward_history = []
action_history = []
new_observation_history = []
done_history = []

max_history = 10_000

last_time_tick = time.time_ns()
last_plt_update = 0

while running:
    frame += 1
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                # Hardcoded GUI
                pos = event.pos
                if pos[0] > 300 and pos[0] < 340 and pos[1] > 40 and pos[1] < 80:
                    limited_tick_time = not limited_tick_time
                if pos[0] > 300 and pos[0] < 340 and pos[1] > 90 and pos[1] < 130:
                    training = not training
                if pos[0] > 300 and pos[0] < 340 and pos[1] > 140 and pos[1] < 180:
                    draw_matplotlib = not draw_matplotlib

    new_time_tick = time.time_ns()

    if limited_tick_time:
        while new_time_tick < last_time_tick + 50_000_000:
            new_time_tick = time.time_ns()
            continue
    
    for i in range(4):
        snake_game_gym = snake_games[i]
        observation = last_observations[i]
        action = snake.Direction.Right.value
        if (random.random() < exploration) and not i == 0:
            action = random.randint(0, 3)
        else:
            state = observation_to_array(observation)

            action_list = model(state).numpy()
            action, q = best_action(action_list)

        exploration = exploration * 0.999
        if exploration < 0.1:
            exploration = 0.1
        observation_history.append(observation)
        
        observation, reward, done, info = snake_game_gym.step(action)

        last_observations[i] = observation
        reward_history.append(reward)
        action_history.append(action)
        new_observation_history.append(observation)
        done_history.append(done)

        if len(observation_history) > max_history:
            observation_history.pop(0)
            reward_history.pop(0)
            action_history.pop(0)
            new_observation_history.pop(0)
            done_history.pop(0)

        if done:
            if i == 0:
                score_per_game.append(len(snake_game_gym._game.snake.body) - 3)
            snake_game_gym.reset()
            frame_since_begin = 0

    last_time_tick = new_time_tick
    if frame % 8 == 0 and training:
        if frame > 10000:
            discount_factor = 0.9
        if len(observation_history) < 32:
            pass
        else:
            size_training = 16
            batch_size = 16
            X, Y = evaluate_q_values(model, model_target, size_training, observation_history, reward_history, action_history, new_observation_history, done_history)

            model.fit(X, Y, batch_size = batch_size, epochs = 1)

    if frame % 1000 == 0:
        model_target.set_weights(model.get_weights())


    renderer.fill((0, 0, 0))
    snake_games[0].render()
    snake_games[1].render()
    snake_games[2].render()
    snake_games[3].render()
    draw_gui.draw_gui(snake_game_gym.renderer, training, limited_tick_time, draw_matplotlib)

    new_time = time.time_ns()

    if new_time > last_plt_update + 10_000_000_000 and draw_matplotlib:
        ax.scatter(range(len(score_per_game)), score_per_game, color = (0.5, 0.5, 0.5))
        ax.plot(range(len(score_per_game)), mean_value_list(score_per_game, 20), color = (1.0, 0.0, 0.0))
        ax.plot(range(len(score_per_game)), mean_value_list(score_per_game, 100), color = (0.0, 1.0, 0.0))
        canvas_plot.draw()
        canvas_plot_renderer = canvas_plot.get_renderer()
        data = canvas_plot_renderer.buffer_rgba().tobytes()
        size = fig.get_size_inches()
        
        matplotlib_image = pygame.image.frombuffer(data, (int(size[0] * fig.dpi), int(size[1] * fig.dpi)), "RGBA")
        last_plt_update = new_time


    if matplotlib_image:
        renderer.blit(matplotlib_image, (20, 220))
        pass
        
    pygame.display.flip()