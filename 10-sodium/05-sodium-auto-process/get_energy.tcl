
mol new ionized.pdb
mol addfile output.vel type namdbin waitfor all

set all [atomselect top all]
# set hyd [atomselect top "mass < 1.009"]
set fil [open mass_velocities.dat w]
# set file2 [open raw.dat w]
# foreach m [$all get mass] v [$all get {x y z}] {
# puts $m
# puts $fil [expr 0.5* $m * [vecdot $v $v]]
# }
# foreach v [$hyd get {x y z}] {
# puts $file2 [vecdot $v $v]
# }

foreach m [$all get mass] v [$all get {x y z}] {
puts $fil $m,[vecdot $v $v]
}

# close $file2
close $fil
