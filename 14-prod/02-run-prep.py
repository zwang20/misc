"""
run prep.py

makes and runs min and equil
"""

# pylint: disable=C0103

import os
import subprocess

from common import get_prefix_list, get_batch_number
from common import tleap_template
from common import generic_template
from common import min_run, min_io
from common import equil_run, equil_io
from common import constraint_frozen
from common import qsub_min_equil

batch = get_batch_number()
prefix_list = get_prefix_list(batch)
print(batch)
for index, prefix in enumerate(prefix_list):
    print(index, prefix)
    index_1 = index + len(prefix_list)

    # 0. check for fake frequencies
    assert (
        subprocess.run(
            ["grep ' Frequencies --' */*.log | grep '  -'"], shell=True, check=False
        ).returncode
        != 0
    ), "fake frequencies found"

    # 1. convert .com to .xyz
    subprocess.run(["cp", f"gauss/{prefix}.log", f"xyz/{prefix}.log"], check=True)
    subprocess.run(["perl", "-w", "crin", "xyz", f"xyz/{prefix}.log"], check=True)

    # 2. create mol2 file
    subprocess.run(
        ["cp", f"FreeSolv/mol2files_gaff/mobley_{prefix}.mol2", "mol2/"], check=True
    )
    subprocess.run(["chmod", "-x", f"mol2/mobley_{prefix}.mol2"], check=True)

    # write new file
    with (
        open(f"mol2/mobley_{prefix}.mol2", encoding="utf-8") as input_mol2,
        open(f"mol2/qm_{prefix}.mol2", "w", encoding="utf-8") as output_file,
        open(f"xyz/{prefix}.xyz", encoding="utf-8") as input_xyz,
    ):
        while not (line := input_mol2.readline()).startswith("@<TRIPOS>ATOM"):
            output_file.write(line)
        output_file.write(line)
        num_atoms = int(input_xyz.readline().strip())
        input_xyz.readline()
        counter = 0
        while not (line := input_mol2.readline()).startswith("@<TRIPOS>BOND"):
            xyz_type, new_x_str, new_y_str, new_z_str = input_xyz.readline().split()
            new_x, new_y, new_z = float(new_x_str), float(new_y_str), float(new_z_str)
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

            updated_line = f"{line_list[0]:>7} {line_list[1]:<8}{new_x:> 10.4f}{new_y:> 10.4f}{new_z:> 10.4f} {line_list[5]}"  # pylint: disable=C0301
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
        subprocess.run(
            ["wc", "-l", f"mol2/mobley_{prefix}.mol2"], capture_output=True, check=True
        )
        .stdout.decode("utf-8")
        .split()[0]
    )
    output_line_count = (
        subprocess.run(
            ["wc", "-l", f"mol2/qm_{prefix}.mol2"], capture_output=True, check=True
        )
        .stdout.decode("utf-8")
        .split()[0]
    )

    assert input_line_count == output_line_count, (input_line_count, output_line_count)

    # 3. create pdb file
    # Do binary search

    subprocess.run(["cp", f"mol2/qm_{prefix}.mol2", "."], check=True)
    low, high = (0.0, 20.0)
    curr = 10.0
    while True:
        with open("leap.in", "w", encoding="utf-8") as f:
            f.write(tleap_template.format(prefix=prefix, size=curr))

        # solvate molecule
        subprocess.run(
            ["tleap", "-s", "-f", "leap.in"],
            capture_output=True,
            check=True,
        )

        # add beta to molecule
        subprocess.run(
            [
                "sed",
                "-i",
                "/MOL/s/1\\.00  0\\.00/1.00  1.00/g",
                f"mobley_{prefix}.pdb",
            ],
            check=True,
        )

        # get size
        with open(f"mobley_{prefix}.pdb", encoding="utf-8") as f:
            x, y, z = map(float, f.readline().split(maxsplit=4)[1:4])
            print(x, y, z)

        num_atoms = int(
            subprocess.run(
                [f"cat mobley_{prefix}.pdb | grep ATOM | wc -l"],
                shell=True,
                capture_output=True,
                check=True,
            ).stdout.decode("utf-8")
        )

        print(num_atoms, curr)
        if num_atoms > 3000:
            high = curr
            curr = (low + high) / 2
        elif num_atoms < 2900:
            low = curr
            curr = (low + high) / 2
        else:
            break
        assert abs(high - low) > 1e-06, "Does not converge"

    subprocess.run(["rm", f"qm_{prefix}.mol2"], check=True)
    os.makedirs(f"aa-prep/{batch}/{index}", exist_ok=True)
    os.makedirs(f"aa-prep/{batch}/{index_1}", exist_ok=True)
    for suffix in ("inpcrd", "pdb", "prmtop"):
        subprocess.run(
            ["cp", f"mobley_{prefix}.{suffix}", f"aa-prep/{batch}/{index}/"], check=True
        )
        subprocess.run(
            ["mv", f"mobley_{prefix}.{suffix}", f"aa-prep/{batch}/{index_1}/"],
            check=True,
        )

    # write input files
    # normal
    with open(f"aa-prep/{batch}/{index}/min.namd", "w", encoding="utf-8") as f:
        f.write(
            generic_template.format(
                io=min_io.format(prefix=prefix),
                x=x,
                y=y,
                z=z,
                run=min_run,
                prefix=prefix,
                margin=8.0,
                constraints="",
            )
        )

    with open(f"aa-prep/{batch}/{index}/equil.namd", "w", encoding="utf-8") as f:
        f.write(
            generic_template.format(
                io=equil_io.format(prefix=prefix),
                run=equil_run,
                x=x,
                y=y,
                z=z,
                prefix=prefix,
                margin=8.0,
                constraints="",
            )
        )

    # frozen
    with open(f"aa-prep/{batch}/{index_1}/min.namd", "w", encoding="utf-8") as f:
        f.write(
            generic_template.format(
                io=min_io.format(prefix=prefix),
                x=x,
                y=y,
                z=z,
                run=min_run,
                prefix=prefix,
                margin=8.0,
                constraints=constraint_frozen.format(prefix=prefix),
            )
        )

    with open(f"aa-prep/{batch}/{index_1}/equil.namd", "w", encoding="utf-8") as f:
        f.write(
            generic_template.format(
                io=equil_io.format(prefix=prefix),
                run=equil_run,
                x=x,
                y=y,
                z=z,
                prefix=prefix,
                margin=8.0,
                constraints=constraint_frozen.format(prefix=prefix),
            )
        )

# # write qsub file
# with open(f"aa-prep/{batch}/{batch}.prep", "w", encoding="utf-8") as f:
#     f.write(qsub_min_equil.format(length=len(prefix_list) * 2 - 1))
#
# # copy files
# subprocess.run(
#     ["scp", "-r", f"aa-prep/{batch}", "kdm:/srv/scratch/z5358697/aa-prep/"], check=True
# )
#
# # qsub
# subprocess.run(
#     [
#         "ssh",
#         "katana",
#         f"{{ cd /srv/scratch/z5358697/aa-prep/{batch}; qsub {batch}.prep || qsub {batch}.prep ; }}",  # pylint: disable=C0301
#     ],
#     check=True,
# )
