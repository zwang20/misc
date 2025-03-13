"""
run prep.py

makes and runs min and equil
"""

# pylint: disable=C0103

import subprocess

from common import get_prefix_list

for prefix in get_prefix_list():
    print(prefix)

    # 0. check for fake frequencies
    # os.system("grep ' Frequencies --' */*.log")
    assert (
        subprocess.run(
            ["grep ' Frequencies --' */*.log | grep '  -'"], shell=True, check=False
        ).returncode
        != 0
    ), "fake frequencies found"

    # 1. convert .com to .xyz
    subprocess.run(["cp", f"gauss/{prefix}.log", f"xyz/{prefix}.log"], check=True)
    subprocess.run(["perl", "-w", "crin", "xyz", f"xyz/{prefix}.log"], check=True)
