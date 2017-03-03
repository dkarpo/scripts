#!/usr/bin/python3
#
# Print an ASCII grid of an Android unlock pattern
#
# Author: Derrick Karpo
# Date: April 21, 2013
#

import argparse, textwrap
from itertools import zip_longest
import sys


def grouper(n, iterable, padvalue=None):
    """Collect data into fixed-length chunks or blocks"""
    return zip_longest(*[iter(iterable)]*n, fillvalue=padvalue)


def generateUnlockPatternTable(pattern, base=0, pcolumns=3, prows=3):
    """Takes an unlock pattern as a list() and returns as ASCII picture of the
    unlock pattern.  Example pattern input would be 'result = [2, 5, 8, 7, 6]'.
    You can specify the number of columns and rows in the unlock pattern if you
    are dealing with an Android device that doesn't use the default 3x3 unlock
    grid."""
    SUBSTITUTE_CHAR = '#'
    table = [x for x in range(base,pcolumns*prows+base)]
    table = [str(x) if not x in pattern else SUBSTITUTE_CHAR for x in table]

    print('%ix%i Pattern:' % (pcolumns, prows))
    for row in grouper(pcolumns, table, "-"):
        print(('{:>3}'*pcolumns).format(*row))

class parser(argparse.ArgumentParser):
    def error(self, message):    
        usage = self.usage
        self.usage = None
        self.print_usage(_sys.stderr)
        self.exit(2, _('%s: error: %s\n') % (self.prog, message))
        self.usage = usage


def main():
    # setup the argument parser for the command line arguments
    parser = argparse.ArgumentParser(
        prog='android-pattern-print.py',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent("""\
            Generate an ASCII table of an Android pattern lock.
            ie. android-pattern-print.py \'[2, 5, 8, 7, 6]\'"""))
    
    parser.add_argument('pattern', action='store',
                        help='ie. \'[2, 5, 8, 7, 6]\'')
    parser.add_argument('-base', type=int,
                        choices=range(0,2), default=0,
                        help='Base number of pattern.  Defaults to %(default)i.  Set to 1 for CelleBrite or other tools that use 1 for the first digit.')
    parser.add_argument('-pc', type=int,
                        choices=range(3,7), default=3,
                        help='Number of pattern columns.  Defaults to %(default)i.')
    parser.add_argument('-pr', type=int,
                        choices=range(3,7), default=3,
                        help='Number of pattern rows.  Defaults to %(default)i.')
    args = parser.parse_args()

    # # output help and exit when no arguments are given
    # if len(sys.argv) < 1:
    #     parser.print_help()
    #     return

    # generate the pattern table
    try:
        # strip the pre- and post- [] characters, whitespace, and
        # convert the string of integers to a list of integers
        pattern = [int(x.strip()) for x in args.pattern[1:-1].split(',')]
        generateUnlockPatternTable(pattern, args.base, args.pc, args.pr)
    except Exception as e:
        sys.exit('Error: {0}.  Please confirm your pattern formatting.'
                 .format(str(e)))


if __name__ == "__main__":
    main()
