#!/usr/bin/bash

nice -n 19 namd3 +p4 sodium.conf | tee sodium.log
