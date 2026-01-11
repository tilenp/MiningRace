from dataclasses import dataclass
from decimal import Decimal


class MiningCardState:
    pass


@dataclass
class Reserved(MiningCardState):
    # track days to stay in reserved state
    days_left: int


@dataclass
class Active(MiningCardState):
    # track accumulated BTC the card has mined over its lifetime
    mined_btc: Decimal


class Deactivated(MiningCardState):
    pass