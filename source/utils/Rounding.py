from decimal import Decimal, ROUND_HALF_EVEN


def round_btc(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.0000000001"), rounding=ROUND_HALF_EVEN)