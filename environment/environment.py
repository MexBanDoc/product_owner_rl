from environment.backlog_env import BacklogEnv
from environment.userstory_env import UserstoryEnv
from game.game import ProductOwnerGame
from game.game_constants import UserCardType
import torch
import numpy as np
from game.game_generators import get_buggy_game_1

BUG = UserCardType.BUG
TECH_DEBT = UserCardType.TECH_DEBT


class ProductOwnerEnv:
    IS_SILENT = False

    def __init__(self, userstory_env=None, backlog_env=None, with_sprint=True):
        self.game = ProductOwnerGame()
        self.backlog_env = BacklogEnv() if backlog_env is None else backlog_env
        self.backlog_env.with_sprint = with_sprint
        self.userstory_env = UserstoryEnv() if userstory_env is None else userstory_env

        self.meta_space_dim = 18

        self.state_dim = self.meta_space_dim + \
            self.userstory_env.userstory_space_dim + \
            self.backlog_env.backlog_space_dim

        self.with_sprint = with_sprint

        if with_sprint:
            self.state_dim += self.backlog_env.sprint_space_dim

        self.current_state = self._get_state()

        self.meta_action_dim = 7
        self.userstory_max_action_num = + \
            self.userstory_env.us_common_count + \
            self.userstory_env.us_bug_count + \
            self.userstory_env.us_td_count
        self.backlog_max_action_num = + \
            self.backlog_env.backlog_commons_count + \
            self.backlog_env.backlog_bugs_count + \
            self.backlog_env.backlog_tech_debt_count

        self.sprint_max_action_num = 0
        if with_sprint:
            self.sprint_max_action_num = + \
                self.backlog_env.sprint_commons_count + \
                self.backlog_env.sprint_bugs_count + \
                self.backlog_env.sprint_tech_debt_count
        self.action_n = self.meta_action_dim + \
            self.userstory_max_action_num + \
            self.backlog_max_action_num + \
            self.sprint_max_action_num

        self.actions = {
            0: self._perform_start_sprint_action,
            1: self._perform_decomposition,
            2: self._perform_release,
            3: self._perform_buy_robot,
            4: self._perform_buy_room,
            5: self._perform_statistical_research,
            6: self._perform_user_survey,
            "card": self._perform_action_card
        }

    def reset(self):
        self.game = ProductOwnerGame()
        self.current_state = self._get_state()
        return self.current_state

    def _get_state(self, in_tensor=False):
        context = self.game.context
        state = [
            context.current_sprint,
            context.get_money() / 10 ** 5,
            context.customers,
            context.get_loyalty(),
            context.credit / 10 ** 5,
            context.available_developers_count,
            context.current_rooms_counter,
            self.game.backlog.get_max_hours() - self.game.backlog.calculate_hours_sum(),
            context.blank_sprint_counter,
            context.is_new_game,
            self.game.backlog.can_start_sprint(),
            self.game.hud.release_available,
            self.game.userstories.release_available,
            self.game.userstories.statistical_research_available,
            self.game.userstories.user_survey_available,
            *self._get_completed_cards_count(),
            *self.userstory_env.encode(self.game.userstories.stories_list),
            *self.backlog_env.encode(self.game.backlog, context)
        ]
        assert len(state) == self.state_dim
        if in_tensor:
            return torch.tensor(state)
        else:
            return np.array(state, dtype=np.float32)

    def _get_completed_cards_count(self):
        completed_cards = self.game.completed_us
        completed_us_count, completed_bug_count, completed_td_count = 0, 0, 0
        for card_info in completed_cards:
            if card_info.card_type == BUG:
                completed_bug_count += 1
            elif card_info.card_type == TECH_DEBT:
                completed_td_count += 1
            else:
                completed_us_count += 1
        return completed_us_count, completed_bug_count, completed_td_count

    def step(self, action: int):
        # new_state, reward, done, info
        reward = 0
        credit_before = self.game.context.credit
        reward_bit = self._perform_action(action)
        reward += self._get_credit_reward(credit_before)
        reward += self._get_reward()
        reward += reward_bit
        self.current_state = self._get_state()
        return self.current_state, reward, self.game.context.done, None

    def _get_credit_reward(self, credit_before):
        credit_after = self.game.context.credit
        if credit_before > 0 and credit_after <= 0:
            return 10
        return 0

    def _get_reward(self):
        # sprint_penalty = +1
        # money_reward = self.game.context.get_money() / 10 ** 6
        done = self.game.context.done
        if done:
            if self.game.context.get_money() > 1e6:
                reward_for_endgame = 500
            else:
                reward_for_endgame = -50
        else:
            reward_for_endgame = 0
        return reward_for_endgame

    def _get_reward_for_starting_sprint(self, money_before, sprint_hours):
        money_after = self.game.context.get_money()
        base_reward = (money_after - money_before) / 1e4
        if base_reward < 0:
            return base_reward
        if len(self.game.backlog.sprint) > 0:
            return base_reward
        if sprint_hours > 0:
            return base_reward / 10
        else:
            return 0

    def _perform_start_sprint_action(self):
        if not self.game.backlog.can_start_sprint():
            self._log_start_sprint(False)
            return -10
        money_before = self.game.context.get_money()
        sprint_hours = self.game.backlog.calculate_hours_sum()
        self.game.backlog_start_sprint()
        reward = self._get_reward_for_starting_sprint(money_before, sprint_hours)
        self._log_start_sprint(True)

        return reward

    def _perform_decomposition(self) -> int:
        is_release_available = self.game.userstories.release_available
        if is_release_available:
            self.game.userstories_start_release()
            self._log_decomposition(True)
            return 0
        self._log_decomposition(False)
        return -10
    
    def _perform_release(self) -> int:
        is_release_available = self.game.hud.release_available
        if is_release_available:
            self.game.hud_release_product()
            # loyalty = self.game.context.get_loyalty()
            # customers = self.game.context.customers
            # return loyalty * customers * 3 / 10
            self._log_release(True)
            return 0
        self._log_release(False)
        return -10

    def _perform_buy_robot(self) -> int:
        room_num = self._get_min_not_full_room_number()
        if room_num == -1:
            self._log_buy(False)
            return -10
        worker_count_before = self.game.context.available_developers_count
        self.game.buy_robot(room_num)
        worker_count = self.game.context.available_developers_count
        if worker_count_before == worker_count:
            self._log_buy(False)
            return -10
        self._log_buy(True)
        return 0
    
    def _perform_buy_room(self) -> int:
        room_num = self._get_min_available_to_buy_room_number()
        if room_num == -1:
            self._log_buy(False)
            return -10
        worker_count_before = self.game.context.available_developers_count
        self.game.buy_room(room_num)
        worker_count = self.game.context.available_developers_count
        if worker_count_before == worker_count:
            self._log_buy(False)
            return -10
        self._log_buy(True)
        return 0
    
    def _perform_statistical_research(self) -> int:
        if not self.game.userstories.statistical_research_available:
            self._log_statistical_research(False)
            return -10
        stories_before = len(self.game.userstories.stories_list)
        self.game.press_statistical_research()
        stories_after = len(self.game.userstories.stories_list)
        if stories_before == stories_after:
            self._log_statistical_research(False)
            return -10
        self._log_statistical_research(True)
        return 0
    
    def _perform_user_survey(self) -> int:
        if not self.game.userstories.user_survey_available:
            self._log_user_survey(False)
            return -10
        stories_before = len(self.game.userstories.stories_list)
        self.game.press_user_survey()
        stories_after = len(self.game.userstories.stories_list)
        if stories_before == stories_after:
            self._log_user_survey(False)
            return -10
        self._log_user_survey(True)
        return 0
    
    def _perform_action(self, action: int):
        if action < self.meta_action_dim:
            return self.actions[action]()
        
        return self.actions["card"](action - self.meta_action_dim)

    def _perform_action_card(self, card_id: int) -> int:
        if card_id < self.userstory_max_action_num:
            return self._perform_action_userstory(card_id)
        
        card_id = card_id - self.userstory_max_action_num
        if card_id < self.backlog_max_action_num:
            return self._perform_action_backlog_card(card_id)
        
        card_id = card_id - self.backlog_max_action_num
        return self._perform_remove_sprint_card(card_id)

    def _perform_action_backlog_card(self, card_id: int) -> int:
        backlog_env = self.backlog_env
        card = self._get_card_of_unknown_type(backlog_env.backlog_commons,
                                              backlog_env.backlog_bugs,
                                              backlog_env.backlog_tech_debt,
                                              backlog_env.backlog_commons_count,
                                              backlog_env.backlog_bugs_count,
                                              card_id)

        if card is None:
            self._log_backlog_card(False)
            return -10

        hours_after_move = self.game.backlog.calculate_hours_sum() + card.info.hours
        if hours_after_move > self.game.backlog.get_max_hours():
            self._log_backlog_card(False)
            return -10

        self.game.move_backlog_card(card)
        self._log_backlog_card(True)
        return 0

    def _perform_action_userstory(self, card_id: int):
        us_env = self.userstory_env
        card = self._get_card_of_unknown_type(us_env.userstories_common,
                                              us_env.userstories_bugs,
                                              us_env.userstories_td,
                                              us_env.us_common_count,
                                              us_env.us_bug_count,
                                              card_id)
        if card is None or not self.game.userstories.available:
            self._log_us_card(False)
            return -10

        if not card.is_movable:
            self._log_us_card(False)
            return -1

        self.game.move_userstory_card(card)
        self._log_us_card(True)
        return 0

    def _perform_remove_sprint_card(self, card_id: int):
        backlog_env = self.backlog_env
        card = self._get_card_of_unknown_type(backlog_env.sprint_commons,
                                              backlog_env.sprint_bugs,
                                              backlog_env.sprint_tech_debt,
                                              backlog_env.sprint_commons_count,
                                              backlog_env.sprint_bugs_count,
                                              card_id)

        if card is None:
            self._log_sprint_card(False)
            return -10

        self.game.move_sprint_card(card)
        self._log_sprint_card(True)
        return -8

    def _get_card_of_unknown_type(self, commons, bugs, tech_debt,
                                  common_count, bug_count, card_id):
        card = self._get_card(commons, card_id)
        card_id = card_id - common_count
        if card is None:
            card = self._get_card(bugs, card_id)
        card_id = card_id - bug_count
        if card is None:
            card = self._get_card(tech_debt, card_id)

        return card

    def _get_card(self, sampled, index):
        if 0 <= index < len(sampled):
            return sampled[index]
        return None

    def _get_min_not_full_room_number(self):
        offices = self.game.office.offices
        for i in range(len(offices)):
            room = offices[i]
            if room.can_buy_robot:
                return i
        return -1

    def _get_min_available_to_buy_room_number(self):
        offices = self.game.office.offices
        for i in range(len(offices)):
            room = offices[i]
            if room.can_buy_room:
                return i
        return -1

    def _log_start_sprint(self, is_successful):
        if self.IS_SILENT:
            return
        print()
        if is_successful:
            money_after = self.game.context.get_money()
            loyalty = self.game.context.get_loyalty()
            customers = self.game.context.customers
            print(f"{money_after / 1e5:2.4f}, {loyalty:2.4f}, {customers:3.4f}")

    def _log_decomposition(self, is_successful):
        if self.IS_SILENT:
            return
        end = "♦" if is_successful else ""
        print("dec", end=end)

    def _log_release(self, is_successful):
        if self.IS_SILENT:
            return
        end = "♥" if is_successful else ""
        print("rel", end=end)

    def _log_buy(self, is_successful):
        if self.IS_SILENT:
            return
        end = "↓" if is_successful else ""
        print("buy", end=end)

    def _log_statistical_research(self, is_successful):
        if self.IS_SILENT:
            return
        end = "♣" if is_successful else ""
        print("stat", end=end)

    def _log_user_survey(self, is_successful):
        if self.IS_SILENT:
            return
        end = "♣" if is_successful else ""
        print("sur", end=end)

    def _log_backlog_card(self, is_successful):
        if self.IS_SILENT:
            return
        current_hours = self.game.backlog.calculate_hours_sum()
        max_sprint_hours = self.game.backlog.get_max_hours()
        end = f"{current_hours}/{max_sprint_hours}" if is_successful else ""
        print("b", end=end)

    def _log_us_card(self, is_successful):
        if self.IS_SILENT:
            return
        end = "♪" if is_successful else ""
        print("u", end=end)

    def _log_sprint_card(self, is_successful):
        if self.IS_SILENT:
            return
        end = "!" if is_successful else ""
        print("s", end=end)


class LoggingEnv(ProductOwnerEnv):
    def __init__(self, userstory_env=None, backlog_env=None):
        super().__init__(userstory_env, backlog_env)
        self.IS_SILENT = False

    def step(self, action: int):
        new_state, reward, done, info = super().step(action)
        print(action, reward)
        return new_state, reward, done, info


class BuggyProductOwnerEnv(ProductOwnerEnv):
    def __init__(self, userstory_env=None, backlog_env=None):
        super().__init__(userstory_env, backlog_env)
        self.game = get_buggy_game_1()
        self.current_state = self._get_state()
    
    def reset(self):
        self.game = get_buggy_game_1()
        self.current_state = self._get_state()
        return self.current_state
