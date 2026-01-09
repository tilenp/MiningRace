from dataclasses import dataclass
from decimal import Decimal


class MiningCardState:
    pass


@dataclass
class Reserved(MiningCardState):
    days_left: int


@dataclass
class Active(MiningCardState):
    mined_btc: Decimal


class Deactivated(MiningCardState):
    pass