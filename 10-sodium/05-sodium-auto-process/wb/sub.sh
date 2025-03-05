#!/usr/bin/bash
cd wb_1 && { qsub wb_1; cd ..; }
cd wb_2 && { qsub wb_2; cd ..; }
cd wb_5 && { qsub wb_5; cd ..; }
cd wb_10 && { qsub wb_10; cd ..; }
cd wb_20 && { qsub wb_20; cd ..; }
cd wb_50 && { qsub wb_50; cd ..; }
cd wb_100 && { qsub wb_100; cd ..; }
cd wb_200 && { qsub wb_200; cd ..; }
cd wb_500 && { qsub wb_500; cd ..; }
cd wb_1000 && { qsub wb_1000; cd ..; }
cd wb_2000 && { qsub wb_2000; cd ..; }
cd wb_5000 && { qsub wb_5000; cd ..; }
cd wb_10000 && { qsub wb_10000; cd ..; }
