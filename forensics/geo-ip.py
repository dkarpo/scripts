#!/usr/bin/python
#
# Attempt to geographically locate an IPv4 address.
#
# Requires the GeoLite City database from MaxMind for local lookups.  For local
# lookups download 'GeoLiteCity.dat' in the same directory as the script.  See:
#
# * http://www.maxmind.com/app/geolitecity
#
# Author: Derrick Karpo
# Date:   January 23, 2008
#

import os
import sys

try:
    import GeoIP
    from optparse import OptionParser
except ImportError:
    raise ImportError, 'Missing GeoIP and OptionParser modules for python.'


def parseOptions():
    if len(sys.argv) == 1:
        sys.argv.append('-h')

    usage = "usage: %prog [-l|-w] ip"
    description = "Attempt to geographically locate an IP address"

    parser = OptionParser(usage=usage, description=description)
    parser.add_option("-l", action="store_true", dest="dolocal",
                      help="Use local database (recommended).")
    parser.add_option("-w", action="store_true", dest="doweb",
                      help="Use Internet for lookup.")
    parser.add_option("-i", action="store", type="string", dest="infile",
                      help="Read input from FILE", metavar="FILE")
    (opts, args) = parser.parse_args()
    return (opts, args)


def main():
    # local and web lookup results
    results_local_lookup = {}
    results_web_lookup = {}

    # read command line options
    (opts, args) = parseOptions()

    # parse file
    if opts.infile:
        try:
            f = open(opts.infile, 'r')
        except:
            print "Unable to open input file '%s'" % opts.infile

    # search local database
    if opts.dolocal:
        __dir__ = os.path.dirname(os.path.abspath(__file__))
        geoip_lib = os.path.join(__dir__, 'GeoLiteCity.dat')
        geoip = GeoIP.open(geoip_lib, GeoIP.GEOIP_MEMORY_CACHE)

        # parse command line ip's
        for ip in args:
            try:
                r = geoip.record_by_addr(ip)
                results_local_lookup[ip] = (r['city'],
                          r['region'],
                          r['country_name'])
            except:
                results_local_lookup[ip] = None

    # search web
    if opts.doweb:
        geoip = GeoIP.new(GeoIP.GEOIP_MEMORY_CACHE)

        for ip in args:
            results_web_lookup[ip] = geoip.country_code_by_addr(ip)

    # print the local results
    if results_local_lookup:
        results_local_lookups = sorted(results_local_lookup.iteritems(), key=lambda(k,v): k)
        print "*** local results ***"
        for result in results_local_lookups:
            print result

    # print the web results
    if results_web_lookup:
        # note: web lookup always returns "None" if not found
        results_web_lookups = sorted(results_web_lookup.iteritems(), key=lambda(k,v): k)
        print "*** web results ***"
        for result in results_web_lookups:
            print result


if __name__ == "__main__":
    main()
