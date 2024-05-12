class Agent:
    def __init__(self, name, agent_id):
        self.name = name
        self.agent_id = agent_id

    def act(self, observation):
        raise NotImplementedError

    def close(self):
        pass

    def reset(self):
        pass

    def save(self, filename):
        pass

    def load(self, filename):
        pass