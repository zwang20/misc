#!/usr/bin/python

import parmed as pmd

from common import prefix_list, skip_list


for prefix in prefix_list:
    print(prefix)

    # load the xyz file
    parm = pmd.load_file(
        f"FreeSolv/amber/mobley_{prefix}.prmtop", xyz=f"com/{prefix}.xyz"
    )
    print(parm)
    parm.save(f"{prefix}.mol2")
    assert False
