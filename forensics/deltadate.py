#!/usr/bin/python
#
# Calculate the delta between two dates and/or times.
#
# Author: Derrick Karpo
# Date:   August 29, 2008
#

import re
import sys
import time
from datetime import datetime

try:
    from optparse import OptionParser
except ImportError:
    raise ImportError, 'This program requires the OptionParser extension for Python.'


def parseOptions():
    if len(sys.argv) == 1:
        sys.argv.append('-h')

    usage = "usage: %prog 'date1' 'date2' (date format is '%m/%d/%Y %H:%M:%S')"
    description = "Determine the delta between two dates/time."

    parser = OptionParser(usage=usage, description=description)
    parser.add_option("-d", action="store_true", dest="debug",
                      help="Run the script with debug values for testing.")
    (opts, args) = parser.parse_args()
    return (opts, args)


def main():
    # read command line options
    (opts, args) = parseOptions()

    if opts.debug:
        # sample data
        date1 = '01/01/2008 18:20:20'
        date2 = '01/02/2008 19:40:40'
        print "Using sample data %s and %s." % (date1, date2)
    else:
        date1 = sys.argv[1]
        date2 = sys.argv[2]

    for date in date1, date2:
        pattern = re.compile("\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}")
        match = pattern.search(date)

        if match:
            continue
        else:
            print "Date %s is not in format '%%m/%%d/%%Y %%H:%%M:%%S' " \
                  "ie. '01/01/2008 15:20:20'" % date
            exit(1)

    pattern = '%m/%d/%Y %H:%M:%S'
    t1 = datetime.strptime(date1, pattern)
    t2 = datetime.strptime(date2, pattern)
    s1 = time.mktime(t1.timetuple())
    s2 = time.mktime(t2.timetuple())

    diff = t2 - t1
    weeks, days = divmod(diff.days, 7)

    print '%i seconds' % (s2 - s1)
    print '%s hours.' % diff
    print '%i weeks and %i days.' % (weeks, days)


if __name__ == "__main__":
    main()
