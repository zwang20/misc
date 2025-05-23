#!/usr/bin/python
import re

prefix = "3323117"
# 0. copy mol2 files
# 1. convert mol2 to xyz
with (
    open(f"aa-crest/{prefix}/mobley_{prefix}.mol2") as input_file,
    open(f"aa-crest/{prefix}/mobley_{prefix}.xyz", "w") as output_file,
):
    input_file.readline()
    input_file.readline()
    atom_count_ref = int(input_file.readline().split()[0])
    output_file.write(f" {atom_count_ref}\n\n")
    atom_count = 0
    while not input_file.readline().strip().startswith("@<TRIPOS>ATOM"):
        pass
    while not (input_line := input_file.readline().strip()).startswith("@<TRIPOS>BOND"):
        line = input_line.split()
        x, y, z = map(float, line[2:5])
        output_line = f"{re.sub(r'\d+$', '', line[1]).strip(): <2}    {x: 2f}    {y: 2f}    {z: 2f}\n"
        assert len(output_line) == 42, (output_line, len(output_line))
        output_file.write(output_line)
        atom_count += 1
    assert atom_count == atom_count_ref, (atom_count, atom_count_ref)

# crest mobley_3323117.xyz --gfn2 --gbsa h2o -T $(nproc)
