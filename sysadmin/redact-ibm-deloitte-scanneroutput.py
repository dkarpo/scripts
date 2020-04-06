#!/usr/bin/env python3
#
# Redacts data from the IBM + Deloitte 'Collection_Function.vbs' XML
# output to remove private information which is unique to the
# environment such a filename paths and user ID's. The script will
# also pretty print the XML output to make it easier to read.
#
# Author: Derrick Karpo
# Date:   February 16, 2020
#

import os
import sys
import argparse
import logging
from lxml import etree
from pathlib import PureWindowsPath


def main():
    # setup the argument parser for the command line arguments
    parser = argparse.ArgumentParser(
        prog='redact-ibm-deloitte-scanneroutput.py',
        description='''Redacts data from the IBM + Deloitte 'Collection_Function.vbs' XML output to remove private information which is unique to the environment. ie. Filename paths and user ID's within the XML.''',
        usage='%(prog)s -i /opt/orig-dir -o /opt/redacted-dir'
    )

    parser.add_argument("-f", "--force", action="store_true", dest="force",
                        help="Force overwriting the output directory.")
    parser.add_argument("-l", metavar="logfile", action="store",
                        help="Enable logging to a file (will suppress all console logging).")
    parser.add_argument('-i', metavar='input_dir', action='store',
                        required=True,
                        help='Directory of XML log files to sanitize.')
    parser.add_argument('-o', metavar='output_dir', action='store',
                        required=True,
                        help='Destination directory to save sanitized XML log files to.')
    args = parser.parse_args()

    # output help and exit when no arguments are given
    if len(sys.argv) == 1:
        parser.print_help()
        return

    # logging to console or redirect to a file if '-l' is provided
    logging.basicConfig(level=logging.INFO,
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
            logging.info("Output directory '%s' exists, won't overwrite unless forced with '-f'. Exiting!"
                         % args.o)
            sys.exit()
    else:
        # bail if the input directory doesn't exist.
        logging.info("Input directory '%s' does not exist. Exiting." % args.i)
        sys.exit("Input directory '%s' does not exist. Exiting." % args.i)

    # parse each input directory file and sanitize it accordingly
    for root, dirs, files in os.walk(args.i):
        for fn in files:
            try:
                INPUT_FILE = os.path.join(root, fn)
                OUTPUT_FILE = os.path.join(args.o, fn)

                # read in the file and sanitize it
                try:
                    # log which file we are processing
                    logging.info("Parsing '%s'" % INPUT_FILE)

                    # read in the entire original XML file and parse it
                    with open(INPUT_FILE, mode='r') as input_file:
                        parser = etree.XMLParser(ns_clean=True)

                        try:
                            tree = etree.parse(INPUT_FILE, parser)
                        # skip the file if it doesn't appear to be XML
                        except etree.XMLSyntaxError:
                            logging.warning("File '%s' does not appear to be XML. Skipping." % INPUT_FILE)
                            continue

                        xmlroot = tree.getroot()
                        input_file.close()

                        # setup the namespace, override the 'None' namespace which panics lxml, nuke it
                        nsmap = xmlroot.nsmap.copy()
                        nsmap['ns'] = nsmap[None]
                        nsmap.pop(None)

                        # redact the <Script> <User> elements
                        redactedUserTotal = 0
                        for element in tree.iterfind('//ns:Script', namespaces=nsmap):
                            for child in element.iterfind('ns:User', namespaces=nsmap):
                                try:
                                    child.text = 'redacted'
                                    redactedUserTotal += 1
                                except:
                                    e = sys.exc_info()[0]
                                    continue

                        # redact the <FileNames> <Path> 'qualified_path' element attributes
                        redactedPathTotal = 0
                        for element in tree.iterfind('//ns:FileNames', namespaces=nsmap):
                            for child in element:
                                try:
                                    pathStart = PureWindowsPath(child.attrib['qualified_path']).anchor
                                    pathEnd = PureWindowsPath(child.attrib['qualified_path']).name
                                    redacted = PureWindowsPath(pathStart).joinpath('***', pathEnd)
                                    child.attrib['qualified_path'] = str(redacted)
                                    redactedPathTotal += 1
                                except:
                                    e = sys.exc_info()[0]
                                    continue

                        # how many items were redacted
                        if (args.l):
                            logging.info("Script -> Admin 'User' items redacted: %i" % redactedUserTotal)
                            logging.info("FileName Path 'qualified_path' items redacted: %i" % redactedPathTotal)

                        # write out the tree, nice and pretty
                        try:
                            tree.write(OUTPUT_FILE,
                                       pretty_print=True,
                                       xml_declaration=True,
                                       encoding='UTF-8')
                        except:
                            logging.warning("Something bad happened!")


                        # parsing complete
                        logging.info("Done parsing '%s'" % INPUT_FILE)
                        logging.info("----------------------------------------------")
                except OSError as e:
                    logging.info("Failed to write '%s'" % (OUTPUT_FILE, e.strerror))
            except OSError as e:
                logging.info("Failed to read '%s': %s" % (INPUT_FILE, e.strerror))


if __name__ == "__main__":
    main()
