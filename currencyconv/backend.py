# Author: Martin Babinsky <martbab@gmail.com>
# See LICENSE file for license

"""
Backend which facilitates the conversion operations
"""

from collections.abc import Mapping
import json
import logging
import os

from forex_python import converter

logger = logging.getLogger(__name__)


class ConversionError(Exception):
    """
    Base class for the errors during rate conversion
    """
    pass


class UnknownCurrencyCode(ConversionError):
    def __init__(self, *codes):
        msg = "Unknown currency codes: {}".format(', '.join(codes))
        super().__init__(msg)


class InputCurrencySameAsOutput(ConversionError):
    pass


class Converter:
    """
    Class which facilitates the conversion of a currency `base` to other
    currencies using `rate_dict`

    :param base: base currency
    :param rate_dict: A dictionary of conversion rates keyed by 3-letter
    currency symbol
    """
    def __init__(self, base, rate_dict):
        self.base = base
        self.rates = rate_dict
        logger.debug(
            "Initializing base currency '%s' and rate dict '%s'",
            base, rate_dict)

    def _yield_rates(self, amount, output_currencies):
        for code, rate in self.rates.items():
            if output_currencies and code not in output_currencies:
                continue

            yield code, amount * rate

    def convert(self, amount, *output_currencies):
        """
        Convert an amount in the base currency to output currencies
        :param amount: An amount of money in base currency
        :param output_currencies: 3-letter codes of output currencies

        :raises: UnknownCurrencyCode if there are unknown codes in the output
            currencies
        """
        if output_currencies:
            if (self.base,) == output_currencies:
                raise InputCurrencySameAsOutput(
                    "input currency '{}' is the same as output currency "
                    "'{}".format(self.base, output_currencies))

            known_rates = set(self.rates.keys())
            output_rates = set(output_currencies)

            unknown_rates = output_rates - known_rates
            if not known_rates.issuperset(output_rates):
                raise UnknownCurrencyCode(*sorted(unknown_rates))

        return {code: result for code, result in self._yield_rates(
            amount, output_currencies)}


def default_converter(base):
    """
    Return default converter which uses forex_python (frontend to fixer.io
    rates)
    """
    try:
        return Converter(base, converter.CurrencyRates().get_rates(base))
    except converter.RatesNotAvailableError:
        raise UnknownCurrencyCode(base)


def _parse_raw_currency_data():
    converter_package_path = os.path.dirname(
        os.path.abspath(converter.__file__))

    json_path = os.path.join(
        converter_package_path, 'raw_data', 'currencies.json')

    logger.debug("Loading JSON data from %s", json_path)

    with open(json_path, 'r', encoding='utf-8') as f:
        return json.loads(f.read())


class SymbolIndex(Mapping):
    """
    mapping of currency symbols to one or more 3-letter ISO codes

    NOTE: this class is using internal implementation details of forex_python
    package and may break anytime
    """
    def __init__(self):
        self._index = {}

        json_data = _parse_raw_currency_data()

        for item in json_data:
            symbol = item['symbol']
            code = item['cc']
            self._index.setdefault(symbol, []).append(code)

        logger.debug("Symbol index contents: %s", self._index)

    def __getitem__(self, key):
        return self._index[key]

    def __len__(self):
        return len(self._index)

    def __iter__(self):
        return iter(self._index)
