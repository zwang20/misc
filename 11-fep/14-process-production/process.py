#!/usr/bin/python
import os
import subprocess
import glob

todo_list = list(
    i.split()[0].split("_")[1]
    for i in """
mobley_9073553 methylsulfanylmethane          chosen for thioether
""".strip().split(
        "\n"
    )
)

for mobley_id in todo_list:
    print(mobley_id)
    os.chdir(mobley_id)

    # combine fepouts
    os.system(
        f"cat fw0/mobley_{mobley_id}_fw0.fepout fw1/mobley_{mobley_id}_fw1.fepout > mobley_{mobley_id}_fw.fepout"
    )
    os.system(
        f"cat bw0/mobley_{mobley_id}_bw0.fepout bw1/mobley_{mobley_id}_bw1.fepout > mobley_{mobley_id}_bw.fepout"
    )
    os.system(
        f"cat fwf0/mobley_{mobley_id}_fwf0.fepout fwf1/mobley_{mobley_id}_fwf1.fepout > mobley_{mobley_id}_fwf.fepout"
    )
    os.system(
        f"cat bwf0/mobley_{mobley_id}_bwf0.fepout bwf1/mobley_{mobley_id}_bwf1.fepout > mobley_{mobley_id}_bwf.fepout"
    )

    # frozen
    subprocess.run(
        ["xvfb-run", "vmd"],
        input=f"parsefep -forward mobley_{mobley_id}_fwf.fepout -backward mobley_{mobley_id}_bwf.fepout -bar".encode(
            "utf-8"
        ),
    ).check_returncode()
    os.system(f"mv ParseFEP.log ParseFEP_frozen.log")

    # thawed
    subprocess.run(
        ["xvfb-run", "vmd"],
        input=f"parsefep -forward mobley_{mobley_id}_fw.fepout -backward mobley_{mobley_id}_bw.fepout -bar".encode(
            "utf-8"
        ),
    ).check_returncode()

    os.system("tail -n 1 ParseFEP.log")
    os.system("tail -n 1 ParseFEP_frozen.log")

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
