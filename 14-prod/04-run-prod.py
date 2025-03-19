"""
run-prod.py

runs prod

"""

# pylint: disable=C0103

import os
import subprocess

from common import get_prefix_list
from common import generic_template
from common import prod_io, prod_run
from common import constraint_frozen, constraint_gpu
from common import qsub_frozen, qsub_gpu

batch = input("Batch number:")
prefix_list = get_prefix_list(batch)

for index, prefix in enumerate(prefix_list):
    print(index, prefix)
    index_1 = index + len(prefix_list)
    index_2 = index + len(prefix_list) * 2
    index_3 = index + len(prefix_list) * 3

    # copy files
    for i in (index, index_1, index_2, index_3):
        os.makedirs(f"ab-prod/{batch}/{i}", exist_ok=True)
        subprocess.run(["cp", "fep.tcl", f"ab-prod/{batch}/{i}/"], check=True)
        for suffix in (".prmtop", ".pdb", "_equil.coor", "_equil.vel", "_equil.xsc"):
            if i in (index, index_1):
                subprocess.run(
                    [
                        "cp",
                        f"aa-prep/{batch}/{index}/mobley_{prefix}{suffix}",
                        f"ab-prod/{batch}/{i}/",
                    ],
                    check=True,
                )
            else:
                subprocess.run(
                    [
                        "cp",
                        f"aa-prep/{batch}/{index_1}/mobley_{prefix}{suffix}",
                        f"ab-prod/{batch}/{i}/",
                    ],
                    check=True,
                )
    # get size
    with open(f"aa-prep/{batch}/{index}/mobley_{prefix}.pdb", encoding="utf-8") as f:
        x, y, z = map(float, f.readline().split(maxsplit=4)[1:4])

    # relaxed forward
    with open(f"ab-prod/{batch}/{index}/prod.namd", "w", encoding="utf-8") as f:
        f.write(
            generic_template.format(
                io=prod_io.format(prefix=prefix),
                prefix=prefix,
                x=x,
                y=y,
                z=z,
                margin=2.0,
                constraints=constraint_gpu,
                run=prod_run.format(
                    prefix=prefix, mode=index, start=0, end=1, step=0.05
                ),
            )
        )
    # relaxed reversed
    with open(f"ab-prod/{batch}/{index_1}/prod.namd", "w", encoding="utf-8") as f:
        f.write(
            generic_template.format(
                io=prod_io.format(prefix=prefix),
                prefix=prefix,
                x=x,
                y=y,
                z=z,
                margin=2.0,
                constraints=constraint_gpu,
                run=prod_run.format(
                    prefix=prefix, mode=index, start=1, end=0, step=-0.05
                ),
            )
        )
    # frozen forward
    with open(f"ab-prod/{batch}/{index_2}/prod.namd", "w", encoding="utf-8") as f:
        f.write(
            generic_template.format(
                io=prod_io.format(prefix=prefix),
                prefix=prefix,
                x=x,
                y=y,
                z=z,
                margin=2.0,
                constraints=constraint_frozen.format(prefix=prefix),
                run=prod_run.format(
                    prefix=prefix, mode=index, start=0, end=1, step=0.05
                ),
            )
        )
    # frozen reversed
    with open(f"ab-prod/{batch}/{index_3}/prod.namd", "w", encoding="utf-8") as f:
        f.write(
            generic_template.format(
                io=prod_io.format(prefix=prefix),
                prefix=prefix,
                x=x,
                y=y,
                z=z,
                margin=2.0,
                constraints=constraint_frozen.format(prefix=prefix),
                run=prod_run.format(
                    prefix=prefix, mode=index, start=1, end=0, step=-0.05
                ),
            )
        )

# write qsub files
with open(f"ab-prod/{batch}/{batch}.gpu", "w", encoding="utf-8") as f:
    f.write(qsub_gpu.format(start=0, end=len(prefix_list) * 2 - 1))
with open(f"ab-prod/{batch}/{batch}.frozen", "w", encoding="utf-8") as f:
    f.write(
        qsub_frozen.format(start=len(prefix_list) * 2, end=len(prefix_list) * 4 - 1)
    )

# copy files
subprocess.run(
    ["scp", "-r", f"ab-prod/{batch}", "kdm:/srv/scratch/z5358697/ab-prod/"], check=True
)

# qsub
subprocess.run(
    [
        "ssh",
        "katana",
        f"{{ cd /srv/scratch/z5358697/ab-prod/{batch}; qsub {batch}.frozen || qsub {batch}.frozen ; }}",  # pylint: disable=C0301
    ],
    check=True,
)

subprocess.run(
    [
        "ssh",
        "katana",
        f"{{ cd /srv/scratch/z5358697/ab-prod/{batch}; qsub {batch}.gpu || qsub {batch}.gpu ; }}",  # pylint: disable=C0301
    ],
    check=True,
)
