#!/usr/bin/python

import os
import subprocess

todo_list = list(
    i.split()[0].split("_")[1]
    for i in """
mobley_2146331 formaldehyde                   chosen for aldehyde
mobley_6091882 ethylene                       chosen for alkene
mobley_8983100 bromomethane                   chosen for alkyl bromide
mobley_4434915 chloromethane                  chosen for alkyl chloride
mobley_9029594 fluoromethane                  chosen for alkyl fluoride
mobley_4364398 iodomethane                    chosen for alkyl iodide
mobley_525934  methanethiol                   chosen for alkylthiol; thiol (sulfanyl)
mobley_8260524 prop-1-yne                     chosen for alkyne
mobley_7532833 acetonitrile                   chosen for carbonitrile
mobley_7015518 methoxymethane                 chosen for dialkyl ether
mobley_6474572 chloroethylene                 chosen for halogen derivative
mobley_7261305 hydrazine                      chosen for hydrazine derivative
mobley_6714389 methanamine                    chosen for primary aliphatic amine (alkylamine); primary amine
mobley_5692472 N-methylmethanamine            chosen for secondary aliphatic amine (dialkylamine); secondary amine
mobley_9073553 methylsulfanylmethane          chosen for thioether

""".strip().split(
        "\n"
    )
)

for mobley_id in todo_list:
    os.chdir(mobley_id)
    # forward
    print(
        sum(
            float(i)
            for i in subprocess.run(
                [
                    f"cat mobley_{mobley_id}_fw.fepout | grep '#Free energy change for lambda window' | cut -d ' ' -f 12"
                ],
                shell=True,
                capture_output=True,
            )
            .stdout.decode("utf-8")
            .split()
        ),
        end=",",
    )

    # bw
    print(
        sum(
            float(i)
            for i in subprocess.run(
                [
                    f"cat mobley_{mobley_id}_bw.fepout | grep '#Free energy change for lambda window' | cut -d ' ' -f 12"
                ],
                shell=True,
                capture_output=True,
            )
            .stdout.decode("utf-8")
            .split()
        ),
        end=",,",
    )

    print(
        subprocess.run(
            ["tail -n 1 ParseFEP.log | cut -d ' ' -f 7"],
            shell=True,
            capture_output=True,
        )
        .stdout.decode("utf-8")
        .strip(),
        end=",",
    )

    # forward
    print(
        sum(
            float(i)
            for i in subprocess.run(
                [
                    f"cat mobley_{mobley_id}_fwf.fepout | grep '#Free energy change for lambda window' | cut -d ' ' -f 12"
                ],
                shell=True,
                capture_output=True,
            )
            .stdout.decode("utf-8")
            .split()
        ),
        end=",",
    )

    # bw
    print(
        sum(
            float(i)
            for i in subprocess.run(
                [
                    f"cat mobley_{mobley_id}_bwf.fepout | grep -F '#Free energy change for lambda window' | cut -d ' ' -f 12"
                ],
                shell=True,
                capture_output=True,
            )
            .stdout.decode("utf-8")
            .split()
        ),
        end=",,",
    )

    print(
        subprocess.run(
            ["tail -n 1 ParseFEP_frozen.log | cut -d ' ' -f 7"],
            shell=True,
            capture_output=True,
        )
        .stdout.decode("utf-8")
        .strip(),
        end=",",
    )
    print()
    os.chdir("..")
