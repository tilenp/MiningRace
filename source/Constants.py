from decimal import Decimal, ROUND_CEILING

from source.utils.Rounding import round_btc

BTC_PRICE = Decimal("91000")

# licence
PRIME_LICENCE_COST = round_btc(Decimal("1200") / BTC_PRICE)
PLATINUM_LICENCE_COST = round_btc(Decimal("1000") / BTC_PRICE)
PRIME_MAX_NUM_CARDS = 50
PLATINUM_MAX_NUM_CARDS = 30

# card
# fix card cost estimation, it makes it too expensive
CARD_COST: Decimal = round_btc((Decimal("-1976") + Decimal("0.026") * BTC_PRICE) / BTC_PRICE)
CARD_MINES_BTC_PER_DAY = Decimal("0.0000245")
CARD_PROFIT_THRESHOLD = Decimal("14")
CARD_NUM_MINING_DAYS = (CARD_COST / CARD_MINES_BTC_PER_DAY).to_integral_value(rounding=ROUND_CEILING)