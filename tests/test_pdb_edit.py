#!/usr/bin/env python3
#  coding=utf-8
import unittest
import os
from che696_examples.pdb_edit import main
from che696_examples.common import diff_lines, capture_stderr, silent_remove, capture_stdout
import logging

# logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
DISABLE_REMOVE = logger.isEnabledFor(logging.DEBUG)

__author__ = 'hmayes'

DATA_DIR = os.path.join(os.path.dirname(__file__), 'test_data')
SUB_DATA_DIR = os.path.join(DATA_DIR, 'pdb_edit')

DEF_INI = os.path.join(SUB_DATA_DIR, 'pdb_edit.ini')
# noinspection PyUnresolvedReferences
DEF_OUT = os.path.join(SUB_DATA_DIR, 'new.pdb')
GOOD_OUT = os.path.join(SUB_DATA_DIR, 'glue_autopsf_short_good.pdb')
GOOD_MOL_CHANGE_OUT = os.path.join(SUB_DATA_DIR, 'glue_autopsf_short_mol_change_good.pdb')
GOOD_MOL_CHANGE_RENUM_OUT = os.path.join(SUB_DATA_DIR, 'glue_autopsf_short_mol_change_renum_good.pdb')

MOL_CHANGE_INI = os.path.join(SUB_DATA_DIR, 'pdb_edit_mol_change.ini')
MOL_CHANGE_RENUM_INI = os.path.join(SUB_DATA_DIR, 'pdb_edit_mol_renum.ini')

ADD_ELEMENT_INI = os.path.join(SUB_DATA_DIR, 'pdb_edit_add_element.ini')
ADD_ELEMENT_OUT = os.path.join(SUB_DATA_DIR, 'glue_autopsf_short_no_elements_new.pdb')
GOOD_ADD_ELEMENT_OUT = os.path.join(SUB_DATA_DIR, 'glue_autopsf_short.pdb')

READ_ELEM_DICT_INI = os.path.join(SUB_DATA_DIR, 'pdb_edit_add_element_read_dict.ini')
GOOD_READ_ELEM_OUT = os.path.join(SUB_DATA_DIR, 'glue_autopsf_short_read_dict_good.pdb')

READ_ELEM_DICT_KEEP_ELEM_INI = os.path.join(SUB_DATA_DIR, 'pdb_edit_read_elem_dict_keep_elem.ini')

EMRE_ADD_ELEMENT_INI = os.path.join(SUB_DATA_DIR, 'pdb_edit_emre_add_element.ini')
EMRE_ADD_ELEMENT_OUT = os.path.join(SUB_DATA_DIR, 'emre_test_new.pdb')
GOOD_EMRE_ADD_ELEMENT_OUT = os.path.join(SUB_DATA_DIR, 'emre_test_good.pdb')

QMMM_OUT_INI = os.path.join(SUB_DATA_DIR, 'pdb_edit_qmmm_output.ini')
QMMM_PDB_IN = os.path.join(SUB_DATA_DIR, 'glue_revised.pdb')
QMMM_PDB_OUT = os.path.join(SUB_DATA_DIR, 'glue_revised_new.pdb')
QMMM_OUT = os.path.join(SUB_DATA_DIR, 'amino_id.dat')
GOOD_QMMM_OUT = os.path.join(SUB_DATA_DIR, 'amino_id_good.dat')
VMD_ATOMS_OUT = os.path.join(SUB_DATA_DIR, 'vmd_protein_atoms.dat')
GOOD_VMD_ATOMS_OUT = os.path.join(SUB_DATA_DIR, 'vmd_protein_atoms_good.dat')

# For catching errors
ATOM_DICT_REPEAT_INI = os.path.join(SUB_DATA_DIR, 'pdb_edit_repeat_key.ini')
ATOM_DICT_BAD_INI = os.path.join(SUB_DATA_DIR, 'pdb_edit_bad_reorder.ini')
NO_PDB_INI = os.path.join(SUB_DATA_DIR, 'pdb_edit_no_pdb.ini')
UNEXPECTED_KEY_INI = os.path.join(SUB_DATA_DIR, 'pdb_edit_wrong_key.ini')
CHECK_WATER_ORDER_INI = os.path.join(SUB_DATA_DIR, 'pdb_edit_check_water_order.ini')
ADD_ELEMENT_MISSING_TYPE_INI = os.path.join(SUB_DATA_DIR, 'pdb_edit_missing_type_add_element.ini')
ADD_ELEMENT_MISSING_OUT = os.path.join(SUB_DATA_DIR, 'glue_autopsf_short_missing_type_new.pdb')
ADD_ELEMENT_MISSING_ORIG = os.path.join(SUB_DATA_DIR, 'glue_autopsf_short_missing_type.pdb')

WATER_OUT_OF_ORDER_MESSAGES = ["Expected an OH2 atom", "Expected an H1 atom", "Expected an H2 atom",
                               "Water not in order on line"]


class TestPDBEditMain(unittest.TestCase):
    # Testing normal function; can use inputs here as examples
    def testReorderAtoms(self):
        try:
            with capture_stdout(main, ["-c", DEF_INI]) as output:
                for message in WATER_OUT_OF_ORDER_MESSAGES:
                    self.assertFalse(message in output)
            self.assertFalse(diff_lines(DEF_OUT, GOOD_OUT))
        finally:
            silent_remove(DEF_OUT)

    def testChangeMol(self):
        try:
            main(["-c", MOL_CHANGE_INI])
            self.assertFalse(diff_lines(DEF_OUT, GOOD_MOL_CHANGE_OUT))
        finally:
            silent_remove(DEF_OUT, disable=DISABLE_REMOVE)

    def testChangeRenumMol(self):
        try:
            main(["-c", MOL_CHANGE_RENUM_INI])
            self.assertFalse(diff_lines(DEF_OUT, GOOD_MOL_CHANGE_RENUM_OUT))
        finally:
            silent_remove(DEF_OUT, disable=DISABLE_REMOVE)

    def testAddElements(self):
        try:
            silent_remove(ADD_ELEMENT_OUT)
            main(["-c", ADD_ELEMENT_INI])
            self.assertFalse(diff_lines(ADD_ELEMENT_OUT, GOOD_ADD_ELEMENT_OUT))
        finally:
            silent_remove(ADD_ELEMENT_OUT, disable=DISABLE_REMOVE)

    def testAddElemReadDict(self):
        # There will be a missing element because of a missing key in the specified dictionary
        test_input = ["-c", READ_ELEM_DICT_INI]
        try:
            silent_remove(ADD_ELEMENT_OUT)
            if logger.isEnabledFor(logging.DEBUG):
                main(test_input)
                silent_remove(ADD_ELEMENT_OUT)
            with capture_stderr(main, test_input) as output:
                self.assertTrue("Please add atom type" in output)
            self.assertFalse(diff_lines(ADD_ELEMENT_OUT, GOOD_READ_ELEM_OUT))
        finally:
            silent_remove(ADD_ELEMENT_OUT, disable=DISABLE_REMOVE)

    def testAddElemReadDictNoOverwrite(self):
        # Make sure preserves the element from the original pdb even though not in the read dict
        test_input = ["-c", READ_ELEM_DICT_KEEP_ELEM_INI]
        try:
            silent_remove(DEF_OUT)
            if logger.isEnabledFor(logging.DEBUG):
                main(test_input)
            else:
                with capture_stderr(main, ["-c", READ_ELEM_DICT_KEEP_ELEM_INI]) as output:
                    self.assertTrue("Please add atom type" in output)
                self.assertFalse(diff_lines(DEF_OUT, GOOD_ADD_ELEMENT_OUT))
        finally:
            silent_remove(DEF_OUT, disable=DISABLE_REMOVE)

    def testEmreAddElements(self):
        # As above, but a larger/different PDB
        try:
            main(["-c", EMRE_ADD_ELEMENT_INI])
            self.assertFalse(diff_lines(EMRE_ADD_ELEMENT_OUT, GOOD_EMRE_ADD_ELEMENT_OUT))
        finally:
            silent_remove(EMRE_ADD_ELEMENT_OUT, disable=DISABLE_REMOVE)

    def testPrintQMMM(self):
        try:
            main(["-c", QMMM_OUT_INI])
            self.assertFalse(diff_lines(QMMM_PDB_OUT, QMMM_PDB_IN))
            self.assertFalse(diff_lines(QMMM_OUT, GOOD_QMMM_OUT))
            self.assertFalse(diff_lines(VMD_ATOMS_OUT, GOOD_VMD_ATOMS_OUT))
        finally:
            silent_remove(QMMM_PDB_OUT, disable=DISABLE_REMOVE)
            silent_remove(QMMM_OUT, disable=DISABLE_REMOVE)
            silent_remove(VMD_ATOMS_OUT, disable=DISABLE_REMOVE)


class TestPDBEditCatchImperfectInput(unittest.TestCase):
    # Testing for elegant failure and hopefully helpful error messages
    def testHelp(self):
        test_input = ['-h']
        if logger.isEnabledFor(logging.DEBUG):
            main(test_input)
        with capture_stderr(main, test_input) as output:
            self.assertFalse(output)
        with capture_stdout(main, test_input) as output:
            self.assertTrue("optional arguments" in output)

    def testNoIni(self):
        # main(["-c", "ghost.ini"])
        with capture_stderr(main, ["-c", "ghost.ini"]) as output:
            self.assertTrue("Could not read file" in output)

    def testMissingReqKey(self):
        # main(["-c", NO_PDB_INI])
        with capture_stderr(main, ["-c", NO_PDB_INI]) as output:
            self.assertTrue("Missing config val" in output)

    def testUnexpectedKey(self):
        # main(["-c", UNEXPECTED_KEY_INI])
        with capture_stderr(main, ["-c", UNEXPECTED_KEY_INI]) as output:
            self.assertTrue("Unexpected key" in output)

    def testRepeatKeyNumDict(self):
        # main(["-c", ATOM_DICT_REPEAT_INI])
        with capture_stderr(main, ["-c", ATOM_DICT_REPEAT_INI]) as output:
            self.assertTrue("non-unique" in output)

    def testReadBadAtomNumDict(self):
        # main(["-c", ATOM_DICT_BAD_INI])
        with capture_stderr(main, ["-c", ATOM_DICT_BAD_INI]) as output:
            self.assertTrue("xx" in output)
            self.assertTrue("Problems with input" in output)

    def testAddElementsMissingType(self):
        test_input = ["-c", ADD_ELEMENT_MISSING_TYPE_INI]
        try:
            if logger.isEnabledFor(logging.DEBUG):
                main(test_input)
            else:
                with capture_stderr(main, test_input) as output:
                    # testing that only get the warning once, so check output length. May change wording a bit,
                    # so checked than less than length + a buffer (which is less than if multiple warnings are printed)
                    self.assertLess(len(output), 200)
                    self.assertTrue("Please add atom type" in output)
                self.assertFalse(diff_lines(ADD_ELEMENT_MISSING_OUT, ADD_ELEMENT_MISSING_ORIG))
        finally:
            silent_remove(ADD_ELEMENT_MISSING_OUT, disable=DISABLE_REMOVE)

    def testCheckWaterOrder(self):
        test_input = ["-c", CHECK_WATER_ORDER_INI]
        if logger.isEnabledFor(logging.DEBUG):
            main(test_input)
        try:
            with capture_stderr(main, test_input) as output:
                for message in WATER_OUT_OF_ORDER_MESSAGES:
                    self.assertTrue(message in output)
                self.assertLess(len(output), 650)
        finally:
            silent_remove(DEF_OUT, disable=DISABLE_REMOVE)
