from decimal import Decimal

from source.Constants import BTC_PRICE, CARD_COST, CARD_NUM_MINING_DAYS, PRIME_LICENCE_COST
from source.licence.LicenceBuilder import LicenceType, LicenceBuilder
from source.user.User import User
from source.utils.Metrics import compound_annual_growth_rate


class Simulator:

    def simulate(self, user: User, days: int) -> Decimal:
        # simulate mining over days
        for day in range(1, days + 1):
            # mine
            user.mine_for_day()
            # add new licences with cards if there is enough days left for licences to expire
            if day <= days - 365:
                user.add_new_licence_with_cards(licence_type=LicenceType.PLATINUM, num_cards=10)
            # add new cards
            num_cards_added = user.add_new_cards()
            # print out the state for each day: BTC amount in USD, how many cards were added
            print( f"day: {day}, BTC value: ${(user.btc_amount * BTC_PRICE):.2f}, number of cards added: {num_cards_added}")
        # return total BTC amount for the user
        return user.btc_amount


if __name__ == "__main__":
    # configure licence builder
    licence_builder = LicenceBuilder(licence_type=LicenceType.PRIME).set_num_cards(num_cards=14)
    # build licence with cards and cost
    licence, cost = licence_builder.build()
    # create a user
    user = User()
    # add licence to user
    user.licences.add(licence)
    # create simulator
    simulator = Simulator()
    # run simulation
    days = 365
    btc_amount = simulator.simulate(user=user, days=days)
    # calculate CAGR
    cagr = compound_annual_growth_rate(
        beginning_value=cost,
        ending_value=btc_amount,
        years=Decimal(days) / Decimal("365"),
    )
    print("--- Results ---")
    print(f"Bitcoin price: ${BTC_PRICE:.2f}")
    print(f"Prime licence cost: ${(PRIME_LICENCE_COST * BTC_PRICE):.2f}")
    print(f"card cost: ${(CARD_COST * BTC_PRICE):.2f}")
    print(f"card lifetime: {CARD_NUM_MINING_DAYS} days")
    print(f"invested amount: ${(cost * BTC_PRICE):.2f}")
    print(f"final amount: ${(btc_amount * BTC_PRICE):.2f}")
    print(f"CAGR: {(cagr * 100):.2f}%")
