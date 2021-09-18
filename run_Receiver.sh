#! /bin/bash

NBPROC=`nproc --all`

for i in $(seq 1 $NBPROC);
 do
   tmp_file="$(mktemp /tmp/myscript.XXXXXX)"
   echo "$i. Running Mandelbrot Receiver and logging on $tmp_file"
   nohup /home/luc/GitHub/mandelbrot-distributed/.venv/bin/python /home/luc/GitHub/mandelbrot-distributed/receive_Mandelbrot.py >$tmp_file 2>&1 &
done