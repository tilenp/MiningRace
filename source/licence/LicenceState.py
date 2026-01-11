from dataclasses import dataclass


class LicenceState:
    pass


@dataclass
class Valid(LicenceState):
    # track how many days are left until the licence expires
    days_left: int


class Expired(LicenceState):
    pass
