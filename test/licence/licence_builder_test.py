from decimal import Decimal

import pytest

from source.Constants import PRIME_LICENCE_COST, PRIME_MAX_NUM_CARDS, PLATINUM_LICENCE_COST, PLATINUM_MAX_NUM_CARDS, \
    CARD_COST
from source.licence.LicenceBuilder import LicenceBuilder, LicenceType


def test_prime_licence_config():
    builder = LicenceBuilder(licence_type=LicenceType.PRIME)

    assert builder.licence_cost == PRIME_LICENCE_COST
    assert builder.max_cards == PRIME_MAX_NUM_CARDS


def test_platinum_licence_config():
    builder = LicenceBuilder(licence_type=LicenceType.PLATINUM)

    assert builder.licence_cost == PLATINUM_LICENCE_COST
    assert builder.max_cards == PLATINUM_MAX_NUM_CARDS


def test_too_many_cards_raises():
    builder = LicenceBuilder(licence_type=LicenceType.PRIME)

    with pytest.raises(ValueError, match=f"{LicenceType.PRIME.name} licence can only have {PRIME_MAX_NUM_CARDS} cards"):
        builder.set_num_cards(num_cards=PRIME_MAX_NUM_CARDS + 1)


def test_cards_cost_calculation():
    builder = LicenceBuilder(licence_type=LicenceType.PRIME)
    builder.set_num_cards(num_cards=10)

    assert builder.cards_cost == Decimal("10") * CARD_COST

def test_build_adds_cards():
    builder = LicenceBuilder(licence_type=LicenceType.PRIME).set_num_cards(num_cards=5)

    licence, package_cost = builder.build()

    assert len(licence.cards) == 5

def test_package_cost():
    builder = LicenceBuilder(licence_type=LicenceType.PRIME).set_num_cards(num_cards=3)

    licence, package_cost = builder.build()

    expected_cost = PRIME_LICENCE_COST + Decimal("3") * CARD_COST
    assert package_cost == expected_cost
