#!/usr/bin/python3
#
# Traverse a directory of files and make a copy of the tree which
# includes only files with valid mime types.
#
# Note:   Anything specified under the EXCLUDE_MIME variable will be
#         filtered out of the destination directory.
#
# Note 2: This entire script and playing with relative and non-relative
#         paths is gross.  There must be a simpler way to do this...
#
# Author: Derrick Karpo
# Date:   September 12, 2013
#

import os
import magic
import sys
import argparse
from collections import Counter
import shutil
from shutil import copyfile


def locateFilesRelative(root):
    for path, dirs, files in os.walk(root):
        for fn in files:
            relDir = os.path.relpath(path, root)
            relFile = os.path.join(relDir, fn)
            yield(relFile)


def confirmMime(fn):
    return(magic.from_file(fn, mime=True))


def copyFile(fn, inputdir, outputdir):
    if not os.path.exists(outputdir):
        os.mkdir(outputdir)

    try:
        copy_from = os.path.join(inputdir, fn)
        copy_to = os.path.join(outputdir, fn)
        copy_to_directory = os.path.split(copy_to)[0]

        if not os.path.exists(copy_to_directory):
            os.makedirs(copy_to_directory)

        shutil.copy(copy_from, copy_to)
    except OSError as e:
        print('Failed to copy %s: %s' % (fn, e.strerror))


def main():
    # MIME types to exclude from the copy
    EXCLUDE_MIME = ['binary', 'unknown']

    # The signature to give unconfirmed files (should be rarely hit, ie. dangling symlinks)
    UNCONFIRMED_SIGNATURE = 'unknown'

    # file categories
    all_files = {}

    # setup the argument parser for the command line arguments
    parser = argparse.ArgumentParser(
        prog='mime-identify.py',
        description = '''Identify and classify files by MIME type with the option to
                         create a clean tree of files which pass an EXCLUDE_MIME list.''')

    parser.add_argument('-s', action='store_true',
                        dest='statistics', help='Generate statistics summary on all MIME types.')
    parser.add_argument('-i', metavar='input_directory', action='store',
                        dest='inputdir', required=True, help='ie. /opt/dirtyfiles')
    parser.add_argument('-o', metavar='output_directory', action='store',
                        dest='outputdir', help='ie. /opt/cleanfiles')
    parser.add_argument("-v", "--verbose", action="store_true",
                        dest='verbose',
                        help="Enable verbose output (useful for debugging).")
    args = parser.parse_args()

    # output help and exit when no arguments are given
    if len(sys.argv) == 1:
        parser.print_help()
        return

    # process all files and directories in the input directory
    if os.path.exists(args.inputdir):
        # look at all files, if the MIME can be confirmed then assign it
        for fn in locateFilesRelative(args.inputdir):
            try:
                # a valid mime was located
                all_files[fn] = confirmMime(os.path.join(args.inputdir, fn))
            except:
                # this should be rarely hit (ie. dangling symlinks)
                all_files[fn] = UNCONFIRMED_SIGNATURE

        # debug output - print all the files and their mime types
        if args.verbose:
            print("DEBUG: The following files were found in {!s}:".format(args.inputdir))
            for k, v in all_files.items():
                print('{!s} {!s}'.format(k, v))
            print("")

        # a clean list of files to copy with exclusions applied
        for k, v in all_files.items():
            all_files_clean = {k:v for k, v in all_files.items() if v not in EXCLUDE_MIME}

        # debug output - print clean lists of files and their mime types
        if args.verbose:
            print("DEBUG: The following non-excluded files were found in {!s}:".format(args.inputdir))
            for k, v in all_files_clean.items():
                print('{!s} {!s}'.format(k, v))
            print("")

        # copy files to the output directory
        if args.outputdir:
            if not os.path.exists(args.outputdir):
                # copy all confirmed files to the target directory
                print('Copying confirmed MIME files:')
                print('\tFrom {!s}'.format(args.inputdir))
                print('\tTo   {!s}'.format(args.outputdir))

                for k, v in all_files_clean.items():
                    # debug output
                    if args.verbose:
                        print('Copying {!s} -> {!s}'.format(os.path.join(args.inputdir, k), args.outputdir))
                    copyFile(k, args.inputdir, args.outputdir)

                print("Copying Complete.\n")
            else:
                sys.exit('{!s} already exists.  Exiting.'.format(args.outputdir))

        # calculate MIME statistics
        if args.statistics:
            stats_all_files = Counter([values[1] for values in
                                       all_files.items()])

            print("### MIME Statistics ###")
            print('{0:35} {1:10d}'.format('Total files found', len(all_files)))
            print('{0:35} {1:10d}'.format('Total files excluded', len(all_files)-len(all_files_clean)))

            print("\n### MIME Breakdown ###")
            for k, v in sorted(stats_all_files.items()):
                print('{0:35} {1:10d}'.format(k, v))
    else:
        sys.exit('Input directory {!s} does not exist.  Exiting.'.format(args.inputdir))


if __name__ == "__main__":
    main()
