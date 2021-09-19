#! /bin/bash
## Install the mandelbrot worker environment, both the dequeuer one as well as the mandelbrot binary one


HOSTNAME=`hostname`

if [ "$HOSTNAME" = "Luc-Ubuntu" ]; then
    echo "Should not run in that machine, Exiting"
    ssh alex-ubuntu1.local:/home/luc/AUTOMATION/mandelbrot-distributed/run_Receiver.sh
    exit 1
else

    pkill -f receive_Mandelbrot.py

    BASE_DIR=$HOME/AUTOMATION
    mkdir -p $BASE_DIR
    cd $BASE_DIR

    rm -rf mandelbrot-cpp

    git clone https://github.com/LucChoubert/mandelbrot-cpp.git
 
    INSTALL_DIR=$BASE_DIR/mandelbrot-cpp
    cd $INSTALL_DIR
    make clean
    make build
    make install



    rm -rf mandelbrot-distributed

    git clone https://github.com/LucChoubert/mandelbrot-distributed.git

    INSTALL_DIR=$BASE_DIR/mandelbrot-distributed
    cd $INSTALL_DIR
    python3 -m venv .venv
    source .venv/bin/activate
    pip3 install -r requirements.txt

fi