# Author: Martin Babinsky <martbab@gmail.com>
# See LICENSE file for license

"""
Unit tests for app
"""
import pytest

from currencyconv import backend, app

example_symbol_mappings = {
  "\u062f.\u0625;": ["AED"],
  "$": ["ARS", "AUD", "USD"],
  "Kz": ["AOA"]
}


def example_codes():
    codes = []
    for val in example_symbol_mappings.values():
        codes.extend(val)

    return codes


def mock_default_converter(base):
    codes = example_codes()

    if base not in codes:
        raise backend.UnknownCurrencyCode()

    return backend.Converter(base, {code: 1.0 for code in codes})


def mock_symbol_index():
    return example_symbol_mappings


@pytest.yield_fixture()
def testing_app(monkeypatch):
    monkeypatch.setattr('currencyconv.backend.SymbolIndex', mock_symbol_index)
    monkeypatch.setattr(
        'currencyconv.backend.default_converter', mock_default_converter)

    yield app


class TestApp:
    def test_invalid_input_currency_raises_error(self, testing_app):
        with pytest.raises(backend.UnknownCurrencyCode):
            testing_app.App("UNK")

    def test_ambiguous_input_currency_raises_error(self, testing_app):
        with pytest.raises(app.AmbiguousInputSymbol):
            testing_app.App('$')

    def test_conversion_without_output_currencies(self, testing_app):
        a = testing_app.App('Kz')
        result = a.convert(1.0)

        assert sorted(result) == sorted(example_codes())

    def test_conversion_of_single_output_currency(self, testing_app):
        a = testing_app.App('Kz')
        result = a.convert(1.0, 'USD')
        assert result['USD'] == 1.0

    def test_conversion_of_ambiguous_output_currency(self, testing_app):
        a = testing_app.App('Kz')
        result = a.convert(1.0, '$')
        assert sorted(result) == sorted(example_symbol_mappings['$'])
