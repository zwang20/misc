#!/usr/bin/python
import subprocess
import os

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


for index, prefix in enumerate(prefix_list):

    if prefix != '9073553':
        continue
    print(index, prefix, end=" ", flush=True)

    subprocess.run(
        ["xvfb-run", "vmd"],
        input=f"parsefep -forward relaxed/{index}/mobley_{prefix}_{index}.fepout -backward relaxed/{index + len(prefix_list)}/mobley_{prefix}_{index + len(prefix_list)}.fepout -bar".encode(
            "utf-8"
        ),
    )
    os.system(f"mv ParseFEP.log ParseFEP_{prefix}.log")

    os.system(f"grep error ParseFEP_{prefix}.log")
