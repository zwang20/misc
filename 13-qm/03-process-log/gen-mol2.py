#!/usr/bin/python

import subprocess
from common import prefix_list, skip_list

print(
    """sample lines
     24 H14         3.7750    0.2200   10.1920 hc        1 MOL      0.046700
     14 C7         10.5550   -2.3160    1.4930 ca        1 MOL     -0.130600
     15 C8         10.6720   -1.1340    2.2210 ca        1 MOL     -0.098500
     26 H12       -10.3250   -1.6360    0.2910 hc        1 MOL      0.074200
"""
)
for prefix in prefix_list:
    if prefix in skip_list:
        continue
    print(prefix)

    # copy file
    subprocess.run(
        ["cp", f"FreeSolv/mol2files_gaff/mobley_{prefix}.mol2", "mol2/"]
    ).check_returncode()
    subprocess.run(["chmod", "-x", f"mol2/mobley_{prefix}.mol2"]).check_returncode()

    # write new file
    with (
        open(f"mol2/mobley_{prefix}.mol2") as input_mol2,
        open(f"mol2/qm_{prefix}.mol2", "w") as output_file,
        open(f"com/{prefix}.xyz") as input_xyz,
    ):
        while not (line := input_mol2.readline()).startswith("@<TRIPOS>ATOM"):
            output_file.write(line)
        output_file.write(line)
        num_atoms = int(input_xyz.readline().strip())
        input_xyz.readline()
        counter = 0
        while not (line := input_mol2.readline()).startswith("@<TRIPOS>BOND"):
            xyz_type, new_x, new_y, new_z = input_xyz.readline().split()
            new_x, new_y, new_z = float(new_x), float(new_y), float(new_z)
            line_list = line.split(maxsplit=5)
            assert (
                len(line_list[5]) == 30
            ), f"incorrect length {len(line_list[5])}"  # including newline
            assert xyz_type in line_list[1], f"{xyz_type} not in {line_list[1]}"
            old_x, old_y, old_z = (
                float(line_list[2]),
                float(line_list[3]),
                float(line_list[4]),
            )

            distance = (
                (new_x - old_x) ** 2 + (new_y - old_y) ** 2 + (new_z - old_z) ** 2
            )
            assert distance < 0.5

            updated_line = f"{line_list[0]:>7} {line_list[1]:<8}{new_x:> 10.4f}{new_y:> 10.4f}{new_z:> 10.4f} {line_list[5]}"
            print(line, end="")
            print(updated_line, end="")
            assert len(updated_line) == 77, len(updated_line)

            counter += 1
            assert counter <= num_atoms
            output_file.write(updated_line)
        output_file.write(line)
        while line := input_mol2.readline():
            output_file.write(line)

    input_line_count = (
        subprocess.run(["wc", "-l", f"mol2/mobley_{prefix}.mol2"], capture_output=True)
        .stdout.decode("utf-8")
        .split()[0]
    )
    output_line_count = (
        subprocess.run(["wc", "-l", f"mol2/qm_{prefix}.mol2"], capture_output=True)
        .stdout.decode("utf-8")
        .split()[0]
    )

    assert input_line_count == output_line_count, (input_line_count, output_line_count)
