import tkinter as tk
import json
import pickle

# from footpong_v1 import run_game
from agents.greedy_agent import GreedyAgent
from agents.random_agent import RandomAgent
from agents.balanced_agent import BalancedAgent
from agents.goal_keeper_agent import GoalKeeperAgent
from agents.role_agent import RoleAgent
from game_statistics import GameStatistics
import pygame
from env.constants import *
import env.footpong as ftenv
import threading

game_running = False

def run_game(n_games=5, tick_rate=0):
    with open('roles.json', 'r') as f:
        saved_agents = json.load(f)

    env = ftenv.footpong(render_mode="human")
    env.render()

    statistics = []

    agents = []

    for i in range(1, 5):
        if saved_agents[f"player{i}"] == "greedy":
            agents.append(GreedyAgent(f"player{i}", agent_id=i))
        elif saved_agents[f"player{i}"] == "random":
            agents.append(RandomAgent(f"player{i}", agent_id=i))
        elif saved_agents[f"player{i}"] == "balanced":
            agents.append(BalancedAgent(f"player{i}", agent_id=i))
        elif saved_agents[f"player{i}"] == "goal_keeper":
            agents.append(GoalKeeperAgent(f"player{i}", agent_id=i))
        elif saved_agents[f"player{i}"] == "role_agent(goalkeeper, greedy)":
            agents.append(RoleAgent(f"player{i}", i, {
                "defender": GoalKeeperAgent,
                "attacker": GreedyAgent,
            }))
        elif saved_agents[f"player{i}"] == "role_agent(goalkeeper, balanced)":
            agents.append(RoleAgent(f"player{i}", i, {
                "defender": GoalKeeperAgent,
                "attacker": BalancedAgent,
            }))
    clock = pygame.time.Clock()
    for i in range(n_games):
        if not able_to_run:
                break
        observations, _ = env.reset(seed=42)
        statistics.append(GameStatistics(env.agents))
        env.game.set_statistics(statistics[-1])
        while env.agents:
            if not able_to_run:
                break
            actions = {}
            for agent in env.agents:
                actions[agent] = agents[env.agent_name_mapping[agent]].act(observations[agent])

            observations, _, _, _, _ = env.step(actions)
            env.render()
            if tick_rate != 0:
                clock.tick(tick_rate)
        statistics[-1].print_statistics()
        print(f"Game {i} finished")

    if statistics is not None:
        statistics = [s.get_dict() for s in statistics]
        statistics_dict = {game: statistics[game] for game in range(len(statistics))}
        print(statistics_dict)
        with open("statistics.json", "w") as f:
            json.dump(statistics_dict, f)
        # dump pickle
        with open("statistics.pkl", "wb") as f:
            pickle.dump(statistics_dict, f)
    env.close()

def save_agent_and_start_game():
    global game_running
    if game_running:
        return
    global able_to_run
    able_to_run = True
    roles = {
        "player1": agent_var1.get(),
        "player2": agent_var2.get(),
        "player3": agent_var3.get(),
        "player4": agent_var4.get(),
    }
    with open('roles.json', 'w') as f:
        json.dump(roles, f)
    global game_thread
    game_thread = threading.Thread(target=run_game, args=(n_games_var.get(), tick_rate_var.get()))
    game_running = True
    game_thread.start()

def end_game():
    global able_to_run
    able_to_run = False
    game_thread.join()
    global game_running
    game_running = False

root = tk.Tk()
root.title("Footpong Simulator")
root.geometry("500x300")
frame = tk.Frame(root)
agent_var1 = tk.StringVar(frame)
agent_var2 = tk.StringVar(frame)
agent_var3 = tk.StringVar(frame)
agent_var4 = tk.StringVar(frame)

possible_agents = ["greedy", "random", "balanced", "goalkeeper", "role_agent(goalkeeper, greedy)", "role_agent(goalkeeper, balanced)"]

agent_var1.set(possible_agents[0])
agent_var2.set(possible_agents[0])
agent_var3.set(possible_agents[0])
agent_var4.set(possible_agents[0])

# Define number of games
n_games_var = tk.IntVar(frame)
n_games_var.set(5)
# Clock tick rate
tick_rate_var = tk.IntVar(frame)
tick_rate_var.set(0)

tk.Label(frame, text="Number of games").grid(row=0, column=0)
tk.Entry(frame, textvariable=n_games_var).grid(row=1, column=0, pady=(0,20))
tk.Label(frame, text="Tick rate").grid(row=0, column=1)
tk.Entry(frame, textvariable=tick_rate_var).grid(row=1, column=1, pady=(0,20))

tk.Label(frame, text="Team Red", font=("TkDefaultFont", 10, "bold")).grid(row=2, column=0)
tk.Label(frame, text="Team Green", font=("TkDefaultFont", 10, "bold")).grid(row=2, column=1)
row_base = 3
tk.Label(frame, text="Player 1 agent").grid(row=row_base, column=0)
tk.OptionMenu(frame, agent_var1, *possible_agents).grid(row=row_base+1, column=0)

tk.Label(frame, text="Player 2 agent").grid(row=row_base, column=1)
tk.OptionMenu(frame, agent_var2, *possible_agents).grid(row=row_base+1, column=1)

tk.Label(frame, text="Player 3 agent").grid(row=row_base+2, column=0)
tk.OptionMenu(frame, agent_var3, *possible_agents).grid(row=row_base+3, column=0)

tk.Label(frame, text="Player 4 agent").grid(row=row_base+2, column=1)
tk.OptionMenu(frame, agent_var4, *possible_agents).grid(row=row_base+3, column=1)


tk.Button(frame, text="Start game", width=25, command=save_agent_and_start_game).grid(row=row_base+4, column=0, columnspan=2, pady=(20,0))

tk.Button(frame, text="End game", width=25, command=end_game).grid(row=row_base+5, column=0, columnspan=2)
frame.pack()
frame.place(relx=0.5, rely=0.5, anchor="center")
root.mainloop()
