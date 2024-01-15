import unittest
from environment.backlog_env import BacklogEnv
from game.backlog.backlog import Backlog
from game.backlog_card.backlog_card import Card
from game.backlog_card.card_info import CardInfo
from game.game_constants import UserCardType
from game.game_variables import GlobalContext
from game.userstory_card.userstory_card_info import UserStoryCardInfo
from game.game_colors import ColorStorage


class TestBacklogEnv(unittest.TestCase):
    def setUp(self):
        self.color_storage = ColorStorage()
        self.color_storage.get_unused_color = lambda x: 1
        self.context = GlobalContext()
        self.backlog = Backlog(self.context)
        self.env = BacklogEnv(backlog_commons_count=1, backlog_bugs_count=1,
                              backlog_tech_debt_count=1,
                              sprint_commons_count=1, sprint_bugs_count=1, sprint_tech_debt_count=1)
        self.size = self.env.backlog_space_dim + self.env.sprint_space_dim

    def test_encode_empty_backlog(self):
        encoding = self.env.encode(self.backlog, self.context)

        self.assertSequenceEqual(encoding, [0] * self.size)

    def test_encode_full_backlog(self):
        queue = self.backlog.backlog
        self.fill_queue(queue)

        encoding = self.env.encode(self.backlog, self.context)

        self.assertSequenceEqual(encoding, [1, 2, 1, 10, 2, 3, 10, 3, 4, 10,
                                            0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

    def test_encode_full_sprint(self):
        self.fill_queue(self.backlog.sprint)
        encoding = self.env.encode(self.backlog, self.context)

        self.assertSequenceEqual(encoding, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                            1, 2, 1, 10, 2, 3, 10, 3, 4, 10])

    def fill_queue(self, queue):
        for i in range(self.env.backlog_commons_count):
            card = Card()
            card_info = CardInfo(1, None, 1, "S", UserCardType.S)
            card_info.hours += 1
            card.add_data(card_info)
            queue.append(card)
        self.context.current_stories[1] = UserStoryCardInfo("S", 0, self.color_storage)

        for i in range(self.env.backlog_bugs_count):
            card = Card()
            card_info = CardInfo(2, None, 2, "Bug", UserCardType.BUG)
            card_info.hours += 1
            card.add_data(card_info)
            queue.append(card)
        self.context.current_stories[2] = UserStoryCardInfo("Bug", 0, self.color_storage)

        for i in range(self.env.backlog_tech_debt_count):
            card = Card()
            card_info = CardInfo(3, None, 3, "TechDebt", UserCardType.TECH_DEBT)
            card_info.hours += 1
            card.add_data(card_info)
            queue.append(card)
        self.context.current_stories[3] = UserStoryCardInfo("TechDebt", 0, self.color_storage)