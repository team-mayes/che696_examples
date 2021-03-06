#!/usr/bin/env python3
#  coding=utf-8

"""
Tests for the common lib.
"""
import logging
import shutil
import tempfile
import unittest
import os
import numpy as np
from che696_examples.common import (find_files_by_dir, read_csv, write_csv, str_to_bool,
                                    diff_lines, create_out_fname, conv_raw_val, read_csv_dict,
                                    InvalidDataError,
                                    pbc_calc_vector, pbc_vector_avg, unit_vector, vec_angle, vec_dihedral, calc_k,
                                    read_csv_header, get_fname_root, fmt_row_data, quote, dequote,
                                    list_to_file, silent_remove, read_csv_to_dict)

__author__ = 'hbmayes'

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
LOGGER_ON = logger.isEnabledFor(logging.DEBUG)


# Constants #
DATA_DIR = os.path.join(os.path.dirname(__file__), 'test_data')
SUB_DATA_DIR = os.path.join(DATA_DIR, 'common')
PDB_DIR = os.path.join(DATA_DIR, 'pdb_edit')
FES_DIR = os.path.join(SUB_DATA_DIR, 'fes_out')
DEF_FILE_PAT = 'fes*.out'
CORR_KEY = 'corr'
COORD_KEY = 'coord'
FREE_KEY = 'free_energy'
RAD_KEY_SEQ = [COORD_KEY, FREE_KEY, CORR_KEY]

ELEM_DICT_FILE = os.path.join(PDB_DIR, 'element_dict.csv')
ATOM_DICT_FILE = os.path.join(PDB_DIR, 'atom_reorder.csv')
GOOD_ATOM_DICT = {1: 20, 2: 21, 3: 22, 4: 23, 5: 24, 6: 25, 7: 26, 8: 27, 9: 2, 10: 1, 11: 3, 12: 4, 13: 5, 14: 6,
                  15: 7, 16: 8, 17: 9, 18: 10, 19: 11, 20: 12, 21: 13, 22: 14, 23: 15, 24: 16, 25: 17, 26: 18, 27: 19}


CSV_FILE = os.path.join(SUB_DATA_DIR, 'rad_PMF_last2ns3_1.txt')
FRENG_TYPES = [float, str]

ORIG_WHAM_ROOT = "PMF_last2ns3_1"
ORIG_WHAM_FNAME = ORIG_WHAM_ROOT + ".txt"
ORIG_WHAM_PATH = os.path.join(DATA_DIR, ORIG_WHAM_FNAME)
SHORT_WHAM_PATH = os.path.join(DATA_DIR, ORIG_WHAM_FNAME)
EMPTY_CSV = os.path.join(SUB_DATA_DIR, 'empty.csv')

OUT_PFX = 'rad_'

# Data #

CSV_HEADER = ['coord', 'free_energy', 'corr']
GHOST = 'ghost'

# Output files #

DIFF_LINES_BASE_FILE = os.path.join(SUB_DATA_DIR, 'diff_lines_base_file.csv')
DIFF_LINES_PREC_DIFF = os.path.join(SUB_DATA_DIR, 'diff_lines_prec_diff.csv')
DIFF_LINES_ONE_VAL_DIFF = os.path.join(SUB_DATA_DIR, 'diff_lines_one_val_diff.csv')
DIFF_LINES_MISS_VAL = os.path.join(SUB_DATA_DIR, 'diff_lines_miss_val.csv')
MISS_LINES_MISS_LINE = os.path.join(SUB_DATA_DIR, 'diff_lines_miss_line.csv')
DIFF_LINES_ONE_NAN = os.path.join(SUB_DATA_DIR, 'diff_lines_one_nan.csv')
DIFF_LINES_ONE_NAN_PREC_DIFF = os.path.join(SUB_DATA_DIR, 'diff_lines_one_nan.csv')

DIFF_LINES_SCI_FILE = os.path.join(SUB_DATA_DIR, 'cv_analysis_quat.log')
DIFF_LINES_ALT_SCI_FILE = os.path.join(SUB_DATA_DIR, 'cv_analysis_quat_good.log')

IMPROP_SEC = os.path.join(SUB_DATA_DIR, 'glue_improp.data')
IMPROP_SEC_ALT = os.path.join(SUB_DATA_DIR, 'glue_improp_diff_ord.data')

# To test PBC math
PBC_BOX = np.full(3, 24.25)
A_VEC = [3.732, -1.803, -1.523]
B_VEC = [4.117, 0.135, -2.518]
GOOD_A_MINUS_B = np.array([-0.385, -1.938, 0.995])
GOOD_A_B_AVG = np.array([3.9245, -0.834, -2.0205])
C_VEC = [24.117, -20.135, -52.518]
GOOD_A_MINUS_C = np.array([3.865, -5.918, 2.495])
GOOD_A_C_AVG = np.array([1.7995, 1.156, -2.7705])

VEC_1 = np.array([3.712, -1.585, -3.116])
VEC_2 = np.array([4.8760, -1.129, -3.265])
VEC_3 = np.array([5.498, -0.566, -2.286])
VEC_4 = np.array([5.464, -1.007, -0.948])

VEC_21 = np.array([-1.164, -0.456, 0.149])
VEC_23 = np.array([0.622, 0.563, 0.979])
VEC_34 = np.array([-0.034, -0.441, 1.338])

# vec21 = {ndarray} [-1.164 -0.456  0.149]
# vec23 = {ndarray} [ 0.622  0.563  0.979]
# vec34 = {ndarray} [-0.034 -0.441  1.338]


UNIT_VEC_3 = np.array([0.91922121129527656, -0.094630630337054641, -0.38220074372881085])
ANGLE_123 = 120.952786591
DIH_1234 = 39.4905248514


def expected_dir_data():
    """
    :return: The data structure that's expected from `find_files_by_dir`
    """
    return {os.path.abspath(os.path.join(FES_DIR, "1.00")): ['fes.out'],
            os.path.abspath(os.path.join(FES_DIR, "2.75")): ['fes.out', 'fes_cont.out'],
            os.path.abspath(os.path.join(FES_DIR, "5.50")): ['fes.out', 'fes_cont.out'],
            os.path.abspath(os.path.join(FES_DIR, "multi")): ['fes.out', 'fes_cont.out',
                                                              'fes_cont2.out', 'fes_cont3.out'],
            os.path.abspath(os.path.join(FES_DIR, "no_overwrite")): ['fes.out'], }


def csv_data():
    """
    :return: Test data as a list of dicts.
    """
    rows = [{CORR_KEY: 123.42, COORD_KEY: "75", FREE_KEY: True},
            {CORR_KEY: 999.43, COORD_KEY: "yellow", FREE_KEY: False}]
    return rows


def is_one_of_type(val, types):
    """Returns whether the given value is one of the given types.

    :param val: The value to evaluate
    :param types: A sequence of types to check against.
    :return: Whether the given value is one of the given types.
    """
    result = False
    val_type = type(val)
    for tt in types:
        if val_type is tt:
            result = True
    return result


# Tests #

class TestRateCalc(unittest.TestCase):
    """
    Tests calculation of a rate coefficient by the Eyring equation.
    """
    def test_calc_k(self):
        temp = 900.0
        delta_g = 53.7306
        rate_coeff = calc_k(temp, delta_g)
        self.assertEqual(rate_coeff, 1.648326791137026)


class TestFindFiles(unittest.TestCase):
    """
    Tests for the file finder.
    """

    def test_find(self):
        found = find_files_by_dir(FES_DIR, DEF_FILE_PAT)
        exp_data = expected_dir_data()
        self.assertEqual(len(exp_data), len(found))
        for key, files in exp_data.items():
            found_files = found.get(key)
            self.assertCountEqual(files, found_files)


class TestReadFirstRow(unittest.TestCase):

    def testFirstRow(self):
        self.assertListEqual(CSV_HEADER, read_csv_header(CSV_FILE))

    def testEmptyFile(self):
        self.assertIsNone(read_csv_header(EMPTY_CSV))


class TestFnameManipulation(unittest.TestCase):
    def testOutFname(self):
        """
        Check for prefix addition.
        """
        self.assertTrue(create_out_fname(ORIG_WHAM_PATH, prefix=OUT_PFX).endswith(
            os.sep + OUT_PFX + ORIG_WHAM_FNAME))

    def testGetRootName(self):
        """
        Check for prefix addition.
        """
        root_name = get_fname_root(ORIG_WHAM_PATH)
        self.assertEqual(root_name, ORIG_WHAM_ROOT)
        self.assertNotEqual(root_name, ORIG_WHAM_FNAME)
        self.assertNotEqual(root_name, ORIG_WHAM_PATH)


class TestReadCsvDict(unittest.TestCase):
    def testReadAtomNumDict(self):
        # Will renumber atoms and then sort them
        test_dict = read_csv_dict(ATOM_DICT_FILE)
        self.assertEqual(test_dict, GOOD_ATOM_DICT)

    def testReadPDBDict(self):
        test_type = 'HY1'
        test_elem = 'H'
        test_dict = read_csv_dict(ELEM_DICT_FILE, pdb_dict=True, strip=True)
        self.assertTrue(test_type in test_dict)
        self.assertEqual(test_elem, test_dict[test_type])
        self.assertEqual(31, len(test_dict))

    def testStringDictAsInt(self):
        # Check that fails elegantly by passing returning value error
        try:
            test_dict = read_csv_dict(ELEM_DICT_FILE, one_to_one=False)
            self.assertFalse(test_dict)
        except ValueError as e:
            self.assertTrue("invalid literal for int()" in e.args[0])

    def testStringDictCheckDups(self):
        # Check that fails elegantly
        try:
            test_dict = read_csv_dict(ELEM_DICT_FILE, ints=False, )
            self.assertFalse(test_dict)
        except InvalidDataError as e:
            self.assertTrue("Did not find a 1:1 mapping" in e.args[0])


class TestReadCsv(unittest.TestCase):
    def testReadCsv(self):
        """
        Verifies the contents of the CSV file.
        """
        result = read_csv(CSV_FILE)
        self.assertTrue(result)
        for row in result:
            self.assertEqual(3, len(row))
            self.assertIsNotNone(row.get(FREE_KEY, None))
            self.assertIsInstance(row[FREE_KEY], str)
            self.assertIsNotNone(row.get(CORR_KEY, None))
            self.assertIsInstance(row[CORR_KEY], str)
            self.assertIsNotNone(row.get(COORD_KEY, None))
            self.assertIsInstance(row[COORD_KEY], str)

    def testReadTypedCsv(self):
        """
        Verifies the contents of the CSV file.
        """
        result = read_csv(CSV_FILE, data_conv={FREE_KEY: float,
                                               CORR_KEY: float,
                                               COORD_KEY: float, })
        self.assertTrue(result)
        for row in result:
            self.assertEqual(3, len(row))
            self.assertIsNotNone(row.get(FREE_KEY, None))
            self.assertTrue(is_one_of_type(row[FREE_KEY], FRENG_TYPES))
            self.assertIsNotNone(row.get(CORR_KEY, None))
            self.assertTrue(is_one_of_type(row[CORR_KEY], FRENG_TYPES))
            self.assertIsNotNone(row.get(COORD_KEY, None))
            self.assertIsInstance(row[COORD_KEY], float)

    def testReadTypedCsvAllConv(self):
        """
        Verifies the contents of the CSV file using the all_conv function.
        """
        result = read_csv(CSV_FILE, all_conv=float)
        self.assertTrue(result)
        for row in result:
            self.assertEqual(3, len(row))
            self.assertIsNotNone(row.get(FREE_KEY, None))
            self.assertTrue(is_one_of_type(row[FREE_KEY], FRENG_TYPES))
            self.assertIsNotNone(row.get(CORR_KEY, None))
            self.assertTrue(is_one_of_type(row[CORR_KEY], FRENG_TYPES))
            self.assertIsNotNone(row.get(COORD_KEY, None))
            self.assertIsInstance(row[COORD_KEY], float)


class TestWriteCsv(unittest.TestCase):
    def testWriteCsv(self):
        tmp_dir = None
        data = csv_data()
        try:
            tmp_dir = tempfile.mkdtemp()
            tgt_fname = create_out_fname(SHORT_WHAM_PATH, prefix=OUT_PFX, base_dir=tmp_dir)

            write_csv(data, tgt_fname, RAD_KEY_SEQ)
            csv_result = read_csv(tgt_fname,
                                  data_conv={FREE_KEY: str_to_bool,
                                             CORR_KEY: float,
                                             COORD_KEY: str, })
            self.assertEqual(len(data), len(csv_result))
            for i, csv_row in enumerate(csv_result):
                self.assertDictEqual(data[i], csv_row)
        finally:
            shutil.rmtree(tmp_dir)


class TestReadCSVToDict(unittest.TestCase):
    def testReadCSVToDict(self):
        f_name = os.path.join(SUB_DATA_DIR, 'align_input1.csv')
        col_name = 'timestep'
        dict_from_csv = read_csv_to_dict(f_name, col_name)
        test_dict = {20349000: {'timestep': 20349000.0, 'a': 1.08940815703, 'b': 2.5576246461, 'c': 1.46821648907},
                     20349100: {'timestep': 20349100.0, 'a': 1.06137248961, 'b': 2.54961064343, 'c': 1.48823815382},
                     20349200: {'timestep': 20349200.0, 'a': 1.07719799833, 'b': 2.5555802304, 'c': 1.47838223207},
                     20349300: {'timestep': 20349300.0, 'a': 1.03661136199, 'b': 2.48012048137, 'c': 1.44350911938},
                     20349400: {'timestep': 20349400.0, 'a': 1.06251718339, 'b': 2.47131876633, 'c': 1.40880158294},
                     20349500: {'timestep': 20349500.0, 'a': 1.10603563003, 'b': 2.5709271159, 'c': 1.46489148587},
                     20349600: {'timestep': 20349600.0, 'a': 1.03610901651, 'b': 2.50963384288, 'c': 1.47352482637},
                     20349700: {'timestep': 20349700.0, 'a': 1.07721143937, 'b': 2.55911153734, 'c': 1.48190009798}}
        self.assertDictEqual(dict_from_csv, test_dict)

    def testReadCSVToDictNoSuchCol(self):
        e = None
        try:
            f_name = os.path.join(SUB_DATA_DIR, 'align_input1.csv')
            col_name = 'ghost'
            read_csv_to_dict(f_name, col_name)
            self.assertIsNotNone(e)
        except InvalidDataError as e:
            self.assertIsNotNone(e)


class TestFormatData(unittest.TestCase):
    def testFormatRows(self):
        raw = [{"a": 1.3333322333, "b": 999.222321}, {"a": 333.44422222, "b": 17.121}]
        fmt_std = [{'a': '1.3333', 'b': '999.2223'}, {'a': '333.4442', 'b': '17.1210'}]
        self.assertListEqual(fmt_std, fmt_row_data(raw, "{0:.4f}"))


class TestDiffLines(unittest.TestCase):
    def testSameFile(self):
        self.assertFalse(diff_lines(DIFF_LINES_BASE_FILE, DIFF_LINES_BASE_FILE))

    def testMachinePrecDiff(self):
        self.assertFalse(diff_lines(DIFF_LINES_BASE_FILE, DIFF_LINES_PREC_DIFF))

    def testMachinePrecDiff2(self):
        self.assertFalse(diff_lines(DIFF_LINES_PREC_DIFF, DIFF_LINES_BASE_FILE))

    def testDiff(self):
        diffs = diff_lines(DIFF_LINES_ONE_VAL_DIFF, DIFF_LINES_BASE_FILE)
        self.assertEqual(len(diffs), 2)

    def testDiffColNum(self):
        diff_list_line = diff_lines(DIFF_LINES_MISS_VAL, DIFF_LINES_BASE_FILE)
        self.assertEqual(len(diff_list_line), 2)

    def testMissLine(self):
        diff_line_list = diff_lines(DIFF_LINES_BASE_FILE, MISS_LINES_MISS_LINE)
        self.assertEqual(len(diff_line_list), 1)
        self.assertTrue("- 540010,1.04337066817119" in diff_line_list[0])

    def testDiffOrd(self):
        diff_line_list = diff_lines(IMPROP_SEC, IMPROP_SEC_ALT, delimiter=" ")
        self.assertEqual(13, len(diff_line_list))

    def testDiffOneNan(self):
        diff_line_list = diff_lines(DIFF_LINES_BASE_FILE, DIFF_LINES_ONE_NAN)
        self.assertEqual(2, len(diff_line_list))

    def testDiffBothNanPrecDiff(self):
        # make there also be a precision difference so the entry-by-entry comparison will be made
        diff_line_list = diff_lines(DIFF_LINES_ONE_NAN_PREC_DIFF, DIFF_LINES_ONE_NAN)
        self.assertFalse(diff_line_list)

    def testSciVectorsPrecDiff(self):
        self.assertFalse(diff_lines(DIFF_LINES_SCI_FILE, DIFF_LINES_ALT_SCI_FILE))


class TestQuoteDeQuote(unittest.TestCase):
    def testQuoting(self):
        self.assertTrue(quote((0, 1)) == '"(0, 1)"')

    def testNoQuotingNeeded(self):
        self.assertTrue(quote('"(0, 1)"') == '"(0, 1)"')

    def testDequote(self):
        self.assertTrue(dequote('"(0, 1)"') == '(0, 1)')

    def testNoDequoteNeeded(self):
        self.assertTrue(dequote("(0, 1)") == '(0, 1)')

    def testDequoteUnmatched(self):
        self.assertTrue(dequote('"' + '(0, 1)') == '"(0, 1)')


class TestConversions(unittest.TestCase):
    def testNotBool(self):
        try:
            str_to_bool("hello there neighbor")
        except ValueError as e:
            self.assertTrue("Cannot covert" in e.args[0])

    def testIntList(self):
        int_str = '2,3,4'
        int_list = [2, 3, 4]
        self.assertEqual(int_list, conv_raw_val(int_str, []))

    def testNotIntMissFlag(self):
        non_int_str = 'a,b,c'
        try:
            conv_raw_val(non_int_str, [])
        except ValueError as e:
            self.assertTrue("invalid literal for int()" in e.args[0])

    def testNotIntList(self):
        non_int_str = 'a,b,c'
        non_int_list = ['a', 'b', 'c']
        self.assertEqual(non_int_list, conv_raw_val(non_int_str, [], int_list=False))


class TestVectorPBCMath(unittest.TestCase):
    def testSubtractInSameImage(self):
        self.assertTrue(np.allclose(pbc_calc_vector(VEC_1, VEC_2, PBC_BOX), VEC_21))
        self.assertTrue(np.allclose(pbc_calc_vector(VEC_3, VEC_2, PBC_BOX), VEC_23))
        self.assertFalse(np.allclose(pbc_calc_vector(VEC_3, VEC_2, PBC_BOX), VEC_21))
        self.assertTrue(np.allclose(pbc_calc_vector(A_VEC, B_VEC, PBC_BOX), GOOD_A_MINUS_B))

    def testSubtractInDiffImages(self):
        self.assertTrue(np.allclose(pbc_calc_vector(A_VEC, C_VEC, PBC_BOX), GOOD_A_MINUS_C))

    def testAvgInSameImage(self):
        self.assertTrue(np.allclose(pbc_vector_avg(A_VEC, B_VEC, PBC_BOX), GOOD_A_B_AVG))

    def testAvgInDiffImages(self):
        self.assertTrue(np.allclose(pbc_vector_avg(A_VEC, C_VEC, PBC_BOX), GOOD_A_C_AVG))

    def testUnitVector(self):
        test_unit_vec = unit_vector(VEC_3)
        self.assertTrue(np.allclose(test_unit_vec, UNIT_VEC_3))
        self.assertFalse(np.allclose(test_unit_vec, VEC_1))

    def testAngle(self):
        self.assertAlmostEqual(vec_angle(VEC_21, VEC_23), ANGLE_123)

    def testDihedral(self):
        self.assertAlmostEqual(vec_dihedral(VEC_21, VEC_23, VEC_34), DIH_1234)
