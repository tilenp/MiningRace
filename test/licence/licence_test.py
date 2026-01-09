from decimal import Decimal

import pytest

from source.Constants import PRIME_LICENCE_COST, CARD_MINES_BTC_PER_DAY
from source.licence.Licence import Licence
from source.licence.LicenceState import Valid, Expired
from source.mining_unit.MiningCard import MiningCard
from source.mining_unit.MiningCardState import Active, Deactivated, Reserved


def test_can_add_mining_card_under_limit():
    licence = Licence(
        cost=PRIME_LICENCE_COST,
        max_num_cards=2,
        state=Valid(days_left=365),
    )
    licence.add_mining_card(MiningCard())
    assert licence.can_add_mining_card() is True


def test_can_add_mining_card_at_limit():
    licence = Licence(
        cost=PRIME_LICENCE_COST,
        max_num_cards=2,
        state=Valid(days_left=365),
    )
    licence.add_mining_card(MiningCard())
    licence.add_mining_card(MiningCard())
    assert licence.can_add_mining_card() is False


def test_can_add_mining_card_above_card_mining_days_threshold():
    licence = Licence(
        cost=PRIME_LICENCE_COST,
        max_num_cards=2,
        card_num_mining_days=90,
        state=Valid(days_left=91),
    )

    assert licence.can_add_mining_card() is True


def test_can_add_mining_card_at_card_mining_days_threshold():
    licence = Licence(
        cost=PRIME_LICENCE_COST,
        max_num_cards=2,
        card_num_mining_days=90,
        state=Valid(days_left=90),
    )

    assert licence.can_add_mining_card() is False


def test_can_add_mining_card_when_expired():
    licence = Licence(
        cost=PRIME_LICENCE_COST,
        max_num_cards=2,
        state=Expired(),
    )

    assert licence.can_add_mining_card() is False


def test_add_mining_card_adds_card():
    licence = Licence(
        cost=PRIME_LICENCE_COST,
        max_num_cards=2,
    )
    card = MiningCard()
    licence.add_mining_card(card)
    # assert
    assert card in licence.cards
    assert len(licence.cards) == 1


def test_add_mining_card_raises_when_at_max_cards():
    licence = Licence(
        cost=PRIME_LICENCE_COST,
        max_num_cards=1,
        state=Valid(days_left=365),
    )
    licence.add_mining_card(MiningCard())

    with pytest.raises(RuntimeError, match=f"Should not add a new card"):
        licence.add_mining_card(MiningCard())

    # ensure state is unchanged
    assert len(licence.cards) == 1


def test_add_mining_card_raises_when_not_enough_days_left():
    licence = Licence(
        cost=PRIME_LICENCE_COST,
        max_num_cards=5,
        state=Valid(days_left=30),  # below threshold
    )

    with pytest.raises(RuntimeError, match=f"Should not add a new card"):
        licence.add_mining_card(MiningCard())

    assert len(licence.cards) == 0


def test_add_mining_card_raises_when_licence_expired():
    licence = Licence(
        cost=PRIME_LICENCE_COST,
        max_num_cards=5,
        state=Expired(),
    )

    with pytest.raises(RuntimeError, match=f"Should not add a new card"):
        licence.add_mining_card(MiningCard())

    assert len(licence.cards) == 0


def test_remove_deactivated_mining_cards():
    licence = Licence(
        cost=PRIME_LICENCE_COST,
        max_num_cards=2,
    )
    # cards
    active_card = MiningCard(state=Active(mined_btc=Decimal("0")))
    deactivated_card = MiningCard(state=Deactivated())
    # add cards
    licence.add_mining_card(active_card)
    licence.add_mining_card(deactivated_card)
    # remove deactivated cards
    licence._remove_deactivated_mining_cards()
    # assert
    assert deactivated_card not in licence.cards
    assert active_card in licence.cards
    assert len(licence.cards) == 1


def test_remove_deactivated_is_idempotent():
    licence = Licence(
        cost=PRIME_LICENCE_COST,
        max_num_cards=2,
    )
    # add card
    card = MiningCard(state=Deactivated())
    licence.add_mining_card(card)
    # remove deactivated cards
    licence._remove_deactivated_mining_cards()
    licence._remove_deactivated_mining_cards()
    # assert
    assert len(licence.cards) == 0


def test_acknowledge_mining_day_from_two_days_left():
    licence_state = Valid(days_left=2)
    licence = Licence(
        cost=PRIME_LICENCE_COST,
        max_num_cards=5,
        state=licence_state,
    )

    licence._acknowledge_mining_day(state=licence_state)

    assert isinstance(licence.state, Valid)
    assert licence.state.days_left == 1


def test_acknowledge_mining_day_expires_at_one_day():
    licence_state = Valid(days_left=1)
    licence = Licence(
        cost=PRIME_LICENCE_COST,
        max_num_cards=5,
        state=licence_state,
    )

    licence._acknowledge_mining_day(state=licence_state)

    assert isinstance(licence.state, Expired)


def test_get_daily_mining_amount_raises_when_expired():
    licence = Licence(
        cost=PRIME_LICENCE_COST,
        max_num_cards=5,
        state=Expired(),
    )

    with pytest.raises(RuntimeError, match="Only valid licence can mine"):
        licence.get_daily_mining_amount()


def test_get_daily_mining_amount_with_no_cards():
    licence = Licence(
        cost=PRIME_LICENCE_COST,
        max_num_cards=5,
        state=Valid(days_left=10),
    )

    mined = licence.get_daily_mining_amount()

    assert mined == Decimal("0")
    assert isinstance(licence.state, Valid)
    assert licence.state.days_left == 9


def test_get_daily_mining_amount_sums_multiple_cards():
    card1 = MiningCard(
        cost=Decimal("1"),
        mines_btc_per_day=Decimal("0.1"),
        profit_threshold=Decimal("10"),
        state=Active(mined_btc=Decimal("0")),
    )
    card2 = MiningCard(
        cost=Decimal("1"),
        mines_btc_per_day=Decimal("0.2"),
        profit_threshold=Decimal("10"),
        state=Active(mined_btc=Decimal("0")),
    )
    licence = Licence(
        cost=PRIME_LICENCE_COST,
        max_num_cards=5,
        state=Valid(days_left=10),
        cards={card1, card2},
    )

    mined = licence.get_daily_mining_amount()

    assert mined == Decimal("0.3")
    assert isinstance(licence.state, Valid)
    assert licence.state.days_left == 9


def test_get_daily_mining_amount_removes_deactivated_cards():
    card = MiningCard(
        cost=Decimal("1"),
        mines_btc_per_day=Decimal("0.1"),
        profit_threshold=Decimal("10"),
        state=Active(mined_btc=Decimal("1")),
    )
    licence = Licence(
        cost=PRIME_LICENCE_COST,
        max_num_cards=5,
        state=Valid(days_left=10),
        cards={card},
    )

    mined = licence.get_daily_mining_amount()
    assert mined == Decimal("0.1")
    assert card not in licence.cards


def test_get_daily_mining_amount_mines_on_last_valid_day():
    card = MiningCard(
        state=Active(mined_btc=Decimal("0")),
    )
    licence = Licence(
        cost=PRIME_LICENCE_COST,
        max_num_cards=5,
        state=Valid(days_left=1),
        cards={card},
    )

    mined = licence.get_daily_mining_amount()

    assert mined == CARD_MINES_BTC_PER_DAY
    assert isinstance(licence.state, Expired)


def test_reserved_cards_do_not_mine_but_progress():
    licence = Licence(
        cost=PRIME_LICENCE_COST,
        max_num_cards=2,
    )
    # add card
    card = MiningCard(state=Reserved(days_left=1))
    licence.add_mining_card(card)
    # mine
    mined = licence.get_daily_mining_amount()
    # assert
    assert mined == Decimal("0")
    # card's activation days were reduced, it went into active status
    assert isinstance(card.state, Active)


def test_licence_full_lifecycle():
    licence = Licence(
        cost=PRIME_LICENCE_COST,
        max_num_cards=2,
    )
    card1 = MiningCard(
        cost=Decimal("1"),
        mines_btc_per_day=Decimal("0.5"),
        profit_threshold=Decimal("10"),
        state=Reserved(days_left=1),
    )
    card2 = MiningCard(
        cost=Decimal("1"),
        mines_btc_per_day=Decimal("0.5"),
        profit_threshold=Decimal("10"),
        state=Reserved(days_left=1),
    )
    # add cards
    licence.add_mining_card(card1)
    licence.add_mining_card(card2)
    # 1st day -> cards go into active state, but dont mine
    mined = licence.get_daily_mining_amount()
    assert mined == Decimal("0")
    assert len(licence.cards) == 2
    # 2nd day -> cards mine
    mined = licence.get_daily_mining_amount()
    assert mined == Decimal("1")  # 0.5 + 0.5
    assert len(licence.cards) == 2
    # 3rd day -> cards mine
    mined = licence.get_daily_mining_amount()
    assert mined == Decimal("1")  # 0.5 + 0.5
    assert len(licence.cards) == 2
    # 4th day -> cards mine and clip mining to at most 14%
    mined = licence.get_daily_mining_amount()
    assert mined == Decimal("0.2")  # 0.1 + 0.1, reached target mining amount
    assert len(licence.cards) == 0  # cards were deactivated and removed
