#!/usr/bin/bash
cd hmore_1 && { qsub hmore_1; cd ..; }
cd hmore_2 && { qsub hmore_2; cd ..; }
cd hmore_5 && { qsub hmore_5; cd ..; }
cd hmore_10 && { qsub hmore_10; cd ..; }
cd hmore_20 && { qsub hmore_20; cd ..; }
cd hmore_50 && { qsub hmore_50; cd ..; }
cd hmore_100 && { qsub hmore_100; cd ..; }
cd hmore_200 && { qsub hmore_200; cd ..; }
cd hmore_500 && { qsub hmore_500; cd ..; }
cd hmore_1000 && { qsub hmore_1000; cd ..; }
cd hmore_2000 && { qsub hmore_2000; cd ..; }
cd hmore_5000 && { qsub hmore_5000; cd ..; }
cd hmore_10000 && { qsub hmore_10000; cd ..; }
