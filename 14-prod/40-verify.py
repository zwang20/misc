#!/usr/bin/python

import os
import subprocess

from common import generic_template
from common import prod_io, prod_run
from common import constraint_frozen, constraint_gpu
from common import qsub_frozen, qsub_gpu

# uninstall old kernel (-6.12.12+bpo)

prefix_list = """
3323117
2481002
6239320
1723043
4039055
""".strip().split('\n')

prefixes = {
        "3323117": (18, 0, 4),
        "6239320": (18, 1, 5),
        "1723043": (18, 2, 6),
        '4039055': (18, 3, 7),
}

# rf
# ./zz-verify/{prefix}/{0-19}/
# rr
# ./zz-verify/{prefix}/{20-39}/
# ff
# ./zz-verify/{prefix}/{40-59}/
# fr
# ./zz-verify/{prefix}/{60-79}/

for prefix, indices in prefixes.items():
    print(prefix)

    for i in range(80):
        os.makedirs(f"zz-verify/{prefix}/{i}", exist_ok=True)
        subprocess.run(["cp", "fep.tcl", f"zz-verify/{prefix}/{i}/"], check=True)
        # get size
        with open(f"aa-prep/{indices[0]}/{indices[1]}/mobley_{prefix}.pdb", encoding="utf-8") as f:
            x, y, z = map(float, f.readline().split(maxsplit=4)[1:4])

        # loop over all runners
        for suffix in (".prmtop", ".pdb", "_equil.coor", "_equil.vel", "_equil.xsc"):
            if i < 40:
                subprocess.run(
                    [
                        "cp",
                        f"aa-prep/{indices[0]}/{indices[1]}/mobley_{prefix}{suffix}",
                        f"zz-verify/{prefix}/{i}/",
                    ],
                    check=True,
                )
                if i < 20:
                    # relaxed forward
                    with open(f"zz-verify/{prefix}/{i}/prod.namd", "w", encoding="utf-8") as f:
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
                                    prefix=prefix, mode=i, start=i / 20, end=i / 20 + 0.05, step=0.05
                                ),
                            )
                        )
                else:
                    # relaxed reversed
                    with open(f"zz-verify/{prefix}/{i}/prod.namd", "w", encoding="utf-8") as f:
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
                                    prefix=prefix, mode=i, start=1 - (i - 20) / 20, end=1 - (i - 20) / 20 - 0.05, step=-0.05
                                ),
                            )
                        )
            else:
                subprocess.run(
                    [
                        "cp",
                        f"aa-prep/{indices[0]}/{indices[2]}/mobley_{prefix}{suffix}",
                        f"zz-verify/{prefix}/{i}/",
                    ],
                    check=True,
                )
                if i < 60:
                    # frozen forward
                    with open(f"zz-verify/{prefix}/{i}/prod.namd", "w", encoding="utf-8") as f:
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
                                    prefix=prefix, mode=i, start=(i - 40) / 20, end=(i-40) / 20 + 0.05, step=0.05
                                ),
                            )
                        )
                else:
                    # frozen reversed
                    with open(f"zz-verify/{prefix}/{i}/prod.namd", "w", encoding="utf-8") as f:
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
                                    prefix=prefix, mode=i, start=1 - (i - 60) / 20, end=1 - (i - 60) / 20 - 0.05, step=-0.05
                                ),
                            )
                        )

    # write qsub
    with open(f"zz-verify/{prefix}/{prefix}.gpu", "w", encoding="utf-8") as f:
        f.write(qsub_gpu.format(start=0, end=39))
    with open(f"zz-verify/{prefix}/{prefix}.frozen", "w", encoding="utf-8") as f:
        f.write(qsub_frozen.format(start=40, end=79))

with open("zz-verify/qsub.sh", 'w') as f:
    f.write("#!/usr/bin/bash\n")
    f.write("set -e\n")
    for prefix in prefixes:
        f.write(f"cd {prefix}; qsub {prefix}.gpu; qsub {prefix}.frozen; cd .. \n")
