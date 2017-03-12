#!/usr/bin/env python3
#
# Traverse a directory of WeChat Audio files and do the following:
#   1. Copy AMR files as is.
#   2. Convert SILK files with the SILK decoder and further convert to .wav
#   3. Jam a fakey AMR header onto everything else.
#   4. Optional: Convert all files to .mp3
#
# Author: Derrick Karpo
# Date:   January 17, 2016
#
# Notes:
# o This program requires 'decoder' for SILK audio files.
#   - $ git clone https://github.com/ppwwyyxx/wechat-dump.git
#   - $ wechat-dump/third-party/compile_silk.sh
#   - $ sudo /bin/cp wechat-dump/third-party/silk/decoder /usr/local/bin
# o This program requires 'sox' to convert raw SILK files to .wav
#   - $ sudo apt-get install so
# o This program requires 'avconv' to convert .wav files to .mp3
#   - $ sudo apt-get install libav-tools
#

import os
import sys
import argparse
import logging
import subprocess
from shutil import copyfile


def main():
    # setup the argument parser for the command line arguments
    parser = argparse.ArgumentParser(
        prog='wechat-audio-parser.py',
        description='Make WeChat audio files playable')

    parser.add_argument("-f", "--force", action="store_true",
                        dest="force", help="Force overwriting the output directory.")
    parser.add_argument("-m", "--mp3", action="store_true",
                        dest="mp3", help="Convert all audio to MP3 format.")
    parser.add_argument("-l", metavar="logfile", action="store",
                        required=True, help="Enable logging to a file. (required)")
    parser.add_argument('-i', metavar='input_directory', action='store',
                        required=True, help='ie. /opt/originalfiles (required)')
    parser.add_argument('-o', metavar='output_directory', action='store',
                        required=True, help='ie. /opt/fixedupfiles (required)')
    args = parser.parse_args()

    # output help and exit when no arguments are given
    if len(sys.argv) == 1:
        parser.print_help()
        return

    # enable verbose debug logging if called for with '-v'
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)-15s %(levelname)s %(message)s',
                        datefmt='%b %d %H:%M:%S',
                        filename=args.l,
                        filemode='a')
    # define a handler for logging INFO and higher to the console
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(name)-15s %(levelname)s %(message)s',
                                  datefmt='%b %d %H:%M:%S')
    console.setFormatter(formatter)

    # define a handler for all other logging
    logging.getLogger('').addHandler(console)

    # define some custom definitions so we know which stage of the script failed
    logAMR = logging.getLogger('AMR raw')
    logAMRConversion = logging.getLogger('AMR conversion')
    logSILKConversion = logging.getLogger('SILK conversion')
    logMP3Conversion = logging.getLogger('MP3 conversion')

    # test if the external applications exist
    SILKDECODER='/usr/local/bin/decoder'
    SOX='/usr/bin/sox'
    AVCONV='/usr/bin/avconv'
    for EXTERNAL_APPLICATION in SILKDECODER, SOX, AVCONV:
        if not os.path.isfile(EXTERNAL_APPLICATION):
            logging.info("External application '%s' could not be found.  Exiting."
                         % EXTERNAL_APPLICATION)
            sys.exit()

    # confirm the input directory exists and create the output directory
    if os.path.exists(args.i):
        # create the destination directory if it doesn't exist
        if not os.path.exists(args.o):
            os.mkdir(args.o)
        elif args.force:
            # don't stop if force is specified
            pass
        else:
            logging.info("'%s' exists and I won't overwrite it unless forced.  Exiting."
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
                OUTPUT_FILE = os.path.join(args.o, root.lstrip(os.sep), fn)

                # create the output directory if it doesn't exist
                OUTPUT_FILE_PATH = os.path.split(OUTPUT_FILE)[0]
                if not os.path.exists(OUTPUT_FILE_PATH):
                    os.makedirs(OUTPUT_FILE_PATH)

                # read in the input file header (first 32 bytes)
                with open(INPUT_FILE, mode='r', encoding = "ISO-8859-1") as input_file:
                    HEADER_ORIGINAL_FILE = input_file.read(32)
                    input_file.close()

                    # test the header to see what it might be, then do stuff!
                    if 'AMR' in HEADER_ORIGINAL_FILE:
                        try:
                            logAMR.debug("'%s' appears to be an AMR file already.  Copying."
                                         % INPUT_FILE)
                            copyfile(INPUT_FILE, OUTPUT_FILE)
                        except:
                            logAMR.info("Failed to copy '%s'" % OUTPUT_FILE)
                    elif 'SILK' in HEADER_ORIGINAL_FILE:
                        # a multi-step process:
                        #   o run SILK decoder and convert the audio to raw format
                        #   o run sox and convert the raw audio to .wav format and remove the raw
                        #   o delete the raw SILK audio file
                        logSILKConversion.debug("'%s' appears to be a SILK file.  Converting...."
                                               % INPUT_FILE)
                        try:
                            subprocess.check_call([SILKDECODER, INPUT_FILE, OUTPUT_FILE, '-quiet'],
                                                  stdout=open(os.devnull, 'wb'))
                            subprocess.check_call([SOX, '-traw', '-b16', '-esigned-integer',
                                                   '-r24000', OUTPUT_FILE, OUTPUT_FILE + '.wav'],
                                                  stdout=open(os.devnull, 'wb'))
                            logSILKConversion.debug("Deleting '%s'." % OUTPUT_FILE)
                            os.remove(OUTPUT_FILE)
                        except:
                            logSILKConversion.info("Failed to write '%s'" % OUTPUT_FILE)
                    else:
                        logAMRConversion.debug("'%s' unknown.  Adding AMR header.... "
                                              % INPUT_FILE)
                        try:
                            # read in the entire original file
                            with open(INPUT_FILE, mode='rb') as input_file:
                                ENTIRE_ORIGINAL_FILE = input_file.read()
                                input_file.close()

                                # write out the header + original file contents
                                AMRHEADER=b'\x23\x21\x41\x4D\x52\x0A'
                                HEADER_PLUS_FILE = AMRHEADER + ENTIRE_ORIGINAL_FILE
                                output_file = open(OUTPUT_FILE, "wb")
                                output_file.write(HEADER_PLUS_FILE)
                                output_file.close()
                        except:
                            logAMRConversion.info("Failed to write '%s'" % OUTPUT_FILE)
            except OSError as e:
                logging.info("Failed to open '%s': %s" % (INPUT_FILE, e.strerror))


    # optional: convert all output files to mp3 and remove the original file
    if args.mp3:
        for root, dirs, files in os.walk(args.o):
            for fn in files:
                INPUT_FILE = os.path.join(root, fn)
                try:
                    logMP3Conversion.debug("Converting '%s' to mp3." % INPUT_FILE)
                    subprocess.check_call([AVCONV, '-loglevel','quiet', '-i',
                                           INPUT_FILE, INPUT_FILE + '.mp3'])
                    logMP3Conversion.debug("Deleting '%s'." % INPUT_FILE)
                    os.remove(INPUT_FILE)
                except:
                    logMP3Conversion.info("Failed to convert '%s'" % fn)


if __name__ == "__main__":
    main()
