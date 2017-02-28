#!/usr/bin/python3
#
# Traverse a directory of files and overwrite every file with a sane file.
# This is useful when you need to redact a directory of pictures with a
# single clean picture and keep the original file names.
#
# Author: Derrick Karpo
# Date:   April 21, 2016
#

import os
import sys
import argparse

def locateFilesRelative(root):
    for path, dirs, files in os.walk(root):
        for fn in files:
            relDir = os.path.relpath(path, root)
            relFile = os.path.join(relDir, fn)
            yield(relFile)


def sanitizeFile(sanefile, outputfile):
    try:
        f = open(outputfile, 'wb')
        f.write(sanefile)
        f.close()
    except OSError as e:
        print('Failed to sanitize %s: %s' % (fn, e.strerror))


def main():
    # file categories
    files_processed = {}
    files_failed = {}

    # setup the argument parser for the command line arguments
    parser = argparse.ArgumentParser(
        prog='redact-files.py',
        description = '''Recursively overwrite all files in a directory with a single clean file.''')

    parser.add_argument('-i', type=argparse.FileType('rb'), metavar='input_file', action='store',
                        dest='inputfile', required=True, help='ie. clean-picture.jpg')
    parser.add_argument('-o', metavar='output_directory', action='store',
                        dest='outputdir', required=True, help='ie. /opt/directory-to-overwrite')
    args = parser.parse_args()

    # output help and exit when no arguments are given
    if len(sys.argv) == 1:
        parser.print_help()
        return

    # open up our clean file and read it in
    with args.inputfile as f:
        cleanfile = f.read()

    # overwrite all files in the output directory
    if os.path.exists(args.outputdir):
        # look at all files, open them, and overwrite their contents..
        for fn in locateFilesRelative(args.outputdir):
            try:
                files_processed[fn] = sanitizeFile(cleanfile, os.path.join(args.outputdir, fn))
            except:
                # this should be rarely hit (ie. permissions issues)
                files_failed[fn] = 'FAILED'
    else:
        sys.exit('Outupt directory {!s} does not exist.  Exiting.'.format(args.outputdir))

    # report on the files processed
    print('### File Processed ###')
    print('{0:20} {1:10d}'.format('Files overwritten:', len(files_processed)))
    print('{0:20} {1:10d}'.format('Files which failed:', len(files_failed)))

    # if files failed to process, report them
    if files_failed:
        print('\n' + '### Files which failed to process ###')
        for fn in files_failed:
            print(fn)


if __name__ == "__main__":
    main()
