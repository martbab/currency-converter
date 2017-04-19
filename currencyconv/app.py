# Author: Martin Babinsky <martbab@gmail.com>
# See LICENSE file for license

"""
Application layer that forwards requests to backend
"""

import logging

from currencyconv import backend

logger = logging.getLogger(__name__)


class AppError(Exception):
    """
    Base for application errors
    """
    pass


class AmbiguousInputSymbol(AppError):
    """
    Raised when the input currency symbol resolves to multiple 3-letter codes
    """
    pass


class App:
    """
    Intermediary that proxies requests to backend
    """
    def __init__(self, input_currency):
        self.index = backend.SymbolIndex()
        self.base = self._resolve_input_currency(input_currency)
        self.converter = self._init_converter(self.base)

    def _resolve_input_currency(self, input_currency):
        """
        resolve input currency symbol or code. If the string is not in the
        index, pass it unchanged. In this case the underlying code handles the
        existence of this currency.

        :param input_currency: input symbol or code

        :raises: AmbiguousInputSymbol if the symbol resolves to multiple
            currency codes
        """
        base = input_currency

        try:
            resolved_codes = self.index[input_currency]
        except KeyError:
            pass
        else:
            if len(resolved_codes) > 1:
                raise AmbiguousInputSymbol(
                    "Ambiguous input currency symbol: '{}'".format(base))

            base = resolved_codes[0]

        return base

    def _init_converter(self, input_currency):
        """
        initialize converter using input currency. First try to resolve the
        incoming symbol using the index. If the symbol is ambiguous (i. e. more
        than a single ISO code corresponds to a symbol, common for dollars),
        raise an error.
        """

        return backend.default_converter(input_currency)

    def convert(self, amount, *output_currencies):
        """
        Convert the amount using the specified output currencies. Try to
        resolve currency symbols into 3-letter codes usable by backend
        converter. In case of multiple codes, issue a warning about ambiguous
        symbol
        """
        logger.debug("Output currency specification: %s", output_currencies)
        resolved_currencies = []
        for currency in output_currencies:
            try:
                resolved_codes = [
                    code for code in self.index[currency] if code
                    in self.converter.rates]

                logger.debug(
                    "Resolved codes for currency %s: %s",
                    currency,
                    resolved_codes)

                if len(resolved_codes) > 1:
                    logger.warning(
                        "Symbol '%s' resolves to multiple currency codes: %s",
                        currency,
                        resolved_codes)
                    logger.warning("Results will be printed for all of them")
                    logger.warning("Specify 3-letter code to unambiguously"
                                   " determine the output currency")

                # only append those resolved codes the underlying converter
                # knows about. This prevents mismatches between symbol index
                # and known rates during resolution
                resolved_currencies.extend(resolved_codes)
            except KeyError:
                resolved_currencies.append(currency)

        logger.debug("Resolved currency codes: %s", resolved_currencies)
        return self.converter.convert(amount, *resolved_currencies)
