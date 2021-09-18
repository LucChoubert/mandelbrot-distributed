#! /bin/bash

INSTALL_DIR=$HOME/AUTOMATION/mandelbrot-distributed

NBPROC=`nproc --all`

for i in $(seq 1 $NBPROC);
 do
   tmp_file="$(mktemp /tmp/receive_Mandelbrot.XXXXXX)"
   echo "$i. Running Mandelbrot Receiver and logging on $tmp_file"
   nohup nice -10 $INSTALL_DIR/.venv/bin/python $INSTALL_DIR/receive_Mandelbrot.py >$tmp_file 2>&1 &
done