from environment import ProductOwnerEnv
from algorithms.deep_q_networks import DQN


class BaseStudy:
    def __init__(self, env: ProductOwnerEnv, agent, trajectory_max_len) -> None:
        self.env = env
        self.agent: DQN = agent
        self.trajectory_max_len = trajectory_max_len

    def fit_agent(self, state, action, reward, done, next_state):
        return self.agent.fit(state, action, reward, done, next_state)

    def play_trajectory(self, init_state):
        total_reward = 0
        state = init_state
        t = 0
        not_sprint_count = 0
        done = False
        while not done:
            action = self.agent.get_action(state)
            if action == 0:
                not_sprint_count = 0
            else:
                not_sprint_count += 1
            if not_sprint_count > 20:
                action = 0
                not_sprint_count = 0
                print("\\next")
            next_state, reward, done, _ = self.env.step(action)

            self.fit_agent(state, action, reward, done, next_state)

            state = next_state
            total_reward += reward

            t += 1
            if t == self.trajectory_max_len:
                break

        return total_reward

    def study_agent(self, episode_n):
        for episode in range(episode_n):
            state = self.env.reset()
            self.play_trajectory(state)
