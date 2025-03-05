#!/usr/bin/bash
cd hydrogen_1 && { qsub hydrogen_1; cd ..; }
cd hydrogen_2 && { qsub hydrogen_2; cd ..; }
cd hydrogen_5 && { qsub hydrogen_5; cd ..; }
cd hydrogen_10 && { qsub hydrogen_10; cd ..; }
cd hydrogen_20 && { qsub hydrogen_20; cd ..; }
cd hydrogen_50 && { qsub hydrogen_50; cd ..; }
cd hydrogen_100 && { qsub hydrogen_100; cd ..; }
cd hydrogen_200 && { qsub hydrogen_200; cd ..; }
cd hydrogen_500 && { qsub hydrogen_500; cd ..; }
cd hydrogen_1000 && { qsub hydrogen_1000; cd ..; }
cd hydrogen_2000 && { qsub hydrogen_2000; cd ..; }
cd hydrogen_5000 && { qsub hydrogen_5000; cd ..; }
cd hydrogen_10000 && { qsub hydrogen_10000; cd ..; }
