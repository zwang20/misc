#!/usr/bin/python
# already finished job: 6278874

import subprocess
import json
import sys
import time

from tqdm import tqdm


def loop():
    qstat_process = subprocess.run(
        [
            "ssh",
            "kdm",
            """qstat -f -Fjson | jq '.Jobs | with_entries(select(.value.Job_Owner | startswith("z5358697")))'""",
        ],
        capture_output=True,
    )
    print(qstat_process.stderr.decode("utf-8"))
    too_many_jobs = False
    if "Not Running: " in qstat_process.stdout.decode("utf-8"):
        too_many_jobs = True
    qstat_process.check_returncode()
    jobs = json.loads(qstat_process.stdout.decode("utf-8"))

    print()
    print("job_id   job_name             job_state")
    running_job_int, queuing_job_int, exiting_job_int = 0, 0, 0
    for job_id, v in jobs.items():
        # print(v.keys())
        # print(job_id.split('.')[0], v['Job_Name'], v['job_state'])
        print(
            f"{job_id.split('.')[0]: <8} {v['Job_Name']: <20} {v['job_state']} ",
            end=" ",
        )
        if "comment" in v:
            print(v["comment"])
        else:
            print()
        match v["job_state"]:
            case "R":
                running_job_int += 1
            case "Q":
                queuing_job_int += 1
            case "E":
                exiting_job_int += 1
            case x:
                print(f"Unknown job state {x}")
                assert False
                sys.exit(1)
    print()
    print(
        f"{running_job_int} jobs running, {queuing_job_int} jobs queuing, {exiting_job_int} jobs exiting"
    )
    print(f"{len(jobs)} jobs in total")
    print(f"Sleeping for 10 seconds")
    time.sleep(10)
    if too_many_jobs:
        print("Too many jobs")
        return False

    print("Checking folders on server")
    server_ls_process = subprocess.run(
        ["ssh", "kdm", "ls /srv/scratch/z5358697/automated"], capture_output=True
    )
    server_ls_process.check_returncode()
    server_folders = server_ls_process.stdout.decode("utf-8").split()[:-1]
    print(f"{len(server_folders)} folders found")

    with open("FreeSolv/database.txt") as f:
        for line in f:
            if line.startswith("mobley_"):
                prefix = line.split(";")[0].split("_")[1]
                if prefix not in server_folders:
                    break

    print(f"Generating folder {prefix}")
    subprocess.run(["python", "automate.py", prefix]).check_returncode()

    print(f"copying files")
    subprocess.run(
        ["scp", "-r", prefix, "kdm:/srv/scratch/z5358697/automated/"]
    ).check_returncode()

    print(f"submitting job")
    subprocess.run(
        [
            "ssh",
            "katana",
            f"cd /srv/scratch/z5358697/automated/{prefix} && qsub {prefix}_equilibrate",
        ]
    ).check_returncode()


while True:
    loop()
