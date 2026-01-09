from dataclasses import dataclass


class LicenceState:
    pass


@dataclass
class Valid(LicenceState):
    days_left: int


class Expired(LicenceState):
    pass
