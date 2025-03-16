#!/usr/bin/python

import subprocess
import time

MAX_SIZE = 104857600


def get_files():

    output = []

    git_process = subprocess.run(["git", "status", "-u"], capture_output=True)

    print(git_process.stderr.decode("utf-8"))
    git_process.check_returncode()

    for line in git_process.stdout.decode("utf-8").split("\n"):
        if line.startswith("\t") and not line.endswith("/") and not line.endswith(")"):
            if ":" in line:
                output.append(line.split(maxsplit=1)[1])
            else:
                output.append(line.strip())

    return output


subprocess.run(['git', 'pull'], check=True)

for filename in get_files():
    print(filename)
    subprocess.run(["git", "add", filename]).check_returncode()
    subprocess.run(["git", "commit", "-m", filename]).check_returncode()
    subprocess.run(["git", "push"]).check_returncode()
    time.sleep(10)
