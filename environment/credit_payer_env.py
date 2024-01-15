from environment.backlog_env import BacklogEnv
from environment.userstory_env import UserstoryEnv
from environment.environment import ProductOwnerEnv


class CreditPayerEnv(ProductOwnerEnv):
    def __init__(self, userstory_env=None, backlog_env=None, with_sprint=True):
        if userstory_env is None:
            userstory_env = UserstoryEnv(6, 0, 0)
        if backlog_env is None:
            backlog_env = BacklogEnv(20, 0, 0, 4, 0, 0)
        super().__init__(userstory_env, backlog_env, with_sprint)

    def step(self, action: int):
        context = self.game.context
        loyalty_before = context.get_loyalty()
        customers_before = context.customers

        new_state, reward, done, info = super().step(action)

        done = self.game.context.current_sprint == 35 or done
        reward += self._get_credit_payer_reward(loyalty_before, customers_before)

        return new_state, reward, done, info

    def _get_credit_payer_reward(self, loyalty_before, customers_before):
        context = self.game.context
        loyalty_after = context.get_loyalty()
        customers_after = context.customers

        potential_before = loyalty_before * customers_before
        potential_after = loyalty_after * customers_after
        difference = potential_after - potential_before

        reward = difference * 3

        return reward
