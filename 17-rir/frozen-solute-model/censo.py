import sys

from common import katana_censo

assert len(sys.argv) == 2, (sys.argv, len(sys.argv))
assert sys.argv[1].startswith("data/"), sys.argv[1]

with open(f"{sys.argv[1]}", "w") as f:
    f.write(katana_censo.format())
