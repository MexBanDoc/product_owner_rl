import os
import matplotlib.pyplot as plt

from pipeline.study_agent import load_dqn_agent
from pipeline.aggregator_study import AggregatorStudy
from algorithms.deep_q_networks import DQN, DoubleDQN
from environment import CreditPayerEnv, TutorialSolverEnv, ProductOwnerEnv

if __name__ == "__main__":
    env = ProductOwnerEnv(with_sprint=False)
    state_dim = env.state_dim
    action_n = env.action_n

    trajectory_max_len = -1
    episode_n = 1000

    # epsilon_decrease = 1 / (trajectory_max_len * episode_n)
    epsilon_decrease = 1e-4

    agent_tutorial = load_dqn_agent("./models/tutorial_agent.pt")

    agent = DoubleDQN(state_dim, action_n, tau=0.001, epsilon_decrease=epsilon_decrease)
    agent_credit_start = load_dqn_agent("./models/credit_start_agent.pt")
    agent_credit_end = load_dqn_agent("./models/credit_end_agent.pt")

    study = AggregatorStudy(env, agents=[agent_tutorial, agent_credit_start,
                                         agent_credit_end, agent],
                            trajectory_max_len=trajectory_max_len, save_rate=100)

    try:
        study.study_agent(episode_n + 100)
    except KeyboardInterrupt:
        pass

    rewards = study.rewards_log

    os.makedirs('figures', exist_ok=True)

    plt.plot(rewards, '.')
    plt.xlabel("Trajectory")
    plt.ylabel('Reward')
    plt.savefig('figures/rewards.png')
    plt.show()

    plt.plot(study.sprints_log, '.')
    plt.title('Sprints count')
    plt.xlabel("Trajectory")
    plt.ylabel("Sprint")
    plt.savefig('figures/sprints.png')
    plt.show()

