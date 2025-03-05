#!/usr/bin/bash
cd hless_1 && { qsub hless_1; cd ..; }
cd hless_2 && { qsub hless_2; cd ..; }
cd hless_5 && { qsub hless_5; cd ..; }
cd hless_10 && { qsub hless_10; cd ..; }
cd hless_20 && { qsub hless_20; cd ..; }
cd hless_50 && { qsub hless_50; cd ..; }
cd hless_100 && { qsub hless_100; cd ..; }
cd hless_200 && { qsub hless_200; cd ..; }
cd hless_500 && { qsub hless_500; cd ..; }
cd hless_1000 && { qsub hless_1000; cd ..; }
cd hless_2000 && { qsub hless_2000; cd ..; }
cd hless_5000 && { qsub hless_5000; cd ..; }
cd hless_10000 && { qsub hless_10000; cd ..; }
