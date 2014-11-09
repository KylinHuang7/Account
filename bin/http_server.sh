#!/bin/sh
PYTHON=/usr/local/bin/python2.6
cd /var/www/accounts/bin

function start(){
    cd ..
    setsid $PYTHON -m webserver 8020 </dev/null >>logs/web.log 2>&1 &
    echo $! > logs/web.pid
    cd bin
}

function stop(){
    stop_process ../logs/web.pid
}

function stop_process(){
    pid=`cat $1`
    kill $pid
    while kill -0 $pid 2>/dev/null; do
        echo -n .
        sleep 1
    done
    echo -e "\033[1;31mstopped\033[0m"
    rm -f $1
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        stop >/dev/null
        start
        echo restarted
        ;;
    *)
        echo "Usage: $0 start|stop|restart"
        exit 1
esac

