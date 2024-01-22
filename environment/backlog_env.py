from game.backlog.backlog import Backlog
from game.backlog_card.backlog_card import Card
from game.common_methods import sample_n_or_less, sample_n_or_zero
from game.game_constants import UserCardType


from typing import List, Tuple

from game.game_variables import GlobalContext

BUG = UserCardType.BUG
TECH_DEBT = UserCardType.TECH_DEBT

BACKLOG_COMMON_FEATURE_COUNT = 7
BACKLOG_BUG_FEATURE_COUNT = 3
BACKLOG_TECH_DEBT_FEATURE_COUNT = 3


def split_cards_in_types(cards: List[Card]):
    commons = []
    bugs = []
    tech_debts = []
    for card in cards:
        card_info = card.info
        if card_info.card_type == BUG:
            bugs.append(card)
        elif card_info.card_type == TECH_DEBT:
            tech_debts.append(card)
        else:
            commons.append(card)

    return commons, bugs, tech_debts


class BacklogEnv:
    def __init__(self, backlog_commons_count=20, backlog_bugs_count=5, backlog_tech_debt_count=1,
                 sprint_commons_count=4, sprint_bugs_count=1, sprint_tech_debt_count=1) -> None:
        self.backlog_commons_count = backlog_commons_count
        self.backlog_bugs_count = backlog_bugs_count
        self.backlog_tech_debt_count = backlog_tech_debt_count

        self.sprint_commons_count = sprint_commons_count
        self.sprint_bugs_count = sprint_bugs_count
        self.sprint_tech_debt_count = sprint_tech_debt_count

        self.backlog_space_dim = self.backlog_commons_count * BACKLOG_COMMON_FEATURE_COUNT + \
            self.backlog_bugs_count * BACKLOG_BUG_FEATURE_COUNT + \
            self.backlog_tech_debt_count * BACKLOG_TECH_DEBT_FEATURE_COUNT

        self.sprint_space_dim = self.sprint_commons_count * BACKLOG_COMMON_FEATURE_COUNT + \
            self.sprint_bugs_count * BACKLOG_BUG_FEATURE_COUNT + \
            self.sprint_tech_debt_count * BACKLOG_TECH_DEBT_FEATURE_COUNT

        self.backlog_commons = []
        self.backlog_bugs = []
        self.backlog_tech_debt = []

        self.sprint_commons = []
        self.sprint_bugs = []
        self.sprint_tech_debt = []

        self.with_sprint = True

    def _set_backlog_cards(self, commons, bugs, tech_debt):
        self.backlog_commons = commons
        self.backlog_bugs = bugs
        self.backlog_tech_debt = tech_debt

    def _set_sprint_cards(self, commons, bugs, tech_debt):
        self.sprint_commons = commons
        self.sprint_bugs = bugs
        self.sprint_tech_debt = tech_debt

    def encode(self, backlog: Backlog, context) -> List[int]:
        counts = (self.backlog_commons_count,
                  self.backlog_bugs_count, self.backlog_tech_debt_count)
        backlog_encoding = self._encode_queue(
            backlog.backlog, counts, self._set_backlog_cards, context)
        assert len(backlog_encoding) == self.backlog_space_dim

        sprint_encoding = []

        if self.with_sprint:
            counts = (self.sprint_commons_count, self.sprint_bugs_count,
                      self.sprint_tech_debt_count)
            sprint_encoding = self._encode_queue(
                backlog.sprint, counts, self._set_sprint_cards, context)
            assert len(sprint_encoding) == self.sprint_space_dim

        return backlog_encoding + sprint_encoding

    def _encode_queue(self, cards: List[Card], counts: Tuple[int, int, int], setter, context):
        commons, bugs, tech_debt = split_cards_in_types(cards)
        commons_count, bugs_count, tech_debt_count = counts

        commons = sample_n_or_zero(commons, commons_count)
        bugs = sample_n_or_zero(bugs, bugs_count)
        tech_debt = sample_n_or_zero(tech_debt, tech_debt_count)
        setter(commons, bugs, tech_debt)

        commons_len = BACKLOG_COMMON_FEATURE_COUNT * commons_count
        commons_encoding = self._encode_cards(
            commons, self._encode_common_card, commons_len, context)

        bugs_len = BACKLOG_BUG_FEATURE_COUNT * bugs_count
        bugs_encoding = self._encode_cards(bugs, self._encode_bug, bugs_len, context)

        tech_debt_len = BACKLOG_TECH_DEBT_FEATURE_COUNT * tech_debt_count
        tech_debt_encoding = self._encode_cards(
            tech_debt, self._encode_tech_debt, tech_debt_len, context)

        encoding = commons_encoding + bugs_encoding + tech_debt_encoding

        return encoding

    def _encode_cards(self, cards, encoder, result_len, context) -> List[int]:
        result = []
        for card in cards:
            result.extend(encoder(card, context))
        padding = result_len - len(result)
        result.extend([0] * padding)
        return result

    def _encode_common_card(self, card: Card, context: GlobalContext) -> List[int]:
        card_info = card.info
        us_card_info = context.current_stories[card_info.us_id]
        encoded = [card_info.base_hours,
                   card_info.hours,
                   card_info.card_type.value,
                   10 * (1 - us_card_info.completed_part),
                   us_card_info.loyalty,
                   us_card_info.customers_to_bring,
                   context.current_sprint - us_card_info.spawn_sprint]
        assert len(encoded) == BACKLOG_COMMON_FEATURE_COUNT
        return encoded

    def _encode_bug(self, card: Card, context: GlobalContext) -> List[int]:
        card_info = card.info
        us_card_info = context.current_stories[card_info.us_id]
        encoded = [card_info.base_hours, card_info.hours,
                   10 * (1 - us_card_info.completed_part)]
        assert len(encoded) == BACKLOG_BUG_FEATURE_COUNT
        return encoded

    def _encode_tech_debt(self, card: Card, context: GlobalContext) -> List[int]:
        card_info = card.info
        us_card_info = context.current_stories[card_info.us_id]
        encoded = [card_info.base_hours, card_info.hours,
                   10 * (1 - us_card_info.completed_part)]
        assert len(encoded) == BACKLOG_TECH_DEBT_FEATURE_COUNT
        return encoded
