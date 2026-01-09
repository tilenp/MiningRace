from dataclasses import dataclass, field
from decimal import Decimal

from source.Constants import CARD_NUM_MINING_DAYS
from source.licence.LicenceState import LicenceState, Valid, Expired
from source.mining_unit.MiningCard import MiningCard
from source.mining_unit.MiningCardState import Deactivated


@dataclass(eq=False)
class Licence:
    cost: Decimal
    max_num_cards: int
    state: LicenceState = field(default_factory=lambda: Valid(days_left=365))
    cards: set[MiningCard] = field(default_factory=set)
    card_num_mining_days: int = CARD_NUM_MINING_DAYS

    def can_add_mining_card(self) -> bool:
        # can the licence accept another card
        max_num_cards_reached = len(self.cards) >= self.max_num_cards
        # will a new card be able to mine a profit until the licence expires
        enough_days_left = isinstance(self.state, Valid) and self.state.days_left > self.card_num_mining_days
        return not max_num_cards_reached and enough_days_left

    def add_mining_card(self, mining_card: MiningCard) -> None:
        if self.can_add_mining_card():
            self.cards.add(mining_card)
        else:
            raise RuntimeError(f"Should not add a new card")

    def _remove_deactivated_mining_cards(self) -> None:
        # collect deactivated cards
        deactivated_cards = {card for card in self.cards if isinstance(card.state, Deactivated)}
        # remove deactivated cards
        self.cards -= deactivated_cards

    def _collect_btc_from_cards(self) -> Decimal:
        # collect mined BTC from all cards
        mined_today = Decimal("0")
        for card in self.cards:
            mined_today += card.get_daily_mining_amount()
        return mined_today

    def _acknowledge_mining_day(self, state: Valid) -> None:
        valid_for_days = state.days_left - 1
        if valid_for_days > 0:
            self.state = Valid(days_left=valid_for_days)
        else:
            self.state = Expired()

    def get_daily_mining_amount(self) -> Decimal:
        state = self.state
        # should not be called on expired licence
        if not isinstance(state, Valid):
            raise RuntimeError(f"Only valid licence can mine")
        # collect BTC all cards have mined today
        mined_today = self._collect_btc_from_cards()
        # remove deactivated cards
        self._remove_deactivated_mining_cards()
        # acknowledge mining day
        self._acknowledge_mining_day(state=state)
        # return mined BTC
        return mined_today
