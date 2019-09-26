#!/usr/bin/python3
#
# Download the raw .csv tracking from the "Tracking The World" website.
#
# Author: Derrick Karpo
# Date: September 20, 2019
#

import requests
import sys
import argparse
from bs4 import BeautifulSoup
from datetime import datetime, timedelta


def main():
    # setup the argument parser for the command line arguments
    parser = argparse.ArgumentParser(
        prog='tracking-the-world-csv.py',
        description = "Download the raw .csv file from 'Tracking The World'.",
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-u', action='store', dest='username', required=True,
                        help='Username (required: ie. 12345)')
    parser.add_argument('-p', action='store', dest='password', default='0000',
                        help='Password (optional: default is 0000)')
    parser.add_argument('-s', action='store', dest='startdate', required=True,
                        help='ie. 01-15-2019')
    parser.add_argument('-e', action='store', dest='enddate', required=True,
                        help='ie. 02-15-2019')

    args = parser.parse_args()

    # output help and exit when no arguments are given
    if len(sys.argv) == 1:
        parser.print_help()
        return

    # set the base URL plus start and end dates
    urlBase = 'http://map.trackingtheworld.com'
    startDate = datetime.strptime(args.startdate, '%m-%d-%Y')
    endDate = datetime.strptime(args.enddate, '%m-%d-%Y')
    deltaDate = timedelta(days=1)

    # fail if dates are reversed
    if startDate > endDate:
        sys.exit("Start date is after the end date! Please confirm the dates specified.")

    # loop through all the days
    while startDate <= endDate:
        try:
            # build our initial request URL
            urlFirst = urlBase + '/gmap-bmap.aspx?name=' + args.username + '&calDate=' + startDate.strftime('%m/%d/%Y') + '%2012:00:00%20AM&gpasswd=' + args.password

            # pull the initial HTML which contains the CSV link
            r = requests.get(urlFirst)
            rcontent = r.content
            soup = BeautifulSoup(rcontent, features='lxml')
            # grab the CSV link via the "id=HyperLink2" tag
            a = soup.find(id='HyperLink2', href=True)

            # find the CSV link within the HTML
            try:
                csvhref = a['href']
            except TypeError:
                # if the link can't be found, move on to the next day
                print("No link found for {}. Continuing...".format(startDate))
                startDate += deltaDate
                continue

            # connect to the CSV link and download it
            fname = csvhref.rsplit('/')[1]
            csvurl = urlBase + '/archives/' + fname
            fname = startDate.strftime('%m-%d-%Y') + '-' + fname
            print("Found CSV download link for {}. Saving as {}...".format(startDate, fname), end = "")
            r = requests.get(csvurl)

            # write out the CSV as 'date + original filename' to your currect directory
            try:
                open(fname, 'wb').write(r.content)
                print("done.")
            except Exception as e:
                sys.exit("({})".format(e))

            # move on to the next day
            startDate += deltaDate
        except requests.exceptions.RequestException:
            sys.exit("Failed to connect to {}. Please check the base URL".format(urlBase))
        except Exception as e:
            sys.exit("({})".format(e))


if __name__ == "__main__":
    main()
