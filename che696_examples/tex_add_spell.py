#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Given a file with columns of data (comma or space separated):
return a file that has lines filtered by specified min and max values
"""

from __future__ import print_function

import argparse
import shutil
import sys

from latex_tools.tex_common import (warning, InvalidDataError,
                                    GOOD_RET, INPUT_ERROR)

try:
    # noinspection PyCompatibility
    from ConfigParser import ConfigParser, NoSectionError, ParsingError
except ImportError:
    # noinspection PyCompatibility
    from configparser import ConfigParser, NoSectionError, ParsingError, DuplicateOptionError

__author__ = 'hbmayes'


# Constants #

# Config File Sections

# Defaults
DEF_FILE_PAT = '*tex'
DEF_DICT = '/Applications/texmaker.app/Contents/Resources/en_user.dic'


def parse_cmdline(argv):
    """
    Returns the parsed argument list and return code.
    `argv` is a list of arguments, or `None` for ``sys.argv[1:]``.
    """
    if argv is None:
        argv = sys.argv[1:]

    # initialize the parser object:
    parser = argparse.ArgumentParser(description='Adds a word to a Hunspell-type dictionary file.')

    parser.add_argument("-s", "--sfx", help="Suffix to be added after word (and after a '/'. For example, 'SM' will "
                                            "allow the word to be made plural and possessive. See hunspell "
                                            "documentation for more documentation on codes.", default='')

    parser.add_argument("-d", "--dict_loc", help="Location of the dictionary file to be modified. "
                                                 "The default is: '{}'".format(DEF_DICT), default=DEF_DICT)

    parser.add_argument("new_word", help="The word to add to the dictionary", type=str)

    args = None
    try:
        args = parser.parse_args(argv)
    except (InvalidDataError, IOError, DuplicateOptionError, SystemExit) as e:
        if hasattr(e, 'code') and e.code == 0:
            return args, GOOD_RET
        warning(e)
        parser.print_help()
        return args, INPUT_ERROR

    return args, GOOD_RET


def add_word(new_word, suffix, dict_file):
    """
    Backs a dict backup; overwrites with new word added and sorted; suffix added to new word if applicable
    :param new_word: any new word; not checking for duplicates
    :param suffix: a code to add, according to Hunspell
    :param dict_file: location of dictionary file
    :return:
    """
    print("Adding word '{}' to file: {}".format(new_word, dict_file))

    dict_back = dict_file + '.bak'
    shutil.move(dict_file, dict_back)
    with open(dict_back, "r") as f:
        lines = f.readlines()

    if len(suffix) > 0:
        new_word = new_word + "/" + suffix

    lines[0] = new_word + '\n'
    num_words = len(lines)

    with open(dict_file, "w") as f:
        f.write("{}\n".format(num_words))
        for line in sorted(lines):
            f.write("{}".format(line))


def main(argv=None):
    # Read input
    args, ret = parse_cmdline(argv)
    if ret != GOOD_RET or args is None:
        return ret

    add_word(args.new_word, args.sfx, args.dict_loc)

    return GOOD_RET  # success


if __name__ == '__main__':
    status = main()
    sys.exit(status)
