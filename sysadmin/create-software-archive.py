#!/usr/bin/python3
#
# Simple script to recurse through a directory, find files that are symlinked,
# and compress them into an gzip archive.  This can be used to create deployable
# bundles of software for USB field keys etc.  You can wildcard the symlink
# search so you can find 'TCUFIELD', or 'TCUFIELD*', or 'TCUFIELD[123]' etc.
#
# Author: Derrick Karpo
# Date:   August 7, 2018
#

import argparse
import glob
import os.path
import sys
import tarfile


def main():
    # setup the argument parser for the command line arguments
    parser = argparse.ArgumentParser(
        prog='create-software-archive.py',
        description = "Recurse a directory, find specific symlinked files, and add them to an archive.\n\n" \
                      "ie. '%(prog)s -s TCUFIELD* -i /opt/software -o /opt/software/FIELDKEY.gz'",
                      formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('-s', metavar='symlink', action='store',
                        required=True, help='ie. TCUFIELD')
    parser.add_argument('-i', metavar='input_directory', action='store',
                        required=True, help='ie. /opt/software')
    parser.add_argument('-o', metavar='output_archive', action='store',
                        required=True, help='ie. /opt/fieldkey.gz')
    parser.add_argument("-v", "--verbose", action="store_true",
                      dest="verbose",
                      help="Enable verbose output (useful for debugging).")
    args = parser.parse_args()

    # output help and exit when no arguments are given
    if len(sys.argv) == 1:
        parser.print_help()
        return

    # prepare the archive
    try:
        tar = tarfile.open(args.o, 'w:gz')
    except Exception as e:
        print(sys.stderr, "Exception: %s" % str(e))
        sys.exit("Failed to create the archive!  Exiting.")

    # traverse the input directory, find all the things, and archive them
    SEARCHDIR = os.path.join(args.i, '**', args.s)
    for filename in glob.iglob(SEARCHDIR, recursive=True):
        if os.path.islink(filename):
            (dir, fn) = os.path.split(filename)
            try:
                os.chdir(dir)
                tar.add(os.readlink(fn))
            except Exception as e:
                print("Exception: %s" % str(e))
                print("Failed to add %s.  Permissions issue?" % filename)

    # all done!
    tar.close



if __name__ == "__main__":
    main()
