#!/usr/bin/python

import subprocess
import time

MAX_SIZE = 104857600


def get_files():

    output = []
    deleted = []

    git_process = subprocess.run(
        ["git", "status", "-u"], capture_output=True, check=True
    )

    print(git_process.stderr.decode("utf-8"))

    for line in git_process.stdout.decode("utf-8").split("\n"):
        if line.startswith("\t") and not line.endswith("/") and not line.endswith(")"):
            if "deleted:" in line:
                deleted.append(line.split(maxsplit=1)[1])
            elif ":" in line:
                output.append(line.split(maxsplit=1)[1])
            else:
                output.append(line.strip())

    return deleted, output


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


subprocess.run(["git", "pull"], check=True)
subprocess.run(["git", "reset"], check=True)
subprocess.run(["git", "push"], check=True)

deleted, output = get_files()

for files in chunks(deleted, 128):
    start = time.perf_counter()
    subprocess.run(["git", "add"] + files, check=True)
    subprocess.run(["git", "commit", "-m", "remove files"]).check_returncode()
    subprocess.run(["git", "push"]).check_returncode()
    duration = time.perf_counter() - start
    if duration < 5:
        time.sleep(5 - duration)

for files in chunks(output, 8):
    start = time.perf_counter()
    subprocess.run(["git", "add"] + files, check=True)
    subprocess.run(["git", "commit", "-m", "add files"]).check_returncode()
    subprocess.run(["git", "push"]).check_returncode()
    duration = time.perf_counter() - start
    if duration < 5:
        time.sleep(5 - duration)

