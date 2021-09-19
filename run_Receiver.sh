#! /bin/bash
## Run the mandelbrot dequeurs as many as there are core on the machines
## Kill all of the running one first and clean the previous log files

INSTALL_DIR=$HOME/AUTOMATION/mandelbrot-distributed

NBPROC=`nproc --all`

pkill -f receive_Mandelbrot.py
rm -f /tmp/receive_Mandelbrot.*

for i in $(seq 1 $NBPROC);
 do
   tmp_file="$(mktemp /tmp/receive_Mandelbrot.XXXXXX)"
   echo "$i. Running Mandelbrot Receiver and logging on $tmp_file"
   nohup nice -10 $INSTALL_DIR/.venv/bin/python $INSTALL_DIR/receive_Mandelbrot.py >$tmp_file 2>&1 &
done