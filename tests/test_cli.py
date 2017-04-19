# Author: Martin Babinsky <martbab@gmail.com>
# See LICENSE file for license

"""
tests for the frontend layer
"""

import json
import pytest

from currencyconv import cli


test_result = {
    "USD": 0.4,
    "AUD": 0.53

}

input_amount = 10.0
input_currency = 'CZK'


@pytest.yield_fixture()
def json_formatter():
    f = cli.JSONFormatter(input_amount, input_currency)
    yield f


class TestJSONFormatter:
    def test_json_loads_of_equals_dumps(self, json_formatter):
        result = json_formatter(test_result)
        result_dict = json.loads(result)
        assert result_dict['input']['amount'] == input_amount
        assert result_dict['input']['currency'] == input_currency
        assert result_dict['output'] == test_result
