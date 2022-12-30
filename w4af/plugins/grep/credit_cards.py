"""
credit_cards.py

Copyright 2008 Andres Riancho

This file is part of w4af, http://w4af.org/ .

w4af is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation version 2 of the License.

w4af is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with w4af; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

"""
import re

import w4af.core.data.constants.severity as severity

from w4af.core.controllers.plugins.grep_plugin import GrepPlugin
from w4af.core.data.kb.vuln import Vuln

SPACE_RE = re.compile(r'\s+')

def passes_luhn_check(value):
    """
    The Luhn check against the value which can be an array of digits,
    numeric string or a positive integer.
    
    Example credit card numbers can be found here:

    https://www.paypal.com/en_US/vhelp/paypalmanager_help/credit_card_numbers.htm
    """
    value = re.sub(SPACE_RE, '', value)
    nDigits = len(value)
    nSum = 0
    isSecond = False

    for i in range(nDigits - 1, -1, -1):
        d = ord(value[i]) - ord('0')

        if (isSecond == True):
            d = d * 2

        # We add two digits to handle
        # cases that make two digits after
        # doubling
        nSum += d // 10
        nSum += d % 10

        isSecond = not isSecond

    if (nSum % 10 == 0):
        return True
    else:
        return False


class credit_cards(GrepPlugin):
    """
    This plugin detects the occurrence of credit card numbers in web pages.

    :author: Alexander Berezhnoy (alexander.berezhnoy |at| gmail.com)
    """

    def __init__(self):
        GrepPlugin.__init__(self)

        cc_regex = r'((^|\s)\d{4}[- ]?(\d{4}[- ]?\d{4}|\d{6})[- ]?(\d{5}|\d{4})?($|\s))'
        #    (^|[^\d])                        Match the start of the string, or something that's NOT a digit
        #    \d{4}[- ]?                       Match four digits, and then (optionally) a "-" or a space
        #    (\d{4}[- ]?\d{4}|\d{6})          Match one of the following:
        #            - Four digits, and then (optionally) a "-" or a space and then four digits again (VISA cards)
        #            - Six digits (AMEX cards)
        #    [- ]?                            Match a "-" or a space (optionally)
        #    (\d{5}|\d{4})                    Match the final digits, five or four digits
        #    ($|[^\d])                        Match the end of the string, or something that's NOT a digit

        self._cc_regex = re.compile(cc_regex, re.M)

    def grep(self, request, response):
        """
        Plugin entry point, search for the credit cards.
        :param request: The HTTP request object.
        :param response: The HTTP response object
        :return: None
        """
        if not response.is_text_or_html():
            return

        if not response.get_code() == 200:
            return

        clear_text_body = response.get_clear_text_body()

        if clear_text_body is None:
            return

        found_cards = self._find_card(clear_text_body)

        for card in found_cards:
            desc = 'The URL: "%s" discloses the credit card number: "%s"'
            desc %= (response.get_url(), card)

            v = Vuln('Credit card number disclosure', desc,
                     severity.LOW, response.id, self.get_name())

            v.set_url(response.get_url())
            v.add_to_highlight(card)

            self.kb_append_uniq(self, 'credit_cards', v, 'URL')

    def _find_card(self, body):
        """
        :return: A list of matching credit card numbers
        """
        res = []

        match_list = self._cc_regex.findall(body)

        for match_set in match_list:
            possible_cc = match_set[0]
            possible_cc = possible_cc.strip()

            if passes_luhn_check(possible_cc):
                res.append(possible_cc)

        return res

    def get_long_desc(self):
        """
        :return: A DETAILED description of the plugin functions and features.
        """
        return """
        This plugins scans every response page to find the strings that are
        likely to be credit card numbers.
        """
