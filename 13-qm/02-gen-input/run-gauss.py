#!/usr/bin/python
import itertools
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

for prefix, host in zip(
    prefix_list, itertools.cycle(("katana1", "katana2", "katana3"))
):
    print(prefix, host)
    print(
        f"{{ cd /srv/scratch/z5358697/com; module load gaussian/09-D.01; g09 < {prefix}.com | tee {prefix}.log; }}"
    )
    subprocess.run(
        [
            "ssh",
            host,
            f"{{ cd /srv/scratch/z5358697/com; module load gaussian/09-D.01; g09 < {prefix}.com | tee {prefix}.log; }}",
        ]
    ).check_returncode()
