#!/usr/bin/python
for mode in ["fw0", "fw1", "bw0", "bw1", "fwf0", "fwf1", "bwf0", "bwf1"]:
	print(f"cd {mode}")
	print("cp ../prep/mobley_{prefix}_equil.coor .")
	print("cp ../prep/mobley_{prefix}_equil.vel  .")
	print("cp ../prep/mobley_{prefix}_equil.xsc  .")
	print(f"qsub {{prefix}}_{mode}")
	print("cd ..")
