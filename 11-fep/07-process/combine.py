#!/usr/bin/python
# combines the energies from energies.csv and FreeSolv database into combined.csv

from tqdm import tqdm
import subprocess

with open("energies.csv") as input_file:
    with open("combined.csv", "w") as output_file:
        for line in tqdm(input_file):
            prefix = line.split(",")[0]
            grep_process = subprocess.run(
                ["grep", f"mobley_{prefix}", "FreeSolv/database.txt"],
                capture_output=True,
            )
            grep_process.check_returncode()
            o = grep_process.stdout.decode("utf-8").split("; ")
            output_file.write(f"{line.strip()},{','.join(o[3:7])}\n")
