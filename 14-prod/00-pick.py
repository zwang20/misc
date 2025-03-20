"""
pick.py

picks molecules that may be intresting from database.txt
"""

# pylint: disable=C0103,I1101,E1101

import rdkit.Chem  # type: ignore[import-untyped]
import rdkit.Chem.Lipinski  # type: ignore[import-untyped]

from common import get_previous_files

previous_files = get_previous_files()

skip_prefix_list = []

for previous_file in previous_files:
    with open(f"batch/{previous_file}", encoding="utf-8") as f:
        for line in f:
            if line:
                skip_prefix_list.append(line.strip())

with open("bad.txt", encoding="utf-8") as f:
    for line in f:
        if line.strip():
            skip_prefix_list.append(line.split()[0])

intresting_molecules: list[tuple[str, str, int, int]] = []

with open("database.txt", encoding="utf-8") as f:
    for line in f:
        if line.startswith("#"):
            continue
        line_list = line.split(";")
        prefix = line_list[0].strip().split("_")[1]

        if prefix in skip_prefix_list:
            continue

        smiles = line_list[1].strip()
        iupac = line_list[2].strip()

        mol = rdkit.Chem.rdmolfiles.MolFromSmiles(smiles)
        num_rotatable_bonds = rdkit.Chem.Lipinski.NumRotatableBonds(mol)
        if num_rotatable_bonds:
            continue
        mol = rdkit.Chem.AddHs(mol)
        num_atoms = len(mol.GetAtoms())
        intresting_molecules.append((prefix, iupac, num_atoms, num_rotatable_bonds))

intresting_molecules.sort(key=lambda x: x[2] + x[3] * 10)

length = len(intresting_molecules)
print(length, "molecules found")
print("writing 10 molecules to file")
i = 0
while True:
    if f"{i}.txt" in previous_files:
        i += 1
        continue
    with open(f"batch/{i}.txt", "w", encoding="utf-8") as f:
        c = 0
        for prefix, iupac, _1, _2 in intresting_molecules:
            f.write(f"{prefix}\n")
            print(f"{prefix}\t{iupac}")
            c += 1
            if c >= 10:
                break
    break
