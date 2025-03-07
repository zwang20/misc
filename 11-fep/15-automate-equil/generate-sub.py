#!/usr/bin/python
import os

with open("database.txt") as input_file:

    # delete previous
    os.system("rm sub*.sh")

    counter = 0
    for input_line in input_file:
        if input_line.startswith("#"):
            continue
        prefix = input_line.strip().split(";", 1)[0].strip().split("_")[1]

        with open(f"sub{counter // 50}.sh", "a") as output_file:
            output_file.write("#!/usr/bin/bash\n")
            output_file.write("set -e\n")
            output_file.write(f"cd {prefix}; qsub {prefix}_prep; cd .. \n")
        counter += 1
