#!/usr/bin/python
import os
import subprocess
import glob

todo_list = [
    # "2146331",
    # "6091882",
    # "8983100",
    "4434915",
]

for mobley_id in todo_list:
    os.chdir(mobley_id)

    for mode in ["fw0", "fw1", "bw0", "bw1", "fwf0", "fwf1", "bwf0", "bwf1"]:
        os.chdir(mode)

        # find .o*
        output = glob.glob(f"{mobley_id}_{mode}.o*")
        assert len(output) == 1
        output = output[0]

        # check job is successful
        subprocess.run(
            ["grep", "^Job execution was successful. Exit Status 0. ", output],
            capture_output=True,
        ).check_returncode()

        # get walltime
        walltime = (
            subprocess.run(["grep", "^Walltime: ", output], capture_output=True)
            .stdout.decode("utf-8")
            .split()[1]
        )

        # get memory usage
        resources = (
            subprocess.run(["grep", "^| k", output], capture_output=True)
            .stdout.decode("utf-8")
            .split()
        )
        hostname = resources[1]
        memory = resources[8]

        # get fep
        fep = (
            subprocess.run(
                [
                    "grep",
                    "-F",
                    "net change until now is",
                    f"mobley_{mobley_id}_{mode}.fepout",
                ],
                capture_output=True,
            )
            .stdout.decode("utf-8")
            .strip()
            .split("\n")[-1]
            .split()[-1]
        )

        print(f"{fep},{hostname},{walltime},{memory}")

        os.chdir("..")
    os.chdir("..")
