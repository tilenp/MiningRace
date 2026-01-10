from decimal import Decimal

from source.Constants import CARD_MINES_BTC_PER_DAY, PRIME_LICENCE_COST, PLATINUM_LICENCE_COST, CARD_COST
from source.licence.Licence import Licence
from source.licence.LicenceBuilder import LicenceType
from source.licence.LicenceState import Valid, Expired
from source.mining_unit.MiningCard import MiningCard
from source.mining_unit.MiningCardState import Active, Reserved
from source.user.User import User


def test_remove_expired_licences_none_expired():
    # create licences
    licence1 = Licence(cost=Decimal("100"), max_num_cards=2, state=Valid(days_left=10))
    licence2 = Licence(cost=Decimal("100"), max_num_cards=2, state=Valid(days_left=5))
    user = User(licences={licence1, licence2}, btc_amount=Decimal("0"))

    # remove expired licences
    user._remove_expired_licences()

    # assert nothing removed
    assert user.licences == {licence1, licence2}


def test_remove_expired_licences_some_expired():
    licence1 = Licence(cost=Decimal("100"), max_num_cards=2, state=Expired())
    licence2 = Licence(cost=Decimal("100"), max_num_cards=2, state=Valid(days_left=5))
    user = User(licences={licence1, licence2}, btc_amount=Decimal("0"))

    # remove expired licences
    user._remove_expired_licences()

    # assert only the valid licence remains
    assert user.licences == {licence2}


def test_remove_expired_licences_all_expired():
    licence1 = Licence(cost=Decimal("100"), max_num_cards=2, state=Expired())
    licence2 = Licence(cost=Decimal("100"), max_num_cards=2, state=Expired())
    user = User(licences={licence1, licence2}, btc_amount=Decimal("0"))

    # remove expired licences
    user._remove_expired_licences()

    # assert all removed
    assert user.licences == set()


def test_mine_for_day_mines_all_licences():
    # create licences with active cards
    card1 = MiningCard(state=Active(mined_btc=Decimal("0")))
    licence1 = Licence(cost=Decimal("100"), max_num_cards=2, cards={card1})

    card2 = MiningCard(state=Active(mined_btc=Decimal("0")))
    licence2 = Licence(cost=Decimal("100"), max_num_cards=2, cards={card2})

    user = User(licences={licence1, licence2}, btc_amount=Decimal("1"))

    # mine for the day
    user.mine_for_day()

    # assert BTC updated
    assert user.btc_amount == Decimal("1") + 2 * CARD_MINES_BTC_PER_DAY


def test_mine_for_day_removes_expired_licences():
    # licence1 that's about to expire
    card1 = MiningCard(state=Active(mined_btc=Decimal("0")))
    licence1 = Licence(cost=Decimal("100"), max_num_cards=2, state=Valid(days_left=1), cards={card1})
    # licences is valid
    card2 = MiningCard(state=Active(mined_btc=Decimal("0")))
    licence2 = Licence(cost=Decimal("100"), max_num_cards=2, cards={card2})

    user = User(licences={licence1, licence2}, btc_amount=Decimal("0"))

    # mine for the day
    user.mine_for_day()

    # assert expired account removed
    assert licence1 not in user.licences
    # valid account remains and mined
    assert licence2 in user.licences
    assert user.btc_amount == 2 * CARD_MINES_BTC_PER_DAY


def test_add_new_race_account_creates_account_and_deducts_btc():
    # setup: user has two licences with BTC
    licence1 = Licence(cost=PRIME_LICENCE_COST, max_num_cards=5)
    licence2 = Licence(cost=PRIME_LICENCE_COST, max_num_cards=5)
    user = User(
        licences={licence1, licence2},
        btc_amount=PLATINUM_LICENCE_COST + Decimal("10") * CARD_COST + CARD_MINES_BTC_PER_DAY,
    )

    # add new licence
    user.add_new_licence_with_cards(licence_type=LicenceType.PLATINUM, num_cards=10)

    # user should now have one additional licence
    assert len(user.licences) == 3
    # total BTC remaining should be initial BTC minus cost of new licence with cards
    assert user.btc_amount == CARD_MINES_BTC_PER_DAY

    # verify new account has 10 reserved cards
    new_licence = next(licence for licence in user.licences if licence not in {licence1, licence2})
    assert len(new_licence.cards) == 10
    assert all(isinstance(card.state, Reserved) for card in new_licence.cards)


def test_add_new_cards():
    licence = Licence(cost=PRIME_LICENCE_COST, max_num_cards=5)
    user = User(licences={licence}, btc_amount=CARD_COST * Decimal("2.5"))

    user.add_new_cards()

    assert len(licence.cards) == 2
    assert user.btc_amount == CARD_COST / 2


def test_chooses_licence_with_most_remaining_capacity():
    licence_small = Licence(cost=Decimal("100"), max_num_cards=5, cards={MiningCard()})
    licence_big = Licence(cost=Decimal("100"), max_num_cards=10, cards={MiningCard(), MiningCard()})

    user = User(licences={licence_small, licence_big}, btc_amount=CARD_COST * 2)

    user.add_new_cards()

    assert len(licence_small.cards) == 1
    # there was enough BTC for 2 cards
    # both cards were added to big licence cuz it had relatively more capacity
    assert len(licence_big.cards) == 4


def test_stops_when_no_licence_can_add_cards():
    licence_small = Licence(cost=Decimal("100"), max_num_cards=2, cards={MiningCard()})
    licence_big = Licence(cost=Decimal("100"), max_num_cards=3, cards={MiningCard(), MiningCard()})

    user = User(licences={licence_small, licence_big}, btc_amount=CARD_COST * 3)

    user.add_new_cards()

    assert user.btc_amount == CARD_COST
