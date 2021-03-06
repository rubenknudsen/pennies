from __future__ import division, print_function

import datetime as dt
import numpy as np

from pennies.trading import assets
from pennies.trading import trades
from pennies.market.curves import ConstantDiscountRateCurve
from pennies.market.market import RatesTermStructure
from pennies.calculators.payments import BulletPaymentCalculator
from pennies.calculators.trades import TradeCalculator
from pennies.core import CurrencyAmount
from pennies.time import daycount

# TODO - Should this be a class of, or a number of individual, tests?

dt_val = dt.datetime.now()  # note: both date and time
dt_pay = dt_val + dt.timedelta(days=730)
notional = 5.5e6
ccy = "USD"
bullet = assets.BulletPayment(dt_payment=dt_pay, currency=ccy, amount=notional)
trade = trades.Trade(contract=bullet)

rate_discount = 0.05
crv_discount = ConstantDiscountRateCurve(
    dt_valuation=dt_val, zero_rate=rate_discount,
    daycount_function=daycount('Act/365 Fixed'), currency=ccy)
market = RatesTermStructure.of_single_curve(dt_val, crv_discount)
expected_contract_pv = 4976605.8


def test_contract_present_value():
    calculator = BulletPaymentCalculator(bullet, market)
    pv_calc = calculator.present_value()
    assert isinstance(pv_calc, CurrencyAmount)
    assert pv_calc.currency == 'USD'
    assert np.allclose(pv_calc.amount, expected_contract_pv), \
        "calculated present value is not as expected."


def test_contract_present_value_with_rates_zero():
    interest = 0.00
    crv = ConstantDiscountRateCurve(dt_valuation=dt_val, zero_rate=interest)
    market = RatesTermStructure.of_single_curve(dt_val, crv)
    calculator = BulletPaymentCalculator(bullet, market)
    pv_calc = calculator.present_value()
    assert isinstance(pv_calc, CurrencyAmount)
    assert pv_calc.currency == 'USD'
    assert np.allclose(pv_calc.amount, notional), \
        "calculated present value is not as expected."


def test_trade_present_value():
    calculator = TradeCalculator(trade, market)
    pv_calc = calculator.present_value()
    assert isinstance(pv_calc, CurrencyAmount)
    assert pv_calc.currency == 'USD'
    assert np.allclose(pv_calc.amount, expected_contract_pv), \
        "calculated present value is not as expected."


def test_trade_present_value_with_settlement_on_valuationdate():
    trade_w_settlement = trades.Trade(contract=bullet, settlement_dt=dt_val,
                                      settlement_amt=notional)
    calculator = TradeCalculator(trade_w_settlement, market)
    pv_calc = calculator.present_value()
    assert isinstance(pv_calc, CurrencyAmount)
    assert pv_calc.currency == 'USD'
    assert np.allclose(pv_calc.amount, expected_contract_pv + notional), \
        "calculated present value is not as expected."
