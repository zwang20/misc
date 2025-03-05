#!/usr/bin/bash

time nice -n 19 namd3 +p4 test.namd | tee test.log
