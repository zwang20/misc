#!/usr/bin/python

# TODO: implement geometry correction

"SELECT * FROM molecules WHERE compound_id in (SELECT compound_id FROM runs WHERE run_type = 'RelaxedBarGAFF') AND compound_id in (SELECT compound_id FROM runs WHERE run_type = 'FrozenBarCENSO');"

import sqlite3
import subprocess

con = sqlite3.connect("frozen_solute_model_new.db")
cur = con.cursor()

molecules = cur.execute(
    "SELECT * FROM molecules \
    WHERE compound_id in (SELECT compound_id FROM runs WHERE run_type = 'RelaxedBarGAFF' AND status = 'Received') \
    AND compound_id in (SELECT compound_id FROM runs WHERE run_type = 'FrozenBarCENSO' AND status = 'Received')"
).fetchall()
# print(molecules[1])
d = dict()

for compound_id, smiles, iupac, experimental, _, mobley, _, _, _, _, _, _ in molecules:
    print(f"{compound_id = }")
    print(compound_id)

    relaxed_path = cur.execute(
        f"SELECT local_path FROM runs WHERE {compound_id = } AND run_type = 'RelaxedBarGAFF' LIMIT 1"
    ).fetchone()[0]
    print(f"{relaxed_path = }")

    relaxed_bar = float(
        subprocess.run(
            ["tail", "-n1", f"data/{relaxed_path}/ParseFEP.log"],
            check=True,
            capture_output=True,
        )
        .stdout.decode("utf-8")
        .split()[6]
    )
    print(f"{relaxed_bar = }")

    frozen_path = cur.execute(
        f"SELECT local_path FROM runs WHERE {compound_id = } AND run_type = 'FrozenBarCENSO' LIMIT 1"
    ).fetchone()[0]
    print(f"{frozen_path = }")

    frozen_bar = float(
        subprocess.run(
            ["tail", "-n1", f"data/{frozen_path}/ParseFEP.log"],
            check=True,
            capture_output=True,
        )
        .stdout.decode("utf-8")
        .split()[6]
    )
    print(f"{frozen_bar = }")

    d[compound_id] = (smiles, iupac, experimental, mobley, relaxed_bar, frozen_bar)

print("id;smiles;iupac;experimental;mobley;relaxed;frozen;ad(em);ad(mr);ad(rf);ad(ef)")
for k, v in d.items():
    print(
        f"{k};{v[0]};{v[1]};{v[2]};{v[3]};{v[4]};{v[5]};{abs(v[2]-v[3])};{abs(v[3]-v[4])};{abs(v[4]-v[5])};{abs(v[5]-v[2])}"
    )
