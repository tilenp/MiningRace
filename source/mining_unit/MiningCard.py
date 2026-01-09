from dataclasses import dataclass, field
from decimal import Decimal

from source.Constants import CARD_COST, CARD_MINES_BTC_PER_DAY, CARD_PROFIT_THRESHOLD, CARD_EXPENSES_PER_DAY
from source.mining_unit.MiningCardState import MiningCardState, Reserved, Active, Deactivated


@dataclass(eq=False)
class MiningCard:
    cost: Decimal = CARD_COST
    mines_btc_per_day: Decimal = CARD_MINES_BTC_PER_DAY
    state: MiningCardState = field(default_factory=lambda: Reserved(days_left=1))
    profit_threshold: Decimal = CARD_PROFIT_THRESHOLD

    def _handle_reserved_state(self, state: Reserved) -> None:
        # calculate number of days the card still needs to be in reserved state
        days_left = state.days_left - 1
        if days_left > 0:
            # still in reserved state period
            self.state = Reserved(days_left=days_left)
        else:
            # change state into active, mining starts next day
            self.state = Active(mined_btc=Decimal("0"))

    def _handle_active_state(self, state: Active) -> Decimal:
        # card's mining target
        mined_btc_target = (Decimal("1") + (self.profit_threshold / Decimal("100"))) * self.cost
        # amount card can still mine
        diff_to_mining_target = max(Decimal("0"), mined_btc_target - state.mined_btc)
        # calculate how much to mine today
        mined_today = min(self.mines_btc_per_day, diff_to_mining_target)
        # add today's mining to accumulated mining
        mined_btc = state.mined_btc + mined_today
        # update state
        if mined_btc < mined_btc_target:
            self.state = Active(mined_btc=mined_btc)
        else:
            self.state = Deactivated()
        return mined_today

    def get_daily_mining_amount(self) -> Decimal:
        match self.state:
            case Reserved(days_left=days) as reserved:
                self._handle_reserved_state(state=reserved)
                return Decimal("0")
            case Active(mined_btc=btc) as active:
                mined_today = self._handle_active_state(state=active)
                return mined_today
            case _:
                raise RuntimeError(f"Mine called on a card in state: {self.state}")
