# Author: Martin Babinsky <martbab@gmail.com>
# See LICENSE file for license

"""
Integration test executing the whole stack
"""
import json

from forex_python.converter import CurrencyRates
import pytest

from currencyconv import app, backend, cli


class TestCLI:

    def run_cli(self, args):
        test_cli = cli.CLI(args=args)
        return json.loads(test_cli.main())

    def assert_error(self, args, exc, msg=None):
        with pytest.raises(exc) as e:
            self.run_cli(args)

        if msg is not None:
            assert msg in str(e.value)

    def assert_conversion(self, args):
        currency_rates = CurrencyRates()
        result = self.run_cli(args)

        amount = result['input']['amount']
        input_currency = result['input']['currency']

        output = result['output']

        for output_currency, output_amount in output.items():
            assert output_amount == currency_rates.convert(
                input_currency, output_currency, amount)

    def test_invalid_currency_name_raises_error(self):
        self.assert_error(
            [
                '--amount', '10',
                '--input_currency', 'LOL'
            ],
            backend.UnknownCurrencyCode,
            msg="Unknown currency codes: LOL"
        )

    def test_ambiguous_input_symbol_raises_error(self):
        self.assert_error(
            [
                '--amount', '10',
                '--input_currency', '$'
            ],
            app.AmbiguousInputSymbol,
            msg="Ambiguous input currency symbol: '$'"
        )

    def test_conversion_to_all_currencies(self):
        self.assert_conversion(
            [
                '--amount', '10',
                '--input_currency', 'CZK'
            ]
        )

    def test_conversion_to_single_currency(self):
        self.assert_conversion(
            [
                '--amount', '10',
                '--input_currency', 'CZK',
                '--output_currency', 'USD'
            ]
        )

    def test_conversion_to_ambiguous_symbol(self):
        self.assert_conversion(
            [
                '--amount', '10',
                '--input_currency', 'CZK',
                '--output_currency', '$'
            ]
        )

    def test_conversion_from_unicode_symbol(self):
        self.assert_conversion(
            [
                '--amount', '10',
                '--input_currency', 'Kč',
                '--output_currency', 'USD'
            ]
        )

    def test_conversion_from_to_unicode_symbol(self):
        self.assert_conversion(
            [
                '--amount', '10',
                '--input_currency', 'Kč',
                '--output_currency', '€'
            ]
        )
