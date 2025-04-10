#!/usr/bin/python

# // DELETE FROM runs WHERE local_path=-1;

import sqlite3
import subprocess

con = sqlite3.connect("frozen_solute_model_new.db")
cur = con.cursor()


def main():
    # returns a path if invalid path is found, else None

    vacuum_censo_paths = cur.execute("SELECT local_path FROM runs WHERE run_type = 'VacuumCENSO'").fetchall()
    for i in vacuum_censo_paths:
        vacuum_censo_path = i[0]
        vacuum_censo_conf = (
            subprocess.run(
                [f"head -n 2 data/{vacuum_censo_path}/3_REFINEMENT.xyz | tail -n 1"],
                check=True,
                capture_output=True,
                shell=True,
            )
            .stdout.decode("utf-8")
            .strip()
        )
        if not vacuum_censo_conf.startswith('CONF'):
            return vacuum_censo_path

    relaxed_paths = cur.execute(
        "SELECT local_path FROM runs WHERE run_type = 'RelaxedBarGAFF'"
    ).fetchall()

    for i in relaxed_paths:
        relaxed_path = i[0]
        try:
            float(
                subprocess.run(
                    ["tail", "-n1", f"data/{relaxed_path}/ParseFEP.log"],
                    check=True,
                    capture_output=True,
                )
                .stdout.decode("utf-8")
                .split()[6]
            )
        except IndexError:
            return relaxed_path

    frozen_paths = cur.execute(
        "SELECT local_path FROM runs WHERE run_type = 'FrozenBarCENSO'"
    ).fetchall()

    for i in frozen_paths:
        frozen_path = i[0]

        try:
            float(
                subprocess.run(
                    ["tail", "-n1", f"data/{frozen_path}/ParseFEP.log"],
                    check=True,
                    capture_output=True,
                )
                .stdout.decode("utf-8")
                .split()[6]
            )
        except IndexError:
            return frozen_path


local_path = main()
if not local_path:
    exit()
print(f"{local_path = }")

compound_id, run_type = cur.execute(
    f"SELECT compound_id, run_type FROM runs WHERE {local_path = }",
).fetchall()[0]
print(f"{compound_id = }")
print(f"{run_type = }")

for i in cur.execute(
    f"SELECT * FROM runs WHERE {compound_id = }",
).fetchall():
    print(i)
