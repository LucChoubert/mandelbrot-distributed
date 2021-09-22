#! /bin/bash
## Install the mandelbrot worker environment, both the dequeuer one as well as the mandelbrot binary one


HOSTNAME=`hostname`

if [ "$HOSTNAME" = "Luc-Ubuntu" ]; then
    echo "Should not run in that machine, Exiting"
    exit 1
else
    echo "## Running deployment on $HOSTNAME ##"
    pkill -f receive_Mandelbrot.py
    pkill -f Mandelbrot

    BASE_DIR=$HOME/AUTOMATION
    mkdir -p $BASE_DIR
    cd $BASE_DIR

    INSTALL_DIR=$BASE_DIR/mandelbrot-cpp
    rm -rf $INSTALL_DIR
    cd $BASE_DIR
    git clone https://github.com/LucChoubert/mandelbrot-cpp.git
 
    
    cd $INSTALL_DIR
    make clean
    make build
    make install


    INSTALL_DIR=$BASE_DIR/mandelbrot-distributed
    rm -rf $INSTALL_DIR
    cd $BASE_DIR
    git clone https://github.com/LucChoubert/mandelbrot-distributed.git

    cd $INSTALL_DIR
    python3.9 -m venv .venv
    source .venv/bin/activate
    pip3 install -r requirements.txt

fi