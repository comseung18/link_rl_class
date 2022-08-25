from practice_2_3_cliff_utils import CliffGridWorld, GRID_HEIGHT, GRID_WIDTH, TERMINAL_STATES, CLIFF_STATES, START_STATE
import numpy as np
import matplotlib.pyplot as plt
import random

# 탐색 확률
EPSILON = 0.1

# 스텝 사이즈
ALPHA = 0.5

# 감가율
GAMMA = 1.0


# 비어있는 행동 가치 테이블을 0~1 사이의 임의의 값으로 초기화하며 생성함
def generate_initial_q_value(env):
    q_value = np.zeros((GRID_HEIGHT, GRID_WIDTH, env.NUM_ACTIONS))

    for i in range(GRID_HEIGHT):
        for j in range(GRID_WIDTH):
            if (i, j) not in TERMINAL_STATES:
                for action in env.ACTIONS:
                    q_value[i, j, action] = random.random()
    return q_value


# 모든 상태에서 수행 가능한 행동에 맞춰 임의의 정책을 생성함
# 초기에 각 행동의 선택 확률은 모두 같음
def generate_initial_random_policy(env):
    policy = dict()

    for i in range(GRID_HEIGHT):
        for j in range(GRID_WIDTH):
            if (i, j) not in TERMINAL_STATES:
                actions = []
                action_probs = []
                for action in env.ACTIONS:
                    actions.append(action)
                    action_probs.append(0.25)

                policy[(i, j)] = (actions, action_probs)

    return policy


# epsilon-탐욕적 정책 갱신
def update_epsilon_greedy_policy(env, state, q_value, policy):
    max_prob_actions = [action_ for action_, value_
                        in enumerate(q_value[state[0], state[1], :]) if
                        value_ == np.max(q_value[state[0], state[1], :])]

    actions = []
    action_probs = []
    for action in env.ACTIONS:
        actions.append(action)
        if action in max_prob_actions:
            action_probs.append(
                (1 - EPSILON) / len(max_prob_actions) \
                + EPSILON / env.NUM_ACTIONS
            )
        else:
            action_probs.append(
                EPSILON / env.NUM_ACTIONS
            )

    policy[state] = (actions, action_probs)


def sarsa(env, q_value, policy, step_size=ALPHA):
    episode_reward = 0.0
    state = env.reset()
    actions, prob = policy[state]
    action = np.random.choice(actions, size=1, p=prob)[0]
    done = False
    while not done:
        next_state, reward, done, _ = env.step(action)
        episode_reward += reward

        # Q-테이블 갱신
        if done:
            q_value[state[0], state[1], action] += step_size * \
                                                   (reward - q_value[state[0], state[1], action])

            update_epsilon_greedy_policy(env, state, q_value, policy)
        else:
            next_actions, prob = policy[next_state]

            next_action = np.random.choice(next_actions, size=1, p=prob)[0]

            next_q = q_value[next_state[0], next_state[1], next_action]

            q_value[state[0], state[1], action] += step_size * \
                                                   (reward + GAMMA * next_q - q_value[state[0], state[1], action])

            update_epsilon_greedy_policy(env, state, q_value, policy)

            state = next_state
            action = next_action

    return episode_reward


def q_learning(env, q_value, policy, step_size=ALPHA):
    episode_reward = 0.0
    state = env.reset()
    done = False
    while not done:
        actions, prob = policy[state]
        action = np.random.choice(actions, size=1, p=prob)[0]
        next_state, reward, done, _ = env.step(action)
        # print(state, actions, prob, action, next_state, reward)
        episode_reward += reward

        # Q-테이블 갱신
        if done:
            q_value[state[0], state[1], action] += step_size * \
                                                   (reward - q_value[state[0], state[1], action])

            update_epsilon_greedy_policy(env, state, q_value, policy)
        else:
            # 새로운 상태에 대한 기대값 계산
            max_next_q = np.max(q_value[next_state[0], next_state[1], :])

            q_value[state[0], state[1], action] += step_size * \
                                                   (reward + GAMMA * max_next_q - q_value[state[0], state[1], action])

            update_epsilon_greedy_policy(env, state, q_value, policy)

            state = next_state

    return episode_reward


def expected_sarsa(env, q_value, policy, step_size=ALPHA):
    episode_reward = 0.0
    state = env.reset()
    done = False
    while not done:
        actions, prob = policy[state]
        action = np.random.choice(actions, size=1, p=prob)[0]
        next_state, reward, done, _ = env.step(action)
        episode_reward += reward

        # Q-테이블 갱신
        if done:
            q_value[state[0], state[1], action] += step_size * \
                                                   (reward - q_value[state[0], state[1], action])

            update_epsilon_greedy_policy(env, state, q_value, policy)
        else:
            # 새로운 상태에 대한 기대값 계산
            expected_next_q = 0.0
            for action_ in env.ACTIONS:
                action_prob = policy[next_state][1]
                expected_next_q += action_prob[action_] * \
                                   q_value[next_state[0], next_state[1], action_]

            q_value[state[0], state[1], action] += step_size * \
                                                   (reward + GAMMA * expected_next_q - q_value[
                                                       state[0], state[1], action])

            update_epsilon_greedy_policy(env, state, q_value, policy)

            state = next_state

    return episode_reward


# print optimal policy
def print_optimal_policy(env, q_value):
    optimal_policy = []
    for i in range(0, GRID_HEIGHT):
        optimal_policy.append([])
        for j in range(0, GRID_WIDTH):
            if (i, j) in TERMINAL_STATES:
                optimal_policy[-1].append('G')
                continue

            if (i, j) in CLIFF_STATES:
                optimal_policy[-1].append('-')
                continue

            best_action = np.argmax(q_value[i, j, :])
            if best_action == env.ACTION_UP:
                optimal_policy[-1].append('U')
            elif best_action == env.ACTION_DOWN:
                optimal_policy[-1].append('D')
            elif best_action == env.ACTION_LEFT:
                optimal_policy[-1].append('L')
            elif best_action == env.ACTION_RIGHT:
                optimal_policy[-1].append('R')

    for row in optimal_policy:
        print(row)
    print()


# 최대 에피소드
MAX_EPISODES = 500

# 총 실험 횟수 (성능에 대한 평균을 구하기 위함)
TOTAL_RUNS = 10

def td_comparison(env):
    rewards_expected_sarsa = np.zeros(MAX_EPISODES)
    rewards_sarsa = np.zeros(MAX_EPISODES)
    rewards_q_learning = np.zeros(MAX_EPISODES)

    # Q-Table 변수 선언
    q_table_sarsa = None
    q_table_q_learning = None
    q_table_expected_sarsa = None

    for run in range(TOTAL_RUNS):
        print("runs: {0}".format(run))

        # 초기 Q-Table 생성
        q_table_sarsa = generate_initial_q_value(env)
        q_table_q_learning = generate_initial_q_value(env)
        q_table_expected_sarsa = generate_initial_q_value(env)

        # 초기 임의 정책 생성
        policy_sarsa = generate_initial_random_policy(env)
        policy_q_learning = generate_initial_random_policy(env)
        policy_expected_sarsa = generate_initial_random_policy(env)

        for episode in range(MAX_EPISODES):
            rewards_sarsa[episode] += sarsa(
                env, q_table_sarsa, policy_sarsa
            )
            rewards_q_learning[episode] += q_learning(
                env, q_table_q_learning, policy_q_learning
            )
            rewards_expected_sarsa[episode] += expected_sarsa(
                env, q_table_expected_sarsa, policy_expected_sarsa
            )

    # 총 10번 수행에 대해 평균 계산
    rewards_sarsa /= TOTAL_RUNS
    rewards_q_learning /= TOTAL_RUNS
    rewards_expected_sarsa /= TOTAL_RUNS

    # 그래프 출력
    plt.plot(
        rewards_sarsa, linestyle='-',
        color='darkorange', label='SARSA'
    )
    plt.plot(
        rewards_q_learning, linestyle=':',
        color='green', label='Q-Learning'
    )
    plt.plot(
        rewards_expected_sarsa, linestyle='-.',
        color='dodgerblue', label='Expected SARSA'
    )

    plt.xlabel('Episodes')
    plt.ylabel('Episode rewards')
    plt.ylim([-100, 0])
    plt.legend()

    #plt.savefig('images/cliff_td_comparison.png')
    plt.show()
    plt.close()

    # display optimal policy
    print()

    print('[SARSA의 학습된 Q-Table 기반 탐욕적 정책]')
    print_optimal_policy(env, q_table_sarsa)

    print('[Q-Learning의 수렴된 Q-Table 기반 탐욕적 정책]')
    print_optimal_policy(env, q_table_q_learning)

    print('[기대값 기반 SARSA의 수렴된 Q-Table 기반 탐욕적 정책]')
    print_optimal_policy(env, q_table_expected_sarsa)


def cliff_td_comparison_main():
    env = CliffGridWorld(
        height=GRID_HEIGHT,
        width=GRID_WIDTH,
        start_state=START_STATE,
        terminal_states=TERMINAL_STATES,
        transition_reward=-1.0,
        terminal_reward=-1.0,
        outward_reward=-1.0,
        cliff_states_info=[(s, START_STATE, -100.0) for s in CLIFF_STATES]
    )

    td_comparison(env)


if __name__ == '__main__':
    cliff_td_comparison_main()