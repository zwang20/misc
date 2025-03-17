"""
process-prod.py

processes results of production run
"""

# pylint: disable=C0103

import os
import subprocess

from common import get_prefix_list, get_batch_number

batch = get_batch_number()
prefix_list = get_prefix_list(batch)

for index, prefix in enumerate(prefix_list):
    index_1 = index + len(prefix_list)
    index_2 = index + len(prefix_list) * 2
    index_3 = index + len(prefix_list) * 3
    print(index, prefix)

    # make folder
    os.makedirs(f"ac-fep/{batch}/{index}", exist_ok=True)

    # copy files
    subprocess.run(
        [
            "cp",
            f"ab-prod/{batch}/{index}/mobley_{prefix}_{index}.fepout",
            f"ac-fep/{batch}/{index}/{prefix}_relaxed_forward.fepout",
        ],
        check=True,
    )
    subprocess.run(
        [
            "cp",
            f"ab-prod/{batch}/{index_1}/mobley_{prefix}_{index}.fepout",
            f"ac-fep/{batch}/{index}/{prefix}_relaxed_backward.fepout",
        ],
        check=True,
    )
    subprocess.run(
        [
            "cp",
            f"ab-prod/{batch}/{index_2}/mobley_{prefix}_{index}.fepout",
            f"ac-fep/{batch}/{index}/{prefix}_frozen_forward.fepout",
        ],
        check=True,
    )
    subprocess.run(
        [
            "cp",
            f"ab-prod/{batch}/{index_3}/mobley_{prefix}_{index}.fepout",
            f"ac-fep/{batch}/{index}/{prefix}_frozen_backward.fepout",
        ],
        check=True,
    )

    relaxed_input = f"parsefep -forward ac-fep/{batch}/{index}/{prefix}_relaxed_forward.fepout -backward ac-fep/{batch}/{index}/{prefix}_relaxed_backward.fepout -bar"
    frozen_input = f"parsefep -forward ac-fep/{batch}/{index}/{prefix}_frozen_forward.fepout -backward ac-fep/{batch}/{index}/{prefix}_frozen_backward.fepout -bar"

    # calculate bar
    subprocess.run(
        ["xvfb-run", "-a", "vmd"],
        input=relaxed_input.encode("utf-8"),
        check=True,
    )
    subprocess.run(
        ["mv", "ParseFEP.log", f"ac-fep/{batch}/{index}/relaxed_ParseFEP.log"],
        check=True,
    )
    subprocess.run(
        ["xvfb-run", "-a", "vmd"],
        input=frozen_input.encode("utf-8"),
        check=True,
    )
    subprocess.run(
        ["mv", "ParseFEP.log", f"ac-fep/{batch}/{index}/frozen_ParseFEP.log"],
        check=True,
    )
