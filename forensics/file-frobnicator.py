#!/usr/bin/env python3
#
# Traverse a directory of files and prepend or append user supplied bytes to
# the files.  This can be useful when you have a directory of files that are
# unusable until you add a magic byte header or footer to them.
#
# Author: Derrick Karpo
# Date:   January 29, 2017
#

import os
import sys
import argparse
import logging
from binascii import unhexlify


def hex_bytes(arg):
    # strip any whitespae and convert the argument to raw hex
    value = unhexlify(arg.replace(" ", ""))
    return value


def main():
    # setup the argument parser for the command line arguments
    parser = argparse.ArgumentParser(
        prog='file-frobnicator.py',
        description='''Prepend or append bytes to all files in a directory.  Bytes
        can be specified in upper or lower case and with or without spaces.  The
        original files are left untouched and all modifed files are saved to the
        specified output directory.  Both prepending and appending can be done
        individually or simultaneously.''',
        usage='%(prog)s -p ffd8ffe1 -a deadbeef -i /opt/origfiles -o /opt/fixedfiles'
    )

    parser.add_argument("-f", "--force", action="store_true", dest="force",
                        help="Force overwriting the output directory.")
    parser.add_argument("-l", metavar="logfile", action="store",
                        help="Enable logging to a file (will suppress console logging).")
    parser.add_argument('-i', metavar='input_dir', action='store',
                        required=True,
                        help='Directory of files that need added bytes.')
    parser.add_argument('-o', metavar='output_dir', action='store',
                        required=True,
                        help='Destination directory to save fixed up files to.')
    parser.add_argument('-p', metavar='pbytes', action='store', type=hex_bytes,
                        help='Bytes to prepend ie. "ffd8ffe1" (semi-required)')
    parser.add_argument('-a', metavar='abytes', action='store', type=hex_bytes,
                        help='Bytes to append ie. "ffaa" (semi-required)')
    args = parser.parse_args()

    # output help and exit when no arguments are given
    if len(sys.argv) == 1:
        parser.print_help()
        return

    # logging to console or redirect to a file if '-l' is provided
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(filename)-15s %(levelname)s %(message)s',
                        datefmt='%b %d %H:%M:%S',
                        filename=args.l,
                        filemode='a')
    # define a handler for logging INFO and higher to the console
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(filename)-15s %(levelname)s %(message)s',
                                  datefmt='%b %d %H:%M:%S')
    console.setFormatter(formatter)

    # confirm the input directory exists and create the output directory
    if os.path.exists(args.i):
        # create the destination directory if it doesn't exist
        if not os.path.exists(args.o):
            os.mkdir(args.o)
        elif args.force:
            # don't stop if force is specified
            pass
        else:
            logging.info("'%s' exists, won't overwrite unless forced.  Exiting."
                         % args.o)
            sys.exit()
    else:
        # bail if the input directory doesn't exist.
        logging.info("Input directory '%s' does not exist.  Exiting." % args.i)
        sys.exit()

    # parse each input directory file and convert accordingly
    for root, dirs, files in os.walk(args.i):
        for fn in files:
            try:
                INPUT_FILE = os.path.join(root, fn)
                OUTPUT_FILE = os.path.join(args.o, fn)

                # read in the file and add in the bytes!
                try:
                    # log which file we are processing
                    logging.debug("Frobnicating '%s'" % INPUT_FILE)
                    # read in the entire original file
                    with open(INPUT_FILE, mode='rb') as input_file:
                        ORIGINAL_FILE = input_file.read()
                        input_file.close()
                        if (args.p and args.a):
                            # prepended bytes + original file + appended bytes
                            NEW_FILE = args.p + ORIGINAL_FILE + args.a
                        elif (args.p):
                            # prepended bytes + original file
                            NEW_FILE = args.p + ORIGINAL_FILE
                        elif (args.a):
                            # original file + appended bytes
                            NEW_FILE = ORIGINAL_FILE + args.a
                        else:
                            # bail if the user didn't supply any bytes!
                            logging.info("No bytes provided to prepend or append!  Exiting.")
                            sys.exit()

                        # write out the new file with the extra bytes
                        output_file = open(OUTPUT_FILE, "wb")
                        output_file.write(NEW_FILE)
                        output_file.close()
                except OSError as e:
                    logging.info("Failed to write '%s'" % (OUTPUT_FILE, e.strerror))
            except OSError as e:
                logging.info("Failed to read '%s': %s" % (INPUT_FILE, e.strerror))


if __name__ == "__main__":
    main()
