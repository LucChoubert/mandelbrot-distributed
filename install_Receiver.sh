#! /bin/bash

HOSTNAME=`hostname`

if [ "$HOSTNAME" = "Luc-Ubuntu" ]; then
    echo "Should not run in that machine, Exiting"
    exit 1
else

    BASE_DIR=$HOME/AUTOMATION
    mkdir -p $BASE_DIR
    cd $BASE_DIR
    rm -rf mandelbrot-distributed

    git clone https://github.com/LucChoubert/mandelbrot-distributed.git

    INSTALL_DIR=$BASE_DIR/mandelbrot-distributed
    cd $INSTALL_DIR
    python3 -m venv .env
    source .env/bin/activate
    pip3 install -r requirements.txt
fi