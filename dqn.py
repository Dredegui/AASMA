import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import random
import numpy as np
import os
from collections import namedtuple, deque


Transition = namedtuple('Transition',
                        ('state', 'action', 'next_state', 'reward'))

class Net(nn.Module):
    def __init__(self, input_size, output_size, hidden_size=128, hidden_layers=3, device="cpu"):
        super(Net, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        nn.init.normal_(self.fc1.weight, mean=0., std=0.1)
        self.fc2 = nn.Linear(hidden_size, 64)
        nn.init.normal_(self.fc2.weight, mean=0., std=0.1)
        self.fc3 = nn.Linear(64, 32)
        nn.init.normal_(self.fc3.weight, mean=0., std=0.1)
        self.out = nn.Linear(32, output_size)
        nn.init.normal_(self.out.weight, mean=0., std=0.1)
        self.to(device)


    def forward(self, state):
        state = F.relu(self.fc1(state))
        state = F.relu(self.fc2(state))
        state = F.relu(self.fc3(state))
        state = self.out(state)
        return state
    
    def save(self, path):
        if not os.path.exists("models"):
            os.makedirs("models")
        torch.save(self.state_dict(), path)

    def load(self, path, device):
        if os.path.exists(path):
            print(f"Loading model from {path}")
            self.load_state_dict(torch.load(path))
            self.to(device)
    
class DQN():
    def __init__(self, player, gamma=0.99, lr=0.001, epsilon=0.9, len_observation_space=10, len_action_space=5, device="cpu"):
        self.player = player
        self.path = f"models/{player}.pt"
        self.gamma = gamma
        self.lr = lr
        self.epsilon = epsilon
        self.len_observation_space = len_observation_space
        self.len_action_space = len_action_space
        self.batch_size = 256 # TODO review this 
        self.device = device
        self.model = Net(self.len_observation_space, self.len_action_space, device=self.device)
        self.model.load(self.path, device=self.device)
        self.target_model = Net(self.len_observation_space, self.len_action_space, device=self.device)
        self.target_model.load(self.path, device=self.device)
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=self.lr)
        self.loss = nn.MSELoss()
        self.memory = deque(maxlen=10000)

    def check_device(self):
        print(self.device)

    def choose_action(self, state, env):
        if np.random.rand() < self.epsilon:
            return torch.tensor([[env.action_space(self.player).sample()]], device=self.device, dtype=torch.long)
        with torch.no_grad():
            action_value = self.model.to(device=self.device)(state)
            return action_value.max(1).indices.view(1, 1)
    
    def push(self, state, action, next_state, reward):
        self.memory.append(Transition(state, action, next_state, reward))

    def learn(self):
        if len(self.memory) < self.batch_size:
            return
        transitions = random.sample(self.memory, self.batch_size)
        # This converts batch-array of Transitions to Transition of batch-arrays.
        batch = Transition(*zip(*transitions))
        non_final_mask = torch.tensor(tuple(map(lambda s: s is not None, batch.next_state)), device=self.device, dtype=torch.bool)
        non_final_next_states = torch.cat([s for s in batch.next_state if s is not None])

        state_batch = torch.cat(batch.state)
        action_batch = torch.cat(batch.action)
        reward_batch = torch.cat(batch.reward)

        state_action_values = self.model(state_batch).gather(1, action_batch)
        next_state_values = torch.zeros(self.batch_size, device=self.device)
        with torch.no_grad():
            next_state_values[non_final_mask] = self.target_model(non_final_next_states).max(1).values
        # Compute the expected Q values
        expected_state_action_values = (next_state_values * self.gamma) + reward_batch

        # Compute Huber loss
        criterion = nn.SmoothL1Loss()
        loss = criterion(state_action_values, expected_state_action_values.unsqueeze(1))
        # Optimize the model
        self.optimizer.zero_grad()
        loss.backward()
        # In-place gradient clipping
        torch.nn.utils.clip_grad_value_(self.model.parameters(), 100)
        self.optimizer.step()

    def update_target_model(self):
        self.target_model.load_state_dict(self.model.state_dict())

    def soft_update_target_model(self, tau=0.01):
        target_dict = self.target_model.state_dict()
        model_dict = self.model.state_dict()
        for key in model_dict.keys():
            target_dict[key] = (1 - tau) * target_dict[key] + tau * model_dict[key]
        self.target_model.load_state_dict(target_dict)

    def decay_epsilon(self):
        self.epsilon = max(0.1, self.epsilon - 0.005) # 0.0001

    def save_target(self):
        self.target_model.save(self.path)

    