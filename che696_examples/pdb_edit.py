#!/usr/bin/env python
# coding=utf-8
"""
Edit a pdb file to provide missing data
"""

from __future__ import print_function
import os
import sys
import argparse
import numpy as np
from che696_examples.common import (list_to_file, InvalidDataError, warning, process_cfg, create_out_fname,
                                    read_csv_dict, list_to_csv)

try:
    # noinspection PyCompatibility
    from ConfigParser import ConfigParser
except ImportError:
    # noinspection PyCompatibility
    from configparser import ConfigParser


__author__ = 'hmayes'


# Error Codes
# The good status code
GOOD_RET = 0
INPUT_ERROR = 1
IO_ERROR = 2
INVALID_DATA = 3

# Constants #

# Config File Sections
MAIN_SEC = 'main'

# Config keys
PDB_FILE = 'pdb_file'
PDB_NEW_FILE = 'new_pdb_name'
ATOM_REORDER_FILE = 'atom_reorder_old_new_file'
MOL_RENUM_FILE = 'mol_renum_old_new_file'
RENUM_MOL = 'mol_renum_flag'
# TODO: if desired, make a option to add a chain label
# CHAIN_LABEL = 'chain_label_flag'
FIRST_ADD_ELEM = 'first_atom_add_element'
LAST_ADD_ELEM = 'last_atom_add_element'
FIRST_WAT_ID = 'first_wat_atom'
LAST_WAT_ID = 'last_wat_atom'
ADD_ELEMENTS = 'add_element_types'
ELEMENT_DICT_FILE = 'atom_type_element_dict_file'
OUT_BASE_DIR = 'output_directory'
RESID_QMMM = 'resids_qmmm_ca_cb_link'

# PDB file info
PDB_LINE_TYPE_LAST_CHAR = 'pdb_line_type_last_char'
PDB_ATOM_NUM_LAST_CHAR = 'pdb_atom_num_last_char'
PDB_ATOM_TYPE_LAST_CHAR = 'pdb_atom_type_last_char'
PDB_RES_TYPE_LAST_CHAR = 'pdb_res_type_last_char'
PDB_MOL_NUM_LAST_CHAR = 'pdb_mol_num_last_char'
PDB_X_LAST_CHAR = 'pdb_x_last_char'
PDB_Y_LAST_CHAR = 'pdb_y_last_char'
PDB_Z_LAST_CHAR = 'pdb_z_last_char'
PDB_LAST_T_CHAR = 'pdb_last_temp_char'
PDB_LAST_ELEM_CHAR = 'pdb_last_element_char'
PDB_FORMAT = 'pdb_print_format'

# Defaults
DEF_CFG_FILE = 'pdb_edit.ini'
DEF_ELEM_DICT_FILE = os.path.join(os.path.dirname(__file__), 'cfg', 'charmm36_atoms_elements.txt')
DEF_CFG_VALS = {ATOM_REORDER_FILE: None,
                MOL_RENUM_FILE: None,
                ELEMENT_DICT_FILE: None,
                RENUM_MOL: False,
                FIRST_ADD_ELEM: 1,
                LAST_ADD_ELEM: np.inf,
                FIRST_WAT_ID: np.nan,
                LAST_WAT_ID: np.nan,
                OUT_BASE_DIR: None,
                PDB_NEW_FILE: None,
                PDB_FORMAT: '{:6s}{:>5}{:^6s}{:5s}{:>4}    {:8.3f}{:8.3f}{:8.3f}{:22s}{:>2s}{:s}',
                PDB_LINE_TYPE_LAST_CHAR: 6,
                PDB_ATOM_NUM_LAST_CHAR: 11,
                PDB_ATOM_TYPE_LAST_CHAR: 17,
                PDB_RES_TYPE_LAST_CHAR: 22,
                PDB_MOL_NUM_LAST_CHAR: 28,
                PDB_X_LAST_CHAR: 38,
                PDB_Y_LAST_CHAR: 46,
                PDB_Z_LAST_CHAR: 54,
                PDB_LAST_T_CHAR: 76,
                PDB_LAST_ELEM_CHAR: 78,
                ADD_ELEMENTS: False,
                RESID_QMMM: []
                }
REQ_KEYS = {PDB_FILE: str,
            }

HEAD_CONTENT = 'head_content'
ATOMS_CONTENT = 'atoms_content'
TAIL_CONTENT = 'tail_content'


# This is used when need to add atom types to PDB file
C_ATOMS = ' C'
O_ATOMS = ' O'
H_ATOMS = ' H'
N_ATOMS = ' N'
P_ATOMS = ' P'
S_ATOMS = ' S'
CL_ATOMS = 'CL'
NA_ATOMS = 'NA'
K_ATOMS = ' K'
LI_ATOMS = 'LI'
MG_ATOMS = 'MG'
CA_ATOMS = 'CA'
RB_ATOMS = 'RB'
CS_ATOMS = 'CS'
BA_ATOMS = 'BA'
ZN_ATOMS = 'ZN'
CD_ATOMS = 'CD'

# Atom types; used for making QMMM input
C_ALPHA = '  CA  '
C_BETA = '  CB  '
SKIP_ATOM_TYPES = ['  C   ', '  O   ', '  NT  ', '  HNT ', '  CAT ', '  HT1 ', '  HT2 ', '  HT3 ', '  HA  ', '  CAY ',
                   '  HY1 ', '  HY2 ', '  HY3 ', '  CY  ', '  OY  ', '  N   ', '  HN  ', ]


def print_qm_kind(int_list, element_name, fname, mode='w'):
    """
    Writes the list to the given file, formatted for CP2K to read as qm atom indices.

    @param int_list: The list to write.
    @param element_name: element type to designate
    @param fname: The location of the file to write.
    @param mode: default is to write to a new file. Use option to designate to append to existing file.
    """
    with open(fname, mode) as m_file:
        m_file.write('    &QM_KIND {}\n'.format(element_name))
        m_file.write('        MM_INDEX {}\n'.format(' '.join(map(str, int_list))))
        m_file.write('    &END QM_KIND\n')
    if mode == 'w':
        print("Wrote file: {}".format(fname))


def print_qm_links(c_alpha_dict, c_beta_dict, f_name, mode="w"):
    """
    Note: this needs to be tested. Only ran once to get the protein residues set up correctly.
    @param c_alpha_dict: dict of protein residue to be broken to c_alpha atom id
    @param c_beta_dict: as above, but for c_beta
    @param f_name: The location of the file to write.
    @param mode: default is to write to a new file. Use option to designate to append to existing file.
    """
    with open(f_name, mode) as m_file:
        for resid in c_beta_dict:
            m_file.write('    !! Break resid {} between CA and CB, and cap CB with hydrogen\n'
                         '    &LINK\n       MM_INDEX  {}  !! CA\n       QM_INDEX  {}  !! CB\n'
                         '       LINK_TYPE  IMOMM\n       ALPHA_IMOMM  1.5\n'
                         '    &END LINK\n'.format(resid, c_alpha_dict[resid], c_beta_dict[resid]))
    if mode == 'w':
        print("Wrote file: {}".format(f_name))


def create_element_dict(dict_file, pdb_dict=True, one_to_one=False):
    # This is used when need to add atom types to PDB file
    element_dict = {}
    if dict_file is not None:
        return read_csv_dict(dict_file, pdb_dict=pdb_dict, ints=False, one_to_one=one_to_one, strip=True)
    return element_dict


def read_cfg(f_loc, cfg_proc=process_cfg):
    """
    Reads the given configuration file, returning a dict with the converted values supplemented by default values.

    :param f_loc: The location of the file to read.
    :param cfg_proc: The processor to use for the raw configuration values.  Uses default values when the raw
        value is missing.
    :return: A dict of the processed configuration file's data.
    """
    config = ConfigParser()
    good_files = config.read(f_loc)
    if not good_files:
        raise IOError('Could not read file: {}'.format(f_loc))
    main_proc = cfg_proc(dict(config.items(MAIN_SEC)), DEF_CFG_VALS, REQ_KEYS)

    # Assume that elements should be added if a dict file is given
    if (main_proc[ADD_ELEMENTS] or len(main_proc[RESID_QMMM]) > 0) and main_proc[ELEMENT_DICT_FILE] is None:
        main_proc[ELEMENT_DICT_FILE] = DEF_ELEM_DICT_FILE
    if main_proc[ELEMENT_DICT_FILE] is not None:
        main_proc[ADD_ELEMENTS] = True

    return main_proc


def parse_cmdline(argv):
    """
    Returns the parsed argument list and return code.
    `argv` is a list of arguments, or `None` for ``sys.argv[1:]``.
    """
    if argv is None:
        argv = sys.argv[1:]

    # initialize the parser object:
    parser = argparse.ArgumentParser(description='Creates a new version of a pdb file. Atoms will be numbered '
                                                 'starting from one. Options include renumbering molecules.')
    parser.add_argument("-c", "--config", help="The location of the configuration file in ini format. "
                                               "The default file name is {}, located in the "
                                               "base directory where the program as run.".format(DEF_CFG_FILE),
                        default=DEF_CFG_FILE, type=read_cfg)
    args = None
    try:
        args = parser.parse_args(argv)
    except IOError as e:
        warning(e)
        parser.print_help()
        return args, IO_ERROR

    except (KeyError, InvalidDataError, SystemExit) as e:
        if hasattr(e, 'code') and e.code == 0:
            return args, GOOD_RET
        warning("Input data missing:", e)
        parser.print_help()
        return args, INPUT_ERROR

    return args, GOOD_RET


def pdb_atoms_to_file(pdb_format, list_val, fname, mode='w'):
    """
    Writes the list of sequences to the given file in the specified format for a PDB

    @param pdb_format: provides correct formatting
    @param list_val: The list of sequences to write.
    @param fname: The location of the file to write.
    @param mode: default is to write; can allow to append
    """
    with open(fname, mode) as w_file:
        for line in list_val:
            w_file.write(pdb_format.format(*line) + '\n')


def print_pdb(head_data, atoms_data, tail_data, file_name, file_format):
    list_to_file(head_data, file_name)
    pdb_atoms_to_file(file_format, atoms_data, file_name, mode='a')
    list_to_file(tail_data, file_name, mode='a', print_message=False)


# noinspection PyTypeChecker
def process_pdb(cfg, atom_num_dict, mol_num_dict, element_dict):
    pdb_loc = cfg[PDB_FILE]
    pdb_data = {HEAD_CONTENT: [], ATOMS_CONTENT: [], TAIL_CONTENT: []}
    # to allow warning to be printed once and only once
    missing_types = []
    qmmm_elem_id_dict = {}
    ca_res_atom_id_dict = {}
    cb_res_atom_id_dict = {}
    atoms_for_vmd = []

    with open(pdb_loc) as f:
        wat_count = 0
        atom_count = 0
        mol_count = 1

        current_mol = None
        last_mol_num = None
        atoms_content = []

        for line in f:
            line = line.strip()
            if len(line) == 0:
                continue
            line_head = line[:cfg[PDB_LINE_TYPE_LAST_CHAR]]
            # head_content to contain Everything before 'Atoms' section
            # also capture the number of atoms
            if line_head == 'REMARK' or line_head == 'CRYST1':
                pdb_data[HEAD_CONTENT].append(line)

            # atoms_content to contain everything but the xyz
            elif line_head == 'ATOM  ':

                # My template PDB has ***** after atom_count 99999. Thus, I'm renumbering. Otherwise, this this:
                # atom_num = line[cfg[PDB_LINE_TYPE_LAST_CHAR]:cfg[PDB_ATOM_NUM_LAST_CHAR]]
                # For renumbering, making sure prints in the correct format, including num of characters:
                atom_count += 1

                # For reordering atoms
                if atom_count in atom_num_dict:
                    atom_id = atom_num_dict[atom_count]
                else:
                    atom_id = atom_count

                if atom_id > 99999:
                    atom_num = format(atom_id, 'x')
                    if len(atom_num) > 5:
                        warning("Hex representation of {} is {}, which is greater than 5 characters. This"
                                "will affect the PDB output formatting.".format(atom_id, atom_num))
                else:
                    atom_num = '{:5d}'.format(atom_id)

                atom_type = line[cfg[PDB_ATOM_NUM_LAST_CHAR]:cfg[PDB_ATOM_TYPE_LAST_CHAR]]
                atom_type_stripped = atom_type.strip()
                res_type = line[cfg[PDB_ATOM_TYPE_LAST_CHAR]:cfg[PDB_RES_TYPE_LAST_CHAR]]
                mol_num = int(line[cfg[PDB_RES_TYPE_LAST_CHAR]:cfg[PDB_MOL_NUM_LAST_CHAR]])
                pdb_x = float(line[cfg[PDB_MOL_NUM_LAST_CHAR]:cfg[PDB_X_LAST_CHAR]])
                pdb_y = float(line[cfg[PDB_X_LAST_CHAR]:cfg[PDB_Y_LAST_CHAR]])
                pdb_z = float(line[cfg[PDB_Y_LAST_CHAR]:cfg[PDB_Z_LAST_CHAR]])
                occ_t = line[cfg[PDB_Z_LAST_CHAR]:cfg[PDB_LAST_T_CHAR]]
                element = line[cfg[PDB_LAST_T_CHAR]:cfg[PDB_LAST_ELEM_CHAR]]
                last_cols = line[cfg[PDB_LAST_ELEM_CHAR]:]

                # For user-specified changing of molecule number
                if mol_num in mol_num_dict:
                    mol_num = mol_num_dict[mol_num]

                # If doing water molecule checking...
                if cfg[FIRST_WAT_ID] <= atom_count <= cfg[LAST_WAT_ID]:
                    if (wat_count % 3) == 0:
                        current_mol = mol_num
                        if atom_type != '  OH2 ':
                                warning('Expected an OH2 atom to be the first atom of a water molecule. '
                                        'Check line: {}'.format(line))
                        # last_cols = '  0.00  0.00      S2   O'
                    else:
                        if current_mol != mol_num:
                            warning('Water not in order on line:', line)
                        if (wat_count % 3) == 1:
                            if atom_type != '  H1  ':
                                warning('Expected an H1 atom to be the second atom of a water molecule. '
                                        'Check line: {}'.format(line))
                        else:
                            if atom_type != '  H2  ':
                                warning('Expected an H2 atom to be the second atom of a water molecule. '
                                        'Check line: {}'.format(line))
                    wat_count += 1

                if mol_num in cfg[RESID_QMMM] and atom_type not in SKIP_ATOM_TYPES:
                    if atom_type == C_ALPHA:
                        ca_res_atom_id_dict[mol_num] = atom_id
                    else:
                        if atom_type == C_BETA:
                            cb_res_atom_id_dict[mol_num] = atom_id
                        if atom_type_stripped in element_dict:
                            element = element_dict[atom_type_stripped]
                        else:
                            raise InvalidDataError("Did not find atom type '{}' in the element dictionary. Please "
                                                   "provide a new atom type, element dictionary (using keyword {} "
                                                   "in the configuration file) that includes all atom types in the "
                                                   "residues identified with the '{}' key."
                                                   "".format(atom_type_stripped, ELEMENT_DICT_FILE, RESID_QMMM))
                        if element in qmmm_elem_id_dict:
                            qmmm_elem_id_dict[element].append(atom_id)
                        else:
                            qmmm_elem_id_dict[element] = [atom_id]
                        atoms_for_vmd.append(atom_id - 1)

                if cfg[ADD_ELEMENTS] and atom_count <= cfg[LAST_ADD_ELEM]:
                    if atom_type_stripped in element_dict:
                        element = element_dict[atom_type_stripped]
                    else:
                        if atom_type_stripped not in missing_types:
                            warning("Please add atom type '{}' to dictionary of elements. Will not write/overwrite "
                                    "element type in the pdb output.".format(atom_type_stripped))
                            missing_types.append(atom_type_stripped)

                # For numbering molecules from 1 to end
                if cfg[RENUM_MOL]:
                    if last_mol_num is None:
                        last_mol_num = mol_num

                    if mol_num != last_mol_num:
                        last_mol_num = mol_num
                        mol_count += 1
                        if mol_count == 10000:
                            warning("Molecule numbers greater than 9999 will be printed in hex")

                    # Due to PDB format constraints, need to print in hex starting at 9999 molecules.
                    if mol_count > 9999:
                        mol_num = format(mol_count, 'x')
                        if len(mol_num) > 4:
                            warning("Hex representation of {} is {}, which is greater than 4 characters. This"
                                    "will affect the PDB output formatting.".format(atom_id, atom_num))
                    else:
                        mol_num = '{:4d}'.format(mol_count)

                line_struct = [line_head, atom_num, atom_type, res_type, mol_num, pdb_x, pdb_y, pdb_z,
                               occ_t, element, last_cols]
                atoms_content.append(line_struct)

            # tail_content to contain everything after the 'Atoms' section
            else:
                pdb_data[TAIL_CONTENT].append(line)

    # Only sort if there is renumbering
    if len(atom_num_dict) > 0:
        pdb_data[ATOMS_CONTENT] = sorted(atoms_content, key=lambda entry: entry[1])
    else:
        pdb_data[ATOMS_CONTENT] = atoms_content

    if cfg[PDB_NEW_FILE] is None:
        f_name = create_out_fname(cfg[PDB_FILE], suffix="_new", base_dir=cfg[OUT_BASE_DIR])
    else:
        f_name = create_out_fname(cfg[PDB_NEW_FILE], base_dir=cfg[OUT_BASE_DIR])
    print_pdb(pdb_data[HEAD_CONTENT], pdb_data[ATOMS_CONTENT], pdb_data[TAIL_CONTENT],
              f_name, cfg[PDB_FORMAT])

    if len(cfg[RESID_QMMM]) > 0:
        f_name = create_out_fname('amino_id.dat', base_dir=cfg[OUT_BASE_DIR])
        print_mode = "w"
        for elem in sorted(qmmm_elem_id_dict):
            print_qm_kind(qmmm_elem_id_dict[elem], elem, f_name, mode=print_mode)
            print_mode = 'a'
        print_qm_links(ca_res_atom_id_dict, cb_res_atom_id_dict, f_name, mode=print_mode)
        f_name = create_out_fname('vmd_protein_atoms.dat', base_dir=cfg[OUT_BASE_DIR])
        list_to_csv([atoms_for_vmd], f_name, delimiter=' ')


def main(argv=None):
    # Read input
    args, ret = parse_cmdline(argv)
    # TODO: did not show the expected behavior when I didn't have a required cfg in the ini file
    if ret != GOOD_RET or args is None:
        return ret

    cfg = args.config

    # Read and process pdb files
    try:
        atom_num_dict = read_csv_dict(cfg[ATOM_REORDER_FILE])
        mol_num_dict = read_csv_dict(cfg[MOL_RENUM_FILE], one_to_one=False)
        element_dict = create_element_dict(cfg[ELEMENT_DICT_FILE])
        process_pdb(cfg, atom_num_dict, mol_num_dict, element_dict)
    except IOError as e:
        warning("Problems reading file:", e)
        return IO_ERROR
    except (InvalidDataError, ValueError) as e:
        warning("Problems with input:", e)
        return INVALID_DATA

    return GOOD_RET  # success


if __name__ == '__main__':
    status = main()
    sys.exit(status)
