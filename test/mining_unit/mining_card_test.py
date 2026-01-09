from decimal import Decimal

import pytest

from source.mining_unit.MiningCard import MiningCard
from source.mining_unit.MiningCardState import Reserved, Active, Deactivated


def test_reserved_status_counts_down():
    card = MiningCard(
        state=Reserved(days_left=2)
    )

    mined = card.get_daily_mining_amount()

    assert mined == Decimal("0")
    assert isinstance(card.state, Reserved)
    assert card.state.days_left == 1


def test_reserved_transitions_to_active():
    card = MiningCard(
        state=Reserved(days_left=1)
    )

    mined = card.get_daily_mining_amount()

    assert mined == Decimal("0")
    assert isinstance(card.state, Active)
    assert card.state.mined_btc == Decimal("0")


def test_active_mines_btc_per_day():
    card = MiningCard(
        cost=Decimal("1"),
        mines_btc_per_day=Decimal("0.1"),
        profit_threshold=Decimal("10"),  # target = 1.1 BTC
        state=Active(mined_btc=Decimal("0")),
    )

    mined = card.get_daily_mining_amount()

    assert mined == Decimal("0.1")
    assert isinstance(card.state, Active)
    assert card.state.mined_btc == Decimal("0.1")


def test_active_reaches_exact_threshold_and_deactivates():
    card = MiningCard(
        cost=Decimal("1"),
        mines_btc_per_day=Decimal("0.1"),
        profit_threshold=Decimal("10"),  # target = 1.1
        state=Active(mined_btc=Decimal("1.0")),
    )

    mined = card.get_daily_mining_amount()

    assert mined == Decimal("0.1")
    assert isinstance(card.state, Deactivated)


def test_active_does_not_overshoot_threshold():
    card = MiningCard(
        cost=Decimal("1"),
        mines_btc_per_day=Decimal("0.5"),
        profit_threshold=Decimal("10"),  # target = 1.1
        state=Active(mined_btc=Decimal("0.9")),
    )

    mined = card.get_daily_mining_amount()

    assert mined == Decimal("0.2")  # capped at threshold
    assert isinstance(card.state, Deactivated)


def test_deactivated_never_mines():
    card = MiningCard(
        state=Deactivated()
    )

    with pytest.raises(RuntimeError, match=f"Mine called on a card in state: {card.state}"):
        card.get_daily_mining_amount()


def test_full_card_lifecycle():
    card = MiningCard(
        cost=Decimal("1"),
        mines_btc_per_day=Decimal("0.2"),
        profit_threshold=Decimal("10"),  # target = 1.1
        state=Reserved(days_left=2),
    )

    # 1st day -> in reserved state
    mined = card.get_daily_mining_amount()
    assert isinstance(card.state, Reserved)
    assert mined == Decimal("0")
    # 2nd day -> doesnt mine but goes into active state
    mined = card.get_daily_mining_amount()
    assert isinstance(card.state, Active)
    assert mined == Decimal("0")
    # 3rd day -> mining
    mined = card.get_daily_mining_amount()
    assert isinstance(card.state, Active)
    assert card.state.mined_btc == Decimal("0.2")
    assert mined == Decimal("0.2")
    # 4th day -> mining
    mined = card.get_daily_mining_amount()
    assert isinstance(card.state, Active)
    assert card.state.mined_btc == Decimal("0.4")
    assert mined == Decimal("0.2")
    # 5th day -> mining
    mined = card.get_daily_mining_amount()
    assert isinstance(card.state, Active)
    assert card.state.mined_btc == Decimal("0.6")
    assert mined == Decimal("0.2")
    # 6th day -> mining
    mined = card.get_daily_mining_amount()
    assert isinstance(card.state, Active)
    assert card.state.mined_btc == Decimal("0.8")
    assert mined == Decimal("0.2")
    # 7th day -> mining
    mined = card.get_daily_mining_amount()
    assert isinstance(card.state, Active)
    assert card.state.mined_btc == Decimal("1.0")
    assert mined == Decimal("0.2")
    # 8th day -> mining capped at 10% profit, card gets deactivated
    mined = card.get_daily_mining_amount()
    assert isinstance(card.state, Deactivated)
    assert mined == Decimal("0.1")
    # 9th day -> in deactivated state
    with pytest.raises(RuntimeError, match=f"Mine called on a card in state: {card.state}"):
        card.get_daily_mining_amount()
