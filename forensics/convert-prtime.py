#!/usr/bin/python3
#
# Simple script to convert prtime to something usable
# 
# From https://developer.mozilla.org/en/PRTime:
#
# PRTime is a 64-bit integer representing the number of microseconds since
# the NSPR epoch, midnight (00:00:00) 1 January 1970 Coordinated Universal
# Time (UTC).  A time after the epoch has a positive value, and a time before
# the epoch has a negative value.
#
# Author: Derrick Karpo
# Date:   January 10, 2012
#

import sys
import datetime
import argparse


def convert_prtime(prtime):
    """Convert prtime to localtime and UTC time"""
    try:
        divtime = prtime/1e6
        localtime = datetime.datetime.fromtimestamp(divtime)
        utctime = datetime.datetime.utcfromtimestamp(divtime)
        return "%i, %s, %s" % (prtime, localtime, utctime)
    except:
        return "%i, %s, %s" % (prtime, "invalid", "invalid")


def main():
    # setup the argument parser for the command line arguments
    parser = argparse.ArgumentParser(
        prog='convert-prtime.py', 
        description='Convert PRTime to something usable (CSV Output)')

    parser.add_argument('-t', metavar='prtime', nargs='+', type=int, 
                        help='PRTime (ie. 1306678742795922)')
    parser.add_argument('-i', metavar='input_file', 
                        type=argparse.FileType('rt'),
                        help='Read PRTimes from a file, one PRtime per line')
    parser.add_argument('-v', action='version', 
                        version='%(prog)s 0.1', help='Version')
    args = parser.parse_args()

    # output help and exit when no arguments are given
    if len(sys.argv) == 1:
        parser.print_help()
        return

    # holds orginal prtime and converted prtimes
    converted_prtimes = []

    # process '-t' prtime arguments
    if args.t:
        for prtime in args.t:
            try:
                converted_prtimes.append(convert_prtime(prtime))
            except:
                raise

    # process lines from input file
    if args.i:
        for line in args.i:
            try:
                converted_prtimes.append(convert_prtime(int(line)))
            except:
                raise

    # print out the original and converted prtimes in CSV
    print(', '.join(('prtime', 'localtime', 'utctime')))
    for item in converted_prtimes:
        print(item)


if __name__ == "__main__":
    main()
