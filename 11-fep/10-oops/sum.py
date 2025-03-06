#!/usr/bin/python
import subprocess
import matplotlib.pyplot as plt
import numpy as np

outputs = []
for i in range(20):
    outputs.append(
        float(
            subprocess.run(
                [
                    "grep",
                    "-F",
                    "#Free energy change for lambda window",
                    f"prod_{i}/prod_{i}.fepout",
                ],
                capture_output=True,
            )
            .stdout.decode("utf-8")
            .split()[11]
        )
    )
print(outputs)
print(sum(outputs))
test = list(
    float(i)
    for i in """0.433773
1.31907
2.2261
2.51626
2.31257
2.24506
2.42077
2.16954
-0.172994
-0.303304
-0.134046
-0.737401
-0.649164
-0.463183
-1.08164
-0.272687""".split()
)
plt.plot((np.arange(20) + 1) / 20, np.cumsum(outputs))
# plt.plot(np.arange(16) / 16, np.cumsum(test))
# plt.show()

# plt.plot(
#     np.arange(8000) / 8000,
#     list(
#         float(i.split()[-1])
#         for i in subprocess.run(
#             ["grep -F 'FepEnergy:' mobley_1017962_backwards.fepout"],
#             capture_output=True,
#             shell=True,
#         )
#         .stdout.decode("utf-8")
#         .strip()
#         .split("\n")
#     ),
# )
offset = 0.0
y = np.empty(0)
for i in range(20):
    y = np.concat(
        (
            y,
            np.array(
                list(
                    float(i.split()[-1]) + offset
                    for i in subprocess.run(
                        ["grep", "-F", "FepEnergy:", f"prod_{i}/prod_{i}.fepout"],
                        capture_output=True,
                    )
                    .stdout.decode("utf-8")
                    .strip()
                    .split("\n")
                )
            ),
        ),
    )
    offset += float(
        subprocess.run(
            [
                "grep",
                "-F",
                "Free energy change for lambda window",
                f"prod_{i}/prod_{i}.fepout",
            ],
            capture_output=True,
        )
        .stdout.decode("utf-8")
        .strip()
        .split()[11]
    )
    print(len(y))
    assert not len(y) % 10
print(y[0:2])
plt.plot((np.arange(500000) + 1) / 500000, y)
plt.show()
