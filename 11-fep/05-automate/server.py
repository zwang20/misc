#!/usr/bin/python

import subprocess
import json
import sys
import time
from datetime import datetime
from typing import Optional
from tqdm import tqdm  # type: ignore[import-untyped]


def get_server_folders(path: str = "/srv/z5358697/automated/") -> list[str]:
    server_ls_process = subprocess.run(
        ["ssh", "kdm", "ls /srv/scratch/z5358697/automated"], capture_output=True
    )
    server_ls_process.check_returncode()
    return server_ls_process.stdout.decode("utf-8").split()[:-1]


def get_jobs() -> tuple[list[str], int, int, int, bool]:
    qstat_process = subprocess.run(
        [
            "ssh",
            "kdm",
            """qstat -f -Fjson | jq '.Jobs | with_entries(select(.value.Job_Owner | startswith("z5358697")))'""",
        ],
        capture_output=True,
    )

    qstat_process.check_returncode()
    too_many_jobs: bool = (
        qstat_process.stdout.decode("utf-8").count("Not Running: ") > 1
    )
    jobs = json.loads(qstat_process.stdout.decode("utf-8"))
    running_job_int, queuing_job_int, exiting_job_int = 0, 0, 0
    output = []

    for job_id, v in jobs.items():
        output.append(
            f"{job_id.split('.')[0]: <8} {v['Job_Name']: <20} {v['job_state']}  "
        )
        if "comment" in v:
            output[-1] += v["comment"]
        match v["job_state"]:
            case "R":
                running_job_int += 1
            case "Q":
                queuing_job_int += 1
            case "E":
                exiting_job_int += 1
            case x:
                print(f"Unknown job state {x}")
                sys.exit(1)

    return output, running_job_int, queuing_job_int, exiting_job_int, too_many_jobs


prefixes = []
with open("FreeSolv/database.txt") as f:
    for line in f:
        if line.startswith("mobley_"):
            prefixes.append(line.split(";")[0].split("_")[1])
print(f"{len(prefixes) = } loaded")

server_folders = get_server_folders()
for sf in server_folders:
    prefixes.remove(sf)

for prefix in tqdm(prefixes):
    if prefix in server_folders:
        continue

    tqdm.write(f"processing {prefix = }")

    # main loop
    while True:
        output, running_job_int, queuing_job_int, exiting_job_int, too_many_jobs = (
            get_jobs()
        )
        tqdm.write("job_id   job_name             job_state")
        for line in output:
            tqdm.write(line)
        tqdm.write(
            f"{running_job_int} jobs running, {queuing_job_int} jobs queuing, {exiting_job_int} jobs exiting"
        )
        with open("log.csv", "a") as f:
            f.write(
                f"{datetime.now()},{running_job_int},{queuing_job_int},{exiting_job_int}\n"
            )

        if too_many_jobs:
            tqdm.write("Too many jobs, sleeping for 10 seconds")
            time.sleep(10)
            continue

        tqdm.write(f"Generating folder {prefix}")
        subprocess.run(["python", "automate.py", prefix]).check_returncode()

        tqdm.write(f"copying files")
        subprocess.run(
            ["scp", "-r", prefix, "kdm:/srv/scratch/z5358697/automated/"]
        ).check_returncode()

        tqdm.write(f"submitting job")
        subprocess.run(
            [
                "ssh",
                "katana",
                f"cd /srv/scratch/z5358697/automated/{prefix} && qsub {prefix}_equilibrate",
            ]
        ).check_returncode()
        time.sleep(10)
        break
