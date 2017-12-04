import torch
import torch.nn as nn
import torch.optim as optim
from state import State
from player import Player
from monte_carlo_tree import MonteCarloTree, NetEvaluator
from torch.autograd import Variable

class Trainer:

    def __init__(self):
        self.tree = MonteCarloTree(State(), NetEvaluator())
        self.net = self.tree.evaluator.net
        self.alpha = 0.01
        self.optimizer = optim.SGD(self.net.parameters(), lr=self.alpha)
        self.criterion = nn.MSELoss()

    def train(self, k, n):
        for _ in range(k):
            self.train_on_game(n)

    def train_on_game(self, n):
        print('playing game')
        self.tree.play_training_game(n)
        print('training on game')
        game_path = self.tree.game_path
        winner = self.tree.state.score()[0]
        for node in game_path:
            if node.edges[0].a is None: continue
            input_v = node.state.convert_to_net_input()
            target = self.node_to_target(node, winner)
            self.optimizer.zero_grad()
            output = self.net(input_v)
            loss = self.criterion(output, target)
            loss.backward()
            self.optimizer.step()

    def node_to_target(self, node, winner):
        target = [0]*65
        for edge in node.edges:
            x,y = edge.a
            target[x + y*8] = edge.Q
        target[64] = winner
        return Variable(torch.FloatTensor(target))


trainer = Trainer()
trainer.train(10, 5)
print(trainer.net.layer_1.weight.data)
print(trainer.net.layer_2.weight.data)
print(trainer.net.layer_3.weight.data)