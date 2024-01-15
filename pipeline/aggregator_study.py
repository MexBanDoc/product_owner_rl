from pipeline.logging_study import LoggingStudy
from environment import TutorialSolverEnv, CreditPayerEnv, ProductOwnerEnv


class AggregatorStudy(LoggingStudy):
    def __init__(self, env, agents, trajectory_max_len, save_rate=100) -> None:
        assert 0 < len(agents) < 4
        self.stage = len(agents)
        if self.stage == 1:
            assert isinstance(env, TutorialSolverEnv)
        if self.stage == 2:
            assert isinstance(env, CreditPayerEnv)
        if self.stage == 3:
            assert isinstance(env, ProductOwnerEnv)

        self.agents = agents
        super().__init__(env, agents[-1], trajectory_max_len, save_rate)

    def play_trajectory(self, init_state):
        if self.stage == 1:
            return super().play_trajectory(init_state)
        if self.stage == 2:
            tutorial_agent = self.agents[0]
            state, reward, failed = self.play_tutorial(tutorial_agent)
            if failed:
                return reward
            reward += super().play_trajectory(state)
            print(f"full total_reward: {reward}")
            return reward
        if self.stage == 3:
            tutorial_agent = self.agents[0]
            credit_agent = self.agents[1]
            state, reward, failed = self.play_tutorial(tutorial_agent)
            if failed:
                return reward
            state, credit_reward, failed = self.play_credit_payment(credit_agent)
            if failed:
                return reward
            reward += credit_reward
            reward += super().play_trajectory(state)
            print(f"full total_reward: {reward}")
            return reward

    def play_tutorial(self, tutorial_agent):
        env = TutorialSolverEnv(with_sprint=self.env.with_sprint)
        env.game = self.env.game
        done = not self.env.game.context.is_new_game
        state = env._get_state()
        total_reward = 0

        while not done:
            action = tutorial_agent.get_action(state)
            state, reward, done, _ = env.step(action)

            total_reward += reward

        print("tutorial end")
        if env.game.context.get_money() < 0:
            print("tutorial failed")

        return self.env._get_state(), total_reward, env.game.context.get_money() < 0

    def play_credit_payment(self, credit_agent):
        env = CreditPayerEnv(with_sprint=self.env.with_sprint)
        env.game = self.env.game
        done = self.env.game.context.current_sprint == 35
        state = env._get_state()
        total_reward = 0

        while not done:
            action = credit_agent.get_action(state)
            state, reward, done, _ = env.step(action)

            total_reward += reward

        print("credit end")
        if env.game.context.get_money() < 0:
            print("credit failed")

        return self.env._get_state(), total_reward, env.game.context.get_money() < 0
