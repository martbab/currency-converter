# Author: Martin Babinsky <martbab@gmail.com>
# See LICENSE file for license

"""
CLI frontend layer
"""

import argparse
import json
import logging
import sys

from currencyconv import app

logger = logging.getLogger(__name__)


class JSONFormatter:
    """
    convert the result of the currency conversion to the JSON representation as
    follows:
        {
            'input': {
                'amount': AMOUNT,
                'currency': INPUT_CURRENCY
            },
            'output': {
                'AUD': AMOUNT_IN_AUD,
                ...
            }
        }
    """
    def __init__(self, amount, base):
        self.amount = amount
        self.base = base

    def __call__(self, converted_rates):
        result_dict = {
            'input': {
                'amount': self.amount,
                'currency': self.base
            },
            'output': converted_rates
        }
        return json.dumps(result_dict, indent=2, sort_keys=True)


class CLI:
    """
    Main CLI frontend entry point
    """
    def __init__(self, args=None):
        self.parser = self.make_parser()
        self.args = self.parser.parse_args(args=args)
        if self.args.amount is None:
            self.parser.error("--amount is mandatory")

        self.setup_logging()
        logger.debug("Retrieved argument values: %s", self.args)

        self.app = self.init_app(self.args.input_currency)
        self.json_formatter = self.init_formatter(
            self.args.amount, self.app.base)

    def die(self, msg, exc):
        message = "{}: {}".format(msg, exc)
        if self.args.debug:
            logger.debug("Exception trace:", exc_info=True)
        logger.critical(message)
        raise exc

    def make_parser(self):
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '-a',
            '--amount',
            metavar='AMOUNT',
            type=float,
            help="Amount to convert"
        )
        parser.add_argument(
            '-i',
            '--input_currency',
            metavar='ISO_CODE|SYMBOL',
            help="input currency (symbol or 3-letter iso code)"
        )
        parser.add_argument(
            '-o',
            '--output_currency',
            metavar='ISO_CODE|SYMBOL',
            help="output currency (symbol or 3-letter iso code)",
            default=None
        )
        parser.add_argument(
            '-d',
            '--debug',
            action='store_true',
            default=False,
            help="Print verbose information and tracebacks on errors"
        )
        return parser

    def setup_logging(self):
        root_logger = logging.getLogger('')
        root_formatter = logging.Formatter(
            '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
            datefmt='%m-%d %H:%M')
        console = logging.StreamHandler()
        console.setFormatter(root_formatter)

        root_logger.setLevel(
            logging.DEBUG if self.args.debug else logging.INFO)
        root_logger.addHandler(console)

    def init_app(self, input_currency):
        logger.info("initializing app layer")
        try:
            return app.App(input_currency)
        except Exception as e:
            self.die("Failed to initialize app layer", e)

    def init_formatter(self, amount, input_currency):
        logger.info("Initializing JSON printer")
        try:
            return JSONFormatter(amount, input_currency)
        except Exception as e:
            self.die("Failed to initialize app layer", e)

    def main(self):
        output_currency = []
        if self.args.output_currency is not None:
            output_currency = [self.args.output_currency]

        result = self.app.convert(self.args.amount, *output_currency)
        return self.json_formatter(result)


def main():
    try:
        cli = CLI()
        print(cli.main())
    except Exception as e:
        sys.exit(e)

    sys.exit(0)

if __name__ == '__main__':
    main()
