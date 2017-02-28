#!/usr/bin/env python3
#
# Extract the zip archive password from Furious Gold physical or partition dumps.
#
# Author: Derrick Karpo
# Date:   May 4, 2016
#

import sys
import re
import zipfile
import hashlib
import argparse

def extractFuriousGoldZipPassword(archive):
    zf = zipfile.ZipFile(archive)

    # look for Rid (from Android dumps)
    try:
        pattern = re.compile('Rid: (\w+)')
        match = pattern.search(zf.comment.decode())
        passwordHash = match.group(1)
        m = hashlib.sha1()
        m.update(passwordHash.encode('utf-8'))
        return(m.hexdigest().upper())
    except:
        pass

    # look for IMEI (from MTK devices)
    try:
        pattern = re.compile('IMEI1 [OTP]: (\w+)')
        match = pattern.search(zf.comment.decode())
        passwordHash = match.group(1)
        m = hashlib.sha1()
        m.update(passwordHash.encode('utf-8'))
        return(m.hexdigest().upper())
    except:
        sys.exit("Failed to find 'Rid' or 'IMEI' hash in '%s'" % archive)


def main():
    # setup the argument parser for the command line arguments
    parser = argparse.ArgumentParser(
        prog='furious-gold-extract-zip-password.py',
        description = '''Extract the Furious Gold zip password from physical or partition dumps.''')

    parser.add_argument('-i', metavar='input_file', action='store',
                        dest='inputfile', required=True,
                        help='Furious Gold zip archive (ie. MEMORY_DUMP.osp)')
    args = parser.parse_args()

    # output help and exit when no arguments are given
    if len(sys.argv) == 1:
        parser.print_help()
        return

    # open up the zip file and spit out the password
    zipPassword = extractFuriousGoldZipPassword(args.inputfile)
    print("The zip archive password is:", zipPassword)


if __name__ == '__main__':
    main()
