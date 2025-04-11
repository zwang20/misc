"""
convert3

converts runs if and only if the conf is the same in step 2 and 3
"""

import os
import sqlite3
import subprocess

con = sqlite3.connect("frozen_solute_model_new.db")
cur = con.cursor()

censo_paths = cur.execute(
    "SELECT local_path FROM runs WHERE run_type = 'CENSO'"
).fetchall()

for i in censo_paths:
    censo_path = i[0]

    step_2_conf = (
        subprocess.run(
            [f"head -n 2 data/{vacuum_censo_path}/2_OPTIMIZATION.xyz | tail -n 1"],
            check=True,
            capture_output=True,
            shell=True,
        )
        .stdout.decode("utf-8")
        .strip()
    )
    assert step_2_conf.startswith("CONF"), step_2_conf

    step_3_conf = (
        subprocess.run(
            [f"head -n 2 data/{vacuum_censo_path}/3_REFINEMENT.xyz | tail -n 1"],
            check=True,
            capture_output=True,
            shell=True,
        )
        .stdout.decode("utf-8")
        .strip()
    )
    assert step_3_conf.startswith("CONF"), step_3_conf

    assert step_2_conf == step_3_conf, (step_2_conf, step_3_conf)
