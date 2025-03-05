#!/usr/bin/python

import subprocess
import json
from tqdm import tqdm
import os

ls_process = subprocess.run(["ls", "automated.old"], capture_output=True)
ls_process.check_returncode()
prefixes = ls_process.stdout.decode("utf-8").split()[:-1]
print(len(prefixes))
with open("energies.csv") as f:
    for line in f:
        prefixes.remove(line.split(",")[0])
print(len(prefixes))

with open("energies.csv", "a") as f:
    for prefix in tqdm(prefixes):
        tqdm.write(f"processing {prefix= }")

        forwards = f"automated.old/{prefix}/mobley_{prefix}_forwards.fepout"
        backwards = f"automated.old/{prefix}/mobley_{prefix}_backwards.fepout"
        if not (os.path.isfile(forwards) and os.path.isfile(backwards)):
            continue

        vmd_process: subprocess.CompletedProcess = subprocess.run(
            ["xvfb-run", "vmd", "-e", "process_fep.tcl"],
            capture_output=True,
            input=f"parsefep -forward {forwards} -backward {backwards} -bar".encode(
                "utf-8"
            ),
        )
        if vmd_process.returncode == 0:
            for line in vmd_process.stdout.decode("utf-8").split("\n"):
                if "BAR-estimator: total free energy change is" in line:
                    f.write(
                        f"{prefix},{float(line.split()[6])},{float(line.split()[11])}\n"
                    )
                    break

# print("Checking folders on server")
# server_ls_process = subprocess.run(
#     ["ssh", "katana", "ls /srv/scratch/z5358697/automated.old"], capture_output=True
# )
# server_ls_process.check_returncode()
# server_folders = server_ls_process.stdout.decode("utf-8").split()[:-1]
# print(f"{len(server_folders)} folders found")
# requires_processing.update(server_folders)

# print("Checking active jobs")
# qstat_process = subprocess.run(["ssh", "katana", """qstat -f -Fjson | jq '.Jobs | with_entries(select(.value.Job_Owner | startswith("z5358697")))'"""], capture_output=True)
# qstat_process.check_returncode()
# jobs = json.loads(qstat_process.stdout.decode("utf-8"))
# print(f"{len(jobs)} jobs found")
# for job in jobs.values():
#     requires_processing.discard(job["Job_Name"].split("_")[0])


# energies: dict[str, tuple[float, float]] = dict()
# print(f"{len(requires_processing)} requires processing")
# for prefix in requires_processing:
#     subprocess.run(["mkdir", "-p", f"outputs/{prefix}"]).check_returncode()
#     subprocess.run(
#         [
#             "scp",
#             f"katana:/srv/scratch/z5358697/automated.old/{prefix}/mobley_{prefix}_forwards.fepout",
#             f"outputs/{prefix}/mobley_{prefix}_forwards.fepout",
#         ]
#     )
#     subprocess.run(
#         [
#             "scp",
#             f"katana:/srv/scratch/z5358697/automated.old/{prefix}/mobley_{prefix}_backwards.fepout",
#             f"outputs/{prefix}/mobley_{prefix}_backwards.fepout",
#         ]
#     )

#     vmd_process: subprocess.CompletedProcess = subprocess.run(
#         ["xvfb-run", "vmd", "-e", "process_fep.tcl"],
#         capture_output=True,
#         input=f"parsefep -forward outputs/{prefix}/mobley_{prefix}_forwards.fepout -backward outputs/{prefix}/mobley_{prefix}_backwards.fepout -bar".encode(
#             "utf-8"
#         ),
#     )
#     vmd_process.check_returncode()
#     for line in vmd_process.stdout.decode("utf-8").split("\n"):
#         if "BAR-estimator: total free energy change is" in line:
#             energies[prefix] = (float(line.split()[6]), float(line.split()[11]))
#             break
#
# for k, v in energies.items():
#     # TODO: fix this o(n^2) nightmare
#     with open("FreeSolv/database.txt") as f:
#         for line in f:
#             if line.startswith("mobley_"):
#                 data = line.split(";")
#                 prefix = data[0].split("_")[1]
#                 if prefix == k:
#                     print(f"{k},{v[0]},{v[1]},{data[3]},{data[4]},{data[5]},{data[6]}")
#                     break
