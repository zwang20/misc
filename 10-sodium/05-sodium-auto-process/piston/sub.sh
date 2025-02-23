#!/usr/bin/bash
cd piston_1 && { qsub piston_1; cd ..; }
cd piston_2 && { qsub piston_2; cd ..; }
cd piston_5 && { qsub piston_5; cd ..; }
cd piston_10 && { qsub piston_10; cd ..; }
cd piston_20 && { qsub piston_20; cd ..; }
cd piston_50 && { qsub piston_50; cd ..; }
cd piston_100 && { qsub piston_100; cd ..; }
cd piston_200 && { qsub piston_200; cd ..; }
cd piston_500 && { qsub piston_500; cd ..; }
cd piston_1000 && { qsub piston_1000; cd ..; }
cd piston_2000 && { qsub piston_2000; cd ..; }
cd piston_5000 && { qsub piston_5000; cd ..; }
cd piston_10000 && { qsub piston_10000; cd ..; }
