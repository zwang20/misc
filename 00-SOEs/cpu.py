#!/usr/bin/python

import json

with open("pbsnodes.json") as f:
    d = json.load(f)


t = dict()

for k, v in d["nodes"].items():
    print(
        k,
        f'{v["resources_available"]["cputype"]:15}',
        v["resources_available"]["ncpus"],
        sep="\t",
        end="\t",
    )
    if "ngpus" in v["resources_available"]:
        print(v["resources_available"]["ngpus"], v["resources_available"]["gpu_model"])
    else:
        print(0)
    # print(v.keys())
    # print(v["sharing"])
    # print(v["resources_available"]["cputype"])
