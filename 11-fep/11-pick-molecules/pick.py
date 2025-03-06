#!/usr/bin/python
from rdkit import Chem
import collections

# get all the groups
groups = set()
with open("groups.txt") as f:
    for line in f:
        if not line.startswith("mobley_"):
            continue
        groups.update(i.strip() for i in line.split(";")[2:] if i.strip())

compounds = dict()
for i in sorted(groups):
    compounds[i] = ("not_mobley", "not real", 1000000)

no = """
mobley_1075836
mobley_20524
mobley_1636752
mobley_2310185
mobley_313406
mobley_1019269
mobley_3546460
mobley_36119
mobley_3867265
mobley_7010316
mobley_8207196
mobley_8011706
mobley_2261979
mobley_2402487
mobley_6115639
mobley_6522117
mobley_7794077
mobley_7912193
mobley_8558116
mobley_9201263
mobley_1800170
""".strip().split()

with open("groups.txt") as groups_file:
    with open("database.txt") as database_file:
        groups_file.readline()
        database_file.readline()
        database_file.readline()
        database_file.readline()
        for i in range(642):
            group_line = list(i.strip() for i in groups_file.readline().split(";"))
            database_line = list(i.strip() for i in database_file.readline().split(";"))
            assert group_line[0] == database_line[0]
            assert group_line[0].startswith("mobley_")
            if database_line[0] in no:
                continue
            num_atoms = len(Chem.MolFromSmiles(database_line[1]).GetAtoms())
            groups = (i.strip() for i in group_line[2:] if i.strip())
            for g in groups:
                if compounds[g][2] > num_atoms:
                    compounds[g] = (database_line[0], database_line[2], num_atoms)

reversed_compounds = collections.defaultdict(list)
for k, v in compounds.items():
    if v[2] < 4:
        reversed_compounds[(v[0], v[1])].append(k)

for k, v in reversed_compounds.items():
    print(f"{k[0]: <14} {k[1]: <30} chosen for {'; '.join(v)}")
