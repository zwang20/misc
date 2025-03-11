#!/usr/bin/python
import os
import subprocess

prefix_list = list(
    i.split()[0].split("_")[1]
    for i in """
mobley_2146331
mobley_6091882
mobley_8983100
mobley_4434915
mobley_9029594
mobley_4364398
mobley_525934
mobley_8260524
mobley_7532833
mobley_7015518
mobley_6474572
mobley_7261305
mobley_6714389
mobley_5692472
mobley_9073553
""".strip().split(
        "\n"
    )
)


for prefix in prefix_list:
    print(prefix)
    os.makedirs("com", exist_ok=True)
    subprocess.run(
        [
            "obabel",
            f"FreeSolv/mol2files_sybyl/mobley_{prefix}.mol2",
            f"-Ocom/{prefix}.com",
        ]
    )
    subprocess.run(
        ["sed", "s/^#$/#m062X\\/6-31+G(d) OPT Freq=noraman/", "-i", f"com/{prefix}.com"]
    )
