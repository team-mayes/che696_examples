#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Adds a string to the beginning and end of a file.
"""

from __future__ import print_function

import sys
from che696_examples.common import (create_out_fname, warning, ThrowingArgumentParser,
                                    ArgumentParserError, GOOD_RET, INPUT_ERROR, IO_ERROR)

__author__ = 'hmayes'


# Constants #

# Defaults
DEF_BEGIN_STR = ''
DEF_END_STR = ''
DEF_NEW_FNAME = None


def parse_cmdline(argv):
    """
    Returns the parsed argument list and return code.
    `argv` is a list of arguments, or `None` for ``sys.argv[1:]``.
    """
    if argv is None:
        argv = sys.argv[1:]

    # initialize the parser object:
    parser = ThrowingArgumentParser(description='Reads in a file and adds a beginning and/or end to each line. '
                                                'The first argument must be the name of the file to be read.')
    # Below, it is a positional argument, that is required.
    parser.add_argument("file", help="The location of the file to be amended (required).", )
    parser.add_argument("-b", "--begin", help="String to add to the beginning of a line.",
                        default=DEF_BEGIN_STR)
    parser.add_argument("-e", "--end", help="String to add to the end of a line.",
                        default=DEF_END_STR)
    parser.add_argument("-n", "--new_name", help="Name of amended file.",
                        default=DEF_NEW_FNAME)
    args = None

    try:
        args = parser.parse_args(argv)
        if args.begin == DEF_BEGIN_STR and args.end == DEF_END_STR:
            warning("Return file will be the same as the input, as no begin or end strings were passed. "
                    "Use -h for help.")
    except ArgumentParserError as e:
        warning("Argument Parser Error:", e)
        parser.print_help()
        return args, INPUT_ERROR

    return args, GOOD_RET


def process_file(f_name, b_str, e_str, new_f_name):

    if new_f_name is None:
        new_f_name = create_out_fname(f_name, suffix='_amend')

    # open old file first; then if, there is a problem with it, no new file will be created
    with open(f_name) as f:
        with open(new_f_name, 'w') as w_file:
            for line in f:
                line = line.strip()
                w_file.write(b_str + line + e_str + "\n")
    print("Wrote file: {}".format(new_f_name))


def main(argv=None):
    # Read input
    args, ret = parse_cmdline(argv)
    if ret != GOOD_RET:
        return ret

    try:
        process_file(args.file, args.begin, args.end, args.new_name)
    except IOError as e:
        warning("Problems reading file:", e)
        return IO_ERROR

    return GOOD_RET  # success


if __name__ == '__main__':
    status = main()
    sys.exit(status)
