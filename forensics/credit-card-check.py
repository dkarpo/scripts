#!/usr/bin/python
#
# $Id: credit-card-check.py 57 2009-02-26 21:22:21Z dk $
#
# Test a number to see if it passes the Luhn check for credit
# card validity.  Beware false positives.  Beware I say!
#
# Author: Derrick Karpo
# Date:   February 26, 2009
#

import sys

try:
    from optparse import OptionParser
except ImportError:
    raise ImportError, 'This program requires the OptionParser extensions for Python.'


def parseOptions():
    if len(sys.argv) == 1:
        sys.argv.append('-h')
    
    usage = "usage: %prog card# ..."
    description = "Test a credit card number against the Luhn algorithm"

    parser = OptionParser(usage=usage, description=description)
    (opts, args) = parser.parse_args()
    return (opts, args)


def cardLuhnChecksumIsValid(card_number):
    """ checks to make sure that the card passes a luhn mod-10 checksum """
    sum = 0
    num_digits = len(card_number)
    oddeven = num_digits & 1

    for count in range(0, num_digits):
        digit = int(card_number[count])

        if not ((count & 1) ^ oddeven):
            digit = digit * 2
        if digit > 9:
            digit = digit - 9

        sum = sum + digit

    return ((sum % 10) == 0)


def main():
    """Runs program and handles command line options"""

    # read command line options
    (opts, args) = parseOptions()

    # test the card number
    for card in sys.argv[1:]:
        result = cardLuhnChecksumIsValid(card)
        print "%s %s" % (card,result)


if __name__ == "__main__":
    main()
