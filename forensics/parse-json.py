#!/usr/bin/python3
#
# Parse JSON data and pretty print it.  Nothing special.
#
# Author: Derrick Karpo
# Date: April 4, 2013
#

import sys
import json
from pprint import pprint
from optparse import OptionParser


def parseOptions():
    if len(sys.argv) == 1:
        sys.argv.append('-h')

    usage = "usage: %prog [options] filename"
    description = "Parse JSON data and output it in various formats"

    parser = OptionParser(usage=usage, description=description)
    parser.add_option("-p", action="store_true", dest="pprint",
                      help="Pretty print the JSON output.")
    (opts, args) = parser.parse_args()
    return (opts, args)

def main():
    # read command line options
    (opts, args) = parseOptions()

    # read the JSON file and parse it, this is read line-by-line
    # just in case malformed JSON is fed in as we may be able to
    # extract more data than reading in entire file in one read
    try:
        data = []
        with open(args[0]) as f:
            for line in f:
                data.append(json.loads(line))

        if opts.pprint:
            print(data.decode("unicode_escape").encode("utf8","replace"))
    except IOError as e:
        sys.exit("({})".format(e))


if __name__ == "__main__":
    main()
