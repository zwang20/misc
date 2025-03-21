#!/usr/bin/python

import subprocess

import rdkit.Chem  # type: ignore[import-untyped]
import rdkit.Chem.Lipinski  # type: ignore[import-untyped]

prefix_list = []

with open("database.txt", encoding="utf-8") as f:
    for line in f:
        if line.startswith("#"):
            continue
        line_list = line.split(";")
        prefix = line_list[0].strip().split("_")[1]

        smiles = line_list[1].strip()
        iupac = line_list[2].strip()

        mol = rdkit.Chem.rdmolfiles.MolFromSmiles(smiles)
        # num_rotatable_bonds = rdkit.Chem.Lipinski.NumRotatableBonds(mol)
        mol = rdkit.Chem.AddHs(mol)
        num_rotatable_bonds = rdkit.Chem.rdMolDescriptors.CalcNumRotatableBonds(
            mol, strict=0
        )

        if num_rotatable_bonds == 0:
            print(prefix, iupac)
            prefix_list.append(prefix)
print(len(prefix_list))
assert False
done_prefixes = []

for i in range(1, 12):
    # print(f"{i:02}")
    with open(f"batch/{i:02}.txt", encoding="utf-8") as f:
        for index, line in enumerate(f):
            prefix = line.strip()
            if prefix in prefix_list:
                done_prefixes.append(prefix)
                iupac = (
                    subprocess.run(
                        ["grep", prefix, "database.txt"],
                        capture_output=True,
                        check=True,
                    )
                    .stdout.decode("utf-8")
                    .split(";")[2]
                    .strip()
                )
                relaxed_forward = (
                    subprocess.run(
                        [
                            "tail",
                            "-n1",
                            f"ac-fep/{i}/{index}/{prefix}_relaxed_forward.fepout",
                        ],
                        capture_output=True,
                        check=True,
                    )
                    .stdout.decode("utf-8")
                    .split()[18]
                )
                relaxed_backward = (
                    subprocess.run(
                        [
                            "tail",
                            "-n1",
                            f"ac-fep/{i}/{index}/{prefix}_relaxed_backward.fepout",
                        ],
                        capture_output=True,
                        check=True,
                    )
                    .stdout.decode("utf-8")
                    .split()[18]
                )
                relaxed_bar = (
                    subprocess.run(
                        [
                            "tail",
                            "-n1",
                            f"ac-fep/{i}/{index}/relaxed_ParseFEP.log",
                        ],
                        capture_output=True,
                        check=True,
                    )
                    .stdout.decode("utf-8")
                    .split()[6]
                )
                frozen_forward = (
                    subprocess.run(
                        [
                            "tail",
                            "-n1",
                            f"ac-fep/{i}/{index}/{prefix}_frozen_forward.fepout",
                        ],
                        capture_output=True,
                        check=True,
                    )
                    .stdout.decode("utf-8")
                    .split()[18]
                )
                frozen_backward = (
                    subprocess.run(
                        [
                            "tail",
                            "-n1",
                            f"ac-fep/{i}/{index}/{prefix}_frozen_backward.fepout",
                        ],
                        capture_output=True,
                        check=True,
                    )
                    .stdout.decode("utf-8")
                    .split()[18]
                )
                frozen_bar = (
                    subprocess.run(
                        [
                            "tail",
                            "-n1",
                            f"ac-fep/{i}/{index}/frozen_ParseFEP.log",
                        ],
                        capture_output=True,
                        check=True,
                    )
                    .stdout.decode("utf-8")
                    .split()[6]
                )
                print(
                    i,
                    prefix,
                    iupac,
                    relaxed_forward,
                    relaxed_backward,
                    "",
                    "",
                    relaxed_bar,
                    "",
                    frozen_forward,
                    frozen_backward,
                    "",
                    "",
                    frozen_bar,
                    "",
                    sep=";",
                )

print(set(prefix_list) - set(done_prefixes))
