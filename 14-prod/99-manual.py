"""
manual.py

for when things go wrong
"""

# pylint: disable=C0103,E1135

import sys

from common import get_previous_files, get_prefix_list

print("Things have gone wrong")

batch = int(input("Batch number: "))
previous_files = get_previous_files()
assert f"{batch}.txt" in previous_files, f"{batch}.txt not found in batch/"
print()

print("Select mode:")
print("0: first bad")
print("1: select bad")
mode = int(input("Mode: "))
print()

prefix_list = get_prefix_list(batch)
todo_list = []

if mode == 0:
    first_bad = int(input("first bad: "))
    assert str(first_bad) in prefix_list, f"{first_bad} not found in batch {batch}"
    bad = False
    for prefix in prefix_list:
        if prefix == str(first_bad):
            bad = True
        if bad:
            todo_list.append(prefix)

elif mode == 1:
    while bad_prefix := int(input("Bad prefix: ")):
        assert (
            str(bad_prefix) in prefix_list
        ), f"{bad_prefix} not found in batch {batch}"
        todo_list.append(str(bad_prefix))
print()

if not todo_list:
    print("Nothing to do")
    sys.exit()
print("fixing", " ".join(todo_list))

# step = int(input("Step number: "))
# if step == 0:
#     print("00: pick")
#     print("just rerun it lol")
# elif step == 1:
#     print("01: run gauss")
# else:
#     print("Not implemented")

print("Generating temp list 99.txt")
with open("batch/99.txt", "w", encoding="utf-8") as f:
    for prefix in todo_list:
        f.write(f"{prefix}\n")
