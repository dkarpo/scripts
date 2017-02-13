#!/usr/bin/python3
#
# Read in 2 text files and find differences and similarities
# between them or combine them.  Useful for de-duping or
# working with hash sets.
#
# Note: When working with large data sets this script isn't
# super efficient and will balloon in memory.  It works for
# what I need right now.
#
# Author: Derrick Karpo
# Date: July 19, 2014
#

import sys
import argparse
import pandas as pd


def outputFile(newset, args):
    # remove blank line from set
    newset.discard('\n')

    # write sorted output to a file
    if args.o:
        for line in sorted(newset):
            args.o.write(line)


def main():
    # setup the argument parser for the command line arguments
    parser = argparse.ArgumentParser(
        prog='matchy-matchy.py',
        description = """Read in 2 text files and find differences and similarities between them or combine them.\nIn all cases unique results will be outputted with no duplicates.  Note: 64-bit Python\nrecommended for larger datasets.

 ie. Print out the differences between two files to the screen:
     'matchy-matchy.py -d /tmp/1big.md5 /tmp/2big.md5'

 ie. Write out a new file that combines two files:
     'matchy-matchy.py -c /tmp/1big.md5 /tmp/2big.md5 -o /tmp/newbig.md5'""",
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('input_files', metavar='input_files',
                        type=argparse.FileType('rt'),
                        nargs=2,
                        help='Files to read from (read-only mode)')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-s', action='store_true',
                       help='Find similar lines between both files')
    group.add_argument('-d', action='store_true',
                       help='Find different lines between both files')
    group.add_argument('-c', action='store_true',
                       help='Combine files and remove duplicates')
    parser.add_argument('-o', metavar='output_file',
                        type=argparse.FileType('wt'),
                        nargs='?',
                        default=sys.stdout,
                        help='File to write to (defaults to stdout)')
    group.add_argument('-p', action='store_true',
                       help='Use pandas to read and parse the files')
    args = parser.parse_args()

    # output help and exit when no arguments are given
    if len(sys.argv) == 1:
        parser.print_help()
        return

    if args.p:
        infile0set = pd.read_csv(args.input_files[0])
        infile1set = pd.read_csv(args.input_files[1])
        print(infile0set[:10])
        print(infile1set[:10])
    else:
        # create a set() off each input file
        infile0set = set(args.input_files[0])
        infile1set = set(args.input_files[1])

    # process the command arguments
    if args.c:
        newset = infile0set.union(infile1set)
        outputFile(newset, args)

    if args.d:
        newset = infile0set.symmetric_difference(infile1set)
        outputFile(newset, args)

    if args.s:
        newset = infile0set.intersection(infile1set)
        outputFile(newset, args)


if __name__ == "__main__":
    main()
