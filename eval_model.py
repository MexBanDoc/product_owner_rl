from algorithms.deep_q_networks import DoubleDQN
from environment import CreditPayerEnv, TutorialSolverEnv, ProductOwnerEnv
import numpy as np
from pipeline.study_agent import load_dqn_agent, save_dqn_agent
import matplotlib.pyplot as plt

SMALL_SIZE = 16
MEDIUM_SIZE = 20
BIGGER_SIZE = 22

plt.rc('font', size=MEDIUM_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title


def eval_agents_trajectory(env: ProductOwnerEnv, agents, is_silent):
    env.reset()

    stage = len(agents)
    full_reward = 0

    if stage == 1:
        _, reward = play_tutorial(env, agents[0], is_silent)
        full_reward = reward
        print(f"reward tutorial: {reward},"
              f"current sprint: {env.game.context.current_sprint}")
    if stage == 2:
        _, reward = play_tutorial(env, agents[0], is_silent)
        _, credit_reward = play_credit_payment(env, agents[1], is_silent)
        full_reward = reward + credit_reward
        print(f"reward tutorial: {reward},"
              f"reward credit: {credit_reward},"
              f"full reward: {full_reward},"
              f"current sprint: {env.game.context.current_sprint}")
    if stage == 3:
        _, reward = play_tutorial(env, agents[0], is_silent)
        _, credit_reward = play_credit_payment(env, agents[1], is_silent, with_end=False)
        _, credit_reward_end = play_credit_payment(env, agents[2], is_silent, with_end=True)
        full_reward = reward + credit_reward + credit_reward_end
        print(f"reward tutorial: {reward},"
              f"reward credit: {credit_reward},"
              f"reward credit end: {credit_reward_end},"
              f"full reward: {full_reward},"
              f"current sprint: {env.game.context.current_sprint}")
    if stage == 4:
        _, reward = play_tutorial(env, agents[0], is_silent)
        _, credit_reward = play_credit_payment(env, agents[1], is_silent, with_end=False)
        _, credit_reward_end = play_credit_payment(env, agents[2], is_silent, with_end=True)
        _, end_reward = play_some_stage(env, env, agents[3], "end", is_silent)
        full_reward = reward + credit_reward + credit_reward_end + end_reward
        print(f"reward tutorial: {reward},"
              f"reward credit: {credit_reward},"
              f"reward credit end: {credit_reward_end},"
              f"end reward: {end_reward},"
              f"full reward: {full_reward},"
              f"current sprint: {env.game.context.current_sprint}")
        return env.game.context.is_victory, full_reward, env.game.context.get_money(), env.game.context.current_sprint
    return full_reward, env.game.context.current_sprint, env.game.context.get_loyalty(), env.game.context.customers, env.game.context.get_money()


def eval_some_model(env: ProductOwnerEnv, agents, repeat_count: int, is_silent: bool):
    rewards = []
    sprints = []
    loyalties = []
    customers_ep = []
    moneys = []
    wins = []

    for i in range(repeat_count):
        if len(agents) < 4:
            reward, sprint, loyalty, customers, money = eval_agents_trajectory(env, agents, is_silent)
            rewards.append(reward)
            sprints.append(sprint)
            loyalties.append(loyalty)
            customers_ep.append(customers)
            moneys.append(money)
        else:
            is_victory, full_reward, money, sprint = eval_agents_trajectory(env, agents, is_silent)
            rewards.append(full_reward)
            wins.append(int(is_victory))
            moneys.append(money)
            sprints.append(sprint)

    if len(agents) < 4:
        customers_ep = np.array(customers_ep)
        loyalties = np.array(loyalties)

        return (np.median(rewards),
                ("sprints", sprints),
                ("loyalty", loyalties),
                ("customers", customers_ep),
                ("potential money", customers_ep * loyalties * 300),
                ("money", moneys))
    else:
        return (np.median(rewards),
                ("wins", wins),
                ("money", moneys),
                ("sprints", sprints))


def play_tutorial(main_env, tutorial_agent, is_silent=True):
    env = TutorialSolverEnv(with_sprint=main_env.with_sprint)
    return play_some_stage(main_env, env, tutorial_agent, "tutorial end", is_silent)


def play_credit_payment(main_env, credit_agent, is_silent=True, with_end=False):
    env = CreditPayerEnv(with_sprint=main_env.with_sprint, with_end=with_end)
    return play_some_stage(main_env, env, credit_agent, "credit end", is_silent)


def play_some_stage(main_env: ProductOwnerEnv, player: ProductOwnerEnv, agent, line,
                    is_silent=True):
    player.IS_SILENT = is_silent
    player.game = main_env.game
    done = main_env.game.context.get_money() < 0
    state = player._get_state()
    total_reward = 0

    while not done:
        action = agent.get_action(state)
        state, reward, done, _ = player.step(action)

        total_reward += reward

    print(line)

    return main_env._get_state(), total_reward


if __name__ == "__main__":
    env = ProductOwnerEnv(with_sprint=False)
    env.IS_SILENT = True
    agent_tutorial = load_dqn_agent("./models/tutorial_agent.pt")
    agent_credit = load_dqn_agent("./models/credit_start_agent.pt")
    agent_credit_end = load_dqn_agent("./models/credit_end_agent.pt")
    agent_end = load_dqn_agent("./models/end_agent.pt")

    reses = eval_some_model(env, [agent_tutorial, agent_credit, agent_credit_end, agent_end],
                            1000, is_silent=True)
    print(reses[0])
    reses = reses[1:]

    for i in range(0, len(reses)):
        elems = reses[i]
        plt.plot(elems[1], '.')
        plt.xlabel("Trajectory")
        plt.ylabel(elems[0])
        plt.show()

    if len(reses) == 3:
        wins = np.array(reses[0][1])
        print(f"wins:{len(wins[wins == 1])}")
        trajectories = np.arange(len(wins), dtype=np.int32)
        money = np.array(reses[1][1])
        print(f"losses: {len(money[money < 0])}")
        sprints = np.array(reses[2][1])

        plt.plot(trajectories[wins == 1], money[wins == 1], '.', label="win", color="red")
        plt.plot(trajectories[wins == 0], money[wins == 0], '.', label="other", color="blue")
        plt.xlabel("Trajectory")
        plt.ylabel("money")
        plt.legend()
        plt.show()

        plt.plot(trajectories[wins == 1], sprints[wins == 1], '.', label="win", color="red")
        plt.plot(trajectories[wins == 0], sprints[wins == 0], '.', label="other", color="blue")
        plt.xlabel("Trajectory")
        plt.ylabel("sprints")
        plt.legend()
        plt.show()
