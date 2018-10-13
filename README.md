che696_examples
==============================
[//]: # (Badges)
[![Travis Build Status](https://travis-ci.org/REPLACE_WITH_OWNER_ACCOUNT/che696_examples.png)](https://travis-ci.org/REPLACE_WITH_OWNER_ACCOUNT/che696_examples)
[![AppVeyor Build status](https://ci.appveyor.com/api/projects/status/REPLACE_WITH_APPVEYOR_LINK/branch/master?svg=true)](https://ci.appveyor.com/project/REPLACE_WITH_OWNER_ACCOUNT/che696_examples/branch/master)
[![codecov](https://codecov.io/gh/REPLACE_WITH_OWNER_ACCOUNT/che696_examples/branch/master/graph/badge.svg)](https://codecov.io/gh/REPLACE_WITH_OWNER_ACCOUNT/che696_examples/branch/master)

Several Python scripts to serve as examples for ChE 696 individual projects

### Copyright

Copyright (c) 2018, hbmayes, MIT license

#### Acknowledgements
 
Project based on a [Cookiecutter project](https://github.com/team-mayes/cookiecutter-compchem) 
forked from the [Computational Chemistry Python Cookiecutter](https://github.com/choderalab/cookiecutter-python-comp-chem)


Installation
------------

1. Make sure python is installed. Python >=3.5 is recommended. The package is meant to be python 2.7 compatible,
   but primarily tested with Python 3.5 and 3.6. There are many ways to install python.
   We recommend http://conda.pydata.org/miniconda.html

2. From the base folder where you would like the set of files (a new folder will be created, by default called md_utils):
   ~~~
      git clone https://github.com/team-mayes/che696_examples.git
   ~~~

3. To allow the scripts to be found anywhere on your computer using your terminal screen,
   making sure the following folder exists (make it if it does not) and in your .bashrc or .bash_profile 
   path, and remember to source that file after an update:
   ~~~
      $HOME/.local/bin
   ~~~

4. To make a tarball to allow installation:

   a. From the main directory of your project, run:
   ~~~
         python setup.py sdist   
   ~~~
   b. The step above will create the directory 'dist' in the main directory if it does not yet exist, and also a 
   tarball, where the * in the name will be replaced by the current version of the package:
   ~~~
         dist/che696_examples-*.tar.gz
   ~~~
   c. To install this package on your local computer, run:
   ~~~
         pip install dist/che696_examples-*.tar.gz --user
   ~~~
   d. You can also copy the tarball to any other machine (same type of computer or not) and similarly install with 
   pip, just changing the directory name where the tarball exists, as needed.
   e. If you are upgrading the package after the initial install, just add the '--upgrade' flag:
   ~~~
         pip install --upgrade dist/che696_examples-*.tar.gz --user
   ~~~
   
Example
-------

1. To see if the installation worked, try running one of the scripts with the help option. All scripts in
   this package have such an option, which will briefly tell you about the code, e.g.::
   ~~~
       add_to_each_line -h
   ~~~
   
2. Following the help instructions, give it a try!

When the whole git repository is cloned, there will be example input files in the tests/test_data folder.


-------
Scripts
-------

add_to_each_line

- Reads in a file and adds a beginning and/or end to each line. The first argument must be the name of 
  the file to be read.

col_stats

- Given a csv file with columns of data, returns the min, max, avg, and std dev per column. Optionally, it can return
  the maximum value from each column plus a "buffer" length (useful for preparing CP2K input). It can optionally 
  prepare histograms of non-numerical data.

fill_tpl

- Fills in a template file with parameter values. See example *.tpl template files and *.ini configurations files in
  tests/test_data/fill_tpl.

pdb_edit

- Creates a new version of a pdb file applying options such as renumbering molecules.
    - use the option "add_element_types = true" to fill in the column of element types (created originally because 
    VMD dropped them for the protein section; CP2K wants them)
        - by default, it will check all atoms. You can specify a range on which to perform this action with
          'first_atom_add_element' and 'last_atom_add_element'
        - it will only add the element type if it is in the internal atom_type/element dictionary (a warning will show 
          if a type is not in the dictionary). Otherwise, it will leave those columns as they originally were.
        - by default, it loads a dictionary I made based on charmm atom types (charmm_atom_type,element; one per line).
          The user can specify a different dictionary file with "atom_type_element_dict_file"
    - if the user specifies a 'first_wat_atom' and 'last_wat_atom', the program will check that the atoms are printed 
    in the order OH2, H1, H2
        - when using this option, if the first protein atom is not 1 (numbering begins at 1, like in a PDB, not 0, like
          VMD index), use the option "last_prot_atom = " to indicate the first protein atom num
        - this options requires inputting the last protein atom id (add "last_prot_atom = X" to the configuration file,
          where X is the integer (decimal) atom number)
    - by default, the output pdb name of a pdb file called 'struct.pdb' will be 'struct_new.pdb'. You can specify a new
      name with the keyword 'new_pdb_name'
    - by default, the output directory will be the same as that for the input pdb. This can be changed with the 
    'output_directory' keyword
    - the program will renumber atoms starting from 1 (using hex for atom numbers greater than 99999), using a 
    dictionary
      to change order if a csv dictionary of "old,new" indexes is specified with 'atom_reorder_old_new_file'
    - the program will renumber molecules starting from 1 if 'mol_renum_flag = True' is included in the configuration 
    file. Molecules may also be renumbered with by specifying a csv dictionary of "old,new" indexes with 'mol_renum_old_new_file'

tex_add_spell

-  Adds a word to a Hunspell-type dictionary file.
