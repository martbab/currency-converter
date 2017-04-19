# Author: Martin Babinsky <martbab@gmail.com>
# See LICENSE file for license

"""
Basic unit tests for the backend
"""
import random

import pytest

from currencyconv import backend


example_rates = {
    "ABC": 10.000,
    "DEF": 5.000,
    "XYZ": 2.213,
}

default_base = "BSE"
invalid_codes = ["INV", "CDS"]


@pytest.yield_fixture(scope='class')
def converter():
    conv = backend.Converter(default_base, example_rates)
    yield conv


@pytest.yield_fixture(params=list(example_rates))
def individual_code(request):
    yield request.param


class TestConverter:
    """
    Unit tests for converter
    """
    def test_same_input_output_rate_raises_error(self, converter):
        with pytest.raises(backend.InputCurrencySameAsOutput):
            converter.convert(10.0, default_base)

    def test_zero_convertion_returns_zeros(self, converter):
        amounts = converter.convert(0.0)
        for a in amounts.values():
            assert a < 1e-9

    def test_individual_conversion(self, converter, individual_code):
        amount = random.uniform(1, 10)
        result = converter.convert(amount, individual_code)[individual_code]
        assert abs(result - (amount * example_rates[individual_code])) < 1e-9

    def test_invalid_codes_raise_error(self, converter):
        with pytest.raises(backend.UnknownCurrencyCode) as exc:
            converter.convert(10.0, *invalid_codes)

        assert ', '.join(sorted(invalid_codes)) in str(exc.value)

    def test_mixed_codes_raise_error(self, converter):
        output_codes = list(example_rates.keys()) + invalid_codes
        with pytest.raises(backend.UnknownCurrencyCode) as exc:
            converter.convert(10.0, *output_codes)

        assert ', '.join(sorted(invalid_codes)) in str(exc.value)


example_json_output = [
  {"cc": "AED", "symbol": "\u062f.\u0625;", "name": "UAE dirham"},
  {"cc": "AOA", "symbol": "Kz", "name": "Angolan kwanza"},
  {"cc": "ARS", "symbol": "$", "name": "Argentine peso"},
  {"cc": "AUD", "symbol": "$", "name": "Australian dollar"},
]


@pytest.yield_fixture()
def symbol_index(monkeypatch):
    def mock_json_output():
        return example_json_output

    monkeypatch.setattr(
        "currencyconv.backend._parse_raw_currency_data", mock_json_output)
    yield backend.SymbolIndex()


class TestIndex:
    def test_invalid_symbol_raises_keyerror(self, symbol_index):
        with pytest.raises(KeyError):
            symbol_index['invalid_symbol']

    def test_retrieval_of_single_code_mapping(self, symbol_index):
        assert symbol_index["\u062f.\u0625;"] == ["AED"]

    def test_retrieval_of_multiple_code_mapping(self, symbol_index):
        assert sorted(symbol_index["$"]) == ["ARS", "AUD"]
