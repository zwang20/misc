#!/usr/bin/python

# watch jobs (probably)

import os
import subprocess
import time

height = os.get_terminal_size().lines
while True:
    output = (
        subprocess.run(["ssh", "kdm", "qstat -su z5358697 -w -t"], capture_output=True)
        .stdout.decode("utf-8")
        .strip()
        .split("\n")
    )
    for index, line in enumerate(output):
        if index < 4:
            print(line)
        elif not index % 2:
            print(line, end="\t")
        else:
            print(line)
    time.sleep(10)
