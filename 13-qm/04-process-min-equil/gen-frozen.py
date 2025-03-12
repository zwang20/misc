#!/usr/bin/python

import subprocess, os
from common import prefix_list, skip_list

run_template = f"""#!/usr/bin/bash
#PBS -l walltime=12:00:00
#PBS -l mem=1Gb
#PBS -l ncpus=16
#PBS -l select=cpuflags=avx512_vpopcntdq
#PBS -j oe
#PBS -J 0-{len(prefix_list) - 1}
set -e


# check if exists
cd "${{PBS_O_WORKDIR}}/${{PBS_ARRAY_INDEX}}"

echo

echo hostname "$(hostname)"
echo nproc "$(nproc)"
lscpu | grep "Model name"

PATH="/srv/scratch/z5358697/namd_avx512:$PATH" namd3 "+p$(nproc)" frozen.namd
"""

for index, prefix in enumerate(prefix_list):
    if prefix in skip_list:
        continue
    print(index, prefix)

    # check if exit successful
    subprocess.run(
        [
            "grep",
            "-F",
            "Job execution was successful. Exit Status 0.",
            f"min-equil/qm-min-equil.o6296139.{index}",
        ],
        capture_output=True,
    ).check_returncode()

    assert False
