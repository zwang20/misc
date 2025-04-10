#!/usr/bin/python


"SELECT * FROM molecules WHERE compound_id in (SELECT compound_id FROM runs WHERE run_type = 'RelaxedBarGAFF') AND compound_id in (SELECT compound_id FROM runs WHERE run_type = 'FrozenBarCENSO');"

import sqlite3
import subprocess

con = sqlite3.connect("frozen_solute_model_new.db")
cur = con.cursor()

molecules = cur.execute(
    "SELECT * FROM molecules \
    WHERE compound_id in (SELECT compound_id FROM runs WHERE run_type = 'RelaxedBarGAFF' AND status = 'Received') \
    AND compound_id in (SELECT compound_id FROM runs WHERE run_type = 'FrozenBarCENSO' AND status = 'Received') \
    AND compound_id in (SELECT compound_id FROM runs WHERE run_type = 'VacuumCREST' AND status = 'Received') \
    AND compound_id in (SELECT compound_id FROM runs WHERE run_type = 'VacuumCENSO' AND status = 'Received')"
).fetchall()
# print(molecules[1])
d = dict()

for compound_id, smiles, iupac, experimental, _, mobley, _, _, _, _, _, _ in molecules:
    print(f"{compound_id = }")

    vacuum_censo_path = cur.execute(
        f"SELECT local_path FROM runs WHERE {compound_id = } AND run_type = 'VacuumCENSO' LIMIT 1"
    ).fetchone()[0]
    print(f"{vacuum_censo_path = }")

    try:
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
        print(f"{vacuum_censo_conf = }")

        vacuum_censo_energy = float(
            subprocess.run(
                [
                    "jq",
                    f".results.{vacuum_censo_conf}.sp.energy",
                    f"data/{vacuum_censo_path}/3_REFINEMENT.json",
                ],
                check=True,
                capture_output=True,
            )
            .stdout.decode("utf-8")
            .strip()
        )
        print(f"{vacuum_censo_energy = }")

    except subprocess.CalledProcessError:
        continue

    water_censo_path = cur.execute(
        f"SELECT local_path FROM runs WHERE {compound_id = } AND run_type = 'CENSO' LIMIT 1"
    ).fetchone()[0]
    print(f"{water_censo_path = }")

    water_censo_conf = (
        subprocess.run(
            [f"head -n 2 data/{water_censo_path}/3_REFINEMENT.xyz | tail -n 1"],
            check=True,
            capture_output=True,
            shell=True,
        )
        .stdout.decode("utf-8")
        .strip()
    )
    print(f"{water_censo_conf = }")

    water_censo_energy = float(
        subprocess.run(
            [
                "jq",
                f".results.{water_censo_conf}.gsolv.energy_gas",
                f"data/{water_censo_path}/3_REFINEMENT.json",
            ],
            check=True,
            capture_output=True,
        )
        .stdout.decode("utf-8")
        .strip()
    )
    print(f"{water_censo_energy = }")

    correction_hartree = water_censo_energy - vacuum_censo_energy
    print(f"{correction_hartree = }")
    correction = correction_hartree * 627.509474
    print(f"{correction = }")

    relaxed_path = cur.execute(
        f"SELECT local_path FROM runs WHERE {compound_id = } AND run_type = 'RelaxedBarGAFF' LIMIT 1"
    ).fetchone()[0]
    print(f"{relaxed_path = }")

    try:
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
    except IndexError:
        continue

    frozen_path = cur.execute(
        f"SELECT local_path FROM runs WHERE {compound_id = } AND run_type = 'FrozenBarCENSO' LIMIT 1"
    ).fetchone()[0]
    print(f"{frozen_path = }")

    try:
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
    except IndexError:
        continue

    d[compound_id] = (
        smiles,
        iupac,
        experimental,
        mobley,
        relaxed_bar,
        frozen_bar,
        correction,
    )

print("id;smiles;iupac;experimental;mobley;relaxed;frozen;correction")
for k, v in d.items():
    print(f"{k};{v[0]};{v[1]};{v[2]};{v[3]};{v[4]};{v[5]};{v[6]}")
