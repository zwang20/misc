#!/usr/bin/python

# This script converts a CHARMm crd file to a PDB file. (This has been done
# several times before - hopefully this is more successful :-)
#
# EPF 27-03-2000
#

import sys, struct, os
import logging
import traceback
logger = logging.getLogger(__name__)

class CustomFormatter(logging.Formatter):

    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    # format = "%(asctime)s - %(name)s - %(levelname)-8s - %(message)s (%(filename)s:%(lineno)d)"
    format = "%(levelname)-8s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

ch.setFormatter(CustomFormatter())

logger.addHandler(ch)

if len(sys.argv) < 2:
    logger.critical("No crd file found")
    logger.critical("usage: crd2pdb crd-file > pdb-file")
    sys.exit(1)

crd_file_name = sys.argv[1]
logger.info(f"processing {crd_file_name}")

#f = open(crdfile)
with open(crd_file_name) as crd_file:

    print("REMARK   Converted from " + crd_file_name)

    # buffer = f.readline()
    # while buffer[0:1] == "*":
    #     buffer = f.readline()
    while (line := crd_file.readline()).startswith('*'):
        continue

    # numofatoms = float(buffer)
    number_of_atoms = int(line.split()[0])

    atom_count = 0
    while (line := crd_file.readline()):
        try:
            atom_number, residue_number, residue_name, atom_name, x, y, z, segment, residue_chain, beta_factor = line.split()
            atom_number = int(atom_number)
            residue_number = int(residue_number)
            x = float(x)
            y = float(y)
            z = float(z)
            beta_factor = float(beta_factor)
        except ValueError as e:
            logger.critical("Something has gone wrong", exc_info=e)
            sys.exit(1)
        atom_number = int(atom_number)

        if residue_chain.isalpha():
            chain = residue_chain
        else:
            chain = ' '

        if residue_number < 10000:
            atom_data = (atom_number, atom_name, residue_name, chain, residue_number, x, y, z, 0.0, beta_factor)
            pdb_line = "ATOM  %5i  %3s%4s%c%4i    %8.3f%8.3f%8.3f%6.2f%6.2f" % atom_data
        else:
            atom_data = (atom_number, atom_name, residue_name, residue_number, x, y, z, 0.0, beta_factor)
            pdb_line = "ATOM  %5i  %3s%4s%5i    %8.3f%8.3f%8.3f%6.2f%6.2f" % atom_data

        print(pdb_line)

        atom_count += 1


print("REMARK There are " + str(atom_count) + " atoms in this file")
if atom_count != number_of_atoms:
    logger.error(f"{number_of_atoms} decleared in file, but {atom_count} atoms found")
    print(
        "REMARK Actual number of atoms does not match the number given in crd file ("
        + str(number_of_atoms)
        + ")"
    )
