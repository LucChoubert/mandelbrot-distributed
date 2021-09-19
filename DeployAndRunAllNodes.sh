#! /bin/bash
## Install and Run on all nodes

for m in 192.168.1.11 luc@alex-ubuntu1.local luc@lilian-ubuntu1.local
do

    ssh $m "bash -s" -- < /home/luc/GitHub/mandelbrot-distributed/install_Receiver.sh 
    ssh $m "$HOME/AUTOMATION/mandelbrot-distributed/run_Receiver.sh"

done