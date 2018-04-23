#!/bin/bash

pushd `dirname $0` > /dev/null
BASEDIR=`pwd`
popd > /dev/null

init() {
    mkdir -p /data/logs/ims
    mkdir -p /data/logs/imr
    mkdir -p /data/logs/im
    mkdir -p /data/im
}

start() {
    nohup $BASEDIR/ims -log_dir=/data/logs/ims ims.cfg >/data/logs/ims/ims.log 2>&1 &

    nohup $BASEDIR/imr -log_dir=/data/logs/imr imr.cfg >/data/logs/imr/imr.log 2>&1 &

    nohup $BASEDIR/im -log_dir=/data/logs/im im.cfg >/data/logs/im/im.log 2>&1 &

}

stop() {
    killall im
    killall ims
    killall imr
}

case "$1" in
    start)
        start
        ;;

    stop)
        stop
        ;;
    init)
        init
        ;;
    *)
        echo $"Usage: $0 {start|init|stop}"
        exit 2
esac
