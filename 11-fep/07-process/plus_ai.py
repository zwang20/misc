#!/usr/bin/python

from sklearn import linear_model
from sklearn.model_selection import train_test_split
import numpy as np
from rdkit.Chem.rdMolDescriptors import CalcMolFormula
import subprocess
from rdkit import Chem
import matplotlib.pyplot as plt

X = []
y = []
all_atoms = {"C", "Br", "Cl", "P", "O", "S", "N", "F", "I"}
with open("combined.csv") as f:
    for line in f:
        if not line:
            continue
        line = line.split(",")
        molecule = Chem.MolFromSmiles(
            subprocess.run(
                ["grep", f"mobley_{line[0]}", "FreeSolv/database.txt"],
                capture_output=True,
            )
            .stdout.decode("utf-8")
            .split(";")[1]
        )
        d = dict()
        for x in all_atoms:
            d[x] = 0
        X.append([float(line[1])])
        for atom in molecule.GetAtoms():
            d[atom.GetSymbol()] += 1
        X[-1].extend(d.values())
        y.append(float(line[3]))
print(all_atoms)
X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)

reg = linear_model.Ridge()
reg.fit(X_train, y_train)
print(reg.coef_)
print(reg.score(X_test, y_test))
X_after = []
for i in X:
    o = reg.coef_[-1]
    for j, k in enumerate(i):
        o += k * reg.coef_[-j]
    X_after.append(o)
plt.scatter(X_after, y)
plt.show()
