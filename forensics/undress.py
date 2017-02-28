#!/usr/bin/python
#
# Detect multilayer images and graphic file signatures (slightly broken).
#
# Author: Derrick Karpo
# Date: June 3, 2008
#

import glob
import os
import sys
import re
import fnmatch

try:
    from optparse import OptionParser
    from PIL import Image
except ImportError:
    raise ImportError, 'This program requires the OptionParser and PIL extensions for Python.'


def parseOptions():
    if len(sys.argv) == 1:
        sys.argv.append('-h')

    usage = "usage: %prog [options]"
    description = "Search a directory(s) for graphic files to expose " \
                  "multilayer images or files that don't match their " \
                  "file signatures.  ie. %prog -l -s -p '*.psd' -d /var/tmp"

    parser = OptionParser(usage=usage, description=description)
    parser.add_option("-v", action="store_true", dest="do_verbose",
                      help="Enable verbose mode.  This will classify supported and unsupported files.")
    parser.add_option("-l", action="count", dest="do_layered",
                      help="Detect layered images.  Use twice (ie. -ll) to detect and extract layers.")
    parser.add_option("-s", action="store_true", dest="do_signature",
                      help="Check file signatures.")
    parser.add_option("-p", action="store", dest="pattern", default='*',
                      help="File or path to read ie. '*.psd' or '*' (defaults to all files).")
    parser.add_option("-d", action="store", dest="directory", default='.',
                      help="Directory to search (defaults to current directory).")
    (opts, args) = parser.parse_args()
    return (opts, args)


def extractLayersPIL(f):
    """Extract layers from multilayer images using PIL"""
    try:
        i = Image.open(f)
        for index, layer in enumerate(i.layers):
            i.seek(index)
            i.save("%s-layer-%03d.jpg" % (f, index))
    except IOError:
        return


def locateFiles(pattern, root=os.curdir):
    """Locate all files matching supplied filename pattern
       in and below supplied root directory."""
    for path, dirs, files in os.walk(os.path.abspath(root)):
        for filename in fnmatch.filter(files, pattern):
            yield os.path.join(path, filename)


def main():
    """Runs program and handles command line options"""
    # variables
    filesSupported = {}
    filesUnsupported = {}

    # read command line options
    (opts, args) = parseOptions()

    # load 'em up
    for infile in locateFiles(opts.pattern, opts.directory):
        # attempt to open the file with PIL
        try:
            file, ext = os.path.splitext(infile)
            i = Image.open(infile)
        except Exception, anException:
            filesUnsupported[infile] = anException
            continue

        # signature detection
        p = re.compile(i.format, re.IGNORECASE)
        if p.search(ext):
            signature = 'matched'
        else:
            signature = 'unmatched'

        # multilayer detection (could also use i.tell())
        try:
            i.seek(1)
            layered = 'multilayer'
        except EOFError:
            layered = 'singlelayer'

        # software detection (useful for detecting pictures that come from
        # application like 'Macromedia Fireworks MX' which can contain
        # layers that are only viewable and detectable in their native app
        try:
            software = i.info['Software']
        except:
            software = "unknown"

        # done processing
        filesSupported[infile] = i.format, \
                                 i.mode, \
                                 signature, \
                                 layered, \
                                 software

    # now do something
    if opts.do_verbose:
        if filesSupported:
            print 'All Supported Files:'
            for k, v in filesSupported.iteritems():
                print k, v

        if filesUnsupported:
            print '\nUnsupported Files:'
            if filesUnsupported:
                for k, v in filesUnsupported.iteritems():
                    print k, v
            else:
                print 'None'
        print

    if opts.do_layered >= 1:
        print 'Layered:'
        for k, v in filesSupported.iteritems():
            if re.match('multilayer', v[3]):
                print k, v
                if opts.do_layered == 2:
                    extractLayersPIL(k)
        print

    # *** Signature detection is broken in regards to .jpg != JPEG ***
    if opts.do_signature:
        print 'Bad Signatures:'
        for k, v in filesSupported.iteritems():
            if re.match('unmatched', v[2]):
                print k, v
        print


if __name__ == "__main__":
    main()
