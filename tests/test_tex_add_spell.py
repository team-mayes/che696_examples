#!/usr/bin/env python3
# coding=utf-8

import unittest
import os
import logging
from shutil import copyfile
from che696_examples.common import capture_stdout, capture_stderr, diff_lines, silent_remove
from che696_examples.tex_add_spell import main

__author__ = 'hbmayes'

# logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
DISABLE_REMOVE = logger.isEnabledFor(logging.DEBUG)

# Directories #

DATA_DIR = os.path.join(os.path.dirname(__file__), 'test_data')
SUB_DATA_DIR = os.path.join(DATA_DIR, 'tex_add_spell')

# Input files #

USER_DICT = os.path.join(SUB_DATA_DIR, "en_user.dic")
DICT_COPY = os.path.join(SUB_DATA_DIR, "temp_en_user.dic")
DICT_BACK = os.path.join(SUB_DATA_DIR, "temp_en_user.dic.bak")
GOOD_DICT = os.path.join(SUB_DATA_DIR, "good_en_user.dic")
GOOD_DICT2 = os.path.join(SUB_DATA_DIR, "good2_en_user.dic")


# Output files #

# noinspection PyUnresolvedReferences
CSV_OUT = os.path.join(SUB_DATA_DIR, "filtered_column_data.csv")


class TestMain(unittest.TestCase):
    def testGood(self):
        copyfile(USER_DICT, DICT_COPY)
        test_input = ["hello", "-d", DICT_COPY]
        try:
            main(test_input)
            self.assertFalse(diff_lines(DICT_COPY, GOOD_DICT))
        finally:
            silent_remove(DICT_COPY, disable=DISABLE_REMOVE)
            silent_remove(DICT_BACK, disable=DISABLE_REMOVE)

    def testCapitalGood(self):
        copyfile(USER_DICT, DICT_COPY)
        test_input = ["Goodbye", "-s", "S", "-d", DICT_COPY]
        try:
            main(test_input)
            self.assertFalse(diff_lines(DICT_COPY, GOOD_DICT2))
        finally:
            silent_remove(DICT_COPY, disable=DISABLE_REMOVE)
            silent_remove(DICT_BACK, disable=DISABLE_REMOVE)


class TestFailWell(unittest.TestCase):
    def testNoArgs(self):
        test_input = []
        if logger.isEnabledFor(logging.DEBUG):
            main(test_input)

    def testHelp(self):
        test_input = ["-h"]
        if logger.isEnabledFor(logging.DEBUG):
            main(test_input)
        with capture_stderr(main, test_input) as output:
            self.assertFalse(output)
        with capture_stdout(main, test_input) as output:
            self.assertTrue("optional arguments" in output)

    def testMissingWord(self):
        test_input = ["-d", USER_DICT]
        if logger.isEnabledFor(logging.DEBUG):
            main(test_input)
        with capture_stderr(main, test_input) as output:
            self.assertTrue("new_word" in output)


