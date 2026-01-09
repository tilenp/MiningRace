from decimal import Decimal
from enum import Enum

from source.Constants import PRIME_LICENCE_COST, PRIME_MAX_NUM_CARDS, PLATINUM_LICENCE_COST, PLATINUM_MAX_NUM_CARDS, \
    CARD_COST
from source.licence.Licence import Licence
from source.mining_unit.MiningCard import MiningCard


class LicenceType(Enum):
    PRIME = 1
    PLATINUM = 2


class LicenceBuilder:

    def __init__(self, licence_type: LicenceType):
        self.licence_type = licence_type
        self.num_cards = 0
        self.licence_cost = Decimal("0")
        self.max_cards = 0
        self.cards_cost = Decimal("0")
        self._set_licence_config()

    def _set_licence_config(self) -> None:
        match self.licence_type:
            case LicenceType.PRIME:
                self.licence_cost = PRIME_LICENCE_COST
                self.max_cards = PRIME_MAX_NUM_CARDS
            case LicenceType.PLATINUM:
                self.licence_cost = PLATINUM_LICENCE_COST
                self.max_cards = PLATINUM_MAX_NUM_CARDS
            case _:
                raise ValueError("unknown licence type")

    def set_num_cards(self, num_cards: int):
        # verify licence type can accept amount of cards
        if num_cards > self.max_cards:
            raise ValueError(f"{self.licence_type.name} licence can only have {self.max_cards} cards")
        # set num cards
        self.num_cards = num_cards
        # set cost for all cards
        self.cards_cost = num_cards * CARD_COST
        return self

    def _add_initial_cards(self, licence: Licence) -> None:
        # build cards
        mining_cards = [MiningCard() for _ in range(self.num_cards)]
        # add cards to licence
        for mining_card in mining_cards:
            licence.add_mining_card(mining_card=mining_card)

    def build(self) -> (Licence, Decimal):
        # create a licence
        licence = Licence(cost=self.licence_cost, max_num_cards=self.max_cards)
        # add  cards
        self._add_initial_cards(licence=licence)
        # calculate package cost
        package_cost = self.licence_cost + self.cards_cost
        # return licence and cost of licence including initial cards
        return licence, package_cost
