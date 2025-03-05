#!/usr/bin/bash
cd tcouple_1 && { qsub tcouple_1; cd ..; }
cd tcouple_2 && { qsub tcouple_2; cd ..; }
cd tcouple_5 && { qsub tcouple_5; cd ..; }
cd tcouple_10 && { qsub tcouple_10; cd ..; }
cd tcouple_20 && { qsub tcouple_20; cd ..; }
cd tcouple_50 && { qsub tcouple_50; cd ..; }
cd tcouple_100 && { qsub tcouple_100; cd ..; }
cd tcouple_200 && { qsub tcouple_200; cd ..; }
cd tcouple_500 && { qsub tcouple_500; cd ..; }
cd tcouple_1000 && { qsub tcouple_1000; cd ..; }
cd tcouple_2000 && { qsub tcouple_2000; cd ..; }
cd tcouple_5000 && { qsub tcouple_5000; cd ..; }
cd tcouple_10000 && { qsub tcouple_10000; cd ..; }
