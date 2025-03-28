# pylint: disable=C0103

import sys
import os
import subprocess

from common import tleap_template
from common import generic_template
from common import min_io, equil_io
from common import min_run, equil_run
from common import katana_min_equil, gadi_min_equil

assert len(sys.argv) == 2, (sys.argv, len(sys.argv))
prefix = sys.argv[1]


# copy files
subprocess.run(["cp", f"FreeSolv/mol2files_gaff/mobley_{prefix}.mol2", "."], check=True)
subprocess.run(["chmod", "-x", f"mobley_{prefix}.mol2"], check=True)
subprocess.run(["cp", f"FreeSolv/amber/mobley_{prefix}.frcmod", "."], check=True)

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
    assert abs(high - low) > 1e-06, (high, low, abs(high - low), "Does not converge")

# create folder
os.makedirs(f"ba-mm-prep/{prefix}", exist_ok=True)

# move files
subprocess.run(["mv", f"mobley_{prefix}.inpcrd", f"ba-mm-prep/{prefix}/"], check=True)
subprocess.run(["mv", f"mobley_{prefix}.prmtop", f"ba-mm-prep/{prefix}/"], check=True)
subprocess.run(["mv", f"mobley_{prefix}.pdb", f"ba-mm-prep/{prefix}/"], check=True)

# clean up files
subprocess.run(["rm", f"mobley_{prefix}.frcmod"], check=True)
subprocess.run(["rm", f"mobley_{prefix}.mol2"], check=True)
subprocess.run(["rm", f"leap.log"], check=True)

# write input files
with open(f"ba-mm-prep/{prefix}/min.namd", "w", encoding="utf-8") as f:
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

with open(f"ba-mm-prep/{prefix}/equil.namd", "w", encoding="utf-8") as f:
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

with open(f"ba-mm-prep/{prefix}/{prefix}.mm.me.katana", "w", encoding="utf-8") as f:
    f.write(katana_min_equil.format())

with open(f"ba-mm-prep/{prefix}/{prefix}.mm.me.gadi.bw", "w", encoding="utf-8") as f:
    f.write(gadi_min_equil.format(queue="normalbw"))

with open(f"ba-mm-prep/{prefix}/{prefix}.mm.me.gadi.sl", "w", encoding="utf-8") as f:
    f.write(gadi_min_equil.format(queue="normalsl"))

with open(f"ba-mm-prep/{prefix}/{prefix}.mm.me.gadi.sr", "w", encoding="utf-8") as f:
    f.write(gadi_min_equil.format(queue="normalsr"))
