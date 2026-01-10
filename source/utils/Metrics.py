from decimal import Decimal


def compound_annual_growth_rate(
        beginning_value: Decimal,
        ending_value: Decimal,
        years: Decimal,
) -> Decimal:
    return (ending_value / beginning_value) ** (Decimal("1") / years) - Decimal("1")
