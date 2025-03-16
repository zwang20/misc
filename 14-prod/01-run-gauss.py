"""
run-gauss.py

runs gaussian geometry optimization for molecule
"""

# pylint: disable=C0103

import itertools
import random
import subprocess

from common import get_previous_files

previous_files = get_previous_files()

# get prefixes
prefix_list = []
with open(f"batch/{previous_files[-1]}", encoding="utf-8") as f:
    for line in f:
        prefix_list.append(line.strip())

# generate gauss input
for prefix in prefix_list:
    print(prefix)
    subprocess.run(
        [
            "obabel",
            f"FreeSolv/mol2files_sybyl/mobley_{prefix}.mol2",
            f"-Ogauss/{prefix}.com",
        ],
        check=True,
    )

    # use def2SVP for heavy elements
    heavy_elements = False
    with open(f"gauss/{prefix}.com", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                if line.split()[0] in ("I",):
                    heavy_elements = True

    if not heavy_elements:
        subprocess.run(
            [
                "sed",
                "s/^#$/#m062X\\/6-31+G(d) OPT Freq=noraman/",
                "-i",
                f"gauss/{prefix}.com",
            ],
            check=True,
        )
    else:
        subprocess.run(
            [
                "sed",
                "s/^#$/#m062X\\/def2SVP OPT Freq=noraman/",
                "-i",
                f"gauss/{prefix}.com",
            ],
            check=True,
        )

# copy files to server
subprocess.run(["scp", "-r", "gauss", "kdm:/srv/scratch/z5358697/"], check=True)

# shuffle hosts
hosts = ["katana1", "katana2", "katana3"]
random.shuffle(hosts)

# run gauss
for prefix, host in zip(prefix_list, itertools.cycle(hosts)):
    print(prefix, host)

    subprocess.run(
        [
            "ssh",
            host,
            f"{{ cd /srv/scratch/z5358697/gauss; module load gaussian/09-D.01; g09 < {prefix}.com | tee {prefix}.log || g09 < {prefix}.com | tee {prefix}.log; }}",  # pylint: disable=C0301
        ],
        check=True,
    )

# copy files back
subprocess.run(["scp", "-r", "kdm:/srv/scratch/z5358697/gauss", "."], check=True)
