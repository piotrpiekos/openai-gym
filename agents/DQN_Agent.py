from .AbstractAgent import AbstractAgent
from utils.RoundBuffer import RoundBuffer

import numpy as np

from networks.DQN_Network import DQN_PyTorch


class DQN_Agent(AbstractAgent):
    def __init__(self, env):
        super().__init__(env)

        # RL training parameters
        self.MINIBATCH_SIZE = 32

        self.FINAL_EPS = 0.05
        self.START_EPS = 1
        self.EXP_EPISODES = 300
        self.DISCOUNT = 0.9
        ER_SIZE = 1000000

        self.UPDATES_PER_EPOCH = 50000

        self.no_update_moves = 1000

        # network parameters
        self.learning_rate = 0.0001

        # initialization
        self.ER = RoundBuffer(ER_SIZE)

        self.num_updates = 0
        self.cur_episode_num = 0

        # networks
        self.target_network = DQN_PyTorch(self.learning_rate, self.DISCOUNT)
        self.behavior_network = DQN_PyTorch(self.learning_rate, self.DISCOUNT)

    def take_action(self, state):
        cur_eps = max(
            self.START_EPS + (self.FINAL_EPS - self.START_EPS) / self.EXP_EPISODES * self.cur_episode_num,
            self.FINAL_EPS
        )

        if np.random.random() < cur_eps:
            # exploration
            return self.env.action_space.sample()
        else:
            # exploitation
            action_values = self.behavior_network.predict(state)
            return action_values.argmax()

    def observe(self, state, action, reward, next_state, done):
        self.ER.push([state, action, reward, next_state, done])

    def step_train(self):
        if len(self.ER) > self.no_update_moves:
            minibatch = self.ER.sample(self.MINIBATCH_SIZE)
            self.behavior_network.train_on_batch(minibatch, self.target_network)