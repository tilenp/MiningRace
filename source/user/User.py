from dataclasses import dataclass, field
from decimal import Decimal

from source.Constants import CARD_COST
from source.licence.Licence import Licence
from source.licence.LicenceBuilder import LicenceType, LicenceBuilder
from source.licence.LicenceState import Expired
from source.mining_unit.MiningCard import MiningCard


@dataclass
class User:
    licences: set[Licence] = field(default_factory=set)
    btc_amount: Decimal = Decimal("0")

    def _remove_expired_licences(self) -> None:
        # collect expired licences
        expired_licences = {licence for licence in self.licences if isinstance(licence.state, Expired)}
        # remove expired licences
        self.licences -= expired_licences

    def mine_for_day(self) -> None:
        # mine with each licence
        for licence in self.licences:
            self.btc_amount += licence.get_daily_mining_amount()
        # remove expired licences
        self._remove_expired_licences()

    def add_new_licence_with_cards(self, licence_type: LicenceType, num_cards: int) -> None:
        # configure a builder to construct a licence with initial cards
        licence_builder = LicenceBuilder(licence_type=licence_type).set_num_cards(num_cards=num_cards)
        # get a licence with cards and cost
        licence, cost = licence_builder.build()
        # keep buying packages until there is enough BTC
        while self.btc_amount >= cost:
            # pay for licence with cards
            self.btc_amount -= cost
            # add licence with cards to user
            self.licences.add(licence)
            # build new licence with cards package
            licence, cost = licence_builder.build()

    def add_new_cards(self) -> int:
        num_cards_added = 0
        while self.btc_amount >= CARD_COST:
            # Find the best licence to add a card:
            # - can_add_mining_card() is True
            # - has the largest remaining capacity
            licence = max(
                (licence for licence in self.licences if licence.can_add_mining_card()),
                key=lambda l: l.max_num_cards - len(l.cards),
                default=None,
            )
            # skip adding cards if no licence can add mining card
            if licence is None:
                break
            # pay for card
            self.btc_amount -= CARD_COST
            # Add card
            licence.cards.add(MiningCard())
            # acknowledge card added
            num_cards_added = + 1
        # return number of added cards
        return num_cards_added
