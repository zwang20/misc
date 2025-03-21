#!/usr/bin/python


import rdkit.Chem  # type: ignore[import-untyped]
import rdkit.Chem.Lipinski  # type: ignore[import-untyped]

max_rot = 0
max_atom = 0

with open("database.txt", encoding="utf-8") as f:
    for line in f:
        if line.startswith("#"):
            continue
        line_list = line.split(";")
        prefix = line_list[0].strip().split("_")[1]

        smiles = line_list[1].strip()
        iupac = line_list[2].strip()

        mol = rdkit.Chem.rdmolfiles.MolFromSmiles(smiles)
        num_rotatable_bonds = rdkit.Chem.Lipinski.NumRotatableBonds(mol)
        mol = rdkit.Chem.AddHs(mol)
        num_atoms = len(mol.GetAtoms())

        # if num_rotatable_bonds > max_rot:
        #     print(num_rotatable_bonds, num_atoms, prefix, iupac)
        #     max_rot = num_rotatable_bonds
        #     max_atom = num_atoms
        #
        # elif num_rotatable_bonds == max_rot and num_atoms > max_atom:
        #     print(num_rotatable_bonds, num_atoms, prefix, iupac)
        #     max_rot = num_rotatable_bonds
        #     max_atom = num_atoms

        if num_atoms >= 40:
            print(num_rotatable_bonds, num_atoms, prefix, iupac)

"""

mostly herbicides
6 40 1944394 [2-benzhydryloxyethyl]-dimethyl-amine
7 40 2501588 profluralin
8 40 2518989 dialifor
8 42 2725215 nitralin
3 44 5282042 Amitriptyline
7 40 5393242 diazinon
12 41 7754849 ethion

"""
